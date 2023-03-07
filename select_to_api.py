#!/usr/bin/env python3

import psycopg2
import csv


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
        return header, result #returns 2 lists; 2nd is a tuples' list
    except Exception as error:
        print('Error while connecting to database:', error)
    finally:
	# close the communication with the database
        if connection:
            cursor.close()
            connection.close()


def get_data_api(score, model):
    select_data = f'''
    SELECT i.unix_time_insertion AS proc_timestamp, i.name AS image, 
           i.warnings, d.class_name, d.score
    FROM images i
    LEFT JOIN detections d
        ON i.id = d.image_id
        AND d.score > {score}
        AND d.model_id IN (SELECT id FROM models WHERE name = '{model}');
    '''
    data = execute_query(select_data)
    header = [data[0][0], 'image_timestamp', 'image_id']
    header = header + data[0][2:]
    parsed_data = [tuple(header)]
    
    for item in data[1]:
        splitted_image = item[1].split('_') #returns a list
        #floor division. Closer to reality due to delay in getting timestamp
        image_timestamp = int(splitted_image[0]) // 1000
        image_id = splitted_image[1]
        new_item = (item[0], image_timestamp, image_id) + item[2:]
        parsed_data.append(new_item)

    with open('report.csv', 'w') as fp:
        write = csv.writer(fp)

        write.writerows(parsed_data)

#Next development step: add another condition to the query, to filter the images captured/processed yesterday. The captured is a bit more tricky because that date is the first part of the image name...
# Furthermore, maybe I also need to filter all the data for yesterday, including all scores, etc....

if __name__ == '__main__':
    get_data_api(0.1, 'faster_rcnn_1024_parent')
