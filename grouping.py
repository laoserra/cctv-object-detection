#!/usr/bin/env python3

import sys
import pandas as pd
import config_grouping as cg
import boto3
import os

total_groups = cg.GROUPS_IN_A_DAY 
camera_ref_names = cg.load_camera_names('camera_ref.names')
threshold = cg.THRESHOLD
data_issues = ()
s3_client = boto3.client('s3')

def clean_data(df_raw):
    '''Filter attributes of interest for grouping.

    The source file is the CCTV daily counts.'''
    if (df_raw['image_proc'].str.contains("\+00:00").any() & 
            df_raw['image_proc'].str.contains("\+01:00").any()):
        # .copy() is important to avoid a copy/view warning 
        df_GMT = df_raw[df_raw['image_proc'].str.contains("\+00:00")].copy()
        df_GMT['image_proc'] = pd.to_datetime(df_GMT['image_proc'],
                                              format="%Y-%m-%d %H:%M:%S%z")
        df_GMT['image_proc'] = df_GMT['image_proc'].dt.tz_convert('Europe/London')
        df_BST = df_raw[df_raw['image_proc'].str.contains("\+01:00")].copy()
        df_BST['image_proc'] = pd.to_datetime(df_BST['image_proc'],
                                              format="%Y-%m-%d %H:%M:%S%z")
        df_BST['image_proc'] = df_BST['image_proc'].dt.tz_convert('Europe/London')
        df = pd.concat([df_GMT, df_BST])
        df.sort_values(by=['image_proc'], inplace=True)
        df = df.loc[:, ['image_proc', 'image_capt', 'camera_ref']]
    else:
        df = pd.DataFrame()
        df['image_proc'] = pd.to_datetime(df_raw['image_proc'],
                                          format="%Y-%m-%d %H:%M:%S%z")
        df[ 'image_capt'] = df_raw['image_capt']
        df['camera_ref'] = df_raw['camera_ref']
        df.sort_values(by=['image_proc'], inplace=True)

    return df


def grouping(df):
    '''Creates and analyses batches of processed images.'''
    df['group'] = df['image_proc'].diff().dt.seconds.gt(threshold).cumsum()
    number_of_groups = df.iloc[-1,-1] + 1
    df_dup = pd.DataFrame(columns=['image_proc','image_capt','camera_ref','group'])
    cams_per_group = []
    grouped = df.groupby('group')
    for group_id, group in grouped:
        cams_per_group.append(len(group.camera_ref.unique()))
        if group.duplicated(subset=['camera_ref']).any():
            df_temp = group[group.duplicated(subset=['camera_ref'], keep=False)]
            df_dup = pd.concat([df_dup, df_temp])
    average_cams_group = round(sum(cams_per_group) / number_of_groups, 1)
        
    return df_dup, average_cams_group, number_of_groups 

def check_cameras(df_raw):
    '''Analyses cameras/presets present in the data.'''
    missing_cams = []
    cameras_in_file = df_raw.camera_ref.unique().tolist()
    new_cameras = set(cameras_in_file) - set(camera_ref_names)
    missing_cameras = set(camera_ref_names) - set(cameras_in_file)
    # new_cameras should be appended manually and not automatically
    #if new_cameras:
        #append cameras/presets to the source list
    #    cg.append_new_cameras(new_cameras)

    return new_cameras, missing_cameras
 

def main(file_path):
    global data_issues

    data = pd.read_csv(file_path)
    if not data.empty:
        cleaned_data = clean_data(data)
        df, cams_group, groups = grouping(cleaned_data)
        print('Number of batches processed in the day:')
        print(f'Found {groups} batches of images in {total_groups} expected\n')
        print('Duplicated cameras per batch/group:')
        if df.empty:
            print('Found no duplicated cameras')
        else:
            data_issues = data_issues + (2,)
            print(df.to_string(index=False))
        print('\nAverage number of processed cameras per batch in the day:')
        print(f'There\'s a mean of {cams_group} cameras per batch in \
{len(camera_ref_names)} expected')
        new_cams, missing_cams = check_cameras(data)
        print('\nNew cameras found in the processed file:')
        if new_cams:
            print(new_cams)
        else:
            print('No new cameras/presets found')
        print('\nMissing camera/presets in the processed file:')
        if missing_cams:
            print(missing_cams)
        else:
            print('No missing cameras found')

    else:
        print('Found no data in the source file!')
        print(f'Source file: {file_path}')
        data_issues = data_issues + (1,)

    if not data_issues:
        print('\nNo issues found in the data')
        model = file_path.split('-')
        basename = os.path.basename(file_path)
        if  model[-2] == 'tf2':
            try:
                s3_client.upload_file(
                        Filename=file_path,
                        Bucket='cctv-data-ubdc-ac-uk',
                        Key=f'cctv-server-reports/v1/tf2/{basename}')
            except:
                print('\nAn error occurred when trying to upload the file '\
                      f'"{basename}" to aws bucket')
            else:
                print(f'\nfile "{basename}" uploaded successfully to aws bucket')

        elif model[-2] == 'yolo':
            try:
                s3_client.upload_file(
                        Filename=file_path,
                        Bucket='cctv-data-ubdc-ac-uk',
                        Key=f'cctv-server-reports/v1/yolo/{basename}')
            except:
                print('\nAn error occurred when trying to upload the file '\
                      f'"{basename}" to aws bucket')
            else:
                print(f'\nfile "{basename}" uploaded successfully to aws bucket')

        else:
            print(f'\nmodel "{model[3]}" not found. Which aws bucket to '\
                  'upload the file to?')

    else:
        print('issues found :', data_issues)


if __name__ == '__main__':
    main(sys.argv[1])
