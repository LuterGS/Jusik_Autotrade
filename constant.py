import os

_PATH = os.path.dirname(os.path.abspath(__file__)) + "/"
print(_PATH)

"""
환영합니다! 이 constant.py는, 일반 사용자 및 튜닝용으로 가장 많이 거래하는 부분입니다.
각 변수에는 설명이 달려 있으니, 설명을 잘 읽어 주시고 본인에게 맞는 값으로 세팅해주세요!
"""

# 수익률을 의미, 정해진 %만큼의 이득이나 손실을 보면 바로 익절/손절함
MAX_PROFIT_PERCENT = 3      # 이득 퍼센트
MAX_LOSS_PERCENT = 1.5      # 손실 퍼센트

# 한 종목에 투자할 주식의 금액
ONE_JONGMOK_TOTAL_PRICE = 1000000   # 백만원으로 설정

# 단타 거래시 시장가/지정가 거래
# 현재는 무조건 시장가로 거래함

# 단타 거래시 한 번에 유지할 종목 수
TOTAL_JONGMOK_NUM = 7

# 단타할 주식 시장 - 코스피일 경우 "000", 코스닥일 경우 "001", 둘 다 확인할 경우 "101" (str)
TRADE_MARKET = "001"

# 단타시 몇 분 전과의 거래량을 비교할 것인지 (59가 최대값입니다), 해당 시간이 경과한 후 조회를 시작함.
# 예를 들어, 이 값이 30이면, 9시에 개장하면 9시 30분부터 조회를 시작함
TRADE_LAST_MIN = "15"

# 단타시 거래량급증 종목을 요청할 때, 주식 거래의 증가량으로 판단할것인지, 증가율로 판단할것인지
VIEW_AS_PERCENT = 1    # 1이면 증가량으로, 2이면 증가율로 판단

# 단타의 종료시간 - 단타는 통상 12시에 종료합니다. 분 단위로 해야할 경우, 밑의 값까지 적어주세요.
DANTA_END_HOUR = "12"     # "10" ~ "15" 사이어야 합니다. 아닐 시 오류가 날 수 있습니다.
DANTA_END_MIN = "00"      # "00" ~ "59" 사이어야 합니다. 아닐 시 오류가 날 수 있습니다. (HOUR가 "15"일 경우, "00" ~ "19"까지여야 합니다)

# 단타의 종료 종류
# 0으로 설정 시, 종료시간이 되면 보유하고 있던 단타 종목을 퍼센트 상관없이 모두 판 이후, DB에서 추천종목을 모두 불러와 매수합니다.
# 1로 설정 시, 종료시간이 되도 단타 주식을 가지며, 주식이 매도되면 DB에서 추천종목을 불러와 매수합니다.
DANTA_END_METHOD = 0



# sig_b를 위한 Shared Memory 이름
SIGNAL_B = "danta_signal_handling"

# 비동기 큐를 위한 RabbitMQ의 URL/PORT/VHOST/CREDENTIAL/QUEUE 설정 - 비밀번호 등을 파일에서 읽어들여와 Return하는 함수 만듦 (코드에서 공개하지 않음)
def GET_MQ_VALUE():
    return_val = {}
    with open(_PATH + "MQ_VALUE.txt", "r", encoding="utf8") as mqfile:
        for line in mqfile:
            line = line.replace("\n", "").split("=")
            return_val[line[0]] = line[1]
    return return_val


if __name__ == "__main__":
    GET_MQ_VALUE()
