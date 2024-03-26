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

category_index = config.category_index_to_use('yolo')

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
    request.model_spec.name = config.MODEL_NAME_YOLO
    request.model_spec.signature_name = signature_name
    shp = [dim for dim in data_sample.shape]
    request.inputs['input_1'].CopyFrom(tf.make_tensor_proto(data_sample, shape=shp))
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

    # get output dict
    shape = tf.TensorShape(rs_grpc.outputs['tf_op_layer_concat_18'].tensor_shape).as_list()
    shape = shape[1:]
    output_array = np.array(rs_grpc.outputs['tf_op_layer_concat_18'].float_val).reshape(shape)
    output_array = tf.constant(output_array, dtype=tf.float32)
    output_array = tf.expand_dims(output_array, axis=0)
    boxes = output_array[:, :, :4]
    pred_conf = output_array[:, :, 4:]
    #  set score_threshold = 0.0 to write to database
    boxes, scores, classes, nums = tf.image.combined_non_max_suppression(
            boxes=tf.reshape(boxes, (tf.shape(boxes)[0], -1, 1, 4)),
            scores=tf.reshape(pred_conf, (tf.shape(pred_conf)[0], -1,
                                          tf.shape(pred_conf)[-1])),
            max_output_size_per_class=config.MAX_OUTPUT_SIZE_PER_CLASS,
            max_total_size=config.MAX_OUTPUT_SIZE,
            iou_threshold=config.IOU_THRESHOLD,
            score_threshold=config.PREC_REC_THRESHOLD)

    output_dict = {}
    output_dict['detection_boxes'] = np.squeeze(boxes, axis=0)
    output_dict['num_detections'] = int(nums)
    output_dict['detection_scores'] = np.squeeze(scores, axis=0)
    output_dict['detection_classes'] = np.squeeze(tf.cast(classes,
                                                  tf.int32), axis=0)

    return output_dict, boxes, scores, classes, nums


def get_detections(image_name, image_shape, boxes, classes, scores,
                   num_detections, cat_index, min_score_thresh):
    """Retrieve attributes of detected objects of interest."""
    im_width, im_height = image_shape[1], image_shape[0]
    detections = []
    for i in range(num_detections):
        if scores[i] > min_score_thresh:
            box = tuple(boxes[i].tolist())
            if (classes[i] in range(len(cat_index))):
                ymin, xmin, ymax, xmax = box
                class_name = cat_index[classes[i]]
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
                   + config.MODEL_NAME_YOLO\
                   + image_ext
    image = Image.open(image_path)
    image_np = np.array(image)
    image_inference = cv2.resize(image_np, (config.MODEL_SIZE[0],
                                            config.MODEL_SIZE[1]))
    image_inference = image_inference / 255.
    image_inference = np.expand_dims(image_inference, axis=0)
    image_inference = image_inference.astype(np.float32)
    # Actual detection.
    output_dict, boxes, scores, classes, nums =\
        run_inference_for_single_image(host, image_inference)
    # put boxes and labels on image
    # to print only objects above threshold
    counter = 0
    for score in scores[0]:
        if score > config.score_threshold_draw:
            counter += 1
    nums = np.array([counter], dtype=np.int32)
    pred_bbox = [boxes.numpy(), scores.numpy(), classes.numpy(), nums]
    image = utils.draw_bbox(image_np, pred_bbox)
    image = Image.fromarray(image.astype(np.uint8))
    image = cv2.cvtColor(np.array(image), cv2.COLOR_BGR2RGB)
    # save image with bounding boxes
    cv2.imwrite(config.OUTPUT_FOLDER + new_img_name, image)

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
        db.insert_multiple_detections(image_name, config.MODEL_NAME_YOLO, detections)
    else:
        print('no objects detected')


if __name__ == '__main__':

    show_inference(config.HOST,
                   sys.argv[1])
