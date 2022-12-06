import tensorflow as tf
from tensorflow_serving.apis import predict_pb2

def main():
    with tf.io.TFRecordWriter("tf_serving_warmup_requests") as writer:
        # replace <request> with one of:
        # predict_pb2.PredictRequest(..)
        # classification_pb2.ClassificationRequest(..)
        # regression_pb2.RegressionRequest(..)
        # inference_pb2.MultiInferenceRequest(..)
        log = prediction_log_pb2.PredictionLog(
            predict_log=prediction_log_pb2.PredictLog(request=predict_pb2.PredictRequest(..)))
        writer.write(log.SerializeToString())

if __name__ == "__main__":
    main()
