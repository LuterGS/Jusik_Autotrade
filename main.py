import time
import datetime
import signal

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
            # 일단 할거 없음
            # 그러면 그냥 알람 울릴때까지 대기
            signal.sigwait([signal.SIGALRM])
        elif cur_timechunk == 1:    # 현재 시간이 점검 이후, 단타 이전 시간일 때
            # 일단 할거 없음
            # 그러면 그냥 알람 울릴때까지 대기
            signal.sigwait([signal.SIGALRM])
        elif cur_timechunk == 2:    # 현재 시간이 단타 시간일 때
            danta = DantaTrader()
            danta.buy()
            del danta
        elif cur_timechunk == 3:    # 현재 시간이 AI 시간일 때
            # 일단 할거 없음
            # 그러면 그냥 알람 울릴때까지 대기
            signal.sigwait([signal.SIGALRM])
        del cur_timechunk
