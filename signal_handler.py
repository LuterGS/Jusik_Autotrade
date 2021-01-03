import signal
import datetime
import time
from multiprocessing import shared_memory

import constant


def signal_update(cur_num):
    if cur_num == 3:
        return 0
    else:
        cur_num += 1
        return cur_num


def sig_a(signum, frame):
    # 단타 알고리즘이 시작될 때 발생하는 시그널 핸들러
    # 이 시그널에서 단타 알고리즘을 실행시킴과 동시에 sig_b가 실행될 수 있도록 timer를 setting해줘야 한다.

    # 단타 알고리즘이 끝나는 때에 alarm이 발생하도록 alarm을 설정한다.
    cur_time = datetime.datetime.now()
    expected_time = datetime.datetime.strptime(
        cur_time.strftime("%Y%m%d") + str(constant.DANTA_END_HOUR) + str(constant.DANTA_END_MIN),
        "%Y%m%d%H%M"
    )
    signal.alarm(int((expected_time - cur_time).total_seconds()))

    # signal handler를 교체한다.
    signal.signal(signal.SIGUSR2, sig_b)
    print("점검시간을 대비, 5시 15분까지 프로그램을 대기시킵니다.")
    time.sleep(4800)
    # 점검시간이 종료될 때까지 sleep한다.



def sig_b(signum, frame):
    # 단타가 종료되고 AI 알고리즘이 돌아가는 시점을 알려주는 핸들러
    # 이 시그널이 발생하면 단타 알고리즘이 종료되고, AI 알고리즘이 실행된다.

    # 이 다음에 울릴, 장마감 시간을 파악한다.
    cur_time = datetime.datetime.now()
    expected_time = datetime.datetime.strptime(
        cur_time.strftime("%Y%m%d") + "1519", "%Y%m%d%H%M"
    )
    signal.alarm(int((expected_time - cur_time).total_seconds()))

    # signal handler를 교체한다.
    signal.signal(signal.SIGUSR2, sig_c)

    # 이 Shared memory를 생성하면, 단타 알고리즘에서 감지 후 단타 알고리즘이 멈추게 된다.
    checker = shared_memory.SharedMemory(name=constant.SIGNAL_B, create=True, size=10)


def sig_c(signum, frame):
    # 장 종료를 알리는 핸들러
    # 이 시그널이 발생하면, AI 알고리즘을 종료하고 다른 로직을 실행한다.

    # 이 다음에 울릴, 점검시간 (03:55~5:15) 을 파악한다.
    cur_time = datetime.datetime.now() + datetime.timedelta(days=1)
    expected_time = datetime.datetime.strptime(
        cur_time.strftime("%Y%m%d") + "0355", "%Y%m%d%H%M"
    )
    signal.alarm(int((expected_time - cur_time).total_seconds()))

    # signal handler를 교체한다.
    signal.signal(signal.SIGUSR2, sig_d)


def sig_d(signum, frame):
    # 점검시간을 알리는 핸들러
    # 이 시그널이 발생하면, 점검시간동안 대기한 아후 다음 장 시작에 sig_a가 호출되도록 바꾼다.

    # 이 다음에 울릴, 장 시작 시간을 파악한다.
    cur_time = datetime.datetime.now()
    expected_time = datetime.datetime.strptime(
        cur_time.strftime("%Y%m%d") + "09" + constant.TRADE_LAST_MIN, "%Y%m%d%H%M"
    )
    signal.alarm(int((expected_time - cur_time).total_seconds()))

    # signal handler를 교체한다.
    signal.signal(signal.SIGUSR2, sig_a)





