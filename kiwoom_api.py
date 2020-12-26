import sys
import os
import time
import datetime
from collections import deque
from PyQt5.QtCore import QEventLoop
from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
from PyQt5.QAxContainer import *

import else_func

# 예제
class MyWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        # Kiwoom Login
        self.kiwoom = QAxWidget("KHOPENAPI.KHOpenAPICtrl.1")
        self.kiwoom.dynamicCall("CommConnect()")

        # OpenAPI+ Event
        self.kiwoom.OnEventConnect.connect(self.event_connect)
        self.kiwoom.OnReceiveTrData.connect(self.receive_trdata)

        self.setWindowTitle("PyStock")
        self.setGeometry(300, 300, 300, 150)

        label = QLabel('종목코드: ', self)
        label.move(20, 20)

        self.code_edit = QLineEdit(self)
        self.code_edit.move(80, 20)
        self.code_edit.setText("039490")

        btn1 = QPushButton("조회", self)
        btn1.move(190, 20)
        btn1.clicked.connect(self.btn1_clicked)

        self.text_edit = QTextEdit(self)
        self.text_edit.setGeometry(10, 60, 280, 80)
        self.text_edit.setEnabled(False)

    def event_connect(self, err_code):
        if err_code == 0:
            self.text_edit.append("로그인 성공")

    def btn1_clicked(self):
        code = self.code_edit.text()
        self.text_edit.append("종목코드: " + code)

        # SetInputValue
        self.kiwoom.dynamicCall("SetInputValue(QString, QString)", "종목코드", code)

        # CommRqData
        self.kiwoom.dynamicCall("CommRqData(QString, QString, int, QString)", "opt10001_req", "opt10001", 0, "0101")

    def receive_trdata(self, screen_no, rqname, trcode, recordname, prev_next, data_len, err_code, msg1, msg2):
        if rqname == "opt10001_req":
            name = self.kiwoom.dynamicCall("CommGetData(QString, QString, QString, int, QString)", trcode, "", rqname, 0, "종목명")
            volume = self.kiwoom.dynamicCall("CommGetData(QString, QString, QString, int, QString)", trcode, "", rqname, 0, "거래량")

            self.text_edit.append("종목명: " + name.strip())
            self.text_edit.append("거래량: " + volume.strip())


"""
키움증권 API 핸들러

들어가기 전 주의점 (겪은 문제점)
1. 파이썬 버전이 32bit이어야만 동작한다. 그러니, 64bit에선 실행하지 않도록 하자
2. 2020년 12월 20일에 최신화된 키움증권 OpenAPI+를 사용한다.

밑의 클래스 TextKiwoom을 이용하면, 클래스 내 메소드들만 호출하는 방식으로 원하는 값을 얻을 수 있다.
기존의 OpenAPI는 이벤트 핸들러 방식이라 원하는 값 하나를 얻기 위해서 여러 코드를 직접 선언해줘야 했지만, 
해당 클래스를 이용하면 구현된 함수만 호출하면 원하는 값을 return 해준다.

+ 키움증권의 API 요청은 시간당 1000회다. 즉, 한 요청당 3.6초를 해야 한다는 뜻이다. 이걸 Queue로 처리한다.

*주의사항
1. 점검시간에는 접속이 안됨. -> 월~토 05:05~05:10, 일 04:00~04:30
"""

FILEPATH = os.path.dirname(__file__)


class TextKiwoom(QAxWidget):
    FUNC_LOGIN = ["CommConnect()", False]
    FUNC_SET_INPUT_VALUE = ["SetInputValue(QString, QString)", False]
    FUNC_REQUEST_COMM_DATA = ["CommRqData(QString, QString, int, QString)", True]
    FUNC_GET_LOGIN_INFO = ["GetLoginInfo(QString)", False]
    FUNC_GET_COMM_DATA = ["GetCommData(QString, QString, int, QString)", False]
    FUNC_GET_REPEAT_DATA_LEN = ["GetRepeatCnt(QString, QString)", False]
    FUNC_GET_MARKET_CODELIST = ["GetCodeListByMarket(QString)", False]
    FUNC_GET_KOREAN_NAME = ["GetMasterCodeName(QString)", False]
    TRANS_SHOWBALANCE = "opw00004"
    TRANS_GETMINDATA = "opt10080"
    received_data = []
    received = False

    def __init__(self):
        super().__init__()
        # dynamicCall이 3.6초에 한번씩 진행하도록 자동조정
        self._cur_time = datetime.datetime.now()

        # set OCX and login Handler
        self.setControl("KHOPENAPI.KHOpenAPICtrl.1")
        self.OnEventConnect.connect(self._login_handler)
        self.OnReceiveTrData.connect(self._receive_tran)
        self._login()


    def _login(self):
        self._dynamicCall(self.FUNC_LOGIN)
        self.login_event_loop = QEventLoop()
        self.login_event_loop.exec_()

    def _login_handler(self, message):
        if message == 0:
            print(str(datetime.datetime.now()) + "  키움증권 서버 로그인 성공")
        else:
            print(str(datetime.datetime.now()) + "  키움증권 서버 로그인 실패, err:", message)
        self.login_event_loop.exit()

    def _dynamicCall(self, p_str, *args):
        """
        키움증권 API요청이 시간당 1000회고, 아닐 경우에는 초당 5초여서 해당 부분을 반영함
        :param p_str: constant가 들어오며, constant의 두 번째 필드값은 대기해야할지를 알려줌 (대기해야할경우 True, 아니면 False)
        :param args: dynamicCall의 원래 args
        :return: 원래의 dynamicCall 함수 원형
        """
        else_func.check_maintenance()
        if p_str[1]:
            while True:
                timediff = datetime.datetime.now() - self._cur_time
                elapsed_time = timediff.seconds + (timediff.microseconds/1000000)
                if elapsed_time > 3.6:
                    break
        return self.dynamicCall(p_str[0], *args)

    def _send_tran(self, user_trans_name, trans_name, prev_next, screen_no="0101"):
        """
        명세서의 commRqData 함수 + 받은 데이터를 Return하는 함수
        :param user_trans_name: 사용자가 지정한 trans 이름
        :param trans_name: 실제 호출할 TR 명세 (이름)
        :param prev_next: 연속인지, 단일 호출할건지 (0일시 조회만, 2일시 연속)
            -> 아마 쌓아뒀다가 보내는게 가능할 듯?
        :param screen_no: 화면번호 (default로 0101로 설정되어있기 때문에, 그렇게 따라감)
        :return: commRqData에 의한 TR 전송 후의 return값
        """
        self._dynamicCall(self.FUNC_REQUEST_COMM_DATA, user_trans_name, trans_name, prev_next, screen_no)
        self.loop1 = QEventLoop()
        self.loop1.exec_()
        while True:
            if self.received:
                data = self.received_data
                self.received_data = []
                self.received = False
                return data

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
        # print("receive tran : ", screen_no, user_trans_name, trans_name, record_name)
        # Tran의 종류에 따라서 처리를 다르게 해줘야 함
        if user_trans_name == "계좌평가현황요청":
            acc_name = self._dynamicCall(self.FUNC_GET_COMM_DATA, trans_name, user_trans_name, 0, "계좌명")
            balance = self._dynamicCall(self.FUNC_GET_COMM_DATA, trans_name, user_trans_name, 0, "예수금")
            self.received_data.append([user_trans_name, acc_name, balance])
            self.received = True
        if user_trans_name == "주식분봉차트조회요청":
            data_length = self._dynamicCall(self.FUNC_GET_REPEAT_DATA_LEN, trans_name, user_trans_name)
            # print("주식분봉차트조회요청 데이터량 : ", data_length)
            for i in range(data_length):
                timestamp = self._dynamicCall(self.FUNC_GET_COMM_DATA, trans_name, user_trans_name, i, "체결시간")
                price = self._dynamicCall(self.FUNC_GET_COMM_DATA, trans_name, user_trans_name, i, "현재가")
                amount = self._dynamicCall(self.FUNC_GET_COMM_DATA, trans_name, user_trans_name, i, "거래량")
                self.received_data.append([timestamp, price, amount])
            self.received = True

        self.loop1.exit()

    def get_account_num(self):
        account_num = self._dynamicCall(self.FUNC_GET_LOGIN_INFO, ["ACCNO"])
        print(account_num)
        return str(account_num).replace(";", "")

    def get_balance(self, account_num):
        """
        TR opw00004: 계좌평가현황을 사용
        :param account_num: 예수금을 조회하고자 하는 계좌의 계좌번호
        :return: 계좌의 예수금 (int)
        """

        # KOAStudio 참고
        # 4개의 요청한 입력을 넣음
        # 1. 보유계좌번호
        self._dynamicCall(self.FUNC_SET_INPUT_VALUE, "계좌번호", account_num)
        # 2. 비밀번호 (공백)
        self._dynamicCall(self.FUNC_SET_INPUT_VALUE, "비밀번호", "")
        # 3. 상장폐지조회구분. 상장폐지된 주식 포함시 0, 아닐시 1
        self._dynamicCall(self.FUNC_SET_INPUT_VALUE, "상장폐지조회구분", "0")
        # 4. 비밀번호입력매체구분=00
        self._dynamicCall(self.FUNC_SET_INPUT_VALUE, "비밀번호입력매체구분", "00")

        result = self._send_tran("계좌평가현황요청", self.TRANS_SHOWBALANCE, 0, "0001")[0]
        print(result)
        # Warning!
        # 여기서 에러가 날 수 있음 (비밀번호 확인 관련)
        # 이럴 때는 KOAStudio에서 OpenAPI 접속후 우하단 위젯 우클릿 -> 계좌비밀번호 저장 들어가서
        # 해당 비밀번호 저장해놓을 것
        return int(result[2])

    def get_kospi_data(self):
        """
        코스피 주식들을 가져와 "종목코드"_"종목이롬".txt로 저장함
        :return: 성공시 True
        """
        kospi_jusik = self._dynamicCall(self.FUNC_GET_MARKET_CODELIST, "0").split(";")

        while kospi_jusik[0] != "003560":  # 현재 003560 하다가 멈춤
            del kospi_jusik[0]
        print(kospi_jusik[0])

        for code in kospi_jusik:
            self.get_min_jusik_data(code)
        return kospi_jusik

    def get_min_jusik_data(self, ticker: str, save_folder=FILEPATH + "\\data\\min\\"):
        """
        주식 분봉 데이터를 가져오는 함수, 총 1년치의 데이터를 받아온다 가정하고 146번 호출함
            Request당 900번이기 때문에, 총 112번 요청
        :param ticker: 주식의 6자리 번호 (str)
        :param save_folder: 주식의 데이터를 저장하려는 폴더, 데이터는 종목코드_종목이름.txt로 저장됨
        :return: 성공, 실패값 (bool)
        """
        korean_name = self._dynamicCall(self.FUNC_GET_KOREAN_NAME, ticker)
        print(ticker + "_" + korean_name + ".txt 진행 중", end="")
        save_file = open(save_folder + ticker + "_" + korean_name + ".txt", "w", encoding="utf8")
        save_file.write("거래시간, 거래가격, 거래량\n")

        # KOAStudio 참고
        # 3개의 요청한 입력을 넣음
        # 1. 종목코드 - 전문을 조회할 종목코드
        # 2. 틱범위 - 각 데이터의 간격 (분단위), 분 단위로 받아올 것이기 때문에 1로 설정
        # 3. 수정주가구분 - 수정주가를 구분할 것인지, 일단 0으로 받아오자.
        self._dynamicCall(self.FUNC_SET_INPUT_VALUE, "종목코드", ticker)
        self._dynamicCall(self.FUNC_SET_INPUT_VALUE, "틱범위", "1")
        self._dynamicCall(self.FUNC_SET_INPUT_VALUE, "수정주가구분", "0")
        save_file = else_func.write_list_in_file(save_file, self._send_tran("주식분봉차트조회요청", self.TRANS_GETMINDATA, 0))
        for i in range(145):
            time.sleep(3.8)
            print(".", end="")
            self._dynamicCall(self.FUNC_SET_INPUT_VALUE, "종목코드", ticker)
            self._dynamicCall(self.FUNC_SET_INPUT_VALUE, "틱범위", "1")
            self._dynamicCall(self.FUNC_SET_INPUT_VALUE, "수정주가구분", "0")
            save_file = else_func.write_list_in_file(save_file, self._send_tran("주식분봉차트조회요청", self.TRANS_GETMINDATA, 2))
        print(" ")
        save_file.close()

        return True


if __name__ == "__main__":
    app = QApplication(sys.argv)  # 이게 키움증권 Load시 필수임
    test = TextKiwoom()


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
