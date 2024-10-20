# import pika
import time
import requests
import base64
import tempfile
import tensorflow as tf
from typing import Any
from pydantic import BaseModel, NonNegativeInt, PositiveInt


class Timer:
    def __init__(self, message):
        self.message = message

    def __enter__(self):
        self.startTime = time.time()
        print(f"Started {self.message}")

    def __exit__(self, exc_type, exc_value, traceback):
        self.endTime = time.time()
        print(f"Finished {self.message} in {self.endTime - self.startTime} seconds")


# TODO: The information necessary for a worker to independently complete a
# portion of the original task
class SubtaskMessage(BaseModel):
    encoded_model_file_contents: str
    dataset_name: str
    task_id: str
    # Represents the order in which this subtask belongs in the collection of
    # subtasks
    task_num: NonNegativeInt
    # Represents the number of subtasks the original task was divided into
    subtask_count: PositiveInt


class PostResultRequestBody(BaseModel):
    # A base64 encoded string of the binary data contained in a .keras file,
    # representing a finetuned tensorflow model shard
    encoded_model_shard_file_contents: str
    # Represents the order of this subtask result in the
    # collection of subtask results
    task_num: NonNegativeInt
    # Represents the ID of the task from which this subtask was derived
    task_id: str
    # Represents the number of subtasks the original task was divided into
    subtask_count: NonNegativeInt


def _get_first_model_half(base_model, split_layer_name: str):
    split_layer = base_model.get_layer(split_layer_name).output

    return tf.keras.Model(inputs=base_model.input, outputs=split_layer)


def _get_second_model_half(base_model, split_layer_name: str):
    split_layer = base_model.get_layer(split_layer_name).output
    input_part2 = tf.keras.Input(shape=split_layer.shape[1:])
    x = input_part2

    split_layer_index = base_model.layers.index(base_model.get_layer(split_layer_name))
    for layer in base_model.layers[split_layer_index + 1 :]:
        x = layer(x)

    x = tf.keras.layers.Flatten()(x)
    x = tf.keras.layers.Dense(10, activation="softmax")(x)

    model_part2 = tf.keras.Model(inputs=input_part2, outputs=x)

    return model_part2


def finetune(message: dict[str, Any]):
    with Timer("deserialising message body from json"):
        deserialised_message = SubtaskMessage.parse_obj(message)

    with Timer("decoding model file contents from base64 encoding"):
        pass

    with Timer("loading model into memory"):
        base_model = tf.keras.applications.VGG16(
            input_shape=(224, 224, 3), include_top=False, weights="imagenet"
        )
        split_layer_name = "block3_pool"
        model_shard = (
            _get_first_model_half(base_model, split_layer_name)
            if deserialised_message.task_num == 0
            else _get_second_model_half(base_model, split_layer_name)
        )

    # TODO: The dataset is currrently hardcoded, make this parameterised
    with Timer("loading dataset into memory"):
        fashion_mnist = tf.keras.datasets.fashion_mnist
        (x_train, y_train), (x_test, y_test) = fashion_mnist.load_data()

    with Timer("finetuning model"):
        epochs = 1
        model_shard.compile(
            optimizer=tf.keras.optimizers.Adam(learning_rate=0.001),
            loss="sparse_categorical_crossentropy",
        )
        model_shard.fit(x_train, y_train, x_test, y_test, epochs=epochs)

    temp_file = tempfile.NamedTemporaryFile()

    with Timer("exporting model to .keras format"):
        model_shard.save(temp_file.name)

    with Timer("encoding binary data from model shard file to base64 string"):
        # TODO: We might have to seek to the beginning of the temp file before reading
        # its contents
        model_shard_file_contents: bytes = temp_file.read()
        encoded_model_shard_file_contents: str = base64.b64encode(
            model_shard_file_contents
        ).decode("utf-8")
        temp_file.close()

    with Timer("sending results of subtask back to core server"):
        body = PostResultRequestBody(
            encoded_model_shard_file_contents=encoded_model_shard_file_contents,
            task_id=deserialised_message.task_id,
            task_num=deserialised_message.task_num,
            subtask_count=deserialised_message.subtask_count,
        )
        requests.post("http://localhost:8000/result", json=body.model_dump())


def start_polling(url):
    while True:
        response = requests.get(url)

        if response.status_code == 200:
            subtask_message: dict[str, Any] = response.json()
            finetune(subtask_message)
            break
        else:
            time.sleep(1)


def main():
    start_polling("http://localhost:8000/subtask")


main()
