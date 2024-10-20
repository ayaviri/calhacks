from pydantic import BaseModel, NonNegativeInt
from worker.utils import connect_to_rabbitmq_server, Timer


# Represents the aggregated work of each subtask
class Result(BaseModel):
    # The remote URL from which to download the finetuned model
    model_file_url: str


class SubtaskResult(BaseModel):
    encoded_model_shard_file_contents: str
    task_num: NonNegativeInt


# The message schema received by this worker, represents the collection of results
# from each worker's subtask (of model finetuning)
class ResultAggregationMessage(BaseModel):
    subtask_results: list[SubtaskResult]


def aggregate_results(channel, method, properties, body: bytes):
    with Timer("deserialising message body from json"):
        message = ResultAggregationMessage.model_validate_json(str(body))

    # 2) TODO: Aggregate results
    with Timer("aggregating result from each subtask into a single result"):
        # 1) C
        pass

    with Timer("pushing aggregated result to remote file server"):
        result = Result(url="remote_location")

    channel.basic_publish(
        exchange="", routing_key="result", body=result.model_dump_json()
    )


def main():
    rabbitmq_channel = connect_to_rabbitmq_server()
    rabbitmq_channel.basic_consume(
        queue="result_aggregation", on_message_callback=aggregate_results
    )
    rabbitmq_channel.start_consuming()


main()
