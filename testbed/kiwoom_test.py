import constant
import pika
from multiprocessing import Process

class Test:

    get_mq_val = constant.GET_MQ_VALUE()
    # print(get_mq_val)
    _url = get_mq_val['MQ_URL']
    _port = get_mq_val['MQ_PORT']
    _vhost = get_mq_val["MQ_VHOST"]
    _cred = pika.PlainCredentials(get_mq_val['MQ_ID'], get_mq_val['MQ_PW'])
    _send_queue = get_mq_val['MQ_OUT_QUEUE']
    _recv_queue = get_mq_val['MQ_IN_QUEUE']

    def __init__(self):
        self._connection = pika.BlockingConnection(
            pika.ConnectionParameters(self._url, self._port, self._vhost, self._cred))
        self._channel = self._connection.channel()
        self._channel.basic_consume(queue="test", on_message_callback=self.handler, auto_ack=True)

    @classmethod
    def handler(cls, a, b, c, d):
        print(cls._url)
        print(a)
        print(b)
        print(c)
        print(d)
        channel = a
        channel.basic_publish(exchange='', routing_key="to_windows", body=b'test')


    def consume(self):
        self._channel.start_consuming()

    def input_queue(self, i):
        self._channel.basic_publish(exchange='', routing_key="test", body=str(i).encode())


if __name__ == "__main__":


    getter = Test()
    print(getter._channel)
    pr = Process(target=getter._channel.start_consuming, args=())
    pr.start()


    sender = Test()
    for i in range(1):
        sender.input_queue(i)



