import kiwoom_api
import core_func
import constant
import asyncio
import threading

"""
어떻게 프로그램을 짤 것이냐?
내가 관리해주지 않아도 얘가 직접 돌아가면서 거래를 자동으로 해야 함
비동기적으로 일어나며, 여러 개를 수행할 수 있음 -> 단, 현재 종목의 선택은 유저 입력을 (어떤 형식으로든) 받을 수 있어야 함
핵심 기능은,
goroutine을 이용해 매수 후 매도까지는 함수 하나가 전적으로 담당해야 하며,
    -> 겹치지 않게 종목으로 구분한다.
그럼 매수 이전에, 현재 금액 및 적절한 종목 추천이 실시간으로 돌아가야 한다.
적절한 종목 추천을 실시간으로?
    바로 종목을 구매해야 할 필요는 없다.
    돈이 있으면, 그 때 종목을 살펴보는 것이 맞
전체를 도는 반복문이 있어야 하지 않을까?
반복문의 구조
while(True){
    현재 금액을 조사
    if 현재 금액이 일정 액수 이상일 경우:음
        적절한 종목 선택
        선택한 종목으로 trade을 goroutine으로 돌림
}
trade(종목, 개수, 매수금){
    얘는 goroutine으로 돌아가므로, 여기서는 구매가 즉각적으로 이루어져야 한다. 그래야만 얘가 확인중에 새롭게 main에서 if문으로 빠지지 않으니까
    어차피 종목 추천하면 같은 종목이 나올 텐데, 매수최고가 / 매도최저가로 입찰하는게 의미가 있을까?
    그냥 매수 최고금액으로 입찰 후, n분이 지나도 빠지지 않으면 주문취소
    while(True){
        만약 장 마감 시간이면 다음날 장 시작시간까지 기다림
        아닐 경우 종목을 계속 실시간 조회해서
        -> +/- 3% 이상이면 매도 (익절/손절)
    매도금액과 총 이익을 이메일로 보냄
}
"""


"""
프로젝트의 틀이... get_recommend를 다른 별도의 프로그램으로 만들 수 있지 않을까?
DB에 값이 추가되면, 그 값을 읽어들여오는 형식으로 한다면,

프로그램 A는 계속 돌아가면서 추천 종목들을 Update한 후 DB에 저장하고
이 프로그램은 DB에서 해당 종목을 가져와 금액을 토대로 얼마나 살 건지 계산 후 구매 및 구매 성공시 DB값을 이동하는 형식으로.
괜찮은듯...
"""

if __name__ == "__main__":
    while True:
        if kiwoom_api.get_balance() > constant.min_trade_balance:
            ticker, amount = core_func.get_recommend()

            thread = threading.Thread(target=core_func.trade, args=[ticker, amount])
            thread.start()