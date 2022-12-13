#!/usr/bin/env bash

#cd /home/ls283h/Work/cctv-object-detection
cd /home/lserra/Work/UBDC/cctv_object_detection_v2

script_load_tfs=$(pwd)/load_tf_serving.sh
script_load_monitor=$(pwd)/monitor_images_input_folder.sh
SESSIONNAME1="serving"
SESSIONNAME2="monitor"

tmux has-session -t $SESSIONNAME1 &> /dev/null
if [ "$?" != 0 ]; then
    tmux new-session -d -s $SESSIONNAME1
    tmux send-keys -t $SESSIONNAME1 $script_load_tfs C-m
fi

tmux has-session -t $SESSIONNAME2 &> /dev/null
if [ "$?" != 0 ]; then
    tmux new-session -d -s $SESSIONNAME2
    tmux send-keys -t $SESSIONNAME2 $script_load_monitor C-m
fi
