import time
import datetime
import signal

from kiwoom_api import KiwoomHandler
from danta_trader import DantaTrader
import signal_handler
import else_func

"""
설명 작성중...
"""

if __name__ == "__main__":

    # 각자의 상황에 따라 맞는 알고리즘을 불러오고, 해당 알고리즘은 sigwait을 이용해 컨트롤한다.

    while True:
        cur_timechunk = signal_handler.set_alarm()            # 여기서 알람을 설정
        
        if cur_timechunk == 0:      # 현재 시간이 점검전, 장마감 이후일 때
            print(str(datetime.datetime.now()) + "   현재 점검전, 장마감 이후입니다.")
            # 여기서 점검전, 장마감 이후에 할 일을 적어놓음
            # 만약에, 할 일이 계속되는것이라 의도적으로 끊어줘야 할 때, 단타 알고리즘 방법을 사용
            
            signal.sigwait([signal.SIGALRM])    # 이후, 점검 때 울리는 시그널을 기다림
            # 시그널이 울리면, 현재시간은 03:55쯤임.
            # 여기서 Windows handler에게 프로그램을 80분동안 종료하게끔 요청
            print(str(datetime.datetime.now()) + "  점검시간 대비, 80분을 쉽니다.")
            trader = KiwoomHandler()
            trader.program_restart(4800)
            del trader
            
        elif cur_timechunk == 1:    # 현재 시간이 점검 직후, 단타 이전 시간일 때
            print(str(datetime.datetime.now()) + "   현재 점검 이후, 단타알고리즘 전입니다.")
            # 여기서 점검 이후, 단타 시작 전 할 일을 적어놓음
            # 만약에, 할 일이 계속되는것이라 의도적으로 끊어줘야 할 때, 단타 알고리즘 방법을 사용

            signal.sigwait([signal.SIGALRM])  # 이후, 단타 때 울리는 시그널을 기다림

        elif cur_timechunk == 2:    # 현재 시간이 단타 시간일 때
            print(str(datetime.datetime.now()) + "   현재 단타 시간입니다.")
            danta = DantaTrader()
            danta.buy()
            del danta
            # 단타 알고리즘은 계속 돌아가고 있고, 그 중간에 sigalarm이 호출될 뿐이다.
            # sigwait이 사용되지 않음. 따라서 signal_handler.set_alarm에서의 sig_b가 호출된다.
    
        elif cur_timechunk == 3:    # 현재 시간이 AI 시간일 때
            print(str(datetime.datetime.now()) + "   현재 AI 시간입니다.")
            # AI 시간에 할 일을 적어놓음
            # 할 일이 계속되는 것이라 의도적으로 끊어줘야할 때, 단타 알고리즘 방법을 사용
            
            signal.sigwait([signal.SIGALRM])    # 장마감 때 울리는 시그널
        del cur_timechunk
