#!/usr/bin/env bash

# Bash orchestrator, developed by Luis Serra, UBDC, 2023
# Script similar to "monitor_images_input_folder.sh".
# To be used manually to process images in the input folder.
# Instructions: move this script to the main folder and run it.
# To run it do the following in the command line:
# ./process_images_input_folder.sh
# IMPORTANT NOTE: Be sure that monitor_images_input_folder.sh script isn't running.

# path to project main folder
# change to yours, please!
cd '/home/ls283h/projects/cctv-object-detection'

dir_in=$(pwd)/input_folder
script_tf=$(pwd)/detections_main_tensorflow.py
script_yolo=$(pwd)/detections_main_yolo.py
script_blur=$(pwd)/detect_blurred_images.py
dir_logs=$(pwd)/logs
dir_archive=$(pwd)/archive_folder
user=postgres
host=localhost
db=detections

# set warning top limit
end=2

#  setup shell functions for conda and activate environment
eval "$(conda shell.bash hook)"
conda activate cctv

start=`date +%s`

for file in $dir_in/*.jpg
do
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
    warning=$("$script_blur" "$file")
    echo $warning
    if [ "$warning" -ge 1 ] && [ "$warning" -le "$end" ]; then
        echo ---------- image "$filename" not fit for object detection -------------------------------
        psql -U $user -h $host -d $db -c "UPDATE images
                                          SET warnings = $warning
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
done

end=`date +%s`
runtime=$( echo "$end - $start" | bc )
echo elapsed time to make detections on all images in $(basename $dir_in) directory with all models: $runtime sec
