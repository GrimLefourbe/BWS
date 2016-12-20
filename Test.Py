#import ModInfo
#import Extract
#import Net
#import timeit
#import os
#import subprocess
#import traceback
#
#os.chdir("C:\\Coding\\Python workshop\\BWS")
#
#DownloadsLocation = "E:\\Coding\\BWS-Downloads"
#LogsLocation = "C:\\Coding\\Python workshop\\BWS\\Logs"
#
#
#inifile='ModBG2EE.ini'
#if os.path.exists(inifile):
#    t = timeit.timeit("ModInfo.ModList('{}')".format(inifile), setup="import ModInfo", number=10)
#    print('Loading {} : {}'.format(inifile, t))
#    ModDict = ModInfo.ModList(inifile)
#    print('{} mods loaded'.format(len(ModDict)))
#
#    ModsToTest = [(i['Down'],i['Save']) for i in ModDict]
#else:
#    print("{} doesn't exist!".format(inifile))
#    ModsToTest=[]
#
#if 1:
#    for url, filename in ModsToTest:
#        if url == "Manual" or filename == "Manual":
#            continue
#        filename = DownloadsLocation + '\\' + filename
#        if os.path.exists(filename):
#            try:
#                os.remove(filename)
#            except PermissionError:
#                print(ModsToTest, url, filename, filename)
#                raise
#
#dlf = open(LogsLocation + '\\' + 'dlfailed.txt', 'a')
#if 1:
#    for url, filename in ModsToTest:
#        if url == "Manual" or filename == "Manual":
#            continue
#        try:
#            Net.DownloadFile(url.rstrip('/'), DownloadsLocation + '\\' + filename)
#        except:
#            traceback.print_exc(file=dlf)
#dlf.close()
#
#exterrorsf = open(LogsLocation +'\\' + 'extfailed.txt', 'a')
#if 1:
#    cwd = os.getcwd()
#    os.chdir(DownloadsLocation)
#    ModsData=[]
#    for url, filename in ModsToTest:
#        if url == "Manual" or filename == "Manual":
#            continue
#        if os.path.exists(filename):
#            try:
#                ModsData.append((filename, Extract.Check_Archive(filename, exc_file=exterrorsf)))
#                print("{} checked".format(filename))
#
#                t = timeit.timeit("Extract.Check_Archive('{}')".format(filename), setup="import Extract", number=1)
#                print(filename + ':' + str(t))
#
#            except subprocess.CalledProcessError:
#                traceback.print_exc(file=exterrorsf)
#                continue
#
#        else:
#            print("{} doesn't exist!".format(filename))
#    os.chdir(cwd)
#exterrorsf.close()
#print("Work is done!")

import BWS

if __name__ == '__main__':
    T=BWS.BWS(dldir='E:\\Coding\\BWS-Downloads', gamedir='E:\\Coding\\BWS Game', start=0, end=-1)
    # i,j=0,250
    # T.LoadModsData('ModBG2EE.ini')
    # m=T.DownloadMods(T.ModsData[i:j])
    # n=T.ExtMods(T.ModsData[i:j], mode = 1)
    #import Extract
    #t1=rb'(?:\S+\\)?[sS][eE][tT][uU][pP]-(?P<tpname>.*?)\.tp2'
    #t2=rb'((?:\S*?\\)*?)(%(tpname)s)(?=\r?$)(?m)'
    #f=open('tmp.txt','rb')
    #j=f.read()
    #f.close()
    #m=Extract.RegexBytesSeq([t1,t2],j)