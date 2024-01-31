#!/usr/bin/env bash

working_folder="/home/datasci/Work/cctv-object-detection" #UBDC3 server
script_analysis="$working_folder"/grouping.py
dir_logs="$working_folder"/logs/analyses
yesterday_date="$(date -d yesterday +%Y%m%d)"

cd $working_folder

source /home/datasci/.virtualenvs/serving/bin/activate #ubdc3 server

for file in "$working_folder"/daily_reports/*"$yesterday_date".csv.gz
do
    $script_analysis $file > "$dir_logs"/"$(basename $file .csv.gz)".log 2>&1
done