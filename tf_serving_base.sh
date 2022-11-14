#!/usr/bin/env bash

docker run -d --rm --gpus all -p 8500:8500 -p 8501:8501 \
	--mount type=bind,source=/home/datasci/video_analytics/models/widerperson,target=/models/widerperson \
	-e MODEL_NAME=widerperson -t tensorflow/serving:latest-gpu
