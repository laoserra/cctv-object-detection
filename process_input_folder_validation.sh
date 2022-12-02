#!/usr/bin/env bash

dir_in=$(pwd)/input_folder
script_detections=$(pwd)/detections_main.py

source /home/lserra/python-virtual-environments/serving/bin/activate
#source /home/datasci/.virtualenvs/video/bin/activate

start=`date +%s`

for file in $dir_in/*.jpg
do
 echo detected "$(basename $file)" - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
 echo executing faster_rcnn_1024_model_1 script
 python $script_detections $file faster_rcnn_1024_model_1
 echo executing yolov4_model_3 script
 python $script_detections $file yolov4_model_3
done

end=`date +%s`
runtime=$( echo "$end - $start" | bc )
echo elapsed time to make detections on all images in $(basename $dir_in) directory with all models: $runtime sec
