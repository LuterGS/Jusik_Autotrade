import kiwoom_api
import else_func
import constant
import datetime


def get_recommend():
    """
    사야 할 종목의 종목코드를 return함
    -> 전체적으로 인공지능이나 기타 방법론을 이용해 추출함
    -> 이걸 DB에 저장하느냐, 즉 DB 기능을 추가하느냐는 살펴봐야 함
    :return: 2개의 값을 return함.
        1. 주식의 종목코드, 6자리로 된 str
        2. 해당 주식을 몇 개 사야 할 지에 대한 값 (int)
    """
    return "000000", 1


async def trade(ticker: str, amount: int):
    """trade(종목, 개수, 매수금):
    얘는 coroutine으로 돌아가므로, 여기서는 구매가 즉각적으로 이루어져야 한다. 그래야만 얘가 확인중에 새롭게 main에서 if문으로 빠지지 않으니까
    어차피 종목 추천하면 같은 종목이 나올 텐데, 매수최고가 / 매도최저가로 입찰하는게 의미가 있을까?
    그냥 매수 최고금액으로 입찰 후, n분이 지나도 빠지지 않으면 주문취소
    while True:
        만약 장 마감 시간이면 다음날 장 시작시간까지 기다림
        아닐 경우 종목을 계속 실시간 조회해서
        -> +/- 3% 이상이면 매도 (익절/손절)
    매도금액과 총 이익을 이메일로 보냄
    return: 어떤 식으로라도 구매 성공후 익절/손절시 true, 구매 실패시 false
    """
    buy_price, buy_result = kiwoom_api.buy_stock(ticker, amount)
    if buy_result:
        buy_time = datetime.datetime.now()
        while True:
            if kiwoom_api.get_stock(ticker) > 0:  # 구매가 성공했으면
                price, _ = else_func.get_yield(ticker, buy_price)
                kiwoom_api.sell_stock(ticker, amount, price)
                else_func.send_mail()
                return True
            if (datetime.datetime.now() - buy_time).min > constant.buy_wait_time:  # 만약 구매 입찰시 구매 대기시간을 초과하면
                return False

    else:  # 주식 구매입찰 자체가 실패한 경우
        return False
