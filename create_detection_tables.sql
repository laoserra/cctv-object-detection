DROP TABLE IF EXISTS models;
DROP TABLE IF EXISTS images;
DROP TABLE IF EXISTS image_model;
DROP TABLE IF EXISTS detections;

CREATE TABLE IF NOT EXISTS models(
    id INTEGER  PRIMARY KEY,
    name VARCHAR(40) NOT NULL
);

CREATE TABLE IF NOT EXISTS images(
    id INTEGER  PRIMARY KEY,
    unix_time_insertion INTEGER,
    name VARCHAR(40) NOT NULL,
    width INTEGER,
    height INTEGER,
    valid INTEGER DEFAULT 1
);

CREATE TABLE IF NOT EXISTS image_model (
    id INTEGER PRIMARY KEY,
    image_id INTEGER NOT NULL,
    model_id INTEGER NOT NULL,
    FOREIGN KEY(image_id) REFERENCES images (id)
        ON UPDATE NO ACTION
        ON DELETE NO ACTION,
    FOREIGN KEY (model_id) REFERENCES models (id)
        ON UPDATE NO ACTION
        ON DELETE NO ACTION
);

CREATE TABLE IF NOT EXISTS detections (
  id INTEGER PRIMARY KEY,
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

INSERT INTO models(name)
VALUES
    ('faster_rcnn_1024_parent'),
    ('yolov4_9_objs');

.tables
SELECT * FROM models;
