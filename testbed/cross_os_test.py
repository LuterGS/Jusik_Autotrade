import array
import datetime
import pika

import constant
import else_func

class Publisher:
    def __init__(self):
        get_mq_val = constant.GET_MQ_VALUE()
        print(get_mq_val)
        self._url = get_mq_val['MQ_URL']
        self._port = get_mq_val['MQ_PORT']
        self._vhost = get_mq_val["MQ_VHOST"]
        self._cred = pika.PlainCredentials(get_mq_val['MQ_ID'], get_mq_val['MQ_PW'])
        self._send_queue = get_mq_val['MQ_OUT_QUEUE']
        self._recv_queue = get_mq_val['MQ_IN_QUEUE']
        return

    def main(self, data):
        send_data = else_func.array_to_byte(data)
        conn = pika.BlockingConnection(pika.ConnectionParameters(self._url, self._port, self._vhost, self._cred))
        chan = conn.channel()
        chan.basic_publish(exchange='', routing_key=self._send_queue, body=send_data)
        conn.close()
        return


if __name__ == "__main__":
    publisher = Publisher()
    start = datetime.datetime.now()
    for i in range(3):
        publisher.main(["잔액요청", "and this is also array ", str(i)])
    print("elapsed time is : ", datetime.datetime.now() - start)