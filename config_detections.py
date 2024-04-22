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
# PATH_DB = OUTPUT_FOLDER + 'detections.db'

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

# Name of the models
MODEL_NAME_TENSORFLOW = 'faster_rcnn_1024_parent'
MODEL_NAME_YOLO = 'yolov4_9_objs'

# category_index to use depends on the model
def category_index_to_use(model):
    """Set category index to use.

    Model dependent.
    """
    if model == 'tensorflow':
        category_index = label_map_util.create_category_index_from_labelmap(PATH_TO_LABELS)
    else:  # it's the yolo model
        category_index = load_class_names(PATH_TO_COCO_LABELS)

    return category_index

# tensorflow one colour maximum confidence score
TF_THRES_SCORE = 0.0001317993737757206
# NOTE:
# threshold score used is highest obtained for one colour image
# items in detections are ordered by score in descending order
# threshold score may vary in different machines
###############################################################################
