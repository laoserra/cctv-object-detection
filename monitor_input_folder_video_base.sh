#!/usr/bin/env bash

DIR_IN="/home/datasci/video_analytics/input_folder"
DIR_ARCHIVE="/home/datasci/video_analytics/archive_folder"
SCRIPT_VIDEO="/home/datasci/video_analytics/object_tracking.py"
DIR_LOGS="/home/datasci/video_analytics/logs/tf_serving"
LOI=2.8
source /home/datasci/.virtualenvs/video/bin/activate

inotifywait -m -e create -e moved_to --format "%w%f" $DIR_IN | while read file
do
  if [ ${file: -9} == "cam01.mp4" ]
  then
    echo Detected $file, running counts and detections
    python $SCRIPT_VIDEO $file $LOI > $DIR_LOGS/"$(basename $file .mp4).log" 2>&1
    mv $file $DIR_ARCHIVE
  else
    echo Detected $file, running counts and detections
    python $SCRIPT_VIDEO $file 2.4 > $DIR_LOGS/"$(basename $file .mp4).log" 2>&1
    mv $file $DIR_ARCHIVE
  fi
done
