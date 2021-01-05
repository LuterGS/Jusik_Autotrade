import signal
import datetime
import time
from multiprocessing import shared_memory

import constant
import else_func
from kiwoom_api import KiwoomHandler

_SIG_A_INIT_TIME = "09" + constant.TRADE_LAST_MIN
_SIG_B_INIT_TIME = constant.DANTA_END_HOUR + constant.DANTA_END_MIN
_SIG_C_INIT_TIME = "1519"
_SIG_D_INIT_TIME = "0355"
# 점검시간 80분
_END_MAINTENANCE = "0515"


def set_alarm():

    cur_time = else_func.get_hm()
    if int(cur_time) < int(_SIG_D_INIT_TIME):   # 현재 시간이 00:00~03:54일 때 - sig_d 핸들러를 호출하게끔 설정해야 한다.
        signal.alarm(else_func.get_timediff(cur_time, _SIG_D_INIT_TIME))
        signal.signal(signal.SIGALRM, sig_d)
        return 0
    elif int(cur_time) < int(_END_MAINTENANCE):   # 현재 시간이 점검 시간일 때
        # 먼저 켜져있는 Windows에 sleep명령 보냄
        windows = KiwoomHandler()
        timediff = else_func.get_timediff(cur_time, _END_MAINTENANCE)
        windows.program_restart(timediff)
        time.sleep(timediff)
        return 1
    elif int(cur_time) < int(_SIG_A_INIT_TIME): # 현재 시간이 03:55~09:xx(설정시) 일 때 - sig_a 핸들러를 호출하게끔 설정해아 한다.
        signal.alarm(else_func.get_timediff(cur_time, _SIG_A_INIT_TIME))
        signal.signal(signal.SIGALRM, sig_a)
        return 1
    elif int(cur_time) < int(_SIG_B_INIT_TIME): # 현재 시간이 09:xx~12:00 일 때 - sig_b 핸들러를 호출하게끔 설정해아 한다.
        signal.alarm(else_func.get_timediff(cur_time, _SIG_B_INIT_TIME))
        signal.signal(signal.SIGALRM, sig_b)
        return 2
    elif int(cur_time) < int(_SIG_C_INIT_TIME): # 현재 시간이 12:00~15:19 일 때 - sig_c 핸들러를 호출하게끔 설정해야 한다.
        signal.alarm(else_func.get_timediff(cur_time, _SIG_C_INIT_TIME))
        signal.signal(signal.SIGALRM, sig_c)
        return 3
    else:                                       # 현재 시간이 15:20~24:00 일 때 - sig_d 핸들러를 호출하게끔 설정해야 한다.
        signal.alarm(else_func.get_timediff(cur_time, _SIG_D_INIT_TIME, True))
        signal.signal(signal.SIGALRM, sig_d)
        return 0


def sig_a(signum, frame):
    # 단타 알고리즘이 시작될 때 발생하는 시그널 핸들러
    # 얘가 일단 뭔가 해야할 일은 없다.
    print("이제 단타 알고리즘을 시작합니다.")


def sig_b(signum, frame):
    # 단타가 종료되고 AI 알고리즘이 돌아가는 시점을 알려주는 핸들러
    # 이 시그널이 발생하면 단타 알고리즘이 종료되고, AI 알고리즘이 실행된다.

    # 단타 알고리즘은 DantaTrader.buy() 에서 계속 돌아가고 있음
    # 얘를 종료해주기 위해 shared memory를 생성한다.

    # 이 Shared memory를 생성하면, 단타 알고리즘에서 감지 후 단타 알고리즘이 멈추게 된다.
    print("Handler is called!")
    checker = shared_memory.SharedMemory(name=constant.SIGNAL_B, create=True, size=10)


def sig_c(signum, frame):
    # 장 종료를 알리는 핸들러
    # 이 시그널이 발생하면, AI 알고리즘을 종료하고 다른 로직을 실행한다.
    # 일단 할 게 없으므로 냅둔다.
    print("이제 장이 종료되었습니다")


def sig_d(signum, frame):
    # 점검시간을 알리는 핸들러
    # 이 시그널이 발생하면, 점검시간을 피해가도록 일정 시간 쉰다.
    # 현재는 03시 55분부터 05시 15분까지, 총 80분을 쉰다.
    print("점검시간을 대비, 80분을 쉽니다.")





