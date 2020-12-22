import kiwoom_api
import constant


def get_yield(ticker: str, buy_price: int):
    """
    수익률 계산기
    :param ticker: 수익률을 계산할 종목의 종목코드 (str)
    :param buy_price: 종목을 구매했을 당시의 가격 (int)
    :return: constant.py에 정의된 수익률 퍼센트의 이상이거나 이하면 true를 return, 이외는 error
    """
    expected_percent = constant.profit_percent * 0.01

    while True:
        cur_price = kiwoom_api.get_stock_price(ticker, True)
        profit_percent = cur_price - buy_price
        if abs(profit_percent) >= expected_percent:
            return True


def send_mail():
    """
    수익률 메일 보내기
    :return:
    """

    return 0


def write_list_in_file(file_object, content: list):
    for datas in content:
        for data in datas:
            file_object.write(data)
            file_object.write(", ")
        file_object.write("\n")

    return file_object

