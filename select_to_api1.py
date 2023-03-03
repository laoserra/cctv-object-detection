#!/usr/bin/env python3

import pandas as pd
import psycopg2


conn_str = "host=localhost dbname=detections user=postgres"

def get_data_api(score, model):
    select_data = f'''
    SELECT i.name AS image, i.warnings, d.class_name, d.score
    FROM images i
    LEFT JOIN detections d
        ON i.id = d.image_id
        AND d.score > {score}
        AND d.model_id IN (SELECT id FROM models WHERE name = '{model}');
    '''

    return (select_data)

conn = psycopg2.connect(conn_str)
results = pd.read_sql(get_data_api(0.1, 'faster_rcnn_1024_parent'), conn)
print(results)
