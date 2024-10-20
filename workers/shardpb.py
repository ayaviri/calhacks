import tensorflow as tf
import numpy as np
import os
# Load and preprocess data (you can skip this part if you're only testing sharding)
# fashion_mnist = tf.keras.datasets.fashion_mnist
# (x_train, y_train), (x_test, y_test) = fashion_mnist.load_data()

# def preprocess_images(images):
#     images = np.expand_dims(images, axis=-1)
#     images = tf.image.resize(images, [224, 224]).numpy()
#     images = images / 255.0
#     return images

# x_train = preprocess_images(x_train)
# x_test = preprocess_images(x_test)

# x_train_rgb = np.repeat(x_train, 3, axis=-1)
# x_test_rgb = np.repeat(x_test, 3, axis=-1)


base_model = tf.keras.applications.VGG16(
    input_shape=(224, 224, 3),
    include_top=False,
    weights='imagenet'
)
base_model.save("base_model.keras")


split_layer_name = 'block3_pool'
split_layer = base_model.get_layer(split_layer_name).output

# Model Part 1
model_part1 = tf.keras.Model(inputs=base_model.input, outputs=split_layer)

# Model Part 2
input_part2 = tf.keras.Input(shape=split_layer.shape[1:])
x = input_part2

split_layer_index = base_model.layers.index(base_model.get_layer(split_layer_name))
for layer in base_model.layers[split_layer_index + 1:]:
    x = layer(x)

x = tf.keras.layers.Flatten()(x)
x = tf.keras.layers.Dense(10, activation='softmax')(x)

model_part2 = tf.keras.Model(inputs=input_part2, outputs=x)

print("Number of layers in model_part1:", len(model_part1.layers))
print("Number of layers in model_part2:", len(model_part2.layers))

sample_data = tf.random.uniform((2, 224, 224, 3))

intermediate_output = model_part1(sample_data)
print("Intermediate output shape:", intermediate_output.shape)


final_output = model_part2(intermediate_output)
print("Final output shape:", final_output.shape)

def merge_models(model_part1, model_part2):
    full_input = model_part1.input
    intermediate_output = model_part1.output
    full_output = model_part2(intermediate_output)
    full_model = tf.keras.Model(inputs=full_input, outputs=full_output)
    return full_model

full_model = merge_models(model_part1, model_part2)

sample_data = tf.random.uniform((2, 224, 224, 3))  

predictions = full_model.predict(sample_data)
print("Number of layers in merged model:", len(full_model.layers))
print("Predictions shape:", predictions.shape)
print("Predictions:", predictions)
full_model.save = ("trained_model.keras")
