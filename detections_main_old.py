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
#                              Model preparation
################################################################################

category_index = config.category_index_to_use(sys.argv[2])

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

def run_inference_for_single_image(host, data_sample, model_name):

    '''Get an output dictionary with bboxes, scores, classes and 
    number of detections.'''

    stub = create_grpc_stub(host)
    rs_grpc = grpc_request(stub, data_sample, model_name)

    # get output dict depending on the model
    if model_name == 'yolov3_model_2':

        # outputs of interest. 
        #outputs' names may vary according to yolo model. 
        #check model output signatures first
        outputs = ['yolo_nms',
                   'yolo_nms_1',
                   'yolo_nms_2', 
                   'yolo_nms_3']

        shape = []
        output_dict = {}

        # need check grpc outputs values and set conditions
        for output in outputs:
            shape = tf.TensorShape(rs_grpc.outputs[output].tensor_shape).as_list()
            shape = shape[1:]
            if output == 'yolo_nms' or output == 'yolo_nms_1':
                output_dict[output] = rs_grpc.outputs[output].float_val
            elif output == 'yolo_nms_2':
                output_dict[output] = rs_grpc.outputs[output].int64_val
            else:
                output_dict[output] = rs_grpc.outputs[output].int_val
            output_dict[output] = np.array(output_dict[output]).reshape(shape)
            shape = []

        output_dict['detection_boxes'] = output_dict['yolo_nms']
        output_dict['detection_scores'] = output_dict['yolo_nms_1']
        output_dict['detection_classes'] = output_dict['yolo_nms_2']
        # num_detections is an int
        num_detections = int(output_dict.pop('yolo_nms_3'))
        output_dict['num_detections'] = num_detections

    else:

        # outputs of interest
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
            shape = []
        # num_detections is an int
        num_detections = int(output_dict.pop('num_detections'))
        output_dict['num_detections'] = num_detections

        # detection_classes should be ints.
        output_dict['detection_classes'] = output_dict['detection_classes'].astype(np.int64)


    return output_dict


def get_detections(image_name, image_shape, boxes, classes, scores, 
                   num_detections, cat_index, min_score_thresh, model):
    '''Retrieve attributes of detected objects.'''

    im_width, im_height = image_shape[1], image_shape[0]
    detections = []
    for i in range(num_detections):

        #if scores is None or scores[i] > min_score_thresh:
        if scores[i] > min_score_thresh:
            
            box = tuple(boxes[i].tolist())

            if model == 'yolov4_model_3':
                ymin, xmin, ymax, xmax = box
                if classes[i] in range(len(cat_index)):
                    class_name = cat_index[classes[i]]
                else:
                    class_name = 'N/A'

            elif model == 'yolov3_model_2':
                xmin, ymin, xmax, ymax = box
                if classes[i] in range(len(cat_index)):
                    class_name = cat_index[classes[i]]
                else:
                    class_name = 'N/A'


            # it is a zoo model
            else:
                ymin, xmin, ymax, xmax = box
                if classes[i] in cat_index.keys():
                    class_name = cat_index[classes[i]]['name']
                else:
                    class_name = 'N/A'

            (left, right, top, bottom) = (xmin * im_width,
                                          xmax * im_width,
                                          ymin * im_height,
                                          ymax * im_height)

            detections.append(
            {'image': image_name,
             'image_size': {
                 'im_width':im_width, 
                 'im_height':im_height},
             'object': class_name,
             'coordinates': {
                 'left': left,
                 'right': right,
                 'bottom': bottom,
                 'top': top},
             'score': float(scores[i])
            })

    return detections

def show_inference(host, image_path, model_name):
    '''Process inference for a set of images.'''

    # read an image
    image_name = os.path.basename(image_path)
    image_base = os.path.splitext(image_name)[0]
    image_ext= os.path.splitext(image_name)[1]
    new_img_name = image_base + '_bbox_' + model_name + image_ext

    if model_name == 'yolov3_model_2':
        #cv2.imread returns a numpy array
        image_np = cv2.imread(image_path)
        image_inference = tf.expand_dims(image_np, 0)
        image_inference = resize_image(image_inference, (config.MODEL_SIZE[0], 
                                                         config.MODEL_SIZE[1]))
        image_inference = image_inference.numpy()
        # Actual detection.
        output_dict = run_inference_for_single_image(host, image_inference, model_name)

        #not working
        img_to_draw = draw_outputs(
                image_np, 
                output_dict['detection_boxes'], 
                output_dict['detection_scores'], 
                output_dict['detection_classes'], 
                output_dict['num_detections'], 
                category_index)

        #not working
        cv2.imwrite(config.OUTPUT_FOLDER + \
                '/' + new_img_name, img_to_draw)


    elif model_name == 'yolov4_model_3':
        #cv2.imread returns a numpy array
        image_np = cv2.imread(image_path)
        image_np = cv2.cvtColor(image_np, cv2.COLOR_BGR2RGB)
        # the yolo model we are using implies normalization first
        image_inference = cv2.resize(image_np, (config.MODEL_SIZE[0], 
                                                         config.MODEL_SIZE[1]))
        image_inference = image_inference / 255.
        image_inference = np.expand_dims(image_inference, axis=0)
        image_inference = image_inference.astype(np.float32)
        model_path = './models/yolov4_model_3/1'
        saved_model_loaded = tf.saved_model.load(model_path, tags=[tag_constants.SERVING])
        infer = saved_model_loaded.signatures['serving_default']
        batch_data = tf.constant(image_inference)
        pred = infer(batch_data)
        for value in pred.values():
            boxes = value[:, :, :4]
            pred_conf = value[:, :, 4:]

        # score_threshold = 0.0 to write to database
        boxes, scores, classes, nums = tf.image.combined_non_max_suppression(
                boxes=tf.reshape(boxes, (tf.shape(boxes)[0], -1, 1, 4)),
                scores=tf.reshape(pred_conf, (tf.shape(pred_conf)[0], -1, tf.shape(pred_conf)[-1])),
                max_output_size_per_class=100,
                max_total_size=100,
                iou_threshold= .5,
                score_threshold= 0.0) 

        output_dict = {}
        output_dict['detection_boxes'] = np.squeeze(boxes, axis=0)
        output_dict['num_detections'] = int(nums)
        output_dict['detection_scores'] = np.squeeze(scores, axis=0)
        output_dict['detection_classes'] = np.squeeze(tf.cast(classes, tf.int32), axis=0)

        pred_bbox = [boxes.numpy(), scores.numpy(), classes.numpy(), nums.numpy()]
        image = utils.draw_bbox(image_np, pred_bbox)
        image = Image.fromarray(image.astype(np.uint8))
        image = cv2.cvtColor(np.array(image), cv2.COLOR_BGR2RGB)

        cv2.imwrite(config.OUTPUT_FOLDER + \
                '/' + new_img_name, image)

    # otherwise is a zoo model
    else:
        image = Image.open(image_path)
        image_np = np.array(image)
        image_inference = np.expand_dims(image_np, axis=0)
        # Actual detection.
        output_dict = run_inference_for_single_image(host, image_inference, model_name)

        # put boxes and labels on image
        vis_util.visualize_boxes_and_labels_on_image_array(
            image_np,
            output_dict['detection_boxes'],
            output_dict['detection_classes'],
            output_dict['detection_scores'],
            category_index,
            use_normalized_coordinates=True,
            max_boxes_to_draw=200,
            min_score_thresh=config.SCORE_THRESHOLD,
            line_thickness=6)

        # save image with bounding boxes
        im_save = Image.fromarray(image_np)
        im_save.save(config.OUTPUT_FOLDER + '/' + new_img_name)


    detections = get_detections(
        image_name,
        image_np.shape,
        output_dict['detection_boxes'],
        output_dict['detection_classes'],
        output_dict['detection_scores'],
        output_dict['num_detections'],
        category_index,
        config.PREC_REC_THRESHOLD,
        model_name)

    # write initial attributes to image_model table in validation db
    db.insert_image_model_data(model_name, image_name)
    # write detections to validation db
    db.insert_multiple_detections(model_name, image_name, detections)
    # update counts on the image_model table of validation db
    db.update_counts(model_name, image_name, detections)


if __name__ == '__main__':

    show_inference(config.HOST, 
                   sys.argv[1], 
                   sys.argv[2])
