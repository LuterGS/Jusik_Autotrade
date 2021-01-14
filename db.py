import datetime

import redis

import constant

class DB:

    def __init__(self):
        get_db_val = constant.GET_DB_VALUE()
        self._username = "LuterGS"
        self._ip = get_db_val["ip"]
        self._port = int(get_db_val["port"])
        self._password = get_db_val["password"]
        self._db = redis.StrictRedis(host=self._ip, port=self._port, db=0, password=self._password)

        # define key name
        self._not_buy_list = "not_buy_list"

        # define sell, buy type
        self._sell_type = {
            "type": "sell",
            "code": "code",
            "name": "name",
            "amount": "amount",
            "price": "price",
            "total_price": "total_price",
            "profit_percent": "profit_percent",
            "profit_total_price": "profit_total_price"
        }
        self._buy_type = {
            "type": "buy",
            "code": "code",
            "name": "name",
            "amount": "amount",
            "price": "price",
            "total_price": "total_price"
        }

    def _add_user_order_reference(self, log_time: datetime.datetime):
        str_time = log_time.strftime("%Y%m%d%H%M%S%f")
        self._db.rpush(self._username, str_time)
        return str_time

    def add_sell_data(self, cur_time: datetime.datetime, code, name, amount, price, total_price, profit_percent, profit_total_price):
        str_time = self._add_user_order_reference(cur_time)
        self._sell_type["code"] = code
        self._sell_type["name"] = name
        self._sell_type["amount"] = amount
        self._sell_type["price"] = price
        self._sell_type["total_price"] = total_price
        self._sell_type["profit_percent"] = profit_percent
        self._sell_type["profit_total_price"] = profit_total_price
        self._db.hmset(self._username + "_" + str_time, self._sell_type)

    def add_buy_data(self, cur_time: datetime.datetime, code, name, amount, price, total_price):
        str_time = self._add_user_order_reference(cur_time)
        self._buy_type["code"] = code
        self._buy_type["name"] = name
        self._buy_type["amount"] = amount
        self._buy_type["price"] = price
        self._buy_type["total_price"] = total_price
        self._db.hmset(self._username + "_" + str_time, self._buy_type)

    def get_not_buy_list(self):
        return self._db.hgetall(self._not_buy_list)

    def add_not_buy_list(self, name):
        val = self._db.hget(self._not_buy_list, name)
        if val is None:
            self._db.hset(self._not_buy_list, name, 1)
        elif val == b'1':
            self._db.hset(self._not_buy_list, name, 2)
            print("종목 ", name, " 은 총 두 번의 손실을 입었으므로, 오늘은 더 이상 구매하지 않습니다.")


if __name__ == "__main__":
    test = DB()
    print(test.get_not_buy_list())
