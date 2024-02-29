#!/usr/bin/env bash

# Script developed by Luis Serra, UBDC, 2023.
# This script loads the bash orchestrator 
# script in a tmux dedicated session.

cd  /home/datasci/Work/cctv-object-detection  #ubdc3 path

script_load_monitor=$(pwd)/monitor_images_input_folder.sh
SESSIONNAME="monitor"

tmux has-session -t $SESSIONNAME &> /dev/null
if [ "$?" != 0 ]; then
    tmux new-session -d -s $SESSIONNAME
    tmux send-keys -t $SESSIONNAME $script_load_monitor C-m
fi
