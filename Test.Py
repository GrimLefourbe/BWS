import ModRead
import UNZIP
import DL
import timeit
import os
import subprocess

os.chdir("C:\\Coding\\Python workshop\\BWS")

DownloadsLocation = "E:\\Coding\\BWS-Downloads"
LogsLocation = "C:\\Coding\\Python workshop\\BWS\\Logs"


inifile='ModBG2EE.ini'
if os.path.exists(inifile):
    t = timeit.timeit("ModRead.LoadMods('{}')".format(inifile), setup="import ModRead", number=10)
    print('Loading {} : {}'.format(inifile, t))
    ModDict = ModRead.LoadMods(inifile)
    print('{} mods loaded'.format(len(ModDict)))

    ModsToTest = [(i['Down'],i['Save']) for i in ModDict]
else:
    print("{} doesn't exist!".format(inifile))
    ModsToTest=[]

if 1:
    for url, filename in ModsToTest:
        if url == "Manual" or filename == "Manual":
            continue
        filename = DownloadsLocation + '\\' + filename
        if os.path.exists(filename):
            try:
                os.remove(filename)
            except PermissionError:
                print(ModsToTest, url, filename, filename)
                raise

dlf = open(LogsLocation + '\\' + 'dlfailed.txt', 'a')
if 1:
    for url, filename in ModsToTest:
        if url == "Manual" or filename == "Manual":
            continue
        try:
            DL.DownloadFile(url.rstrip('/'),DownloadsLocation + '\\' + filename)
        except:
            print((url,filename), file=dlf)
dlf.close()

exterrorsf = open(LogsLocation +'\\' + 'extfailed.txt', 'a')
if 1:
    for url, filename in ModsToTest:
        if url == "Manual" or filename == "Manual":
            continue
        cwd = os.getcwd()
        os.chdir(DownloadsLocation)
        if os.path.exists(filename):
            try:
                UNZIP.Check_Archive(filename)
                print("{} checked".format(filename))

                t = timeit.timeit("UNZIP.Check_Archive('{}')".format(filename), setup="import UNZIP", number=1)
                print(filename + ':' + str(t))

            except subprocess.CalledProcessError:
                print((url, filename), file=exterrorsf)
                print("Error with {}".format(filename))
                continue
            finally:
                os.chdir(cwd)
        else:
            print("{} doesn't exist!".format(filename))
exterrorsf.close()
print('Those failed :(')
print("All the rest is good!")