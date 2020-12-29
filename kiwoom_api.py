import datetime
import time
import signal
import os
from threading import Thread
from multiprocessing import Process, shared_memory, Queue
import pika

import constant
import else_func


def signal_handler(signum, frame):
    print(signum, frame)





class KiwoomHandler:
    
    REQUESTS = ["잔액요청", "거래량급증요청", "주식구매", "주식판매", "수익률요청"]
    # 주식구매를 위해선 주식코드, 개수, 가격을 요청해야 한다.
    # self._request_kiwoom에 요청하도록 한다.

    def __init__(self):
        # RabbitMQ를 쓰기 위해 기본 정보 불러옴
        get_mq_val = constant.GET_MQ_VALUE()
        # print(get_mq_val)
        self._url = get_mq_val['MQ_URL']
        self._port = get_mq_val['MQ_PORT']
        self._vhost = get_mq_val["MQ_VHOST"]
        self._cred = pika.PlainCredentials(get_mq_val['MQ_ID'], get_mq_val['MQ_PW'])
        self._send_queue = get_mq_val['MQ_OUT_QUEUE']
        self._recv_queue = get_mq_val['MQ_IN_QUEUE']
        self._connection = pika.BlockingConnection(pika.ConnectionParameters(self._url, self._port, self._vhost, self._cred))
        self._channel = self._connection.channel()

        # Shared memory를 위한 이름 설정
        self._name = 10000

        # 먼저 윈도우 출력을 받는 큐를 생성
        self._que_get = Process(target=self._que_getter, args=(self._connect_channel(), self._recv_queue))
        self._que_get.start()

        # test val
        self.testval = False

    def _connect_channel(self):
        connection = pika.BlockingConnection(pika.ConnectionParameters(self._url, self._port, self._vhost, self._cred))
        return connection.channel()

    def _kiwoom(self, req_num: int, **kwargs):

        # 프로세스 생성 및 시작
        channel = self._connect_channel()
        sub_process = Process(target=KiwoomHandler._request_kiwoom, args=(channel, self._send_queue, self.REQUESTS[req_num], kwargs))
        sub_process.start()

        # 프로세스 이름을 이용한 고유 이름을 가진 Shared memory를 불러옴
        process_pid = sub_process.pid
        result_mem = shared_memory.SharedMemory(name="kiwoom_" + str(process_pid), create=True, size=5000)
        # print("Process : ", process_pid, " is created")
        
        # 프로세스에게 Shared memory의 접근을 해제하고 프로그램을 종료하라는 시그널을 보냄
        # os.kill(process_pid, signal.SIGUSR2)
        sub_process.join()
        
        # 이후 Shared memory에서 값을 읽어들여온 후 종료함
        result_value = else_func.byte_to_original(bytes(result_mem.buf), req_num)
        result_mem.close()
        result_mem.unlink()
        return result_value

    @staticmethod
    def _request_kiwoom(channel, send_queue_name, request_name: str, kwargs):
        # 프로세스로 분기시켜서 실행할 생각이며, 분기된 이후 고유의 pid를 가짐을 이용
        def sig(a, b):
            # print("signal handling is called    ", a, b)
            pass
        # 시그널 핸들러를 등록하고, 현재 자신의 pid를 불러옴
        signal.signal(signal.SIGUSR1, sig)
        signal.signal(signal.SIGUSR2, sig)
        cur_pid = os.getpid()
        # print("cur_pid : ", cur_pid)

        # 요청을 보낼 값을 다듬음
        send_data = str(cur_pid).encode() + b'|' + request_name.encode() + b','
        kwargs = list(kwargs.values())
        for i in range(len(kwargs)):
            send_data += kwargs[i].encode() + b','

        print("send_data : ", send_data)

        # Windows에 요청을 보냄
        channel.basic_publish(exchange='', routing_key=send_queue_name, body=send_data)
        # print("send_result : ", result)
        channel.close()

        # _que_setter가 공유 메모리에 값을 다 쓸 때까지 대기함 (오류를 막기 위해, max 한시간까지 대기함)
        signal.sigtimedwait([signal.SIGUSR1], 3600)

    @staticmethod
    def _que_getter(channel, recv_queue_name):
        # 프로세스로 돌아가는 함수
        # 일정 주기마다 계속 RabbitMQ에서 pop을 요청하고, 값이 들어오면 해당 값을 분석한 뒤
        # 결과값을 Shared memory에 작성한 뒤, 요청한 프로세스에게 SIGUSR1을 보냄
        while True:
            # 일정 주기로 값을 계속 받아옴
            time.sleep(0.2)
            value = channel.basic_get(queue=recv_queue_name, auto_ack=True)[2]
            if value is not None:
                # 만약 큐에 값이 있어서 성공적으로 읽어들여왔다면
                try:
                    value = value.split(b'|')  # 프로세스번호와 데이터를 분리하기 위해 '|'를 사용한다.

                    # 해당 프로세스가 열은 Shared memory에 접근해 값을 쓴다.
                    saver = shared_memory.SharedMemory(name="kiwoom_" + value[0].decode(), create=False)
                    saver.buf[:len(value[1])] = value[1]
                    saver.close()

                    # 해당 프로세스에게 signal을 보낸다.
                    os.kill(int(value[0]), signal.SIGUSR1)
                except ProcessLookupError:
                    print(ProcessLookupError)
                except FileNotFoundError:
                    print("Already Missed Target")

    def get_balance(self):
        return self._kiwoom(0)

    def get_highest_trade_amount(self):
        return self._kiwoom(1)

    def buy_jusik(self, code, amount, price):
        return self._kiwoom(2, code=str(code), amount=str(amount), price=str(price))

    def sell_jusik(self, code, amount, price):
        return self._kiwoom(3, code=str(code), amount=str(amount), price=str(price))

    def get_profit_percent(self):
        return self._kiwoom(4)

if __name__ == "__main__":

    test = KiwoomHandler()
    balance = test.get_balance()
    amount = test.get_highest_trade_amount()
    buy_result = test.buy_jusik(code=amount[0][0], amount=1, price=amount[0][2])
    print("get_balance result is : ", test.get_balance())
    print("거래량급증요청!", amount)
    print("주식 하나만 사보기!", buy_result)


def buy_stock(ticker: str, amount: int):
    """
    :param ticker: 구매하고자 하는 종목코드 (str)
    :param amount: 구매하고자 하는 주식 개수 (int)
    :return: 두 개의 값을 return함.
        1. 총 구매한 금액 (int)
        2. 함수의 성공, 실패값 (bool)
    """
    return 1000, False


def sell_stock(ticker: str, amount: int, price: int):
    """
    :param ticker: 판매하고자 하는 종목코드 (str)
    :param amount: 판매하고자 하는 주식 개수 (int)
    :param price: 판매하고자 하는 주식의 가격 (int)
    :return: 성공, 실패값 (bool)
    """
    return True


def get_stock(ticker: str):
    """
    :param ticker: 보유개수를 알고자 하는 종목코드 (int)
    :return: ticker에 해당되는 주식의 보유개수 (int)
    """
    return 20


def get_stock_price(ticker: str, is_buying: bool):
    """
    :param ticker: 가격을 알고자 하는 종목코드 (int)
    :param is_buying: true일 땐 종목의 매수최고가를, false일 땐 종목의 매도최저가를 return함
    :return: is_buying에 따른 주식 종목의 가격
    """
    if is_buying:
        return 1000
    else:
        return 990
