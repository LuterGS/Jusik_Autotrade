import sys
import kiwoom_api
import datetime
from PyQt5.QtWidgets import *
from multiprocessing import Process
import signal
import os
import time

"""
if __name__ == "__main__":

    kospi = open("kospi.txt", "r", encoding="utf8")
    for line in kospi:
        line = line.replace("\t", "").replace("\n", "").split("'")
        print(line)
    # app = QApplication(sys.argv)
    """

def _testfunc1():
    def sig(a, b):
        print("sig", a, b)
    print("ABC_1")
    # sigusr1은 10, 2는 12
    signal.signal(signal.SIGUSR1, sig)

    signal.pause()
    print("sleep for 5 seconds")
    time1 = datetime.datetime.now()
    signal.sigtimedwait([signal.SIGUSR1], 7.6)
    time2 = datetime.datetime.now() - time1
    print(time2)
    print("timed_wait is true?")

def mtest():
    process = Process(target=_testfunc1)
    process.start()
    print(process.pid)
    time.sleep(1)

    os.kill(process.pid, signal.SIGUSR1)
    time.sleep(1)
    print(process.is_alive(), "\n")
    process.join()


if __name__ == "__main__":
    for i in range(3):
        mtest()
    time.sleep(10)

