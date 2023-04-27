#!/usr/bin/env python3

import psycopg2

conn_str = "host=localhost dbname=detections user=postgres"


def execute_query(table, query, condition=None):
    '''Query tables in the database.'''
    try:
        # connect to the PostgreSQL database
        connection = psycopg2.connect(conn_str)
        # create new cursor
        cursor = connection.cursor()
        if condition:
            cursor.execute(query, condition)
        else:
            cursor.execute(query)
        result = cursor.fetchall()
        print(f'Query executed successfully to the {table} table')
        return result  # return list of tuples
    except Exception as error:
        print(f'Error while connecting to table {table}:', error)
    finally:
        # close the communication with the database
        if connection:
            cursor.close()
            connection.close()


def get_row_id(table, rowname):
    '''Get row name id.'''
    select_rowname_id = f'SELECT id FROM {table} WHERE name = %s;'
    rowname_id = execute_query(table, select_rowname_id, (rowname,))
    rowname_id = rowname_id[0][0]  # access int inside tuple inside list

    return rowname_id


def manage_multiple_records(insert_table,
                            list_of_insertions,
                            table):
    try:
        connection = psycopg2.connect(conn_str)
        cursor = connection.cursor()
        cursor.executemany(insert_table, list_of_insertions)
        rc = cursor.rowcount
        connection.commit()
        print(f'A total of {rc} records inserted into the {table} table')
    except Exception as error:
        print(f'Error while connecting to table {table}:', error)
    finally:
        if connection:
            cursor.close()
            connection.close()


def insert_multiple_detections(image_name, model_name, detections):
    '''Insert detections into detections table.'''
    image_id = get_row_id('images', image_name)
    model_id = get_row_id('models', model_name)
    detections_list = []
    item = None
    for detection in detections:
        item = (image_id,
                model_id,
                detection['object'],
                round(detection['coordinates']['left'], 3),
                round(detection['coordinates']['right'], 3),
                round(detection['coordinates']['bottom'], 3),
                round(detection['coordinates']['top'], 3),
                round(detection['score'], 5))
        detections_list.append(item)
        item = None

    insert_detections = '''
    INSERT INTO
      detections(image_id, model_id, class_name, bbox_left,
                 bbox_right, bbox_bottom, bbox_top, score)
    VALUES(%s,%s,%s,%s,%s,%s,%s,%s);
    '''
    manage_multiple_records(insert_detections, detections_list, 'detections')
