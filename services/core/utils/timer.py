import time


class Timer:
    def __init__(self, message):
        self.message = message

    def __enter__(self):
        self.startTime = time.time()
        print(f"Started {self.message}")

    def __exit__(self, exc_type, exc_value, traceback):
        self.endTime = time.time()
        print(f"Finished {self.message} in {self.endTime - self.startTime} seconds")
