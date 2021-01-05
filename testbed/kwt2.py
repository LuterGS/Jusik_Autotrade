import else_func
import datetime

if __name__ == "__main__":
    test2 = datetime.datetime.strptime("2355", "%H%M")
    test1 = datetime.datetime.strptime("0355", "%H%M") + datetime.timedelta(days=1)

    print(int((test1 -test2).total_seconds()))
