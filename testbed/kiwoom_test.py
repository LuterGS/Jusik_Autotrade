import signal

def a_(a, b):
    print("a is called")





if __name__ == "_main__":

    signal.signal(signal.SIGUSR2, a_)