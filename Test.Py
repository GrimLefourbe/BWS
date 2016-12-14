import UNZIP
import DL
import timeit

archives = ["amber-v4.exe", "Scales_of_Balance-master.zip"]

for i in archives:
    t = timeit.timeit("UNZIP.Check_Archive('{}')".format(i),setup="import UNZIP", number=10)
    print(i + ':' + str(t))
