from PyQt5.QAxContainer import *
from PyQt5.QtCore import *
import pandas as pd
import Db
import time


class Stock(QAxWidget):
    def __init__(self):
        super().__init__()
        self.db = Db.StockDb()
        self.db.open_Db()

        self._create_kiwoom_instance()
        self._set_signal_slots()

    # COM을 사용하기 위한 메서드
    def _create_kiwoom_instance(self):
        self.setControl("KHOPENAPI.KHOpenAPICtrl.1")

    def _set_signal_slots(self):
        # 로그인할 시 OnEventConnect 이벤트 발생
        self.OnEventConnect.connect(self._event_connect)
        # tr후 이벤트 발생
        self.OnReceiveTrData.connect(self._receive_tr_data)

    # 로그인 메서드, 로그인 과정에서 프로그램이 진행되면 안 되기 때문에
    # 이벤트 루프 생성
    def comm_connect(self):
        self.dynamicCall("CommConnect()")
        self.login_event_loop = QEventLoop()
        self.login_event_loop.exec_()

    # 로그인 성공 여부 메서드
    def _event_connect(self, err_code):
        if err_code == 0:
            print("connected")
        else:
            print("disconnected")
        self.login_event_loop.exit()

    # tr 입력값을 서버 통신 전에 입력
    # ex. SetInputValue("종목코드","000660")
    def set_input_value(self,id,value):
        self.dynamicCall("SetInputValue(QString,QString)", id, value)

    # tr을 서버에 전송한다
    def comm_rq_data(self, rqname, trcode, next, screen_no):
        self.dynamicCall("CommRqData(QString, QString, int, QString)", rqname, trcode, next, screen_no)
        self.tr_event_loop = QEventLoop()
        self.tr_event_loop.exec_()

    # 서버한테 받은 데이터를 반환한다.
    def _comm_get_data(self, code, real_type, field_name, index, item_name):
        ret = self.dynamicCall("CommGetData(QString, QString, QString, int, QString)", code,
                               real_type, field_name, index, item_name)
        return ret.strip()

    # 서버한테 받은 데이터의 갯수를 반환한다.
    def _get_repeat_cnt(self, trcode, rqname):
        ret = self.dynamicCall("GetRepeatCnt(QString, QString)", trcode, rqname)
        return ret

    def _receive_tr_data(self, screen_no, rqname, trcode, record_name, next, unused1, unused2, unused3, unused4):
        print("receive_tr_data call")
        if next == '2':
            self.remained_data = True
        else:
            self.remained_data = False

        if rqname == "opt10080_req":
            self._opt10080(rqname, trcode)
        elif rqname == "opt10081_req":
            self._opt10081(rqname, trcode)

        try:
            self.tr_event_loop.exit()
        except AttributeError:
            pass

    # KODEX 코스닥 150 레버리지 종목의 분봉 데이터를 요청한다.
    # 약 100일치 분봉 데이터를 요청한다.
    def req_minute_data(self):
        self.set_input_value("종목코드","233740")
        self.set_input_value("틱범위", 1)
        self.set_input_value("수정주가구분", 0)
        self.comm_rq_data("opt10080_req", "opt10080", 0, "1999")

        for i in range(50):
            time.sleep(0.2)
            self.set_input_value("종목코드", "233740")
            self.set_input_value("틱범위", 1)
            self.set_input_value("수정주가구분", 0)
            self.comm_rq_data("opt10080_req", "opt10080", 2, "1999")

        print("코스닥 레버리지 분봉 데이터 저장 성공")

    # KODEX 코스닥 150 레버리지 종목의 일봉 데이터를 요청한다.
    def req_day_data(self):
        self.set_input_value("종목코드","233740")
        self.set_input_value("기준일자", "20171108")
        self.set_input_value("수정주가구분",0)
        self.comm_rq_data("opt10081_req", "opt10081",0,"2000")

        print("코스닥 레버리지 일봉 데이터 저장 성공")

    # 서버에게 받은 분봉 데이터를 kosdaq_leve 테이블에 저장한다.
    # 또한 kosdaq_start 테이블에 매일 시가 정보를 저장한다.
    def _opt10080(self,rqname,trcode):
        data_cnt = self._get_repeat_cnt(trcode,rqname)
        for i in range(data_cnt):
            print("분봉 데이터 저장중")
            day = self._comm_get_data(trcode, "",rqname, i, "체결시간")
            high = self._comm_get_data(trcode, "", rqname, i, "현재가")
            low = self._comm_get_data(trcode, "", rqname, i, "저가")
            if(high[0] == '-'):
                high = high[1:]
            if(low[0] == '-'):
                low = low[1:]
            self.db.insert_Leve(day,int(high),int(low))
            #self.db.insert_Leve(day, abs(int(high)), abs(int(low)))

            if day[8:] == "090000":
                start = self._comm_get_data(trcode, "",rqname, i, "시가")
                if(start[0] == '-'):
                    start = start[1:]
                self.db.insert_Start(day,int(start))
                #self.db.insert_Start(day,abs(int(start)))

        self.db.con.commit()

    # 서버에게 받은 일봉 데이터를 DB에 저장한다.
    def _opt10081(self,rqname, trcode):
        for i in range(150):
            print("일봉 데이터 저장중")
            day = self._comm_get_data(trcode, "",rqname, i, "일자")
            end = self._comm_get_data(trcode, "",rqname, i,"현재가")
            start = self._comm_get_data(trcode, "",rqname, i,"시가")
            self.db.insert_Leve_Day(day,start,end)
        self.db.commit()




if __name__ == "__main__":
    stock = Stock()
    stock.comm_connect()
    stock.req_minute_data()
    stock.req_day_data()