from pydantic import BaseModel, NonNegativeInt


#  ____  _____ ___  _   _ _____ ____ _____
# |  _ \| ____/ _ \| | | | ____/ ___|_   _|
# | |_) |  _|| | | | | | |  _| \___ \ | |
# |  _ <| |__| |_| | |_| | |___ ___) || |
# |_| \_\_____\__\_\\___/|_____|____/ |_|
#
#  ____   ____ _   _ _____ __  __    _    ____
# / ___| / ___| | | | ____|  \/  |  / \  / ___|
# \___ \| |   | |_| |  _| | |\/| | / _ \ \___ \
#  ___) | |___|  _  | |___| |  | |/ ___ \ ___) |
# |____/ \____|_| |_|_____|_|  |_/_/   \_\____/
#


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


#  __  __ _____ ____ ____    _    ____ _____
# |  \/  | ____/ ___/ ___|  / \  / ___| ____|
# | |\/| |  _| \___ \___ \ / _ \| |  _|  _|
# | |  | | |___ ___) |__) / ___ \ |_| | |___
# |_|  |_|_____|____/____/_/   \_\____|_____|
#
#  ____   ____ _   _ _____ __  __    _    ____
# / ___| / ___| | | | ____|  \/  |  / \  / ___|
# \___ \| |   | |_| |  _| | |\/| | / _ \ \___ \
#  ___) | |___|  _  | |___| |  | |/ ___ \ ___) |
# |____/ \____|_| |_|_____|_|  |_/_/   \_\____/
#


class TaskSplitMessage(BaseModel):
    model_file_contents: str
    dataset_file_contents: str
    task_id: str


class SubtaskResult(BaseModel):
    encoded_model_shard_file_contents: str
    task_num: NonNegativeInt


class ResultAggregationMessage(BaseModel):
    subtask_results: list[SubtaskResult]
