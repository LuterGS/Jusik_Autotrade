import sys
import kiwoom_api
from PyQt5.QtWidgets import *

if __name__ == "__main__":

    kospi = open("kospi.txt", "r", encoding="utf8")
    for line in kospi:
        line = line.replace("\t", "").replace("\n", "").split("'")
        print(line)
    # app = QApplication(sys.argv)