import constant
import datetime
import time
from threading import Thread

class ThreadwithReturn(Thread):
    def __init__(self, group=None, target=None, name=None, args=(), kwargs={}):
        Thread.__init__(self, group, target, name, args, kwargs)
        self._return = None

    def run(self):
        if self._target is not None:
            self._return = self._target(*self._args, **self._kwargs)

    def join(self, *args):
        Thread.join(self, *args)
        return self._return


def byte_to_original(input_value: bytes, request_num):
    # 바이트로 된 결과값을 일단 디코딩함 (string으로)

    # print("RAW : ", input_value)
    return_value = input_value.replace(b'\x00', b'').decode()
    # print("TRIMMED : ", return_value)
    if return_value == "FAIL":      # 아무 값도 없을 때 재요청
        print("FAILED AT ", str(datetime.datetime.now()))
        return False
    # print(return_value)
    if request_num == 0:        # 잔액요청일 때
        return int(return_value)
    elif request_num == 1:      # 거래량급증요청일 때
        return_value = return_value.split("/")
        return_value.pop()

        for i in range(len(return_value)):
            return_value[i] = return_value[i].split(",")
            return_value[i][2] = int(return_value[i][2])
        # print("retrval : ", return_value)
        return return_value
    elif request_num == 2 or request_num == 3:      # 주식판매 / 주식구매일 때
        # print(return_value)
        return int(return_value)

    elif request_num == 4:      # 수익률요청일 때
        return_value = return_value.split("/")
        return_value.pop()
        # print("RAW : ", return_value)

        for i in range(1, len(return_value)):
            return_value[i] = return_value[i].split(",")
            # print(return_value)
            return_value[i][6] = float(return_value[i][6])
        # print("수익률 리스트 : ", return_value)

        # print(return_value)
        return return_value
    elif request_num == 5:
        if return_value == "RESTART":
            return True
        else:
            return False


def get_only_code(datas):
    """
    KiwoomHandler.get_profit_percent() 의 결과값에서 종목코드만 추려냄
    """
    codes = []
    for data in datas:
        codes.append(data[0])
    return codes


def get_today():
    return datetime.datetime.now().strftime("%Y%m%d")


def get_hm():
    return datetime.datetime.now().strftime("%H%M")


def get_timediff(time_str1, time_str2, reverse=False):
    # 두 시간의 차를 초단위로 변환, 대신 time_str2가 더 나중 시각임
    time1 = datetime.datetime.strptime(time_str1, "%H%M")
    time2 = datetime.datetime.strptime(time_str2, "%H%M")

    if reverse:
        time2 = time2 + datetime.timedelta(days=1)

    return int((time2 - time1).total_seconds())






def array_to_byte(str_list: list):
    result = b''
    for str_ in str_list:
        result += str_.encode()
        result += b'|'          # add seperator
    print(result)
    return result


def check_maintenance():
    """
    키움증권 요청시 점검시간 피하기.
    점검시간일 때, 혹은 점검시간 직전일 떄 True를 반환함. 그러면 키움증권을 
    점검시간 : 월~토 05:05~05:10, 일 04:00~04:30
    :return: True

    """
    cur_time = datetime.datetime.now()
    if cur_time.weekday() != 6:     # 평일일 때
        if cur_time.hour == 5 and cur_time.minute == 4 and cur_time.second > 45: # 점검 코앞이면
            print("현재시간 : ", cur_time, " 이며, 평일 점검시간 (05:05~05:10)이 다가오므로 점검이 끝날 때까지 대기합니다.")
            time.sleep(360)
            print("현재시간 : ", datetime.datetime.now(), " 대기가 끝났습니다. 다시 작업을 재개합니다.")
        else:
            pass
    else:
        if cur_time.hour == 3 and cur_time.minute == 59 and cur_time.second > 50: # 주말 점검이 코앞이면
            print("현재시간 : ", cur_time, " 이며, 주말 점검시간 (04:00~04:30)이 다가오므로 점검이 끝날 때까지 대기합니다.")
            time.sleep(1830)
            print("현재시간 : ", datetime.datetime.now(), " 대기가 끝났습니다. 다시 작업을 재개합니다.")
        else:
            pass

    return True


