from yolo.utils_yolov3 import load_class_names

################################################################################
#                              Configuration parameters
################################################################################

# class labels
category_index_faster_rcnn = {1: {'id': 1, 'name': 'crowd'},
                              2: {'id': 2, 'name': 'car'},
                              3: {'id': 3, 'name': 'van'},
                              4: {'id': 4, 'name': 'taxi'},
                              5: {'id': 5, 'name': 'bus'},
                              6: {'id': 6, 'name': 'lorry'},
                              7: {'id': 7, 'name': 'pedestrian'},
                              8: {'id': 8, 'name': 'motorcycle'},
                              9: {'id': 9, 'name': 'cyclist'}}

# path to images with bounding boxes
OUTPUT_FOLDER = './output_folder/'

# PATH to existent database
PATH_DB = OUTPUT_FOLDER + 'validation.db'

# path to archive processed images
PATH_TO_ARCHIVE = './archive_folder/'

# List of strings that is used to add correct label for each box
# on the parent model
#PATH_TO_LABELS = './object_detection/data/mscoco_label_map.pbtxt'

# detection threshold (thres=0 to build the precision/recall graph)
PREC_REC_THRESHOLD = 0

# minimum score detection threshold
SCORE_THRESHOLD = 0.5

### Yolo specific configurations ###
#MODEL_SIZE = (416, 416, 3)
MODEL_SIZE = (608, 608, 3)
NUM_CLASSES = 9
PATH_TO_COCO_LABELS = './yolo/coco.names' 
# maximum number of boxes per image?
MAX_OUTPUT_SIZE = 100
# maximum number of boxes per class on each image?
MAX_OUTPUT_SIZE_PER_CLASS = 100
IOU_THRESHOLD = 0.5

#IP address of the model server
HOST = 'localhost'

# category_index to use depends on the model
def category_index_to_use(model_name):
    if model_name == 'faster_rcnn_1024_model_1':
        category_index = category_index_faster_rcnn
    else:
        category_index = load_class_names(PATH_TO_COCO_LABELS)

    return category_index
################################################################################
