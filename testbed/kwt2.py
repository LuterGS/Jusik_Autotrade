import csv
from multiprocessing import shared_memory

if __name__ == "__main__":
    raw = open("test", "w", encoding='utf8')
    csvs = csv.writer(raw)

    raw.write("햐 좋네\n")
    csvs.writerow(["이걸", "테스트", "해보겠습니"])

    test = shared_memory.SharedMemory(name='1234151_sdf', create=False)