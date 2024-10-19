from fastapi import FastAPI, File, UploadFile
from fastapi.middleware.cors import CORSMiddleware
# from server.schemas import PostResultRequestBody

from database.schemas import TaskTable
from utils.timer import Timer
from server.database import create_db_session_factory
from server.utils import abort_on_failure
from server.mq import connect_to_rabbitmq_server

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
    rabbitmq_channel = connect_to_rabbitmq_server()
    rabbitmq_channel.queue_declare(queue="task_split")
    Session = create_db_session_factory()


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
    dataset: UploadFile = File(required=True),
):
    async def handler():
        with Timer("creating task in database"):
            with Session.begin() as session:
                task_id: str = TaskTable.write_task(session)

        with Timer("sending files to task split queue"):
            # TODO: Construct the task message
            rabbitmq_channel.basic_publish(
                exchange="", routing_key="task_split", body="hello world"
            )

        return {"task_id": task_id}

    return await abort_on_failure(handler)


# @app.get("/task/{task_id}")
# def get_task_state(task_id: str):
#     # 1) Subscribe to result aggregation message queue
#     # 2) Upon message receipt, respond with model file download URL
#     return {"calhacks": task_id}


#  _____ ___  ____   __        _____  ____  _  _______ ____
# |  ___/ _ \|  _ \  \ \      / / _ \|  _ \| |/ / ____|  _ \
# | |_ | | | | |_) |  \ \ /\ / / | | | |_) | ' /|  _| | |_) |
# |  _|| |_| |  _ <    \ V  V /| |_| |  _ <| . \| |___|  _ <
# |_|   \___/|_| \_\    \_/\_/  \___/|_| \_\_|\_\_____|_| \_\
#


# @app.post("/result")
# def post_subtask_result(r: PostResultRequestBody):
#     # 1) Write subtask result to database
#     # 2) If all subtask results are available, aggregate them asynchronously, write aggregation to DB
#     # 3) (In core worker) Post message of result aggregation
#     return {"calhacks": "hooray !"}
