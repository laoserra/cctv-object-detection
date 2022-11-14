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


create_models_table = '''
CREATE TABLE IF NOT EXISTS models(
    id INTEGER  PRIMARY KEY,
    name VARCHAR(40) NOT NULL
);
'''
create_ground_truth_table = '''
CREATE TABLE IF NOT EXISTS ground_truth (
  id INTEGER PRIMARY KEY,
  filename_id INTEGER NOT NULL,
  annotator VARCHAR(40) NOT NULL,
  class_name VARCHAR(30),
  bbox_left REAL,
  bbox_right REAL,
  bbox_bottom REAL,
  bbox_top REAL,
  FOREIGN KEY (filename_id) REFERENCES filenames (id)
    ON UPDATE NO ACTION
    ON DELETE NO ACTION
);
'''
create_detections_table = '''
CREATE TABLE IF NOT EXISTS detections (
  id INTEGER PRIMARY KEY,
  unix_time_insertion INTEGER NOT NULL,
  img_mdl_id INTEGER NOT NULL,
  class_name VARCHAR(30) NOT NULL,
  bbox_left REAL,
  bbox_right REAL,
  bbox_bottom REAL,
  bbox_top REAL,
  score REAL,
  FOREIGN KEY (img_mdl_id) REFERENCES image_model (id)
    ON UPDATE NO ACTION
    ON DELETE NO ACTION
);
'''
create_filenames_table = '''
CREATE TABLE IF NOT EXISTS filenames (
    id INTEGER  PRIMARY KEY,
    name VARCHAR(60) NOT NULL,
    image_height INTEGER,
    image_width INTEGER
);
'''
create_image_model_table = '''
CREATE TABLE IF NOT EXISTS image_model (
    id INTEGER PRIMARY KEY,
    unix_time_insertion INTEGER,
    filename_id INTEGER NOT NULL,
    model_id INTEGER NOT NULL,
    bus_counts INTEGER DEFAULT 0,
    car_counts INTEGER DEFAULT 0,
    cyclist_counts INTEGER DEFAULT 0,
    crowd_counts INTEGER DEFAULT 0,
    lorry_counts INTEGER DEFAULT 0,
    motorcycle_counts INTEGER DEFAULT 0,
    pedestrian_counts INTEGER DEFAULT 0,
    taxi_counts INTEGER DEFAULT 0,
    van_counts INTEGER DEFAULT 0,
    FOREIGN KEY(filename_id) REFERENCES filenames (id)
        ON UPDATE NO ACTION
        ON DELETE NO ACTION,
    FOREIGN KEY (model_id) REFERENCES models (id)
        ON UPDATE NO ACTION
        ON DELETE NO ACTION
);
'''

# create database if it does not exist
# create table if not exists
manage_database(create_models_table)
manage_database(create_filenames_table)
manage_database(create_ground_truth_table)
manage_database(create_image_model_table)
manage_database(create_detections_table)

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
    select_image_id = 'SELECT id FROM filenames WHERE name = ?;'
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
    image_model_list = [(round(time.time()), image_id, model_id)]
    
    insert_image_model = '''
    INSERT INTO
      image_model (unix_time_insertion, filename_id, model_id)
    VALUES (?,?,?);
    '''
    manage_multiple_records(insert_image_model, image_model_list, 'image_model')

def get_image_model_id(model_name, image_name):
    '''Get image_model id.'''
    image_id = get_image_id(image_name)
    model_id = get_model_id(model_name)
    select_image_model_id = 'SELECT id FROM image_model \
                             WHERE filename_id = ? \
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
        item = (round(time.time()),
                image_model_id,
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
      detections (unix_time_insertion, img_mdl_id, class_name,
                  bbox_left, bbox_right, bbox_bottom, bbox_top, score)
    VALUES (?,?,?,?,?,?,?,?);
    '''
    manage_multiple_records(insert_detections, detections_list, 'detections')

def update_counts(model_name, image_name, detections):
    '''Update counts on the image_model table after image is processed.'''

    objects_of_interest = [d['name'] for d in 
                           config.category_index_faster_rcnn.values()]

    object_counts = {}
    for obj in objects_of_interest:
        count = 0
        for detection in detections:
            if detection['object'] == obj \
            and detection['score'] > 0.5:
                count += 1
        object_counts[obj] = count



    image_model_id = get_image_model_id(model_name, image_name)
    update_counts = f'''
    UPDATE image_model
    SET bus_counts = {object_counts['bus']},
        car_counts = {object_counts['car']},
        cyclist_counts = {object_counts['cyclist']},
        crowd_counts = {object_counts['crowd']},
        lorry_counts = {object_counts['lorry']},
        motorcycle_counts = {object_counts['motorcycle']},
        pedestrian_counts = {object_counts['pedestrian']},
        taxi_counts = {object_counts['taxi']},
        van_counts = {object_counts['van']}
    WHERE id = {image_model_id};
    '''
    manage_database(update_counts)
