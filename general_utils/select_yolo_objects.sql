CREATE VIEW v_yolo_objects
AS
SELECT i.name AS image, i.warnings, d.class_name, d.score
FROM images i
LEFT JOIN image_model im
ON i.id = im.image_id
LEFT JOIN models m
ON im.model_id = m.id
LEFT JOIN detections d
ON d.img_mdl_id = im.id
WHERE m.name = 'yolov4_9_objs'
AND (d.score >= 0.005 OR im.id NOT IN (SELECT img_mdl_id  FROM detections))
OR i.warnings = 1
