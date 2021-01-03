import time
import datetime
import signal

from danta_trader import DantaTrader
import signal_handler

"""
설명 작성중...
"""

if __name__ == "__main__":

    # 그림에 의하면, 총 4번의 signal이 요청되어야한다.
    # a가 요청되면 buy를, b가 요청되면 buy를 중단해야하며, c가 요청되면 장마감 확인을 하고, d가 요청되면 쉬어야한다.
    # 시그널 4개를 다는 것보다, 각 signal handler가 요청될 때마다 다음 함수를 준비해두는게 낫지 않을까?

    # 처음 sigwait을 걸어놓고 다음꺼가 실행되는 식으로만 하면 괜찮을거같은데....

    handlers = [signal_handler.sig_a, signal_handler.sig_b, signal_handler.sig_c, signal_handler.sig_d]
    start_signal = 0

    trader_a = DantaTrader()
    signal.signal(signal.SIGUSR2, handlers[start_signal])
    signal_handler.signal_update(start_signal)

    while True:
        signal.sigwait([signal.SIGUSR2])        # sig_a를 호출하는 알람
        # sig_a가 호출되었다. 이제부터 단타 알고리즘이 작동해야한다.
        trader_a.buy()      # 단타 알고리즘 작동.

        # 단타 알고리즘 내부에서 sig_b가 호출되었다.
        # 그럼, trader_a를 지운다. 내일 다시 만들 것이다.
        del trader_a
        # 이제 AI 트레이더가 작동해야한다. 일단 지금은 공백
        # TODO : AI 트레이더 만들기

        # 장마감을 확인해야 하므로, 일단 장마감에 울릴 수 있도록 sigwait을 설정한다.
        signal.sigwait([signal.SIGUSR2])        # sig_c를 호출하는 알람
        # 장마감 시간이 지났다. 해야 할 일을 한 뒤에, 점검까지 대기한다.

        # 점검 시간 알람을 등록한다.
        signal.sigwait([signal.SIGUSR2])        # sig_d를 호출하는 알람
        # 점검 시간이 지났다. 이후 각종 할 일을 하자
        # 그러면 처음으로 되돌아가서 다시 sig_a가 호출될 때까지 대기할 것이다.

        # 할 일
        trader_a = DantaTrader()    # 지웠던 단타트레이더를 다시 불러온다 (메모리 관리 차원)

