This project is being developed by Urban Big Data Centre and Glasgow City Council with the aim to present regular counts of persons, vehicles  and cyclists from CCTV images in different locations of Glasgow City Centre. At the time of writing (2023.07.03), counts are being made for every 30 minutes of the day, using more than 50 cameras.

This project has currently four areas of development:
1. Capture of images
2. Process of images
3. [CCTV backend](https://github.com/urbanbigdatacentre/cctv-backend)
4. [CCTV frontend](https://github.com/urbanbigdatacentre/cctv-frontend)

This repo corresponds to the process of images.

This new release aims to:
- Update and simplify existing code from Tensorflow 1 to Tensorflow 2.
- Deploy in-house trained Yolo model to detect different types of vehicles, pedestrians and cyclists.

A simplified flowchart of all the operations occurring at this stage:

![Operations](Image_processing.png)

## Getting started
The current project is deployed in an Ubuntu 20.04 LTS server machine. The instalation process consists in creating all the neccessary folders and installing the requireed software. Below are my notes this process.

Postgres database configuration:

1. [Install postgresql](https://www.postgresql.org/download/linux/ubuntu/)

Follow link: https://devopscube.com/install-postgresql-on-ubuntu/ for password authentication

file "/etc/postgresql/15/main/pg_hba.conf", last line:
# Allow connections to all databases, all  users and all addresses
host    all             postgres             0.0.0.0/0               scram-sha-256


file "/etc/postgresql/14/main/postgresql.conf":
Keep forbidden connection by remote clients in the line "#listen_addresses = 'localhost'"

Test connection with something like: "psql -U postgres -h localhost"

In case I need to restart postgres service: "sudo systemctl restart postgresql"
Confirm all tcp connections: "ss -nlt"

Create .pgpass file at the home directory (ex.):
# hostname:port:database:username:password
localhost:5432:*:postgres:Str0ngP@ssw0rd

To generate a strong password (16 bytes), type in the cmd line (https://ostechnix.com/4-easy-ways-to-generate-a-strong-password-in-linux/): "openssl rand -base64 16"

Follow remaining isntructions in: https://tableplus.com/blog/2019/09/how-to-use-pgpass-in-postgresql.html

Check if path /usr/bin is an environment variable. if not set it up in the .bashrc file: export PATH=/usr/bin:$PATH

git clone project from GitHub and update it with extra files and folders from the personal laptop zipped file.

Update all files, especially the bash files!
In the file "monitor_images_input_folder.sh" change the line correspondent to the activation of the virtualenv.
In the file "process_images_input_folder.sh" change the line correspondent to the activation of the virtualenv.

Also check that tensorflow container version matches the load bash file.

Need to test system with a couple of test images (monitor and process bash files).

Similarly to UBDC2 server, I need to create a cron task to access database, produce a daily gzip file and send it to the aws bucket
In the crontab, I also need to set the following reboot: "@reboot bash /home/lserra/Work/UBDC/cctv_object_detection_v2/reboot_monitor.sh" or something similar.

Install library psycopg in the python environment: "pip install psycopg2". For problems related with prerequisites, refer to manual page: "https://www.psycopg.org/docs/install.html#quick-install".

Check if "identify" already exists with: $identify --version. If not install with: sudo apt install imagemagick.

Check all installed directories. For instance, delete the file "detections.db" from the output folder, if existent.

Check if I need Keith's bash files: "process_folders.sh" and "process_retention.sh".

Check path of the file "reboot_monitor.sh"

File "select_yesterday_data_to_api.py", probably needs to be reconfigured to a bash file and crontask to send a gzip file to aws bucket.

Time zone in the file "sudo vim /etc/postgresql/15/main/postgresql.conf" must be set to 'Europe/London'. Afterwards restart postgresql: 'sudo systemctl restart postgresql'.




Somernotes:
- The column 'camera\_ref' from table 'images' in the database detections, corresponds to the reference of the camera that produced the image. Not to be confused with 'camera\_id'. The same camera can take more than one image. Hence, 'camera\_id' may have more than one 'camera\_ref'. In other words: "camera\_ref = camera\_id + camera\_preset\_id". Example: camera ref "G57P1" = camera\_id "G57" + camera\_preset\_id "P1". "P1" means "preset 1". Other presets could be added to the same camera.

All detected objects of interest are written to the database. However, only objects with a confidence score greater than 50% are written onto the images (in the form of bounding boxes encircling the object), for visual clarity.
