#!/usr/bin/env python3 

import pandas as pd

model = 'tf2'
classes_tf2 = ['car', 'person', 'bicycle', 'motorcycle', 'bus', 'truck']
classes_yolo = ['car', 'pedestrian', 'cyclist', 'motorcycle', 'bus', 'lorry', 'van', 'taxi']

df = pd.read_csv('report_faster_rcnn_1024_parent.csv')
print('read :', df.head())
print('read :', df.shape)
# remove empty rows in which all fields are empty
df = df.dropna(how='all')
print('dropna :', df.head())
print('dropna :', df.shape)
# remove lines with crowd object in it. TO BE REPLACED IN SQL
df = df[df.class_name != 'crowd']
print('delete crowd rows :', df.shape)
# delete duplicated rows, including bboxes
df = df.drop_duplicates()
print('drop duplicates :', df.shape)
print('drop duplicates :', df.head())
# remove bboxes columns (only needed to remove duplicates in previous step)
df = df[[col for col in df.columns if col[:4] != 'bbox']]
print('removed bboxes columns: ', df.head())

# filter data where detections are absent
nan = 0
if df.isna().any().any():
    df_nan = df[df.isna().any(axis=1)]
    # drop columns 'score' and 'class_name'
    df_nan = df_nan[['image_proc', 'image_capt', 'camera_ref', 'warnings']]
    nan = 1
    print('df_nan: ', df_nan)

# group detections by image attributes and class object
df_agg = df.groupby(['image_proc',
                     'image_capt',
                     'camera_ref',
                     'warnings',
                     'class_name'])
# transpose class_name to columns with counts
df_agg = df_agg.size().unstack(fill_value=0).reset_index()
print('df_agg: ', df_agg)
print(df_agg.columns)
print(df_agg.columns[4:])
# check for missing classes of objects and update
df_agg_classes = df_agg.columns[4:]
print('len: ', len(df_agg.columns[4:]))
if len(df_agg_classes) < len(classes_tf2):
    missing_classes = list(set(classes_tf2) - set(df_agg_classes))
    print('missing_classes ', missing_classes )
    for col in missing_classes:
        df_agg[col] = 0

#concatenate nan df with agg df if nan df existent
if nan:
    df = pd.concat([df_nan, df_agg])
    for col in classes_tf2:
        df[col] = df[col].fillna(0).astype(int)
else:
    df = df_agg
print(df)
# reorder columns
columns_order = list(df.columns[:3]) + classes_tf2 + ['warnings']
df = df.reindex(columns = columns_order)
# insert name of model DO THIS AT QUERY DB STEP?
df.insert(3, 'model_name', f'{model}')
print(df)

# print to file
#df.to_csv('tf2_detections.csv.gz',index=False,compression='gzip')
