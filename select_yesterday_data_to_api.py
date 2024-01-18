#!/usr/bin/env python3

import psycopg2
import sys
import pandas as pd
from datetime import datetime, timedelta

classes_tf2 = ['car', 'person', 'bicycle', 'motorcycle', 'bus', 'truck']
classes_yolo = ['car', 'pedestrian', 'cyclist',
                'motorcycle', 'bus', 'lorry', 'van', 'taxi']

yesterday = (datetime.now() - timedelta(days=1)).strftime('%Y%m%d')

conn_str = "host=localhost dbname=detections user=postgres"


def execute_query(query, params=None):
    try:
        # connect to the PostgreSQL database
        with psycopg2.connect(conn_str) as connection:
            # create new cursor
            with connection.cursor() as cursor:
                cursor.execute(query, params)
                header = [descr[0] for descr in cursor.description]
                result = cursor.fetchall()
                # returns one tuple with 2 lists(2nd is a list of tuples)
                return header, result
    except Exception as error:
        print('Error while connecting to database:', error)


def select_yesterday_data(score, model):
    '''Query database to provide data for the api.

       Set desired score threshold and model.'''

    # SQL query
    select_data = '''
    SELECT i.image_proc, i.image_capt, i.camera_ref, i.warnings, d.class_name,
           d.bbox_left, d.bbox_right, d.bbox_bottom, d.bbox_top, d.score
    FROM images i
    LEFT JOIN detections d
        ON i.id = d.image_id
        AND d.score > %s
        AND d.model_id IN (SELECT id FROM models WHERE name = %s)
        AND d.class_name != 'crowd'
    WHERE i.image_capt::date = current_date - INTERVAL '1 day'
    '''
    params = (score, model)
    data = execute_query(select_data, params)

    return data


def clean_data(data):

    df = pd.DataFrame(data[1], columns=data[0])
    # remove empty rows in which all fields are empty
    df = df.dropna(how='all')
    df = df.drop_duplicates()
    # remove bboxes columns (only needed to remove duplicates in previous step)
    df = df[[col for col in df.columns if not col.startswith('bbox')]]

    return df


def group_by_class_name(df_clean, model):

    if model == 'yolov4_9_objs':
        classes = classes_yolo
        model_name = 'yolo'
    else:
        classes = classes_tf2
        model_name = 'tf2'

    df = df_clean
    # filter data where detections are absent
    nan = 0
    if df.isna().any().any():
        df_nan = df[df.isna().any(axis=1)]
        # drop columns 'score' and 'class_name'
        df_nan = df_nan[['image_proc', 'image_capt', 'camera_ref', 'warnings']]
        nan = 1

    # group detections by image attributes and class object
    df_agg = df.groupby(['image_proc',
                         'image_capt',
                         'camera_ref',
                         'warnings',
                         'class_name'])
    # transpose class_name to columns with counts
    df_agg = df_agg.size().unstack(fill_value=0).reset_index()
    # check for missing classes of objects and update df_agg
    df_agg_classes = df_agg.columns[4:]

    if len(df_agg_classes) < len(classes):
        missing_classes = list(set(classes) - set(df_agg_classes))
        for col in missing_classes:
            df_agg[col] = 0

    # concatenate df_nan with df_agg if df_nan existent
    if nan:
        df = pd.concat([df_nan, df_agg])
        for col in classes:
            df[col] = df[col].fillna(0).astype(int)
    else:
        df = df_agg
    # reorder columns
    columns_order = ['image_proc', 'image_capt', 'camera_ref'] \
                    + classes \
                    + ['warnings']
    df = df.reindex(columns=columns_order)
    # insert name of model
    df.insert(3, 'model_name', model_name)

    return model_name, df


def main(score, model):
    data = select_yesterday_data(score, model)
    df_clean = clean_data(data)
    model_name, df = group_by_class_name(df_clean, model)
    report = f'./daily_reports/cctv-report-v2-{model_name}-{yesterday}.csv.gz'
    df.to_csv(report, index=False, compression='gzip')


if __name__ == '__main__':
    main(sys.argv[1], sys.argv[2])
    # main(0.5, 'yolov4_9_objs')
    # get_data_api(0.5, 'faster_rcnn_1024_parent')
