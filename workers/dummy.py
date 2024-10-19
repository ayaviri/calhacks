import tensorflow as tf
from tensorflow.keras import layers, models
import numpy as np

fashion_mnist = tf.keras.datasets.fashion_mnist
(_, _), (x_test, y_test) = fashion_mnist.load_data()

def preprocess_images(images):
    images = np.expand_dims(images, axis=-1)
    images = tf.image.resize(images, [224, 224]).numpy()
    images = images / 255.0
    return images

x_test = preprocess_images(x_test)

x_test_rgb = np.repeat(x_test, 3, axis=-1)  

model = tf.keras.applications.MobileNetV2(
    input_shape=(224, 224, 3),
    include_top=True,
    weights='imagenet'
)

model_id = id(model)
num_layers = len(model.layers)


class ModelShard:
    def __init__(self, model_id, num_layers, ground_truth):
        self.model_id = model_id
        self.num_layers = num_layers
        self.ground_truth = ground_truth  

    def __repr__(self):
        return f"ModelShard(model_id={self.model_id}, num_layers={self.num_layers})"


model_shard = ModelShard(model_id, num_layers, y_test)
print(model_shard)  

model.export('saved_model')


converter = tf.lite.TFLiteConverter.from_saved_model('saved_model')
tflite_model = converter.convert()

with open('mobilenetv2.tflite', 'wb') as f:
    f.write(tflite_model)
print("TensorFlow Lite model saved as 'mobilenetv2.tflite'")
