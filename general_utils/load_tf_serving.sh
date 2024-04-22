#!/usr/bin/env bash

# Run an instance of TF Serving docker 
# serving the YOLOV4 and TF2 models.

# path to project main folder
# change to yours
cd "/home/ls283h/projects/cctv-object-detection"

docker run -d --restart always --gpus all \
           -p 8500:8500 \
           -v "$(pwd)/models/:/models/" \
           -t tensorflow/serving:2.8.2 \
           --model_config_file=/models/models_all.config
