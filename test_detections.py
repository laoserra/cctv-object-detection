# base imports
from PIL import Image
import cv2
import numpy as np
import sys
import os
import grpc
import tensorflow as tf
from tensorflow_serving.apis import predict_pb2
from tensorflow_serving.apis import prediction_service_pb2_grpc
import manage_detections_db as db
import config_detections as config
from object_detection.utils import visualization_utils as vis_util
import yolo.core.utils as utils
from yolo.core.yolov4 import filter_boxes
from tensorflow.python.saved_model import tag_constants

################################################################################
#                    Prepare to use gRPC endpoint from tf serving 
################################################################################

# gRPC API expects a serialized PredictRequest protocol buffer as input


def create_grpc_stub(host, port=8500):

    '''Establish a gRPC channel and a stub.'''

    hostport = f'{host}:{port}'
    options = [('grpc.max_send_message_length', 512 * 1024 * 1024), 
               ('grpc.max_receive_message_length', 512 * 1024 * 1024)]
    channel = grpc.insecure_channel(hostport, options=options)
    stub = prediction_service_pb2_grpc.PredictionServiceStub(channel)

    return stub


def grpc_request(stub, data_sample, model_name, \
                 signature_name='serving_default'):

    '''Call model and signature to make predictions on image.'''

    request = predict_pb2.PredictRequest()
    request.model_spec.name = model_name
    request.model_spec.signature_name = signature_name
    shp = [dim for dim in data_sample.shape]
    if sys.argv[2] == 'yolov4_9_objs':
        request.inputs['input_1'].CopyFrom(tf.make_tensor_proto(data_sample, shape=shp))
    else: #it's the faster rcnn model
        request.inputs['input_tensor'].CopyFrom(tf.make_tensor_proto(data_sample, shape=shp))
    
    result = stub.Predict(request, 100.0)

    return result


################################################################################
#                                  Detection
################################################################################

if __name__ == '__main__':

    if sys.argv[2] == 'yolov4_9_objs':
        image = Image.open(sys.argv[1])
        image_np = np.array(image)
        image_inference = cv2.resize(image_np, (config.MODEL_SIZE[0], 
                                                         config.MODEL_SIZE[1]))
        image_inference = image_inference / 255.
        image_inference = np.expand_dims(image_inference, axis=0)
        image_inference = image_inference.astype(np.float32)
    else: # otherwise is a zoo model
        image = Image.open(sys.argv[1])
        image_np = np.array(image)
        image_inference = np.expand_dims(image_np, axis=0)

    stub = create_grpc_stub(config.HOST)
    print(grpc_request(stub, image_inference, sys.argv[2]))
