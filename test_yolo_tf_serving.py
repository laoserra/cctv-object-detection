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

def show_inference(image_path, model_name):

    '''Process inference for a set of images.'''

    # read an image
    image_name = os.path.basename(image_path)
    image_base = os.path.splitext(image_name)[0]
    image_ext= os.path.splitext(image_name)[1]
    new_img_name = image_base + '_bbox_' + model_name + image_ext

    if model_name == 'yolov4_9_objs':
        image = Image.open(image_path)
        image_np = np.array(image)
        image_inference = cv2.resize(image_np, (config.MODEL_SIZE[0], 
                                                config.MODEL_SIZE[1]))
        image_inference = image_inference / 255.
        image_inference = np.expand_dims(image_inference, axis=0)
        image_inference = image_inference.astype(np.float32)
    else: # otherwise is a zoo model
        image = Image.open(image_path)
        image_np = np.array(image)
        image_inference = np.expand_dims(image_np, axis=0)

    stub = create_grpc_stub(config.HOST)
    rs_grpc = grpc_request(stub, image_inference, model_name)

    shape = tf.TensorShape(rs_grpc.outputs['tf_op_layer_concat_18'].tensor_shape).as_list()
    shape = shape[1:]
    output_array = np.array(rs_grpc.outputs['tf_op_layer_concat_18'].float_val).reshape(shape)
    output_array = tf.constant(output_array, dtype=tf.float32)
    output_array = tf.expand_dims(output_array, axis=0)

    boxes = output_array[:, :, :4]
    pred_conf = output_array[:, :, 4:]
    # set score_threshold = 0.0 to write to database
    boxes, scores, classes, nums = tf.image.combined_non_max_suppression(
            boxes=tf.reshape(boxes, (tf.shape(boxes)[0], -1, 1, 4)),
            scores=tf.reshape(pred_conf, (tf.shape(pred_conf)[0], -1, tf.shape(pred_conf)[-1])),
            max_output_size_per_class=100,
            max_total_size=100,
            iou_threshold= 0.5,
            score_threshold= 0.0) 

    # choose bounding boxes to write to image
    counter = 0
    for score in scores[0]:
        if score > config.score_threshold_draw:
            counter += 1
    nums = tf.constant([counter])
    pred_bbox = [boxes.numpy(), scores.numpy(), classes.numpy(), nums.numpy()]
    image = utils.draw_bbox(image_np, pred_bbox)
    image = Image.fromarray(image.astype(np.uint8))
    image = cv2.cvtColor(np.array(image), cv2.COLOR_BGR2RGB)

    cv2.imwrite(config.OUTPUT_FOLDER + new_img_name, image)


if __name__ == '__main__':

    show_inference(sys.argv[1], sys.argv[2])
