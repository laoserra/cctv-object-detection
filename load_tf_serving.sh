#!/usr/bin/env bash

docker run -d --rm --gpus all \
           -p 8500:8500 \
           -v "$(pwd)/models/:/models/" \
           -t tensorflow/serving:2.8.2 \
           --model_config_file=/models/models_all.config
