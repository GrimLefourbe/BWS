import ModRead
import UNZIP
import DL
import timeit
import os

os.chdir("C:\\Coding\\Python workshop\\BWS")

urls = ['http://gibberlings3.net/forums/index.php?app=downloads&module=display&section=download&do=confirm_download&id=685',
        'https://github.com/subtledoctor/Scales_of_Balance/archive/master.zip',
        'http://lynxlynx.info/ie/modhub.php?CrevsDaak/7C-Yoshi&pre',
        'http://www.shsforums.net/files/download/1007-adrian']
archives = ["amber-v4.exe", "Scales_of_Balance-master.zip", '7C-Yoshi-latest.zip', 'adrian_v3.1.rar']

if 1:
    inifile='Mod.ini'
    if os.path.exists(inifile):
        t = timeit.timeit("ModRead.LoadMods('{}')".format(inifile), setup="import ModRead", number=10)
        print('Loading {} : {}'.format(inifile, t))
        ModList = ModRead.LoadMods(inifile)
        print('{} mods loaded'.format(len(ModList)))
    else:
        print("{} doesn't exist!".format(inifile))

if 0:
    for filename in archives:
        if os.path.exists(filename):
            os.remove(filename)
if 0:
    for url, filename in zip(urls,archives):
        DL.DownloadFile(url,filename)
if 0:
    for i in archives:
        if os.path.exists(i):
            t = timeit.timeit("UNZIP.Check_Archive('{}')".format(i),setup="import UNZIP", number=10)
            print(i + ':' + str(t))
        else:
            print("{} doesn't exist!".format(i))

print("All is good!")