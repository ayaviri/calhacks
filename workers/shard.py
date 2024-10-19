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
train_dataset = tf.data.Dataset.from_tensor_slices((x_train_rgb, y_train))
train_dataset = train_dataset.shuffle(buffer_size=1024).batch(batch_size)

base_model = tf.keras.applications.MobileNetV2(
    input_shape=(224, 224, 3),
    include_top=True,
    weights='imagenet'
)

start_layer_shard1 = 0
end_layer_shard1 = 77 

start_layer_shard2 = 78
end_layer_shard2 = len(base_model.layers)

layers = base_model.layers

shard1_layers = layers[start_layer_shard1:end_layer_shard1]

shard2_layers = layers[start_layer_shard2:end_layer_shard2]

def build_shard(layers_list, input_shape=None):
    inputs = tf.keras.Input(shape=input_shape) if input_shape else layers_list[0].input
    x = inputs
    for layer in layers_list:
        x = layer(x)
    model = tf.keras.Model(inputs=inputs, outputs=x)
    return model

input_shape = (224, 224, 3)
shard1_model = build_shard(shard1_layers, input_shape=input_shape)
shard2_model = build_shard(shard2_layers)

for layer in shard1_model.layers:
    layer.trainable = True

for layer in shard2_model.layers:
    layer.trainable = True

loss_fn = tf.keras.losses.SparseCategoricalCrossentropy()
optimizer = tf.keras.optimizers.Adam()

epochs = 5

for epoch in range(epochs):
    print(f"Epoch {epoch+1}/{epochs}")
    for step, (x_batch, y_batch) in enumerate(train_dataset):
        with tf.GradientTape(persistent=True) as tape:

            x_shard1 = shard1_model(x_batch, training=True)
            
            logits = shard2_model(x_shard1, training=True)
            
            loss_value = loss_fn(y_batch, logits)
        
        gradients_shard2 = tape.gradient(loss_value, shard2_model.trainable_variables)
        gradients_shard1 = tape.gradient(loss_value, shard1_model.trainable_variables)
        
        optimizer.apply_gradients(zip(gradients_shard1, shard1_model.trainable_variables))
        optimizer.apply_gradients(zip(gradients_shard2, shard2_model.trainable_variables))
        
        if step % 100 == 0:
            print(f"Step {step}, Loss: {loss_value.numpy():.4f}")
    
    print(f"Epoch {epoch+1} completed.")

inputs = tf.keras.Input(shape=(224, 224, 3))
x = shard1_model(inputs)
outputs = shard2_model(x)
full_model = tf.keras.Model(inputs=inputs, outputs=outputs)

test_dataset = tf.data.Dataset.from_tensor_slices((x_test_rgb, y_test))
test_dataset = test_dataset.batch(batch_size)

accuracy = tf.keras.metrics.SparseCategoricalAccuracy()

for x_batch, y_batch in test_dataset:
    logits = full_model(x_batch, training=False)
    accuracy.update_state(y_batch, logits)

print(f"Test Accuracy: {accuracy.result().numpy():.4f}")

model_id = id(full_model)
num_layers = len(full_model.layers)

class ModelShard:
    def __init__(self, model_id, num_layers, ground_truth, start_layer, end_layer):
        self.model_id = model_id
        self.num_layers = num_layers
        self.ground_truth = ground_truth
        self.start_layer = start_layer
        self.end_layer = end_layer

    def __repr__(self):
        return (f"ModelShard(model_id={self.model_id}, num_layers={self.num_layers}, "
                f"start_layer={self.start_layer}, end_layer={self.end_layer})")

shard1_info = ModelShard(model_id, num_layers, y_train, start_layer_shard1, end_layer_shard1)
print("Shard 1 Info:", shard1_info)


shard2_info = ModelShard(model_id, num_layers, y_train, start_layer_shard2, end_layer_shard2)
print("Shard 2 Info:", shard2_info)

full_model.save('trained_full_model')
print("Fully trained model saved as 'trained_full_model'")
