#!/usr/bin/env bash

#           -p 8501:8501 \
docker run -d --rm --gpus all \
           -p 8500:8500 \
           -v "$(pwd)/models/:/models/" \
           -t tensorflow/serving:latest-gpu \
           --model_config_file=/models/models_all.config
