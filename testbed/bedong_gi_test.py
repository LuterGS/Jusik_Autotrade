import signal
import os
import random
import time
from multiprocessing import Process, Pipe, Manager, Queue, Lock, shared_memory
import threading
import constant

"""
비동기 큐 처리
"""


class A:
    def __init__(self):
        self.que = Queue()
        self.outque = Queue()
        self.manager = Manager()

    def subprocess(self, str):
        # Process가 실행할 함수
        print("this is subprocess : ", str)
        result = self.manager.list()
        result.append(False)
        self.que.put([str, result])
        while not result[0]:
            if result[0]:
                print(result[1])
                break

    def get_que(self):
        while True:
            time.sleep(1)
            data, result = self.que.get()
            result[0] = True
            result.append(data + "complete!")



class test2:
    def __init__(self):
        self._manager = Manager()
        self._list_ = self._manager.list()
        self._locker = self._manager.Lock()
        self._que = self._manager.Queue(maxsize=1000)
        self._count = self._manager.Value('i', 0)
        for i in range(1000):
            self._list_.append(False)

    def work(self, str):
        self._locker.acquire()
        self._count.value += 1
        num = self._count.value
        self._locker.release()

        self._que.put([str, self._count])
        while self._list_[num] == False:
            pass

        self._locker.acquire()
        ret = self._list_[num]
        self._list_[num] = False
        self._locker.release()
        return ret

    def b(self):
        while True:
            time.sleep(1)
            val, store_point = self._que.get()
            self._list_[store_point] = val + "  complete!"


def signal_handler(signum, frame):
    pass


def put_queue(queue, str):
    # signal handler 등록
    signal.signal(signal.SIGILL, signal_handler)

    res = shared_memory.SharedMemory(name=str, create=True, size=100)
    queue.put([str, threading.get_ident()])
    print(str)
    buffer = res.buf
    os.system("pause")
    """while True:
        # print("Buffer :", bytes(buffer[:10]))
        if bytes(buffer[:9] == b'Complete!'):
            break"""
    print("num ", str, " is received!")
    res.close()
    res.unlink()


def get_queue(que):
    while True:
        time.sleep(1)
        value, signaler = que.get()
        print("Value :", value)
        saver = shared_memory.SharedMemory(name=value, create=False, size=100)
        buf = saver.buf
        buf[:9] = b'Complete!'
        # print("Writed :", bytes(buf[:10]))
        signal.alarm(signaler, signal.SIGILL)
        saver.close()



if __name__ == "__main__":
    print(dir(signal))
    lock = Lock()
    mq = Queue()
    pr = Process(target=get_queue, args=(mq,))
    pr.start()
    for i in range(100):
        subpr = Process(target=put_queue, args=(mq, str(i)))
        subpr.start()
        subpr.join()
        time.sleep(0.2)
    print("end for main")
    time.sleep(10000)

