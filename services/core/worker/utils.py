import pika
import os
import time
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker


def connect_to_rabbitmq_server():
    connection = pika.BlockingConnection(pika.ConnectionParameters(host="localhost"))

    return connection.channel()


pg_user = os.environ.get("POSTGRES_USER")
pg_password = os.environ.get("POSTGRES_PASSWORD")
pg_host = os.environ.get("PGHOST")
pg_port = os.environ.get("PGPORT")
pg_db = os.environ.get("POSTGRES_DB")
db_url = f"postgresql://{pg_user}:{pg_password}@{pg_host}:{pg_port}/{pg_db}"


def create_db_session_factory():
    engine = create_engine(db_url)

    return sessionmaker(autocommit=False, autoflush=True, bind=engine)


class Timer:
    def __init__(self, message):
        self.message = message

    def __enter__(self):
        self.startTime = time.time()
        print(f"Started {self.message}")

    def __exit__(self, exc_type, exc_value, traceback):
        self.endTime = time.time()
        print(f"Finished {self.message} in {self.endTime - self.startTime} seconds")
