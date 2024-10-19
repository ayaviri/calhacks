import tensorflow as tf
import numpy as np

fashion_mnist = tf.keras.datasets.fashion_mnist
(x_train, y_train), (x_test, y_test) = fashion_mnist.load_data()

def preprocess_images(images):
    images = np.expand_dims(images, axis=-1)
    images = tf.image.resize(images, [224, 224]).numpy()
    images = images / 255.0
    return images

x_train = preprocess_images(x_train)
x_test = preprocess_images(x_test)
x_train_rgb = np.repeat(x_train, 3, axis=-1)
x_test_rgb = np.repeat(x_test, 3, axis=-1)

batch_size = 32

train_dataset = tf.data.Dataset.from_tensor_slices((x_train_rgb, y_train)).shuffle(1024).batch(batch_size)
test_dataset = tf.data.Dataset.from_tensor_slices((x_test_rgb, y_test)).batch(batch_size)

base_model = tf.keras.applications.MobileNetV2(
    input_shape=(224, 224, 3),
    include_top=True,
    weights='imagenet'
)

num_layers = len(base_model.layers)
print(f"Total number of layers: {num_layers}")


start_layer_shard1 = 0
end_layer_shard1 = 77  

start_layer_shard2 = 77
end_layer_shard2 = num_layers 

layers = base_model.layers
shard1_layers = layers[start_layer_shard1:end_layer_shard1]
shard2_layers = layers[start_layer_shard2:end_layer_shard2]

def build_shard(layers_list, input_shape=None):
    if input_shape:
        inputs = tf.keras.Input(shape=input_shape)
    else:
        inputs = layers_list[0].input
    x = inputs
    for layer in layers_list:
        x = layer(x)
    return tf.keras.Model(inputs=inputs, outputs=x)

input_shape = (224, 224, 3)
shard1_model = build_shard(shard1_layers, input_shape=input_shape)
shard2_input_shape = shard1_layers[-1].output_shape[1:]
shard2_model = build_shard(shard2_layers, input_shape=shard2_input_shape)

print("Shard 1 Model Summary:")
shard1_model.summary()
print("\nShard 2 Model Summary:")
shard2_model.summary()
