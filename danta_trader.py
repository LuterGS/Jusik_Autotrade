import datetime
import time
import os
import csv
import constant
from multiprocessing import shared_memory

from basic_trader import BasicTrader
from kiwoom_api import KiwoomHandler
import else_func

"""
이제야말로 DB를 써서 버전관리를 시작할 때다!
"""

_PATH = os.path.abspath(os.path.dirname(__file__)) + "/"


class DantaTrader(BasicTrader):

    def __init__(self):
        super().__init__()
        self._kiwoom = KiwoomHandler()

        # 클래스를 선언할 때, 시간에 따라 언제의 상황인지를 알아야하지 않을까?
        # 예를 들어, 단타종료시각 이전에 선언되면 알고리즘이 동작해야하고, 이후에 선언하면 다음날 장시간 전까지는 동작하면 안된다.
        # 장시각을 어떻게 알지?
        self._init_log()

        # 핸들러가 호출되었을 때, 여기에 변화를 주기 위한 무언가를 만든다.

    def _init_log(self):
        # 현재 시간을 파악해, 다음날에 작동할 프로세스면 다음날에 해당하는 파일을 생성하도록 함
        cur_time = datetime.datetime.now()
        if cur_time.hour >= int(constant.DANTA_END_HOUR):
            cur_time += datetime.timedelta(days=1)
        
        raw_writer = open(_PATH + "log/" + cur_time.strftime("%y%m%d") + "_구매목록.txt", "w", encoding='utf8')
        csv_writer = csv.writer(raw_writer)

        self._log_file, self._csv_log = raw_writer, csv_writer

        # 로그 기록 시작
        self._log(["구매 종목코드", "종목이름", "구매개수", "구매가격"])
        self._log("\n\n거래결과")

    def _log(self, oneline):
        if type(oneline) == list:
            self._csv_log.writerow(oneline)
        else:  # if type is string:
            self._log_file.write(oneline + "\n")

    def _sell_jusik(self, sell_detail):
        # KiwoomHandler.sell_jusik의 Wrapper. 로그 남기기 및 화면 출력까지 포함한다.
        self._kiwoom.sell_jusik(sell_detail[0], sell_detail[2], sell_detail[7])
        result = "종목 : " + sell_detail[0] + "    수익률 : " + str(sell_detail[6]) + "    수익금액 : " + str(sell_detail[5])
        print(result)  # 프린트로 로그 찍고
        self._log(result)  # 구매 로그도 찍음

    def _buy_jusik(self, buy_detail):
        # KiwoomHandler.buy_jusik의 Wrapper. 로그 남기기 및 화면 출려까지 포함한다.
        self._kiwoom.buy_jusik(buy_detail[0], buy_detail[1], buy_detail[2])
        result = "종목 : " + buy_detail[0], "  구매가격 : " + buy_detail[1] + "    구매양 : " + str(buy_detail[2])
        print(result)
        self._log(result)

    def _get_recommend(self, one_mungchi: int, selection: int):
        # 주식구매시의 안정성을 위해 입금금액의 97% 만 투자함
        one_mungchi *= 0.97

        # selection 수만큼 사야 할 주식을 가져옴
        buy_list = self._kiwoom.get_highest_trade_amount()[:selection]
        final_list = []
        for data in buy_list:
            final_list.append([data[0], data[1], int(one_mungchi / data[2]), data[2]])
        return final_list

    def buy(self, one_mungchi=constant.ONE_JONGMOK_TOTAL_PRICE, selection=constant.TOTAL_JONGMOK_NUM):
        # 구매에 대한 Tracking
        while True:
            cur_jusik_data = self._kiwoom.get_profit_percent()

            # 일단, 만약 매도로 인한 현재 종목수가 부족할 때
            if len(cur_jusik_data) < constant.TOTAL_JONGMOK_NUM:
                new_recommended = self._get_recommend(one_mungchi, selection)  # 추천종목 받아옴
                recommended_code = else_func.get_only_code(new_recommended)  # 값 비교를 위해 리스트만 떼옴
                current_code = else_func.get_only_code(cur_jusik_data)
                diff_count = constant.TOTAL_JONGMOK_NUM - len(cur_jusik_data)  # 몇개나 다른지 알아봄
                counter = 0
                for i in range(constant.TOTAL_JONGMOK_NUM):  # 다른 개수만큼 주식 구매
                    if current_code.count(recommended_code[i]) == 0:
                        self._buy_jusik(new_recommended[i])
                        counter += 1
                    if counter == diff_count:
                        break
                cur_jusik_data = self._kiwoom.get_profit_percent()  # 다시 Renewel

            # 거래 비교 시작
            for jusik_data in cur_jusik_data:
                if jusik_data[6] > constant.MAX_PROFIT_PERCENT or jusik_data[6] < constant.MAX_LOSS_PERCENT:  # 만약 손익분기를 넘기면
                    self._sell_jusik(jusik_data)  # 주식 판매

            # 시그널 핸들링
            try:  # 만약 시그널이 호출되었을 때는 프로그램 종료
                checker = shared_memory.SharedMemory(name=constant.SIGNAL_B, create=False)
                # 단타 종료시 모든 종목을 팔지, 말지 선택
                if constant.DANTA_END_METHOD == 0:
                    cur_jusik_data = self._kiwoom.get_profit_percent()
                    print("단타가 끝났습니다. 모든 주식을 매매합니다.")
                    self._log("단타가 끝났습니다. 설정에 따라 모든 주식을 매매합니다.")
                    for jusik_data in cur_jusik_data:
                        self._sell_jusik(jusik_data)
                else:
                    print("단타가 끝났습니다. 단타를 종료합니다.")
                self._log_file.close()
                checker.close()
                checker.unlink()
                break
            except FileNotFoundError:
                pass
