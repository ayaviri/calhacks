import tensorflow as tf


strategy = tf.distribute.MultiWorkerMirroredStrategy()


batch_size = 64
num_classes = 10
input_dim = 784

(x_train, y_train), _ = tf.keras.datasets.mnist.load_data()
x_train = x_train.reshape(-1, input_dim).astype('float32') / 255.0

train_dataset = tf.data.Dataset.from_tensor_slices((x_train, y_train))
train_dataset = train_dataset.shuffle(10000).batch(batch_size)

with strategy.scope():
    
    model = tf.keras.models.Sequential([
        tf.keras.layers.Dense(64, activation='relu', input_shape=(input_dim,)),
        tf.keras.layers.Dense(num_classes, activation='softmax')
    ])

    model.compile(loss='sparse_categorical_crossentropy',
                  optimizer='adam',
                  metrics=['accuracy'])

model.fit(train_dataset, epochs=10)
