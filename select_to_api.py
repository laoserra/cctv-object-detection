#!/usr/bin/env python3

import psycopg2
import csv
import sys


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
        return header, result #returns 2 lists; 2nd is a tuples' list
    except Exception as error:
        print('Error while connecting to database:', error)
    finally:
	# close the communication with the database
        if connection:
            cursor.close()
            connection.close()


def get_data_api(score, model):
    '''Query database to provide data for the api.

    The model should be set to name of desired model.'''

    #SQL query
    select_data = f'''
    SELECT i.process_tstz, i.image_tstz, i.image_ref, 
           i.warnings, d.class_name, d.score
    FROM images i
    LEFT JOIN detections d
        ON i.id = d.image_id
        AND d.score > {score}
        AND d.model_id IN (SELECT id FROM models WHERE name = '{model}')
    WHERE i.image_tstz::date = current_date - INTEGER '1';
    '''
    data = execute_query(select_data)

    # prepend header to list of selected records
    data[1][:0] = [tuple(data[0])]

    with open('report.csv', 'w') as fp:
        write = csv.writer(fp)
        write.writerows(data[1])


if __name__ == '__main__':
    get_data_api(sys.argv[1], sys.argv[2])
