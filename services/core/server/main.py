import redis.asyncio as aioredis
from fastapi import FastAPI, File, UploadFile, Form
from fastapi.middleware.cors import CORSMiddleware
from server.schemas import (
    PostResultRequestBody,
    TaskSplitMessage,
    SubtaskResult,
    ResultAggregationMessage,
)

from database.schemas import TaskTable
from utils.timer import Timer
from web_server.database import create_db_session_factory
from web_server.utils import abort_on_failure
from web_server.mq import connect_to_rabbitmq_server

app = FastAPI()
origins = ["*"]
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["GET", "POST", "DELETE"],
    allow_headers=["*"],
)


@app.get("/health")
def health():
    return {"calhacks": "hooray !"}


@app.on_event("startup")
def startup():
    global rabbitmq_channel
    global Session
    global redis
    rabbitmq_channel = connect_to_rabbitmq_server()
    rabbitmq_channel.queue_declare(queue="task_split")
    Session = create_db_session_factory()
    redis = aioredis.Redis()


@app.on_event("shutdown")
def shutdown():
    global rabbitmq_channel
    rabbitmq_channel.close()


#  _____ ___  ____     ____ _     ___ _____ _   _ _____
# |  ___/ _ \|  _ \   / ___| |   |_ _| ____| \ | |_   _|
# | |_ | | | | |_) | | |   | |    | ||  _| |  \| | | |
# |  _|| |_| |  _ <  | |___| |___ | || |___| |\  | | |
# |_|   \___/|_| \_\  \____|_____|___|_____|_| \_| |_|
#


@app.post("/task")
async def submit_task(
    model: UploadFile = File(required=True),
    dataset_name: str = Form(required=True)
):
    async def handler():
        with Timer("reading file contents into memory"):
            model_file_contents = await model.read()

        with Timer("creating task in database"):
            with Session.begin() as session:
                task_id: str = TaskTable.write_task(session)

        with Timer("sending files to task split queue"):
            message = TaskSplitMessage(
                model_file_contents=model_file_contents,
                dataset_name=dataset_name,
                task_id=task_id,
            )
            rabbitmq_channel.basic_publish(
                exchange="", routing_key="task_split", body=message.model_dump_json()
            )

        return {"task_id": task_id}

    return await abort_on_failure(handler)


@app.get("/task/{task_id}")
async def get_task_state(task_id: str):
    def respond_with_result(channel, method, properties, body: bytes):
        # NOTE: This assumes that the body is already a JSON formatted string
        return JSONResponse(content=str(bytes))

    rabbitmq_channel.basic_consume(
        queue="result", on_message_callback=respond_with_result
    )
    rabbitmq_channel.start_consuming()


#  _____ ___  ____   __        _____  ____  _  _______ ____
# |  ___/ _ \|  _ \  \ \      / / _ \|  _ \| |/ / ____|  _ \
# | |_ | | | | |_) |  \ \ /\ / / | | | |_) | ' /|  _| | |_) |
# |  _|| |_| |  _ <    \ V  V /| |_| |  _ <| . \| |___|  _ <
# |_|   \___/|_| \_\    \_/\_/  \___/|_| \_\_|\_\_____|_| \_\
#


@app.post("/result")
async def post_subtask_result(r: PostResultRequestBody):
    async def handler():
        completed_subtasks_key = f"completed_subtasks_{r.task_id}"

        with Timer("serialising request body into json"):
            serialised_subtask: str = r.model_dump_json()

        with Timer("writing json serialised subtask result into redis set"):
            await redis.sadd(completed_subtasks_key, serialised_subtask)

        with Timer("reading all of the subtasks results in the redis set"):
            serialised_subtasks: list[str] = [
                str(subtask) for subtask in await redis.smembers(completed_subtasks_key)
            ]

        if len(serialised_subtasks) == r.subtask_count:
            with Timer("deserialising subtasks pulled from redis"):
                subtasks = [
                    PostResultRequestBody.model_validate_json(ss)
                    for ss in serialised_subtasks
                ]

            with Timer("constructing message to for result aggregation"):
                message = ResultAggregationMessage(
                    subtask_results=[
                        SubtaskResult(
                            output_tensor=s.output_tensor, task_num=s.task_num
                        )
                        for s in subtasks
                    ]
                )

            with Timer("publishing message to aggregate subtask results asychronously"):
                rabbitmq_channel.basic_publish(
                    exchange="",
                    routing_key="result_aggregation",
                    body=message.model_dump_json(),
                )
            return "results now aggregating"

        return "subtask results not fully available yet"

    return await abort_on_failure(handler)
