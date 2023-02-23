#!/usr/bin/env bash

dir_in=$(pwd)/input_folder
script_detections=$(pwd)/detections_main.py
dir_logs=$(pwd)/logs
dir_archive=$(pwd)/archive_folder
user=postgres
host=localhost
db=detections
source /home/lserra/python-virtual-environments/serving/bin/activate
#source /home/datasci/.virtualenvs/video/bin/activate #ubdc2 server
#source /home/datasci/.virtualenvs/serving/bin/activate #ubdc3 server

start=`date +%s`

for file in $dir_in/*.jpg
do
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
done

end=`date +%s`
runtime=$( echo "$end - $start" | bc )
echo elapsed time to make detections on all images in $(basename $dir_in) directory with all models: $runtime sec
