import pika
# TODO: I can't seem to import this, so I'll have to redefine it here
# from server.mq import connect_to_rabbitmq_server


def connect_to_rabbitmq_server():
    connection = pika.BlockingConnection(pika.ConnectionParameters(host="localhost"))

    return connection.channel()


# Called when a message is received, _body_ parameters is a JSON string that
# contains the message body
def split_task(channel, method, properties, body):
    # 1) Deserialise message, perform work upon message receipt
    # 2) Serialise result, hit POST /result endpoint in core
    print(f"received: {body}")


def main():
    rabbitmq_channel = connect_to_rabbitmq_server()
    rabbitmq_channel.basic_consume(queue="task_split", on_message_callback=split_task)
    rabbitmq_channel.start_consuming()


main()
