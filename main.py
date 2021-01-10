import time
import datetime
import signal

from kiwoom_api import KiwoomHandler
from danta_trader import DantaTrader
import signal_handler
import else_func

"""
주식 자동거래 알고리즘
4 타임에 맞춰 돌아가게 설계되어 있다.

1. 9시 15분 ~ 13시 (기본 설정값) : 단타 트레이더가 단타로 거래
    a. 현재 시간으로부터 15분 전부터 현재 시각까지 거래량의 증가량이 높은 상위 주식을 설정된 시장 (코스닥, 코스피, 둘 다)에서 받아온다.
    b. 보유 주식의 종류가 n(기본값 6) 개가 되도록 상위 주식들부터 k(기본값 50만원)원만큼 시장가로 매수한다 (이미 보유중이거나, 두 번의 손실을 입은 주식은 제외)
    c. 3.6초마다 보유 주식의 손익률을 판단하면서, x(기본값 -1)% 미만 혹은 y(기본값 3)% 초과의 손익률을 보이면, 해당 주식을 시장가로 매도한다.
    d. a~c의 과정을 13시까지 반복한다.
2. 13시 ~ 15시 19분 : AI 트레이더가 AI 트레이딩 시작
    a. 현재 알고리즘 구축 중
3.  
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
            danta.trade()
            del danta
            # 단타 알고리즘은 계속 돌아가고 있고, 그 중간에 sigalarm이 호출될 뿐이다.
            # sigwait이 사용되지 않음. 따라서 signal_handler.set_alarm에서의 sig_b가 호출된다.
    
        elif cur_timechunk == 3:    # 현재 시간이 AI 시간일 때
            print(str(datetime.datetime.now()) + "   현재 AI 시간입니다.")
            # AI 시간에 할 일을 적어놓음
            # 할 일이 계속되는 것이라 의도적으로 끊어줘야할 때, 단타 알고리즘 방법을 사용
            
            signal.sigwait([signal.SIGALRM])    # 장마감 때 울리는 시그널
        del cur_timechunk
