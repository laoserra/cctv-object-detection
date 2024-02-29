This project is being developed by Urban Big Data Centre and Glasgow City Council with the aim to present regular counts of persons, vehicles  and cyclists from CCTV images in different locations of Glasgow City Centre. At the time of writing (2023.07.03), counts are being made for every 30 minutes of the day, using more than 50 cameras.

This project has currently four areas of development:
1. CCTV Image Capture
2. [CCTV Image Processing](https://github.com/urbanbigdatacentre/glasgow-cctv-object-detection)
3. [CCTV Backend](https://github.com/urbanbigdatacentre/glasgow-cctv/tree/main/projects/backend)
4. [CCTV Frontend](https://github.com/urbanbigdatacentre/glasgow-cctv/tree/main/projects/frontend)

This repo corresponds to the second area of development, that is, **CCTV Image Processing**.

This new release aims to:
- Update and simplify existing code from Tensorflow 1 to Tensorflow 2.
- Deploy in-house trained Yolo model to detect different types of vehicles, pedestrians and cyclists.

A simplified flowchart of all the operations occurring at this stage:

![Operations](component_2.png)

# Getting started
The current project is deployed in an Ubuntu 20.04 LTS server machine. However, it is possible to run this project in any Linux Debian machine with NVIDIA GPU. 

The instalation process consists in installing the GPU NVIDIA drivers, cloning the project, creating the necessary files and folders, and installing required dependencies. Below are my notes to this process.

## Install Docker Engine
This project makes use of Docker container to serve object detections. Follow instructions [here](https://docs.docker.com/engine/install/). Afterwards, don't forget to perform the [Linux post-installation steps for Docker Engine](https://docs.docker.com/engine/install/linux-postinstall/).

## Install NVIDIA CUDA drivers
There are two options to install nvidia drivers:
1. Distribution-specific packages (RPM and Deb packages).
2. Distribution-independent package (runfile packages).

Citing NVIDIA official docs: *The distribution-independent package has the advantage of working across a wider set of Linux distributions, but does not update the distribution’s native package management system. The distribution-specific packages interface with the distribution’s native package management system. It is recommended to use the distribution-specific packages, where possible.*

Following NVIDIA's advice, we suggest going with the distribution-specific package, in our case, a **deb** package. Installation steps:
1. Check CUDA and Python versions required for tensorflow version [here](https://www.tensorflow.org/install/source#gpu).
1. Check the [pre-installation actions](https://docs.nvidia.com/cuda/cuda-installation-guide-linux/#pre-installation-actions) (optional).
2. Install [cuda drivers](https://docs.nvidia.com/cuda/cuda-quick-start-guide/#ubuntu) according to tensorflow version to be installed (see requirements' file below). Regarding the development environment step, only the PATH variable is needed:
```bash
export PATH=/usr/local/<cuda-version>/bin${PATH:+:${PATH}}
```
To make the environment path persistent, add the path to the `.bashrc` configuration file.

3. Test a sample workload to verify installation:
```bash
sudo docker run --rm --runtime=nvidia --gpus all ubuntu nvidia-smi
```
The output should be something like:
```bash
+-----------------------------------------------------------------------------+
| NVIDIA-SMI 535.86.10    Driver Version: 535.86.10    CUDA Version: 12.2     |
|-------------------------------+----------------------+----------------------+
| GPU  Name        Persistence-M| Bus-Id        Disp.A | Volatile Uncorr. ECC |
| Fan  Temp  Perf  Pwr:Usage/Cap|         Memory-Usage | GPU-Util  Compute M. |
|                               |                      |               MIG M. |
|===============================+======================+======================|
|   0  Tesla T4            On   | 00000000:00:1E.0 Off |                    0 |
| N/A   34C    P8     9W /  70W |      0MiB / 15109MiB |      0%      Default |
|                               |                      |                  N/A |
+-------------------------------+----------------------+----------------------+

+-----------------------------------------------------------------------------+
| Processes:                                                                  |
|  GPU   GI   CI        PID   Type   Process name                  GPU Memory |
|        ID   ID                                                   Usage      |
|=============================================================================|
|  No running processes found                                                 |
+-----------------------------------------------------------------------------+
```

4. If docker container cannot access nvidia, install [NVIDIA Container Toolkit](https://docs.nvidia.com/datacenter/cloud-native/container-toolkit/latest/index.html) and perform previous test.

> [!NOTE]
> To install a distribution-independent package, download and run a [.run file](https://www.nvidia.com/download/index.aspx).

## Install and configure PostgreSQL database

1. [Install latest postgresql](https://www.postgresql.org/download/linux/ubuntu/). Otherwise, it is also possible to use PostgreSQL pre-installed with Ubuntu.

> [!NOTE]
> You can find more detailed instructions [here](https://devopscube.com/install-postgresql-on-ubuntu/).

2. Change password for postgres user:
```bash
sudo -u postgres psql
ALTER USER postgres PASSWORD 'myPassword';
```
3. Forbid connection by remote clients: 
Edit file `/etc/postgresql/<postgres-version>/main/postgresql.conf` and uncomment line `#listen_addresses = 'localhost'`

4. Set time zone to **Europe/London** in the file `/etc/postgresql/<postgres-version>/main/postgresql.conf`
```bash
log_timezone = 'Europe/London'
timezone = 'Europe/London'
``` 
5. Restart postgresql and test connection:

```bash
sudo systemctl restart postgresql`
psql -U postgres -h localhost
```

6. Confirm all tcp connections: `ss -nlt`

7. Create `.pgpass` file in home directory to be used by psql:
```bash
# hostname:port:database:username:password
localhost:5432:*:postgres:Str0ngP@ssw0rd
```

> [!NOTE]
> To generate a strong password (16 bytes), type  `openssl rand -base64 16` in the cmd line (more info [here](https://ostechnix.com/4-easy-ways-to-generate-a-strong-password-in-linux/)).

Set the proper permission so it would be used by psql:
```bash
sudo chmod 600 .pgpass
```
Finally export PGPASSFILE file to sent environment variable:
```bash
export PGPASSFILE='/home/user/.pgpass'
```
Source: Check [here](https://tableplus.com/blog/2019/09/how-to-use-pgpass-in-postgresql.html).

8. Check if path `/usr/bin` is an environment variable. If not set it up in the `.bashrc` file:
```bash
export PATH=/usr/bin:$PATH
```

## Install and configure CCTV project and dependencies

1. Git clone project:
```bash
git clone git@github.com:urbanbigdatacentre/glasgow-cctv-object-detection.git
```

2. Inside the cloned directory, create database `detections` and tables:
```bash
psql -U postgres -h localhost -f ./general_utils/create_detection_tables.sql
```
3. Create the following sub-directories inside the project directory:
```bash
mkdir archive_folder daily_reports input_folder output_folder logs && mkdir logs/analyses logs/aws logs/yesterday 
```
4. Download [zip file](https://gla-my.sharepoint.com/:u:/g/personal/luis_serra_glasgow_ac_uk/EVMXV3d6wGJOiIQo_eYlYagB8Zm1X33Sb9jWkfnnQiA6Qg?e=gvhc9s) with models, pip requirements and a test image. Unzip file and copy directories `faster_rcnn_1024_parent/` and `yolov4_9_objs/` to inside the project `models/` directory.

5. Create a Python Virtual Environment for the project:
```bash
# create virtual environment folder
mkdir ~/.virtualenvs # or any other name of your choose
# create python virtual environment
python3 -m venv ~/.virtualenvs/cctv # or any other name of your choose
```
> [!WARNING]
> It is advisable to use other Python virtual environment for a professional deployment, such as [virtualenv](https://virtualenv.pypa.io/en/latest/). Other options exist though.

6. Install Python packages
In the zip file there's a `requirement.txt` file for Ubuntu 20.04. Run the following command in the python virtual environment created:
```bash
# activate the project virtual environment
source .venv/bin/activate

# install all dependencies from the requirements file
pip install -r requirements.txt
```
Alternative if not working: before pip installing the requirements file, edit it and remove dependencies version.


7. Update all files, especially the bash files!
In the file `monitor_images_input_folder.sh` change the line correspondent to the activation of the virtualenv.
In the file `process_images_input_folder.sh` change the line correspondent to the activation of the virtualenv.

8. Create a cron task to access database, produce a daily gzip file and send it to the aws bucket `crontab -e`:
```bash
SHELL=/bin/bash
PATH=copy-env-path-here
@reboot /home/datasci/Work/glasgow-cctv-object-detection/reboot_monitor.sh
0  2  *  *  * /home/user/glasgow-cctv-object-detection/process_yesterday_data.sh > /dev/null 2>&1
30  2  *  *  * /home/user/glasgow-cctv-object-detection/faulty.sh > /dev/null 2>&1
0  3  *  *  * /home/user/glasgow-cctv-object-detection/analyse_yesterday_data.sh > /dev/null 2>&1
```

9. Check if `identify` already exists:
```bash
identify --version
```
If not install with:
```bash
sudo apt install imagemagick.
```

10. Check path of the file `reboot_monitor.sh`

> [!NOTE]
> Requirements may differ for diifferent Ubuntu releases.

11. Run monitor bash file and tensorflow serving docker container:
```bash
./monitor_images_input_folder.sh
./reboot_monitor.sh
```
12. Test system with a couple of test images (monitor and process bash files).

13. Run one colour image `dark_yellow_canvas.jpg` provided, with tf2 model. Check maximum confidence score obtained in detections list. Afterwards, replace following threshold number in `detections_main.py` file:
```python
detections[0]['score'] > 0.0001317993737757206):
```

> [!NOTE]
> Column `camera_ref` from table `images` in the database detections, corresponds to the reference of the camera that produced the image. Not to be confused with `camera_id`. The same camera can take more than one image. Hence, `camera_id` may have more than one `camera_ref`. In other words: `camera_ref = camera_id + camera_preset_id`. Example: camera ref "G57P1" = camera_id "G57" + camera_preset_id "P1". "P1" means "preset 1". Other presets could be added to the same camera.

> [!NOTE]
> All detected objects of interest are written to the database. However, only the bounding boxes of the objects whose confidence score is greater than 50%, are written onto the images, for visual clarity.