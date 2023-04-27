This is project developed by Urban Big Data Centre and Glasgow City Council with the aim of counting the number of persons and vehicles  and cyclists in cctv images.

This new release aims to:
- update the code from the current cctv project based on tf1 to tf2.
- simplify current code.
- Deploy in-house trained Yolo model to detect different types of vehicles, pedestrians and cyclists.

Database Detections:
- column 'image\_proc' from table 'images', correspond to date and time when image was processed. timezone aware.
- column 'image\_capt' from table 'images', correspond to date and time when image was captured. timezone aware.
- column 'camera\_ref' from table 'images', correspond to the reference of camera that produced the image. Not to be confused with 'camera\_id'. The same camera can take more than one image. Hence, 'camera\_id' may have more than one 'camera\_ref'. In other words: "camera\_ref = camera\_id + camera\_preset\_id". Example: camera ref "G57P1" = camera\_id "G57" + camera\_preset\_id "P1". "P1" means "preset 1". Other presets could be added to the same camera.

All detected objects of interest are written to the database. However, only objects with a confidence score greater than 50% are written onto the images (in the form of bounding boxes encircling the object), for visual clarity.
