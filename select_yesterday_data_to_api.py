#!/usr/bin/env python3

import psycopg2
import sys
import pandas as pd
import gzip
import datetime as dt

classes_tf2 = ['car', 'person', 'bicycle', 'motorcycle', 'bus', 'truck']
classes_yolo = ['car', 'pedestrian', 'cyclist', 
                'motorcycle', 'bus', 'lorry', 'van', 'taxi']

yesterday = dt.datetime.now() - dt.timedelta(days=1)
yesterday = yesterday.strftime('%Y%m%d')


conn_str = "host=localhost dbname=detections user=postgres"


def execute_query(query):
    try:
        # connect to the PostgreSQL database
        connection = psycopg2.connect(conn_str)
        # create new cursor
        cursor = connection.cursor()
        cursor.execute(query)
        header = [descr[0] for descr in cursor.description]
        result = cursor.fetchall()
        return header, result #  one tuple with 2 lists(2nd is a list of tuples)
    except Exception as error:
        print('Error while connecting to database:', error)
    finally:
        # close the communication with the database
        if connection:
            cursor.close()
            connection.close()


def select_yesterday_data(score, model):
    '''Query database to provide data for the api.

       Set desired score threshold and model.'''

    # SQL query
    select_data = f'''
    SELECT i.image_proc, i.image_capt, i.camera_ref, i.warnings, d.class_name,
           d.bbox_left, d.bbox_right, d.bbox_bottom, d.bbox_top, d.score
    FROM images i
    LEFT JOIN detections d
        ON i.id = d.image_id
        AND d.score > {score}
        AND d.model_id IN (SELECT id FROM models WHERE name = '{model}')
        AND d.class_name != 'crowd'
    WHERE i.image_capt::date = current_date - INTEGER '1';
    '''
    data = execute_query(select_data)

    # prepend header to list of selected records
    #data[1][:0] = [tuple(data[0])]

    return data

    '''
    with open(f'report_{model}.csv', 'w') as fp:
        write = csv.writer(fp)
        write.writerows(data[1])
    '''

def clean_data(data):

    df = pd.DataFrame(data[1], columns=data[0])
    print('read data: \n', df.head())
    print('read  data: \n', df.shape)
    # remove empty rows in which all fields are empty
    df = df.dropna(how='all')
    print('dropna: \n', df.head())
    print('dropna: \n', df.shape)
    # remove lines with crowd object in it. TO BE REPLACED IN SQL
    #df = df[df.class_name != 'crowd']
    #print('delete crowd rows :', df.shape)
    # delete duplicated rows, including bboxes
    df = df.drop_duplicates()
    print('drop duplicates: \n', df.shape)
    print('drop duplicates: \n', df.head())
    # remove bboxes columns (only needed to remove duplicates in previous step)
    df = df[[col for col in df.columns if col[:4] != 'bbox']]
    print('removed bboxes columns: ', df.head())

    return df

def group_by_class_name(df_clean, model):

    if model == 'yolov4_9_objs':
        classes = classes_yolo
        model_name = 'yolo'
    else:
        classes = classes_tf2
        model_name = tf2

    df = df_clean
    # filter data where detections are absent
    nan = 0
    if df.isna().any().any():
        df_nan = df[df.isna().any(axis=1)]
        # drop columns 'score' and 'class_name'
        df_nan = df_nan[['image_proc', 'image_capt', 'camera_ref', 'warnings']]
        nan = 1
        print('df_nan: \n', df_nan)

    # group detections by image attributes and class object
    df_agg = df.groupby(['image_proc',
                         'image_capt',
                         'camera_ref',
                         'warnings',
                         'class_name'])
    # transpose class_name to columns with counts
    df_agg = df_agg.size().unstack(fill_value=0).reset_index()
    print('df_agg: \n', df_agg)
    print(df_agg.columns)
    print('df_agg.columns[4:]: \n', df_agg.columns[4:])
    # check for missing classes of objects and update df_agg
    df_agg_classes = df_agg.columns[4:]
    print('len: ', len(df_agg.columns[4:]))

    if len(df_agg_classes) < len(classes):
        missing_classes = list(set(classes) - set(df_agg_classes))
        print('missing_classes ', missing_classes )
        for col in missing_classes:
            df_agg[col] = 0

    #concatenate df_nan with df_agg if df_nan existent
    if nan:
        df = pd.concat([df_nan, df_agg])
        for col in classes:
            df[col] = df[col].fillna(0).astype(int)
    else:
        df = df_agg
    print('concatenated df: \n', df)
    # reorder columns
    columns_order = list(df.columns[:3]) + classes + ['warnings']
    df = df.reindex(columns = columns_order)
    # insert name of model DO THIS AT QUERY DB STEP?
    df.insert(3, 'model_name', model_name)
    print('df with model: \n', df)

def main(score, model):
    data = select_yesterday_data(score, model)
    df_clean = clean_data(data)
    group_by_class_name(df_clean, model)


if __name__ == '__main__':
    main(sys.argv[1], sys.argv[2])
    #main(0.5, 'yolov4_9_objs')
    #clean_data(data)
    #get_data_api(0.5, 'faster_rcnn_1024_parent')
