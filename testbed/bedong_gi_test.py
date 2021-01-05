import signal
import datetime
import time
from kiwoom_api import KiwoomHandler

# 시그널 핸들러 테스트



def main_signal_handling():

    print("setting signal alarm")
    signal.alarm(5)
    print(signal.getsignal(signal.SIGALRM))
    signal.signal(signal.SIGALRM, alarmer)
    print(signal.getsignal(signal.SIGALRM))
    print("signal alarm setted")


def alarmer(signum, a):
    print(signum, a)
    print('a')
    # trader = KiwoomHandler()
    # trader.program_restart(10)
    # del trader


if __name__ == "__main__":


    # 시그널 핸들러 설정
    main_signal_handling()
    signal.sigwait([signal.SIGALRM])
    alarmer(1, 2)
    print("!!")
