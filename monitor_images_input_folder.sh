#!/usr/bin/env bash

# Bash orchestrator for image processing by Luis Serra, UBDC, 2023
# This script orchestrates the following tasks while 
# images finish being created in the input folder:
#    1. Retrieve image attributes and write them into the database
#    2. Check image dimensions and process if adequate (as agreed with GCC)
#    3. Detect object of interest with TF2 model and produce a log file
#    4. Detect object of interest with YOLOV4 model and produce a log file
#    5. Move processed images to the archive folder

dir_in=$(pwd)/input_folder
script_tf=$(pwd)/detections_main_tensorflow.py
script_yolo=$(pwd)/detections_main_yolo.py
dir_logs=$(pwd)/logs
dir_archive=$(pwd)/archive_folder
user=postgres
host=localhost
db=detections

#  setup shell functions for conda and activate environment
eval "$(conda shell.bash hook)"
conda activate cctv

# event "close_write" allows for created files to be closed before processing
inotifywait -m -e close_write,moved_to  --format "%w%f" $dir_in | while read file
do
    if [ "${file: -4}" == ".jpg" ]; then
        filename=$(basename $file)
        width=$(identify -format "%w" $file)
        height=$(identify -format "%h" $file)
        #number of seconds since the epoch
        current_time=$(date +%s)
        image_time_ms="$(awk -F_ '{split($0, arr); print arr[1]}' <<< ${filename})"
        camera_ref="$(awk -F_ '{split($0, arr); print arr[2]}' <<< ${filename})"
        #floor division. Closer to reality due to delay in getting cctv timestamp
        image_time=$(($image_time_ms / 1000))
        image_id=$(psql -qtAX -U $user -h $host -d $db -c "INSERT INTO images (image_proc,image_capt,
                                                                               camera_ref,name,width,height) 
                                                           VALUES(to_timestamp($current_time),to_timestamp($image_time),
                                                                               '$camera_ref','$filename',$width,$height) 
                                                           RETURNING id;")
        if [ "$width" -eq 550 ] && [ "$height" -eq 367 ]; then
            echo ---------- image $filename: Camera in use by GOC -------------------------------
            psql -U $user -h $host -d $db -c "UPDATE images
                                              SET warnings = 1
                                              WHERE id = $image_id;"
            mv $file $dir_archive
        else
            echo ---------- executing faster_rcnn_1024_parent model on image $filename ---------- 
            $script_tf $file > $dir_logs/"$(basename $file .jpg)_rcnn.log" 2>&1 &
            echo ---------- executing yolov4_9_objs model on image $filename -------------------- 
            $script_yolo $file > $dir_logs/"$(basename $file .jpg)_yolo.log" 2>&1 &
            wait
            mv $file $dir_archive
        fi
    fi
done
