import ModRead
import UNZIP
import DL
import timeit
import os
import subprocess

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

        ModsToTest = [(i[6],i[7]) for i in ModList[150:175]]
    else:
        print("{} doesn't exist!".format(inifile))
        ModsToTest = zip(urls, archives)
else:
    ModsToTest=zip(urls,archives)

if 1:
    for url, filename in ModsToTest:
        if url == "Manual" or filename == "Manual":
            continue
        fln = 'Downloads/' + filename
        if os.path.exists(fln):
            try:
                os.remove(fln)
            except PermissionError:
                print(ModsToTest, url, filename, fln)
                raise

if 1:
    for url, filename in ModsToTest:
        if url == "Manual" or filename == "Manual":
            continue
        DL.DownloadFile(url.rstrip('/'),'Downloads/' + filename)
if 1:
    errors = []
    for url, filename in ModsToTest:
        if url == "Manual" or filename == "Manual":
            continue
        fln = 'Downloads/' + filename
        if os.path.exists(fln):
            try:
                t = timeit.timeit("UNZIP.Check_Archive('{}')".format(fln), setup="import UNZIP", number=1)
                print(filename + ':' + str(t))
            except subprocess.CalledProcessError:
                errors.append((url, filename))
                print("Error with {}".format(filename))
                continue
        else:
            print("{} doesn't exist!".format(filename))

print('Those failed :(')
print(errors)
print("All the rest is good!")