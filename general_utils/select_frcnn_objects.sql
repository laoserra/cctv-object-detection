/*
images that exist in the table detections but whose score is less than 
below, are also present in the selection although with d.class_name and 
d.score set to null
SELECT i.name AS image, i.warnings, d.class_name, d.score
FROM images i
LEFT JOIN detections d
    ON i.id = d.image_id
    AND d.score > 0.1
    AND d.model_id IN (SELECT id FROM models WHERE name = 'faster_rcnn_1024_parent')
*/
SELECT i.image_proc, i.image_capt, i.camera_ref, i.warnings, d.class_name,
       d.bbox_left, d.bbox_right, d.bbox_bottom, d.bbox_top, d.score
FROM images i
LEFT JOIN detections d
    ON i.id = d.image_id
    AND d.score > 0.5
    AND d.model_id IN (SELECT id FROM models WHERE name = 'faster_rcnn_1024_parent')
    AND d.class_name != 'crowd'
WHERE i.image_capt::date > '2023-05-09' AND i.image_capt::date < '2023-05-23'
