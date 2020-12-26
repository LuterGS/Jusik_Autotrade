

"""
거래 최소금액을 의미, 이 금액 이상이어야만 해당 금액을 가지고 주식거래 함
"""
MIN_TRADE_BALANCE = 10000

"""
수익률을 의미, 정해진 %만큼의 이득이나 손실을 보면 바로 익절/손절함
"""
MAX_PROFIT_PERCENT = 3
MAX_LOSS_PERCENT = 3


"""
주문 후 기다리는 시간을 의미, 입찰 후 실제로 주문이 행해지기까지를 기다림
이 시간이 지났음에도 주문이 되지 않으면 주문을 취소함
"""
BUY_WAIT_TIME = 15


"""
비동기 큐를 위한 RabbitMQ의 URL/PORT/VHOST/CREDENTIAL/QUEUE 설정
"""
MQ_URL = 'localhost'
MQ_PORT = 5672
MQ_VHOST = 'kiwoom'
MQ_ID, MQ_PW = 'guest', 'guest'
MQ_QUEUE = 'kiwoom_queue'

