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


def aggregate_results(channel, method, properties, body: bytes):
    with Timer("deserialising message body from json"):
        message = ResultAggregationMessage.model_validate_json(str(body))

    # 2) TODO: Aggregate results
    with Timer("aggregating result from each subtask into a single result"):
        # 1) Decode model shards from base64 into byte array
        # 2) Load model shards into memory
        # 3) Merge shards using tensorflow
        # 4) Export merged model to .keras
        pass

    with Timer("pushing aggregated result to remote file server"):
        result = ResultMessage(file_url_model="remote_location")

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
