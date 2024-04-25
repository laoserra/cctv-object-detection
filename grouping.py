#!/usr/bin/env python3

import sys
import pandas as pd
import config_grouping as cg
import boto3
import os
import logging

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

total_groups = cg.GROUPS_IN_A_DAY
camera_ref_names = cg.load_camera_names('camera_ref.names')


def convert_to_datetime(series_dt_obj):
    series_date = pd.to_datetime(series_dt_obj,
                                 format="%Y-%m-%d %H:%M:%S%z")
    series_date = series_date.dt.tz_convert('Europe/London')

    return series_date


def clean_data(df_raw):
    """Filter attributes of interest for grouping.

    And convert string to datetime format.
    """
    # this operation is necessary because conversion to datetime only
    # occurs if datetime is the same among all records. However, this
    # situation does not happen when clocks change.
    if (df_raw['image_capt'].str.contains("\+00:00").any() &
            df_raw['image_capt'].str.contains("\+01:00").any()):
        # .copy() is important to avoid a copy/view warning
        df_GMT = df_raw[df_raw['image_capt'].str.contains("\+00:00")].copy()
        df_GMT['image_capt'] = convert_to_datetime(df_GMT['image_capt'])
        df_BST = df_raw[df_raw['image_capt'].str.contains("\+01:00")].copy()
        df_BST['image_capt'] = convert_to_datetime(df_BST['image_capt'])
        df = pd.concat([df_GMT, df_BST])
        df = df.loc[:, ['image_proc', 'image_capt', 'camera_ref']]
    else:
        df = pd.DataFrame()
        df['image_proc'] = df_raw['image_proc']
        df['image_capt'] = convert_to_datetime(df_raw['image_capt'])
        df['camera_ref'] = df_raw['camera_ref']

    return df


def grouping(df):
    """Creates and analyses batches of processed images."""

    df_dup = pd.DataFrame(columns=['image_proc', 'image_capt',
                                   'camera_ref'])
    cams_per_group = []
    df.set_index('image_capt', inplace=True, drop=False)
    grouped_df = df.groupby(pd.Grouper(freq='30min', closed='left'))
    number_of_groups = 0
    for group_id, group in grouped_df:
        number_of_groups += 1
        cams_per_group.append(len(group.camera_ref.unique()))
        if group.duplicated(subset=['camera_ref']).any():
            df_temp = group[group.duplicated(subset=['camera_ref'],
                                             keep=False)]
            df_dup = pd.concat([df_dup, df_temp])
    average_cams_group = round(sum(cams_per_group) / number_of_groups, 1)

    return df_dup, average_cams_group, number_of_groups


def check_cameras(df_raw):
    """Analyses cameras/presets present in the data."""
    cameras_in_file = df_raw.camera_ref.unique().tolist()
    new_cameras = set(cameras_in_file) - set(camera_ref_names)
    missing_cameras = set(camera_ref_names) - set(cameras_in_file)

    return new_cameras, missing_cameras


def analyse_data(dataframe, file_path):
    """Logs analysis of the data."""
    data_issues = ()

    if not dataframe.empty:
        cleaned_data = clean_data(dataframe)
        df, cams_group, groups = grouping(cleaned_data)
        # checks for errors in batches of images
        logger.info(f'Found {groups} batches of images in %s expected',
                    total_groups)
        if df.empty:
            logger.info('Found no duplicated cameras per batch')
        else:
            data_issues = data_issues + ('duplicated cameras',)
            logger.error('Found duplicated cameras. ' +
                         'Print below shows duplicated camera(s) ' +
                         'alongside correct camera, for debugging.')
            logger.debug(df.to_string(index=False))
        logger.info("There\'s a mean of %s cameras per batch" +
                    " in %s expected in the day",
                    cams_group,
                    len(camera_ref_names))
        # checks for absent cameras and/or for new cameras added
        new_cams, missing_cams = check_cameras(dataframe)
        if new_cams:
            logger.warning('Detected %s new cameras/presets in the data',
                           new_cams)
        else:
            logger.info('No new cameras/presets found in the processed file')
        if missing_cams:
            logger.warning('Missing camera/presets in the processed file: %s',
                           missing_cams)
        else:
            logger.info('No missing cameras/presets found in file')

    else:
        logger.error('Found no data in the source file!')
        logger.info('Source file: %s', file_path)
        data_issues = data_issues + ('empty file',)

    return data_issues


def upload_to_s3(file_path, model_type, basename):
    s3_client = boto3.client('s3')
    try:
        s3_client.upload_file(
                Filename=file_path,
                Bucket='cctv-data-ubdc-ac-uk',
                Key=f'cctv-server-reports/v1/{model_type}/{basename}')
    except Exception as e:
        logger.error('An error occurred when trying to upload the file "%s"' +
                     ' to AWS bucket: %s', basename, e)
    else:
        logger.info('file "%s" uploaded successfully to AWS bucket', basename)


def main(file_path):
    df = pd.read_csv(file_path)
    data_issues = analyse_data(df, file_path)
    if not data_issues:
        logger.info('No issues found in the data')
        model = file_path.split('-')
        model_type = model[-2]
        basename = os.path.basename(file_path)
        if model_type in ['tf2', 'yolo']:
            upload_to_s3(file_path, model_type, basename)
        else:
            logger.error('model "%s" not found. Which AWS bucket' +
                         ' to upload the file to?',
                         model[3])
            data_issues = data_issues + ('model not found',)
    else:
        logger.error('Found "%s" error(s). DATA NOT UPLOADED TO API.',
                     ", ".join(str(item) for item in data_issues))


if __name__ == "__main__":
    main(sys.argv[1])
