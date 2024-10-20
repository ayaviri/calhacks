import pika


def connect_to_rabbitmq_server():
    connection = pika.BlockingConnection(pika.ConnectionParameters(host="localhost"))

    return connection.channel()
