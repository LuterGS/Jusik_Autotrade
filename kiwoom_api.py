import sys

from PyQt5.QtCore import QEventLoop
from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
from PyQt5.QAxContainer import *


class TextKiwoom(QAxWidget):

    FUNC_SET_INPUT_VALUE = "SetInputValue(QString, QString)"
    FUNC_REQUEST_COMM_DATA = "CommRqData(QString, QString, int, QString)"
    FUNC_GET_COMM_DATA = "GetCommData(QString, QString, int, QString)"
    TRANS_SHOWBALANCE = "opw00004"
    received_data = []
    received = False

    def __init__(self):
        super().__init__()

        # set OCX and login Handler
        self.setControl("KHOPENAPI.KHOpenAPICtrl.1")
        self.OnEventConnect.connect(self._login_handler)
        self.OnReceiveTrData.connect(self._receive_tran)
        print("Loading OCX and Register handler complete")
        self._login()

    def _login(self):
        self.dynamicCall("CommConnect()")
        print("dynamicCall Login method complete")
        self.login_event_loop = QEventLoop()
        self.login_event_loop.exec_()
        print("currently loop is active")

    def _login_handler(self, message):
        if message == 0:
            print("키움증권 서버 로그인 성공")
        else:
            print("키움증권 서버 로그인 실패, err:", message)
        self.login_event_loop.exit()

    def _send_tran(self, user_trans_name, trans_name, prev_next, screen_no="0101"):
        """
        명세서의 commRqData 함수
        :param user_trans_name: 사용자가 지정한 trans 이름
        :param trans_name: 실제 호출할 TR 명세 (이름)
        :param prev_next: 연속인지, 단일 호출할건지 (0일시 조회만, 2일시 연속)
            -> 아마 쌓아뒀다가 보내는게 가능할 듯?
        :param screen_no: 화면번호 (default로 0101로 설정되어있기 때문에, 그렇게 따라감)
        :return: 해당 출력값
        """
        result = self.dynamicCall(self.FUNC_REQUEST_COMM_DATA, user_trans_name, trans_name, prev_next, screen_no)
        print("in _send_tran, ", result)
        return result

    def _receive_tran(self, screen_no, user_trans_name, trans_name, record_name, prev_next, u1, u2, u3, u4):
        # 실제 이벤트 핸들러인 OnReceiveTrData의 Python 변형 형이다.
        """
        :param screen_no: _send_tran에서 지정해준 화면번호이다.
        :param user_trans_name: _send_tran에서 지정해준 사용자가 지정한 trans 이름이다.
        :param trans_name: _send_tran 에서 호출받을 실제 TR 이름이다.
        :param record_name: TR의 Output의 이름 중 하나가 아닐까 생각해본다.
        :param prev_next: 연속인지, 단일 호출할건지 (0일시 조회만, 2일시 연속)
        :param u1 ~ u4: 필요없는 값, 명세에 써야한다 나와있어서 넣음
        :return: 해당 명세에 따른 반환값
        """
        print(screen_no, user_trans_name, trans_name, record_name)
        if user_trans_name == "계좌평가현황요청":
            acc_name = self.dynamicCall(self.FUNC_GET_COMM_DATA, trans_name, user_trans_name, 0, "계좌명")
            balance = self.dynamicCall(self.FUNC_GET_COMM_DATA, trans_name, user_trans_name, 0, "예수금")
            print("name:", acc_name, "  balance:", balance)
            self.received_data.append([user_trans_name, acc_name, balance])
            self.received = True
        self.loop1.exit()


    def get_account_num(self):
        account_num = self.dynamicCall("GetLoginInfo(QString)", ["ACCNO"])
        return str(account_num).replace(";", "")

    def get_balance(self, account_num):
        # TR opw00004: 계좌평가현황을 사용

        # KOAStudio 참고
        # 4개의 요청한 입력을 넣음
        # 1. 보유계좌번호
        self.dynamicCall(self.FUNC_SET_INPUT_VALUE, "계좌번호", account_num)
        # 2. 비밀번호 (공백)
        self.dynamicCall(self.FUNC_SET_INPUT_VALUE, "비밀번호", "")
        # 3. 상장폐지조회구분. 상장폐지된 주식 포함시 0, 아닐시 1
        self.dynamicCall(self.FUNC_SET_INPUT_VALUE, "상장폐지조회구분", "0")
        # 4. 비밀번호입력매체구분=00
        self.dynamicCall(self.FUNC_SET_INPUT_VALUE, "비밀번호입력매체구분", "00")

        self._send_tran("계좌평가현황요청", self.TRANS_SHOWBALANCE, 0)
        # Warning!
        # 여기서 에러가 날 수 있음 (비밀번호 확인 관련)
        # 이럴 때는 KOAStudio에서 OpenAPI 접속후 우하단 위젯 우클릿 -> 계좌비밀번호 저장 들어가서
        # 해당 비밀번호 저장해놓을 것
        self.loop1 = QEventLoop()
        self.loop1.exec_()

        while True:
            if self.received:
                data = self.received_data.pop()
                self.received = False
                return data

if __name__ == "__main__":
    app = QApplication(sys.argv)    # 이게 키움증권 Load시 필수임
    test = TextKiwoom()


def get_balance():
    """

    :return: 계좌의 잔고 금액을 int형으로 return
    """
    return 10000


def buy_stock(ticker: str, amount: int):
    """
    :param ticker: 구매하고자 하는 종목코드 (str)
    :param amount: 구매하고자 하는 주식 개수 (int)
    :return: 두 개의 값을 return함.
        1. 총 구매한 금액 (int)
        2. 함수의 성공, 실패값 (bool)
    """
    return 1000, False


def sell_stock(ticker: str, amount: int, price: int):
    """
    :param ticker: 판매하고자 하는 종목코드 (str)
    :param amount: 판매하고자 하는 주식 개수 (int)
    :param price: 판매하고자 하는 주식의 가격 (int)
    :return: 성공, 실패값 (bool)
    """
    return True


def get_stock(ticker: str):
    """
    :param ticker: 보유개수를 알고자 하는 종목코드 (int)
    :return: ticker에 해당되는 주식의 보유개수 (int)
    """
    return 20


def get_stock_price(ticker: str, is_buying: bool):
    """
    :param ticker: 가격을 알고자 하는 종목코드 (int)
    :param is_buying: true일 땐 종목의 매수최고가를, false일 땐 종목의 매도최저가를 return함
    :return: is_buying에 따른 주식 종목의 가격
    """
    if is_buying:
        return 1000
    else:
        return 990
