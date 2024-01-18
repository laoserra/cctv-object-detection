SELECT i.image_capt, i.camera_ref, d.class_name,
       d.bbox_left, d.bbox_right, d.bbox_bottom, d.bbox_top
FROM images i
INNER JOIN detections d
    ON i.id = d.image_id
    AND d.score > 0.5
    AND d.model_id IN (SELECT id FROM models WHERE name = 'yolov4_9_objs')
    AND d.class_name NOT IN ('crowd', 'pedestrian', 'cyclist')
WHERE i.image_capt::date > '2023-12-17'
AND i.camera_ref IN ('C37P2', 'E69')
AND i.width = 1280
AND i.height = 720
AND i.warnings = 0
