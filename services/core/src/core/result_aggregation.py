import base64
import tempfile
import tensorflow as tf
from pydantic import BaseModel, NonNegativeInt
from core.mq import connect_to_rabbitmq_server
from core.utils import Timer
from core.schemas import (
    PostResultRequestBody,
    TaskSplitMessage,
    SubtaskResult,
    ResultAggregationMessage,
    ResultMessage,
    TaskTable,
)


def _get_model_shard(subtask_result):
    temp_file = tempfile.NamedTemporaryFile()
    temp_file.write(base64.b64decode(subtask_result.encoded_model_file_contents))

    return tf.keras.models.load_model(temp_file.name)


def _merge_models(first_subtask_result, second_subtask_result):
    first_model_shard = _get_model_shard(first_subtask_result)
    second_model_shard = _get_model_shard(second_subtask_result)
    full_input = first_model_shard.input
    intermediate_output = first_model_shard.output
    full_output = second_model_shard(intermediate_output)
    full_model = tf.keras.Model(inputs=full_input, outputs=full_output)

    return full_model


def aggregate_results(channel, method, properties, body: bytes):
    with Timer("deserialising message body from json"):
        message = ResultAggregationMessage.model_validate_json(body.decode("utf-8"))

    # TODO: Model merging is fixed to a subtask result pool of 2
    with Timer("aggregating result from each subtask into a single result"):
        merged_model = _merge_models(*message.subtask_results)

    with Timer("pushing aggregated result to remote file server"):
        # TODO: Push this to some sort of object storage ?
        merged_model.save("merged.keras")
        result = ResultMessage(file_url_model="got the model")

    channel.basic_publish(
        exchange="", routing_key="result", body=result.model_dump_json()
    )


def main():
    with Timer("connecting to rabbitmq server"):
        rabbitmq_channel = connect_to_rabbitmq_server()

    with Timer("subscribing to queue and awaiting messages"):
        rabbitmq_channel.basic_consume(
            queue="result_aggregation", on_message_callback=aggregate_results
        )
        rabbitmq_channel.start_consuming()


main()
