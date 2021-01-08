import datetime
import time
import os
import csv
import constant
from multiprocessing import shared_memory

from basic_trader import BasicTrader
from kiwoom_api import KiwoomHandler
from db import DB
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
        print("inithandler complete")
        self._init_log()
        print("initlog complete")

        self._profit = 0

        # DB Log 설정
        self._db = DB()

    def _init_log(self):
        # 현재 시간을 파악해, 다음날에 작동할 프로세스면 다음날에 해당하는 파일을 생성하도록 함
        cur_time = datetime.datetime.now()
        if int(else_func.get_hm()) >= int(constant.DANTA_END_HOUR + constant.DANTA_END_MIN):
            cur_time += datetime.timedelta(days=1)
        
        raw_writer = open(_PATH + "log/" + cur_time.strftime("%y%m%d") + "_구매목록.txt", "a", encoding='utf8')
        csv_writer = csv.writer(raw_writer)

        self._log_file, self._csv_log = raw_writer, csv_writer

        # 로그 기록 시작
        self._log(["구매 종목코드", "종목이름", "구매개수", "구매가격"])
        self._log("\n\n거래결과")

    def _log(self, oneline):
        if type(oneline) == list:
            self._csv_log.writerow(oneline)
        else:  # if type is string:
            self._log_file.write(str(oneline) + "\n")

    def _sell_jusik(self, sell_detail):
        # print(sell_detail)
        # KiwoomHandler.sell_jusik의 Wrapper. 로그 남기기 및 화면 출력까지 포함한다.
        self._kiwoom.sell_jusik(sell_detail[0], sell_detail[2], sell_detail[7])
        result = "종목:" + sell_detail[1] + "(" + sell_detail[0] + "),수익률:" + str(sell_detail[6]) + ",수익금액:" + str(sell_detail[5])
        # 수익금액은 말그대로 손실액수...가 아니네?
        print(result)  # 프린트로 로그 찍고
        self._log(result)  # 구매 로그도 찍음
        self._db.add_sell_data(datetime.datetime.now(), sell_detail[0], sell_detail[1], str(sell_detail[6]), str(sell_detail[5]))
        # 총 수익금 업데이트
        self._profit += int(sell_detail[5])

    def _buy_jusik(self, buy_detail):
        # KiwoomHandler.buy_jusik의 Wrapper. 로그 남기기 및 화면 출려까지 포함한다.
        # print(buy_detail)
        self._kiwoom.buy_jusik(buy_detail[0], buy_detail[2], buy_detail[3])
        result = "종목:" + buy_detail[1] + "(" + buy_detail[0] + "),구매가격:" + str(buy_detail[3]) + ",구매양:" + str(buy_detail[2]) + ",총구매가격:" + str(buy_detail[2] * buy_detail[3])
        self._db.add_buy_data(datetime.datetime.now(), buy_detail[0], buy_detail[1], str(buy_detail[2]), str(buy_detail[3]), str(buy_detail[2]) * buy_detail[3])
        print(result)
        self._log(result)

    def _get_recommend(self, one_mungchi: int, selection: int, not_buy_list: dict, cur_jusik_data: list):
        # 주식구매시의 안정성을 위해 입금금액의 97% 만 투자함
        one_mungchi *= 0.97
        print(not_buy_list, cur_jusik_data)

        # 주식 리스트를 가져온 뒤, 손실 리스트는 뺌
        buy_list = self._kiwoom.get_highest_trade_amount()
        for data in not_buy_list:
            if not_buy_list[data] == 2:
                for i in range(len(buy_list)):
                    if buy_list[i][1] == data:
                        break
                del buy_list[i]

        # 현재 보유중인 주식도 제외함
        for data in cur_jusik_data:
            for i in range(len(buy_list)):
                if buy_list[i][1] == data[1]:
                    break
            del buy_list[i]

        print(buy_list)

        # 상위 목록을 추려내되, 한 주식당 구매가격이 한 주보다 적을 때는 다음 주식을 구매하게끔 함
        counter = 0
        final_list = []
        for i in range(len(buy_list)):
            amount = int(one_mungchi / buy_list[i][2])
            if amount != 0:
                final_list.append([buy_list[i][0], buy_list[i][1], amount, buy_list[i][2]])
                counter += 1
            if counter == selection:
                break
        return final_list

    def buy(self, one_mungchi=constant.ONE_JONGMOK_TOTAL_PRICE, selection=constant.TOTAL_JONGMOK_NUM):
        # 구매에 대한 Tracking
        # 2번 잃었을 때는 해당 종목은 사지 않기 위한 리스트 작성
        not_buy_dict = {}
        while True:
            cur_jusik_data = self._kiwoom.get_profit_percent()
            # print("1", cur_jusik_data)

            # 일단, 만약 매도로 인한 현재 종목수가 부족할 때
            if len(cur_jusik_data) < constant.TOTAL_JONGMOK_NUM:
                # print("im in!")
                new_recommended = self._get_recommend(one_mungchi, selection, not_buy_dict, cur_jusik_data)  # 추천종목 받아옴
                # print(new_recommended)
                diff_count = constant.TOTAL_JONGMOK_NUM - len(cur_jusik_data)  # 몇개나 다른지 알아봄
                for i in range(diff_count):                                 # 다른 종목수만큼 주식 구매
                    self._buy_jusik(new_recommended[i])
                cur_jusik_data = self._kiwoom.get_profit_percent()  # 다시 Renewel

            # 거래 비교 시작
            # print("2", cur_jusik_data)
            for jusik_data in cur_jusik_data:
                # print(jusik_data[6], constant.MAX_LOSS_PERCENT, constant.MAX_PROFIT_PERCENT)
                if jusik_data[6] > constant.MAX_PROFIT_PERCENT: # 만약 이득 분기를 넘기면
                    self._sell_jusik(jusik_data)  # 주식 판매
                elif jusik_data[6] < -1 * constant.MAX_LOSS_PERCENT:  # 만약 손해 분기를 넘기면
                    self._sell_jusik(jusik_data)
                    try:
                        not_buy_dict[jusik_data[1]] += 1
                        if not_buy_dict[jusik_data[1]] == 2:
                            print("종목 ", jusik_data[1], " 은 총 두 번의 손실을 입었으므로, 오늘은 더 이상 구매하지 않습니다.")
                    except KeyError:
                        not_buy_dict[jusik_data[1]] = 1


            # print("End of cycle")

            # 시그널 핸들링
            try:  # 만약 시그널이 호출되었을 때는 프로그램 종료
                checker = shared_memory.SharedMemory(name=constant.SIGNAL_B, create=False)
                print("Handler detected!")
                # 단타 종료시 모든 종목을 팔지, 말지 선택
                if constant.DANTA_END_METHOD == 0:
                    cur_jusik_data = self._kiwoom.get_profit_percent()
                    print("단타가 끝났습니다. 모든 주식을 매매합니다.")
                    self._log("단타가 끝났습니다. 설정에 따라 모든 주식을 매매합니다.")
                    for jusik_data in cur_jusik_data:
                        self._sell_jusik(jusik_data)
                else:
                    print("단타가 끝났습니다. 단타를 종료합니다.")
                self._log("\n오늘의 재구매 없는 주식 : " + str(not_buy_dict))
                self._log("단타 알고리즘의 수익률 : " + str(self._profit))
                self._log_file.close()
                checker.close()
                checker.unlink()
                del self._kiwoom
                break
            except FileNotFoundError:
                pass

            # print("PASS THIS!")
