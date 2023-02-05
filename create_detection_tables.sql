DROP DATABASE IF EXISTS detections;

CREATE DATABASE  detections;

-- connect to newly created database
\c detections

CREATE TABLE models(
    id serial PRIMARY KEY,
    name VARCHAR(40) NOT NULL
);

CREATE TABLE images(
    id serial PRIMARY KEY,
    unix_time_insertion INTEGER,
    name VARCHAR(80) NOT NULL,
    width INTEGER,
    height INTEGER,
    warnings INTEGER DEFAULT 0
);

CREATE TABLE detections (
    image_id INTEGER NOT NULL,
    model_id INTEGER NOT NULL,
    PRIMARY KEY(image_id, model_id),
    class_name VARCHAR(30) NOT NULL,
    bbox_left REAL,
    bbox_right REAL,
    bbox_bottom REAL,
    bbox_top REAL,
    score REAL,
    FOREIGN KEY(image_id) REFERENCES images (id)
        ON DELETE CASCADE,
    FOREIGN KEY (model_id) REFERENCES models (id)
        ON DELETE CASCADE
);

INSERT INTO models(name)
VALUES
    ('faster_rcnn_1024_parent'),
    ('yolov4_9_objs');

-- list newly created tables
\dt

SELECT * FROM models;
