--CREATE VIEW v_frcnn_objects
--AS
SELECT i.name AS image, i.warnings, d.class_name, d.score
FROM images i
LEFT JOIN image_model im
    ON i.id = im.image_id
    AND im.model_id IN (SELECT id FROM models WHERE name = 'faster_rcnn_1024_parent')
LEFT JOIN detections d
    ON d.img_mdl_id = im.id
    AND d.score > 0.1
