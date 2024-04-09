#!/usr/bin/env bash

# Script developed by Luis Serra, UBDC, 2023.
# This script runs a python script which collects 
# data from the database for the CCTV API.
# the arguments are: 50% confidence score and the model to be used.
# Afterwards, the grouping.py script is run on the produced Yolo and TF2 data.
# The outcome is a log file report for each one of the analysed files.

# location of project folder
working_folder="/home/ls283h/projects/cctv-object-detection"
script_yesterday="${working_folder}/select_yesterday_data_to_api.py"
script_analysis="${working_folder}/grouping.py"
dir_logs="${working_folder}/logs"
dir_logs_an="${working_folder}/logs/analyses"
yesterday_date="$(date -d yesterday +%Y%m%d)"
file_yolo="${working_folder}/daily_reports/cctv-report-v2-yolo-${yesterday_date}.csv.gz"
file_tf2="${working_folder}/daily_reports/cctv-report-v2-tf2-${yesterday_date}.csv.gz"

cd ${working_folder}

#  setup shell functions for conda and activate environment
eval "$(conda shell.bash hook)"
conda activate cctv

"${script_yesterday}" 0.5 yolov4_9_objs > "${dir_logs}"/yesterday/select_yesterday_data_to_api_yolo_"$(date +%Y%m%d)".log 2>&1
"${script_yesterday}" 0.5 faster_rcnn_1024_parent > "${dir_logs}"/yesterday/select_yesterday_data_to_api_tf2_"$(date +%Y%m%d)".log 2>&1

wait

${script_analysis} ${file_yolo} > "${dir_logs_an}"/"$(basename ${file_yolo} .csv.gz)".log 2>&1
${script_analysis} ${file_tf2} > "${dir_logs_an}"/"$(basename ${file_tf2} .csv.gz)".log 2>&1
