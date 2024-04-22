#!/usr/bin/env python3

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


###############################################################################
#                              Model preparation
###############################################################################

category_index = config.category_index_to_use('tensorflow')

###############################################################################
#                    Prepare to use gRPC endpoint from tf serving
###############################################################################

# gRPC API expects a serialized PredictRequest protocol buffer as input


def create_grpc_stub(host, port=8500):
    """Establish a gRPC channel and a stub."""
    hostport = f'{host}:{port}'
    options = [('grpc.max_send_message_length', 512 * 1024 * 1024),
               ('grpc.max_receive_message_length', 512 * 1024 * 1024)]
    channel = grpc.insecure_channel(hostport, options=options)
    stub = prediction_service_pb2_grpc.PredictionServiceStub(channel)

    return stub


def grpc_request(stub, data_sample, signature_name='serving_default'):
    """Call model and signature to make predictions on image."""
    request = predict_pb2.PredictRequest()
    request.model_spec.name = config.MODEL_NAME_TENSORFLOW
    request.model_spec.signature_name = signature_name
    shp = [dim for dim in data_sample.shape]
    request.inputs['input_tensor'].CopyFrom(tf.make_tensor_proto(data_sample, shape=shp))
    result = stub.Predict(request, 100.0)

    return result


###############################################################################
#                                  Detection
###############################################################################

def run_inference_for_single_image(host, data_sample):
    """Get an output dictionary with bboxes, scores,
    classes and number of detections per image.
    """
    stub = create_grpc_stub(host)
    rs_grpc = grpc_request(stub, data_sample)

    boxes = None; scores = None; classes = None; nums = None

    # get output dict for outputs of interest
    outputs = ['num_detections',
               'detection_boxes',
               'detection_scores',
               'detection_classes']
    shape = []
    output_dict = {}
    for output in outputs:
        shape = tf.TensorShape(rs_grpc.outputs[output].tensor_shape).as_list()
        shape = shape[1:]
        output_dict[output] = np.array(rs_grpc.outputs[output].float_val).reshape(shape)
    # num_detections is an int
    num_detections = int(output_dict.pop('num_detections'))
    output_dict['num_detections'] = num_detections
    # detection_classes should be ints.
    output_dict['detection_classes'] = output_dict['detection_classes'].astype(np.int64)

    return output_dict, boxes, scores, classes, nums


def get_detections(image_name, image_shape, boxes, classes, scores,
                   num_detections, cat_index, min_score_thresh):
    """Retrieve attributes for detected objects of interest."""
    im_width, im_height = image_shape[1], image_shape[0]
    detections = []
    for i in range(num_detections):
        if scores[i] > min_score_thresh:
            box = tuple(boxes[i].tolist())
            temp = cat_index[classes[i]]['name']
            if (classes[i] in cat_index.keys() and
                    temp in config.objects_of_interest):

                ymin, xmin, ymax, xmax = box
                class_name = temp
                (left, right, top, bottom) = (xmin * im_width,
                                              xmax * im_width,
                                              ymin * im_height,
                                              ymax * im_height)
                detections.append(
                    {'image': image_name,
                     'image_size': {
                         'im_width': im_width,
                         'im_height': im_height},
                     'object': class_name,
                     'coordinates': {
                         'left': left,
                         'right': right,
                         'bottom': bottom,
                         'top': top},
                     'score': float(scores[i])})

    return detections


def show_inference(host, image_path):
    """Process inference for a set of images."""
    # read an image
    image_name = os.path.basename(image_path)
    image_base = os.path.splitext(image_name)[0]
    image_ext = os.path.splitext(image_name)[1]
    new_img_name = image_base\
                   + '_bbox_'\
                   + config.MODEL_NAME_TENSORFLOW\
                   + image_ext
    image = Image.open(image_path)
    image_np = np.array(image)
    image_inference = np.expand_dims(image_np, axis=0)
    # Actual detection.
    output_dict = run_inference_for_single_image(host,
                                                 image_inference)[0]
    # artifice to only print objects of interest.
    # to print all detected objects, replace new_scores_array
    # with output_dict['detection_scores'].
    new_scores_array = np.copy(output_dict['detection_scores'])
    classes = output_dict['detection_classes']
    for i in range(output_dict['num_detections']):
        if (category_index[classes[i]]['name'] not in
                config.objects_of_interest):
            new_scores_array[i] = 0
    vis_util.visualize_boxes_and_labels_on_image_array(
        image_np,
        output_dict['detection_boxes'],
        output_dict['detection_classes'],
        new_scores_array,
        category_index,
        use_normalized_coordinates=True,
        max_boxes_to_draw=200,
        min_score_thresh=config.score_threshold_draw,
        line_thickness=4)
    # save image with bounding boxes
    im_save = Image.fromarray(image_np)
    im_save.save(config.OUTPUT_FOLDER + new_img_name)

    detections = get_detections(
        image_name,
        image_np.shape,
        output_dict['detection_boxes'],
        output_dict['detection_classes'],
        output_dict['detection_scores'],
        output_dict['num_detections'],
        category_index,
        config.PREC_REC_THRESHOLD)

    # only write detections if existent
    if detections:
        # write detections to detections db
        if (detections[0]['score'] > config.TF_THRES_SCORE):
            db.insert_multiple_detections(image_name,
                                          config.MODEL_NAME_TENSORFLOW,
                                          detections)
        else:
            print('no objects detected')
    else:
        print('no objects detected')


if __name__ == '__main__':

    show_inference(config.HOST,
                   sys.argv[1])
