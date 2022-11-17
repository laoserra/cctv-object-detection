# base imports
from PIL import Image
import cv2
import numpy as np
import sys
import os
import tensorflow as tf
import config_detections as config
import yolo.core.utils as utils
#from yolo.core.yolov4 import filter_boxes
from tensorflow.python.saved_model import tag_constants


category_index = config.category_index_to_use(sys.argv[2])


def get_detections(image_name, image_shape, boxes, classes, scores, 
                   num_detections, cat_index, min_score_thresh, model):
    '''Retrieve attributes of detected objects.'''

    im_width, im_height = image_shape[1], image_shape[0]
    detections = []
    for i in range(num_detections):

        #if scores is None or scores[i] > min_score_thresh:
        if scores[i] > min_score_thresh:
            
            box = tuple(boxes[i].tolist())

            ymin, xmin, ymax, xmax = box
            if classes[i] in range(len(cat_index)):
                class_name = cat_index[classes[i]]
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


def show_inference(image_path, model_name):

    '''Process inference for a set of images.'''

    # read an image
    image_name = os.path.basename(image_path)
    image_base = os.path.splitext(image_name)[0]
    image_ext= os.path.splitext(image_name)[1]
    new_img_name = image_base + '_bbox_' + model_name + image_ext

    #cv2.imread returns a numpy array
    image_np = cv2.imread(image_path)
    image_np = cv2.cvtColor(image_np, cv2.COLOR_BGR2RGB)
    # the yolo model we are using implies normalization first
    image_inference = cv2.resize(image_np, (config.MODEL_SIZE[0], 
                                                     config.MODEL_SIZE[1]))
    image_inference = image_inference / 255.
    image_inference = np.expand_dims(image_inference, axis=0)
    image_inference = image_inference.astype(np.float32)
    model_path = './models/yolov4_9_objs/1'
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
            iou_threshold= 0.5,
            score_threshold= 0.0) 
    print(boxes)
    print(scores)

    output_dict = {}
    output_dict['detection_boxes'] = np.squeeze(boxes, axis=0)
    output_dict['num_detections'] = int(nums)
    output_dict['detection_scores'] = np.squeeze(scores, axis=0)
    output_dict['detection_classes'] = np.squeeze(tf.cast(classes, tf.int32), axis=0)

    # need to filter bboxes greater than 50% score. check todo txt file
    pred_bbox = [boxes.numpy(), scores.numpy(), classes.numpy(), nums.numpy()]
    image = utils.draw_bbox(image_np, pred_bbox)
    image = Image.fromarray(image.astype(np.uint8))
    image = cv2.cvtColor(np.array(image), cv2.COLOR_BGR2RGB)

    cv2.imwrite(config.OUTPUT_FOLDER + new_img_name, image)

    detections = get_detections(
        image_name,
        image_np.shape,
        output_dict['detection_boxes'],
        output_dict['detection_classes'],
        output_dict['detection_scores'],
        output_dict['num_detections'],
        category_index,
        0,
        model_name)

    #print(detections)


if __name__ == '__main__':

    show_inference(sys.argv[1], sys.argv[2])
