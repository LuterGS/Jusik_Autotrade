
if __name__ == "__main__":
    str1 = "werwer, werwerwerwer, erere"
    str2 = "werwerwer"

    print(str2.split(","))


    p1 = 900000
    p2 = 7850

    print(p1/p2, int(p1/p2))

    lists = [
        [1, 1000, 2234, "한글"],
        [2, 23423, 1241, "한글2"],
        [3, 2341, 1152, "한글3"]
    ]

    print(lists.index([1, 1000, 2234, "한글"]))