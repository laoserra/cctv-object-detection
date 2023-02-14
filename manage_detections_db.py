#!/usr/bin/env python3

from configparser import ConfigParser
import psycopg2


def config(filename='detections.ini', section='postgresql'):
    # create a parser
    parser = ConfigParser()
    # read config file
    parser.read(filename)

    # get section, default to postgresql
    db = {}
    if parser.has_section(section):
        params = parser.items(section)
        for param in params:
            db[param[0]] = param[1]
    else:
        raise Exception(f'Section {section} not found in the {filename} file')

    return db


# Execute a query to the database
def execute_query(table, query, condition=None):
    '''Query tables in the database.'''

    conn = None
    try:
        # read connection parameters
        params = config()
        # connect to the PostgreSQL database
        conn = psycopg2.connect(**params)
        # create new cursor
        cur = conn.cursor()
        if condition:
            cur.execute(query, condition)
        else:
            cur.execute(query)
        result = cur.fetchall()
        print(f'Query executed successfully to the {table} table')
        cur.close()
        return result #returns list of tuples

    except (Exception, psycopg2.DatabaseError) as error:
        print(f'The error "{error}" ocurred when trying to query the {table} table')

    finally:
        if conn is not None:
            conn.close()


def get_row_id(table, rowname):
    '''Get row name id.'''
    select_rowname_id = f'SELECT id FROM {table} WHERE name = %s;'
    rowname_id = execute_query(table, select_rowname_id, (rowname,))
    rowname_id = rowname_id[0][0] #access int inside tuple inside list

    return rowname_id


def manage_multiple_records(insert_table,
                            list_of_insertions,
                            table):

    conn = None
    try:
        # read connection parameters
        params = config()
        # connect to the PostgreSQL database
        conn = psycopg2.connect(**params)
        # create new cursor
        cur = conn.cursor()
        cur.executemany(insert_table, list_of_insertions)
        rc = cur.rowcount
        conn.commit()
        print(f'A total of {rc} records inserted successfully into the {table} table')
	# close the communication with the database
        cur.close()
    except (Exception, psycopg2.DatabaseError) as error:
        print(f'The error "{error}" ocurred when trying to insert data to the {table} table')
    finally:
        # database connection closed
        if conn is not None:
            conn.close()


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
