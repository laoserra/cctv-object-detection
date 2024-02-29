#!/usr/bin/env bash

# Script developed by Luis Serra, UBDC, 2023.
# This script runs a python script which collects 
# data to be published in the CCTV API.
# the arguments are:
# 50% confidence score and the model to be used.

working_folder="/home/datasci/Work/cctv-object-detection"
script_yesterday="${working_folder}/select_yesterday_data_to_api.py"
dir_logs="${working_folder}/logs"
yesterday_date="$(date -d yesterday +%Y%m%d)"

cd ${working_folder}

source /home/datasci/.virtualenvs/serving/bin/activate #ubdc3 server

"${script_yesterday}" 0.5 yolov4_9_objs > "${dir_logs}"/yesterday/select_yesterday_data_to_api_yolo_"$(date +%Y%m%d)".log 2>&1
"${script_yesterday}" 0.5 faster_rcnn_1024_parent > "${dir_logs}"/yesterday/select_yesterday_data_to_api_tf2_"$(date +%Y%m%d)".log 2>&1

#sleep 1

#aws s3 cp daily_reports/cctv-report-v2-yolo-"${yesterday_date}".csv.gz s3://cctv-data-ubdc-ac-uk/cctv-server-reports/v1/yolo/ > "${dir_logs}"/aws/aws_yolo_"$(date +%Y%m%d)".log 2>&1
#aws s3 cp daily_reports/cctv-report-v2-tf2-"${yesterday_date}".csv.gz s3://cctv-data-ubdc-ac-uk/cctv-server-reports/v1/tf2/ > "${dir_logs}"/aws/aws_tf2_"$(date +%Y%m%d)".log 2>&1
