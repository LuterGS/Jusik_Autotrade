

if __name__ == "__main__":
    test = {"test1":"a", "test2":"b"}

    for data in test:
        print(data)
        print(test[data])

    data = [1, 2, 3, 4, 5, 6, 7]

    for i in range(len(data)):
        if data[i] == 3:
            break
    print("i :", i)
    del data[i]
    print(data)