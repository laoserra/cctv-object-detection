import numpy as np
import config_detections as config
import cv2
from PIL import Image
import tensorflow as tf
from tensorflow.python.framework import tensor_util
from tensorflow_serving.apis import predict_pb2
from tensorflow_serving.apis import prediction_log_pb2

IM_PATH = './input_folder/other_images/G124.jpg'
NUM_RECORDS = 2

def get_image_rcnn(image_path):
    image = Image.open(image_path)
    image_np = np.array(image)
    image_inference = np.expand_dims(image_np, axis=0)
    return image_inference


def main():
    """Generate TFRecords for warming up."""

    with tf.io.TFRecordWriter("tf_serving_warmup_requests") as writer:
        image_rcnn = get_image_rcnn(IM_PATH)
        predict_request = predict_pb2.PredictRequest()
        predict_request.model_spec.name = 'faster_rcnn_1024_parent'
        predict_request.model_spec.signature_name = 'serving_default'
        shp = [dim for dim in image_rcnn.shape]
        predict_request.inputs['input_tensor'].CopyFrom(tf.make_tensor_proto(image_rcnn, shape=shp))
        log = prediction_log_pb2.PredictionLog(
            predict_log=prediction_log_pb2.PredictLog(request=predict_request))
        for r in range(NUM_RECORDS):
            writer.write(log.SerializeToString())    

if __name__ == "__main__":
    main()
