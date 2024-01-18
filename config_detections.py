from object_detection.utils import label_map_util
from yolo.utils_yolov3 import load_class_names

###############################################################################
#                              Configuration parameters
###############################################################################

# objects of interest for frcnn parent model
objects_of_interest = ['bicycle',
                       'car',
                       'person',
                       'motorcycle',
                       'bus',
                       'truck']

# path to images with bounding boxes
OUTPUT_FOLDER = './output_folder/'

# PATH to existent database CHECK THIS AND DELETE!
#PATH_DB = OUTPUT_FOLDER + 'detections.db'

# path to archive processed images
PATH_TO_ARCHIVE = './archive_folder/'

# List of strings that is used to add correct label for each box
# on the parent model
PATH_TO_LABELS = './object_detection/data/mscoco_label_map.pbtxt'

# detection threshold (thres=0 to build the precision/recall graph)
PREC_REC_THRESHOLD = 0

# minimum score detection threshold
SCORE_THRESHOLD = 0.5

# Yolo specific configurations #
MODEL_SIZE = (608, 608, 3)
NUM_CLASSES = 9
PATH_TO_COCO_LABELS = './yolo/coco.names'
# maximum number of boxes per image?
MAX_OUTPUT_SIZE = 100
# maximum number of boxes per class on each image?
MAX_OUTPUT_SIZE_PER_CLASS = 100
IOU_THRESHOLD = 0.5
score_threshold_draw = 0.5

# IP address of the model server
HOST = 'localhost'


# category_index to use depends on the model
def category_index_to_use(model_name):
    if model_name == 'faster_rcnn_1024_parent':
        category_index = label_map_util.create_category_index_from_labelmap(PATH_TO_LABELS)
    else:  # it's a yolo model
        category_index = load_class_names(PATH_TO_COCO_LABELS)

    return category_index
################################################################################
