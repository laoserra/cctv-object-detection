#!/usr/bin/env bash

dir_in=$(pwd)/input_folder
script_detections=$(pwd)/detections_main.py
dir_logs=$(pwd)/logs
dir_archive=$(pwd)/archive_folder
user=postgres
host=localhost
db=detections
source /home/lserra/python-virtual-environments/serving/bin/activate #my laptop path
#source /home/datasci/.virtualenvs/video/bin/activate #ubdc2 path
#source /home/datasci/.virtualenvs/serving/bin/activate #ubdc3 path
#source /home/ls283h/python-virtual-environments/serving/bin/activate #my desktop path

# event "close_write" allows for created files to be closed before processing
inotifywait -m -e close_write,moved_to  --format "%w%f" $dir_in | while read file
do
    if [ "${file: -4}" == ".jpg" ]; then
        filename=$(basename $file)
        width=$(identify -format "%w" $file)
        height=$(identify -format "%h" $file)
        #number of seconds since the epoch
        unix_time=$(date +%s)
        psql -U $user -h $host -d $db -c "INSERT INTO images (unix_time_insertion,name,width,height) 
                                          VALUES($unix_time,'$filename',$width,$height);"
        if [ "$width" -eq 550 ] && [ "$height" -eq 367 ]; then
            echo ---------- image $filename: Camera in use by GOC -------------------------------
            psql -U $user -h $host -d $db -c "UPDATE images
                                              SET warnings = 1
                                              WHERE unix_time_insertion = $unix_time
                                              AND name = '$filename';"
            mv $file $dir_archive
        else
            echo ---------- executing faster_rcnn_1024_parent model on image $filename ---------- 
            $script_detections $file faster_rcnn_1024_parent > $dir_logs/"$(basename $file .jpg)_rcnn.log" 2>&1
            echo ---------- executing yolov4_9_objs model on image $filename -------------------- 
            $script_detections $file yolov4_9_objs > $dir_logs/"$(basename $file .jpg)_yolo.log" 2>&1
            mv $file $dir_archive
        fi
    fi
done
