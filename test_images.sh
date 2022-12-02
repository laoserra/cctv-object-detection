#!/usr/bin/env bash

dir_in=$(pwd)/input_folder

source /home/lserra/python-virtual-environments/serving/bin/activate

for file in $dir_in/*.jpg
do
    filename=$(basename $file)
    width=$(identify -format "%w" $file)
    height=$(identify -format "%h" $file)
    #number of seconds since the epoch
    unix_time=$(date +%s)
    sqlite3 $(pwd)/output_folder/detections.db "INSERT INTO images (unix_time_insertion, name, width, height) 
                                                VALUES($unix_time,'$filename',$width,$height);"

done
