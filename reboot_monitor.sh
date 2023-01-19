#!/usr/bin/env bash

#cd /home/ls283h/Work/cctv-object-detection
cd /home/lserra/Work/UBDC/cctv_object_detection_v2

script_load_monitor=$(pwd)/monitor_images_input_folder.sh
SESSIONNAME="monitor"

tmux has-session -t $SESSIONNAME &> /dev/null
if [ "$?" != 0 ]; then
    tmux new-session -d -s $SESSIONNAME
    tmux send-keys -t $SESSIONNAME $script_load_monitor C-m
fi
