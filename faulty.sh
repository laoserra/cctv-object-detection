#!/usr/bin/env bash

# This script runs the camera_faulty.py script in the Yolo and TF2 data.

working_folder="/home/datasci/Work/cctv-object-detection" #UBDC3 server
script_error="$working_folder"/camera_fault.py
yesterday_date="$(date -d yesterday +%Y%m%d)"

cd $working_folder

source /home/datasci/.virtualenvs/serving/bin/activate #ubdc3 server

for file in "$working_folder"/daily_reports/*"$yesterday_date".csv.gz
do
    $script_error $file >/dev/null 2>&1
done
