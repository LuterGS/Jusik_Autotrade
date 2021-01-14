import time
import signal
import os
import warnings
from multiprocessing import Process, shared_memory
import pika
from pika.exceptions import AMQPConnectionError

import constant
import else_func

warnings.filterwarnings('ignore')


def timechecker_wait(func):
    def wrapper(*args):
        cur_time = time.time()
        timediff = cur_time - args[0]._saved_time
        print(cur_time, args[0]._saved_time, timediff)
        if timediff < 3.6:
            time.sleep(3.6 - timediff)
        args[0]._saved_time = time.time()
        return func(*args)
    return wrapper


def timechecker_instant(func):
    def wrapper(*args):
        cur_time = time.time()
        timediff = args[0]._saved_time - cur_time
        if timediff < 0.2:
            time.sleep(0.2 - timediff)
        args[0]._saved_time = time.time()
        return func(*args)

    return wrapper


class KiwoomHandler:
    REQUESTS = ["잔액요청", "거래량급증요청", "주식구매", "주식판매", "수익률요청", "프로그램재시작", "주식분봉차트조회요청"]

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
        self._connection = pika.BlockingConnection(
            pika.ConnectionParameters(self._url, self._port, self._vhost, self._cred))

        # 먼저 윈도우 출력을 받는 큐를 생성 후 작동
        self._channel = self._connection.channel()# self._connection.channel()
        self._channel.basic_consume(queue=self._recv_queue, on_message_callback=KiwoomHandler._que_getter,
                                    auto_ack=True)
        self._windows_get = Process(target=self._channel.start_consuming, args=())
        self._windows_get.start()

        # 요청 사이의 간격 조정
        self._saved_time = time.time()

    def _connect_channel(self):
        while True:
            try:
                connection = pika.BlockingConnection(pika.ConnectionParameters(self._url, self._port, self._vhost, self._cred))
                break
            except AMQPConnectionError:
                print("커넥션 에러, retrying")
        return connection, connection.channel()

    def _kiwoom(self, req_num: int, buffer_size=5000, **kwargs):
        # 요청한 timestamp 만큼 잠듬

        # 요청을 받을 때까지 반복문
        while True:
            # 프로세스 생성 및 시작
            connection, channel = self._connect_channel()
            sub_process = Process(target=KiwoomHandler._request_kiwoom,
                                  args=(channel, self._send_queue, self.REQUESTS[req_num], kwargs))
            sub_process.start()

            # 프로세스 이름을 이용한 고유 이름을 가진 Shared memory를 불러옴
            process_pid = sub_process.pid
            result_mem = shared_memory.SharedMemory(name="kiwoom_" + str(process_pid), create=True, size=buffer_size)
            # print("Process : ", process_pid, " is created")

            # 프로세스에게 Shared memory의 접근을 해제하고 프로그램을 종료하라는 시그널을 보냄
            sub_process.join()      # 서브프로세스 종료 확인
            result_value = else_func.byte_to_original(bytes(result_mem.buf), req_num)   # 공유메모리에서 값 읽어들여옴
            result_mem.close()
            result_mem.unlink()             # 이후 공유메모리 해제
            
            connection.close()              # 커넥션 닫음

            # print("res:", result_value)

            # 정상적으로 result_value가 False가 아닐 때는 값을 Return한다.
            if result_value:
                # print("Will return")
                return result_value
            # 아닐 때는 재시도 print를 찍는다.
            print("요청이 정상적으로 시도되지 않았습니다. 재요청합니다.")

    @staticmethod
    def _request_kiwoom(channel, send_queue_name, request_name: str, kwargs):
        # 프로세스로 분기시켜서 실행할 생각이며, 분기된 이후 고유의 pid를 가짐을 이용
        def sig(a, b):
            print("signal is called")

        # 시그널 핸들러를 등록하고, 현재 자신의 pid를 불러옴
        signal.signal(signal.SIGUSR1, sig)
        signal.signal(signal.SIGUSR2, sig)
        cur_pid = os.getpid()

        # 요청을 보낼 값을 다듬음
        send_data = str(cur_pid).encode() + b'|' + request_name.encode() + b','
        kwargs = list(kwargs.values())
        for i in range(len(kwargs)):
            send_data += kwargs[i].encode() + b','

        # print("send_data : ", send_data.decode(), "      request pid : ", cur_pid)

        # Windows에 요청을 보냄 - 응답을 받을 때까지
        channel.basic_publish(exchange='', routing_key=send_queue_name, body=send_data)


        # _que_setter가 공유 메모리에 값을 다 쓸 때까지 대기함 (오류를 막기 위해, max 한시간까지 대기함)
        signal.sigtimedwait([signal.SIGUSR1], 20)       # 넉넉하게 20초를 대기함

        # print("send_result : ", result)
        # channel.close()                                 # 대기후 채널 닫음

    @staticmethod
    def _que_getter(channel_info, deliver_info, properties, value: bytes):
        # 큐 핸들러, 큐에 입력값이 들어오면 어떻게 처리할 것인지를 구성

        # 초기에 값을 분리해준다.
        value = value.split(b'|')
        # print(value)

        try:
            # 분리된 값에 토대로 main process에서 생성한 shared_memory에 접근해, queue의 값을 기록한다.
            saver = shared_memory.SharedMemory(name='kiwoom_' + value[0].decode(), create=False)
            saver.buf[:len(value[1])] = value[1]
            saver.close()
            # print("set saver memory complete")

            # 기록이 완료되면, 해당 main의 subprocess에게 SIGUSR1 시그널을 보낸다.
            os.kill(int(value[0]), signal.SIGUSR1)
            # print("send kill complete")

        except ProcessLookupError:
            print("ProcessLookupError 발생!")
        except FileNotFoundError:
            print("해당 요청은 이미 처리되었습니다.")

    # 이 부분에 있는 메소드들은 클래스 외부에서도 접근이 가능한 Public 메소드들임
    # 이 부분에 있는 메소드만을 호출함으로써 외부에서 안정적인 호출이 가능하다.

    @timechecker_wait
    def get_balance(self):
        return self._kiwoom(0, buffer_size=50)

    @timechecker_wait
    def get_highest_trade_amount(self, last_min=constant.TRADE_LAST_MIN, market=constant.TRADE_MARKET,
                                 is_percent=constant.VIEW_AS_PERCENT, is_min=True):
        if is_min:
            min, last_min = "1", last_min
        else:
            min, last_min = "2", ""
        return self._kiwoom(1, buffer_size=5000, last_min=str(last_min), market=str(market), is_percent=str(is_percent), min=min)

    @timechecker_instant
    def buy_jusik(self, code, amount, price):
        return self._kiwoom(2, buffer_size=10, code=str(code), amount=str(amount), price=str(price))

    @timechecker_instant
    def sell_jusik(self, code, amount, price):
        return self._kiwoom(3, buffer_size=10, code=str(code), amount=str(amount), price=str(price))

    @timechecker_wait
    def get_profit_percent(self):
        return_value = self._kiwoom(4, buffer_size=1000)
        del return_value[0]
        return return_value

    def program_restart(self, time_: int):
        self._kiwoom(5, buffer_size=50, sleep_time=0, time=str(time_))
        time.sleep(time_ + 300)

    def program_nosleep_restart(self, time_: int):
        """
        보통의 program_restart는 같이 쉬지만, 이 메소드는 쉬지 않는다.
        적어도, time_ + 60 초가 흐른 뒤에 다시 Windows에 접근할 것을 추천한다 (부팅시간 필요)
        """
        self._kiwoom(5, buffer_size=50, sleep_time=0, time=str(time_))

    def get_past_min_data(self, code, custom_filename=None):
        """
        6개월치 종목코드에 따른 분봉 과거데이터를 파일에 기록한다.
        156100
        """
        @timechecker_wait
        def req_wrapper(savefile, cont="0"):
            return else_func.write_pdata_to_file(self._kiwoom(6, buffer_size=300000, code=str(code), is_continue=cont), savefile)

        if custom_filename is not None:
            filename = custom_filename
        else:
            filename = code + ".txt"
        with open(filename, "w", encoding='utf8') as savefile:
            savefile.write("체결시간,\t현재가,\t거래량,\t시가,\t고가,\t저가,\t수정주가구분,\t수정비율,\t대업종구분,\t소업종구분,\t종목정보,\t수정주가이벤트,\t전일종가\n")
            savefile = req_wrapper(savefile, "0")
            for i in range(55):
                savefile = req_wrapper(savefile, "2")
            return True


    def _sell_jusik(self, sell_detail):
        # print(sell_detail)
        # KiwoomHandler.sell_jusik의 Wrapper. 로그 남기기 및 화면 출력까지 포함한다.
        self.sell_jusik(sell_detail[0], sell_detail[2], sell_detail[7])


if __name__ == "__main__":
    test = KiwoomHandler()
    # test.program_restart(10)
    for i in range(10):
        print(test.get_balance())
        print(test.get_profit_percent())
    # print(val)




    exit(1)
    # # 20200107 TEST 모의투자계좌잔고 : 876만 8069원
    # # print(test.sell_jusik("057030", "42", "8250"))
    # print(test.buy_jusik("057030", "1", "9000"))
    # print(test.get_profit_percent())
    # exit(1)
    #
    # for i in range(10):
    #     print(test.buy_jusik("057030", "1", "9000"))
    #     print(test.get_profit_percent())
    #     print(test.get_highest_trade_amount())
    #     print(test.sell_jusik("057030", "1", "8200"))
    # exit(1)

    val = test.get_highest_trade_amount(is_min=False)
    print(val)
    print(len(val))
    k = 0
    for i in range(len(val)):
        if val[i][0] == "352770":
            k = i
            break

    for j in range(20, len(val)):
        test.get_past_min_data(code=val[j][0], custom_filename=val[j][0] + "_" + val[j][1] + ".txt")
        print(val[j][0] + "_" + val[j][1] + " completed")
    # highest = test.get_highest_trade_amount()
    # print(highest)
    # test.buy_jusik(highest[0][0], 2, highest[0][2])
    # print(test.get_highest_trade_amount())
    # print(test.get_profit_percent())
    # balance = test.get_balance()
    # amount = test.get_highest_trade_amount()
    # buy_result = test.buy_jusik(code=amount[0][0], amount=1, price=amount[0][2])
    # print("get_balance result is : ", test.get_balance())
    # print("거래량급증요청!", amount)
    # print("주식 하나만 사보기!", buy_result)
    # total = test.get_profit_percent()
    # print("len : ", len(total))
    # print(total)
