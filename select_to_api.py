#!/usr/bin/env python3

import psycopg2
import pandas as pd
import re
import datetime


conn_str = "host=localhost dbname=detections user=postgres"

def execute_query(query):
    '''Query database to provide data for the api.

    The model should be set to name of desired model.'''
    try:
        # connect to the PostgreSQL database
        connection = psycopg2.connect(conn_str)
        # create new cursor
        cursor = connection.cursor()
        cursor.execute(query)
        header = [descr[0] for descr in cursor.description]
        result = cursor.fetchall()
        print('Query executed successfully')
        return header, result #returns 2 lists; the 2nd is a a list of tuples
    except Exception as error:
        print('Error while connecting to database:', error)
    finally:
	# close the communication with the database
        if connection:
            cursor.close()
            connection.close()


def get_data_api(score, model):
    select_data = f'''
    SELECT i.name AS image, i.warnings, d.class_name, d.score
    FROM images i
    LEFT JOIN detections d
        ON i.id = d.image_id
        AND d.score > {score}
        AND d.model_id IN (SELECT id FROM models WHERE name = '{model}');
    '''
    data = execute_query(select_data)
#    name_of_image = data[1][0][0]
    name_of_image = '1673598807500_G124_2023_1_13__8_33_31.jpg'
    print(name_of_image)
    print(name_of_image.split('_'))
    unix_time_ms = int(name_of_image.split('_')[0])
    print(re.split('_|\.', name_of_image))
    print(datetime.datetime.fromtimestamp(unix_time_ms / 1000))
#    df = pd.DataFrame(data[1], columns=data[0]) #panda very slow...

    return print(data)

if __name__ == '__main__':
    get_data_api(0.1, 'faster_rcnn_1024_parent')
