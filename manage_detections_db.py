import sqlite3
from sqlite3 import Error
import time
import config_validation_file as config


def create_connection(path_to_db):
    connection = None
    try:
        connection = sqlite3.connect(path_to_db)
        print('Connection to SQLite DB successful')
    except Error as e:
        print(f'The error "{e}" ocurred when trying to connect to db')

    return connection


# Establish a connection to existent database
connection = create_connection(config.PATH_DB)


def manage_database(command, connection_to_db=connection):
    cursor = connection_to_db.cursor()
    try:
        cursor.execute(command)
        connection_to_db.commit()
        print('Commmand executed successfully')
    except Error as e:
        print(f'The error "{e}" ocurred')


# Execute a query to the database
def execute_query(query, condition=None, connection_to_db=connection):
    cursor = connection_to_db.cursor()
    result = None
    try:
        if condition:
            cursor.execute(query, condition)
        else:
            cursor.execute(query)
        result = cursor.fetchall()
        print('Query executed successfully')
        return result #returns list of tuples
    except Error as e:
        print(f'The error "{e}" ocurred')


def manage_multiple_records(insert_table,
                            list_of_insertions,
                            table,
                            connection_to_db=connection):

    cursor = connection_to_db.cursor()

    try:
        cursor.executemany(insert_table, list_of_insertions)
        connection_to_db.commit()
        rc = cursor.rowcount
        print(f'A total of {rc} records inserted successfully into the {table} table')
    except Error as e:
        print(f'The error "{e}" ocurred when trying to insert data to the {table} table')

def get_image_id(image_name):
    '''Get image id.'''
    select_image_id = 'SELECT id FROM images WHERE name = ?;'
    image_id = execute_query(select_image_id, (image_name,))
    image_id = image_id[0][0] #access int inside tuple inside list

    return image_id

def get_model_id(model_name):
    '''Get model id.'''
    select_model_id = 'SELECT id FROM models WHERE name = ?;'
    model_id = execute_query(select_model_id, (model_name,))
    model_id = model_id[0][0] #access int inside tuple inside list

    return model_id

def insert_image_model_data(model_name, image_name):
    '''Insert image and model data into table image_model.'''
    image_id = get_image_id(image_name)
    model_id = get_model_id(model_name)
    image_model_list = [(image_id, model_id)]
    
    insert_image_model = '''
    INSERT INTO
      image_model (image_id, model_id)
    VALUES (?,?);
    '''
    manage_multiple_records(insert_image_model, image_model_list, 'image_model')

def get_image_model_id(model_name, image_name):
    '''Get image_model id.'''
    image_id = get_image_id(image_name)
    model_id = get_model_id(model_name)
    select_image_model_id = 'SELECT id FROM image_model \
                             WHERE image_id = ? \
                             AND model_id = ?;'
    image_model_id = execute_query(select_image_model_id, (image_id, model_id))
    image_model_id = image_model_id[0][0] #access int inside tuple inside list

    return image_model_id

def insert_multiple_detections(model_name, image_name, detections):
    '''Insert detections into detections table.'''
    image_model_id = get_image_model_id(model_name, image_name)
    detections_list = []
    item = None
    for detection in detections:
        item = (image_model_id,
                detection['object'],
                round(detection['coordinates']['left'], 3),
                round(detection['coordinates']['right'], 3),
                round(detection['coordinates']['bottom'], 3),
                round(detection['coordinates']['top'], 3),
                round(detection['score'], 3))
        detections_list.append(item)
        item = None

    insert_detections = '''
    INSERT INTO
      detections (img_mdl_id, class_name, bbox_left, bbox_right, 
                  bbox_bottom, bbox_top, score)
    VALUES (?,?,?,?,?,?,?);
    '''
    manage_multiple_records(insert_detections, detections_list, 'detections')
