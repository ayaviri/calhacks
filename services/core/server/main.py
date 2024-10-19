from fastapi import FastAPI, File, UploadFile
# from server.schemas import PostResultRequestBody

# from database.schemas import TaskTable
# from utils.timer import Timer
# from server.database import Session

app = FastAPI()


@app.get("/health")
def health():
    return {"calhacks": "hooray !"}


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
    print(await model.read())
    print(await dataset.read())
    # with Timer("creating task in database"):
    #     with Session.begin() as session:
    #         task_id: str = TaskTable.writeTask(session)

    # with Timer("sending files to task subdivision queue"):
    #     pass

    # return {"task_id": task_id}


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
