#!/usr/bin/env bash

# Run an instance of TF Serving docker 
# with the YOLOV4 model and TF2 model.

docker run -d --restart always --gpus all \
           -p 8500:8500 \
           -v "$(pwd)/models/:/models/" \
           -t tensorflow/serving:2.8.2 \
           --model_config_file=/models/models_all.config
