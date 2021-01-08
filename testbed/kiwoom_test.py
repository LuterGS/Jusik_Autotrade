from multiprocessing import shared_memory
import signal

if __name__ == "__main__":

    name="test1"

    test1 = shared_memory.SharedMemory(name=name, create=True, size=100)

    test2 = shared_memory.SharedMemory(name=name, create=False)
    test2.buf[:20] = b'Hi this is derik bom'
    test2.close()

    print("n")
    print(bytes(test1.buf))

    test1.close()
    test1.unlink()

    signal.raise_signal(signal.SIGKILL)