This is project developed by Urban Big Data Centre and Glasgow City Council with the aim of counting the number of persons and vehicles in cctv images.

This new project aims to update the code from the current cctv project based on tf1 to tf2 as well as to simplify the current code.

Database Detections:
column 'image\_proc' from table 'images', correspond to date and time when image was processed. timezone aware.
column 'image\_capt' from table 'images', correspond to date and time when image was captured. timezone aware.
column 'camera\_ref' from table 'images', correspond to the reference of camera that produced the image. Not to be confused with 'camera\_id'. The same camera can take more than one image. Hence, 'camera\_id' may have more than one 'camera\_ref'.
