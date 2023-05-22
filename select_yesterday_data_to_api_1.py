#!/usr/bin/env python3
import psycopg2
import sys
import gzip
import datetime as dt

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
        return header, result  # returns 2 lists; 2nd is a tuples' list
    except Exception as error:
        print('Error while connecting to database:', error)
    finally:
        # close the communication with the database
        if connection:
            cursor.close()
            connection.close()


def get_data_api(score):
    '''Query database to provide data for the api.

       Set desired score threshold.'''

    # SQL query
    select_data = f'''
    SELECT i.image_proc, i.image_capt, i.camera_ref,
           i.warnings,
           CASE WHEN d.model_id = 1
           THEN 'tf2'
           ELSE 'yolo' END AS model_name,
           d.class_name, d.score
    FROM images i
    LEFT JOIN detections d
        ON i.id = d.image_id
        AND d.score > {score}
    WHERE i.image_capt::date = current_date - INTEGER '1';
    '''
    data = execute_query(select_data)

    # prepend header to list of selected records
    data[1][:0] = [tuple(data[0])]

    report = f'./daily_reports/cctv-report-v2-{yesterday}.csv.gz'
    with gzip.open(report, 'wt') as fp:
        for item in data[1]:
            fp.write(','.join(str(element) for element in item) + '\n')


if __name__ == '__main__':
    get_data_api(sys.argv[1])
