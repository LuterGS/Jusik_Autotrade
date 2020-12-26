import sys
import kiwoom_api
from PyQt5.QtCore import QEventLoop
from PyQt5.QtWidgets import *
from PyQt5.QAxContainer import *
import time


if __name__ == "__main__":
    app = QApplication(sys.argv)
    print("Now Entering Kiwoom")
    test = kiwoom_api.TextKiwoom()
    print("successfully login to kiwoom")

    # Account get test
    # account_no = test.get_account_num()
    # print(account_no)
    # res = test.get_balance(account_no)
    # print(res)
    # print("Twice!")
    # res = test.get_balance(account_no)
    # print(res)

    # Single getdata test
    # res2 = test.get_min_jusik_data("000020")
    # print(res2)

    test.get_kospi_data()
