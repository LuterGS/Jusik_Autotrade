from multiprocessing import shared_memory


if __name__ == "__main__":

    test1 = shared_memory.SharedMemory(name="test1", create=True, size=100)

    val = bytes(test1.buf).replace(b'\x00', b'').decode()
    print(val)

    if val == "":
        print("NONE!")