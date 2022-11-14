DROP TABLE IF EXISTS models;
DROP TABLE IF EXISTS filenames;

CREATE TABLE models(
    id INTEGER  PRIMARY KEY,
    name VARCHAR(40) NOT NULL
);

CREATE TABLE filenames(
    id INTEGER  PRIMARY KEY,
    name VARCHAR(40) NOT NULL,
    image_height INTEGER,
    image_width INTEGER
);

INSERT INTO models(name)
VALUES
    ('faster_rcnn_1024_model_1'),
    ('yolov3_model_2'),
    ('yolov4_model_3');

INSERT INTO filenames(name,image_height,image_width)
VALUES
    ('20268252346_95477a50c1_z.jpg',480,640),
    ('5882937489_8eb6b6fbc8_z.jpg',480,640),
    ('8280407180_fd1061011b_z.jpg',425,640),
    ('9108877160_b796980c6c_z.jpg',480,640),
    ('G124.jpg',720,1280),
    ('test_1s_000001.jpg',1080,1920),
    ('test_1s_000002.jpg',1080,1920),
    ('test_1s_000003.jpg',1080,1920),
    ('test_1s_000004.jpg',1080,1920),
    ('test_coco.jpg',675,1200);

SELECT * FROM models;
SELECT * FROM filenames;
