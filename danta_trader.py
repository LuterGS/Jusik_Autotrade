import datetime
import os

from basic_trader import BasicTrader
from kiwoom_api import KiwoomHandler


_PATH = os.path.abspath(os.path.dirname(__file__)) + "/"

class DantaTrader(BasicTrader):
    def __init__(self):
        super().__init__()
        self._kiwoom = KiwoomHandler()
        self._buy_list = []

    def get_recommend(self):
        cur_time = datetime.datetime.now()
        if cur_time.hour == 9 and cur_time.minute == 30:
            self._buy_list = self._kiwoom.get_highest_trade_amount()
            return True
        else:
            return False

    def buy(self, one_mungchi=500000, selection=5):
        # 구매리스트에서 값 추려오기
        one_mungchi -= 50000
        self.get_recommend()
        buy_stock_list = self._buy_list[:selection]
        buy_list = []
        for i in range(selection):
            buy_list.append([buy_stock_list[i][0], buy_stock_list[i][1], int(one_mungchi/buy_stock_list[i][2]), buy_stock_list[i][2]])
        print("구매리스트 : ", buy_list)

        # 로그 생성
        savefile = open(_PATH + "log/" + datetime.datetime.now().strftime("%y%m%d") + "_구매목록.txt", "w", encoding='utf8')
        savefile.write("구매 종목코드, 종목이름, 구매개수, 구매가격\n")
        for datas in buy_list:
            for data in datas:
                savefile.write(str(data))
                savefile.write(", ")
            savefile.write("\n")
        savefile.write("\n\n거래결과")

        # 구매 시작
        for data in buy_list:
            self._kiwoom.buy_jusik(data[0], data[2], data[3])

        # 여기서부터 tracking 이 되어야 함.
        completed = []
        while True:
            get_profit = self._kiwoom.get_profit_percent()
            for i in range(len(get_profit)):
                if get_profit[i][2] > 4 or get_profit[i][2] < -1.5:
                    self._kiwoom.sell_jusik(get_profit[i][0], get_profit[i][3], get_profit[i][1])
                    completed.append(get_profit[i])
                    savefile.write("종목 : " + get_profit[i][0] + "   수익률 : " + str(get_profit[i][2]) + "\n")
            if completed:
                for complete in completed:
                    get_profit.remove(complete)
                completed = []
            if not get_profit:
                break
        savefile.close()
        print("오늘 하루도 무사히 벌거나 잃었습니다.")





