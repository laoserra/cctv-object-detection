#!/usr/bin/env bash

# This bash script runs the grouping.py script on the Yolo and TF2 data 
# produced the day before.
# The outcome is a log file report for each one of the analysed files.

working_folder="/home/ls283h/projects/cctv-object-detection" #UBDC desktop
script_analysis="$working_folder"/grouping.py
dir_logs="$working_folder"/logs/analyses
yesterday_date="$(date -d yesterday +%Y%m%d)"

cd $working_folder

source /home/ls283h/.virtualenvs/cctv/bin/activate #ubdc desktop

for file in "$working_folder"/daily_reports/*"$yesterday_date".csv.gz
do
    $script_analysis $file > "$dir_logs"/"$(basename $file .csv.gz)".log 2>&1
done
