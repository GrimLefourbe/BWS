import ModInfo
import Extract
import Net
import os
import sys
import time
import re
import logging
import subprocess

#Solaufein different folder name
#Saradas_magic BG1.1 like Quayle
#Quayle_redonne pas de dossier sans \
#PaintBG
#NPCFlirt exe inside zip
#LongerRoad different folder name
#LaValygar comme Quayle
#Keto comme NPCFlirt
#item upgrade comme Solaufein
#imp asylum comme Quayle
#questpack comme Solaufein
#Banter packs comme Quayle
#Angelo comme Quayle (~)

def loginit(logdir):
    '''
    Taken from Python Logging Cookbook
    :param logdir:
    :return:
    '''
    logging.basicConfig(level=logging.DEBUG,
                        format='%(asctime)s %(name)-12s %(levelname)-8s %(message)s',
                        datefmt='%m-%d %H:%M',
                        filename=logdir + '\\' + time.strftime('BWS_%Y_%m_%d_%H_%M.log'),
                        filemode='w')
    console = logging.StreamHandler()
    console.setLevel(logging.DEBUG)
    formatter = logging.Formatter('%(name)-12s: %(levelname)-8s %(message)s')
    console.setFormatter(formatter)
    logging.getLogger('').addHandler(console)

class BWS:
    def __init__(self, dir=None, dldir=None, logsdir=None, no_gui=True, config=None, start=0, end=-1):
        if dir is None:
            self.dir = sys.path[0]
        else:
            self.dir = dir
        os.chdir(self.dir)
        if dldir is None:
            self.dldir = self.dir + '\\Downloads'
        else:
            self.dldir = dldir
        if logsdir is None:
            self.logsdir = self.dir + '\\Logs'
        else:
            self.logsdir = logsdir
        if config is None:
            self.config = self.dir + r'\Config'
        else:
            self.config = logsdir
        os.makedirs(self.config, exist_ok=True)
        os.makedirs(self.dldir, exist_ok=True)
        os.makedirs(self.logsdir, exist_ok=True)
        loginit(self.logsdir)
        logging.info('basedir is {}, dldir is {}, logsdir is {}'.format(self.dir,self.dldir, self.logsdir))
        self.ModsData = []

        if no_gui:
            inifile=self.config + r'\BG2EE.ini'
            self.No_GUI_loop(inifile, start=start, end=end)
    def LoadModsData(self, inifile=None):
        if inifile is None:
            inifile = self.dir + '\\Mod.ini'

        if os.path.isfile(inifile):

            logging.info('Loading {}'.format(inifile))
            ModsData=ModInfo.ModList(inifile)
            logging.info('{} mods loaded'.format(len(ModsData)))

            for i in ModsData:
                logging.info('Converting {}'.format(i['ID']))
                if i['Size'] not in (None, 'Manual'):
                    i['Size'] = int(i['Size'])
                else:
                    logging.warning('Could not convert {} to int'.format(i['Size']))


            self.ModsData += ModsData
        else:
            logging.warning("{} is not a file".format(inifile))

    def DeleteMods(self, ToDel, dldir=None, logfile=None):
        '''
        ModsToDel should be the list of index of the mods to delete from the download directory
        :param ToDel:
        :return:
        '''
        if dldir is None:
            dldir = self.dldir

        for i in ToDel:
            filename = dldir + '\\' + i['Save']
            if os.path.exists(filename):
                logging.info('Deleting file {}'.format(filename))
                try:
                    os.remove(filename)
                except PermissionError:
                    logging.exception('Error when trying to remove file {}'.format(filename))
                    raise
            else:
                logging.info('Could not find the file {}'.format(filename))

    def DownloadMods(self, ToDl, dldir=None, ModsData=None):
        '''
        ModsToDl should be a list of dicts with entries for Save, Down and Size
        Size can be None, it will then be ignored
        :param dldir:
        :param ToDl:
        :return:
        '''
        if ModsData is None:
            ModsData=self.ModsData
        if dldir is None:
            dldir = self.dldir

        results = []
        for ind in ToDl:
            data=ModsData[ind]
            url, filename, expsize = data['Down'], data['Save'], data['Size']
            if url == "Manual" or filename == "Manual":
                logging.info('Manual download encountered')
                results.append(-1)
                continue

            logging.info('Starting download of {} from {}'.format(filename, url))
            code, size = Net.DownloadFile(url.rstrip('/'), dldir +'\\' + filename)

            if code != 200:
                logging.warning('Received {} code when downloading file {} from {}'.format(code, filename, url))

                results.append(code)
                continue

            #size = os.path.getsize(dldir+'\\' + filename)
            if size != expsize:
                logging.warning('Incorrect download size when downloading {} from {},'
                                ' found size of {} and expected {}'.format(filename, url, size, expsize))
                results.append(2)
                continue

            logging.info('Download of {} from {} went as expected'.format(filename, url))
            results.append(1)

        logging.info('Download of {} files finished'.format(len(ToDl)))
        return results

    def TestMod(self, filepath, modname, basedir=None):
        '''
        Returns 0 if the test didn't complete
        Returns 3 if the test found inconsistencies
        else returns the a dict with containing the tp2 name(tpname) and the path to the main folder(foldpath) of the mod
        :param basedir:
        :return:
        '''
        if basedir is None:
            basedir = self.dir

        #regexlist = [rb'(?:[^\r\n\t\f\v \\]+\\)*(?:[sS][eE][tT][uU][pP]-)?(?P<tpname>[^\r\n\t\f\v \\]*?)\.[Tt][Pp]2',
        #             rb'((?:[^\r\n\t\f\v \\]+?\\)*?)(%(tpname)s)(?=\r?$)(?m)']
        if isinstance(modname,str):
            modname=modname.encode('ascii')
        regexlist = [rb'((?:[^\r\n\t\f\v \\]+?\\)*?)(%s)(?:\\backup\r?$)?(?=\r?$)(?mi)' % modname]

        res = Extract.Check_Archive(filepath,basedir=self.dir, regex=regexlist)

        logging.info('Check_Archive returned {}'.format(res))
        if isinstance(res, int):
            return res
        else:
            return res

    def ExtractMod(self, filepath, basedir=None, targetdir=None):
        '''
        Returns 0 if the extraction didn't complete
        Returns 1 if the extraction went well
        Returns 3 if the extracting went bad

        :param filepath:
        :param basedir:
        :param targetdir:
        :return:
        '''

        if basedir is None:
            basedir = self.dir

        res = Extract.Extract_Archive(filepath, targetdir=targetdir, basedir=basedir)

        return res

    def ExtMods(self, ToExt, mode=0, dldir = None, targetdir=None, basedir=None, ModsData=None):
        '''
        if mode is 1, tests integrity of archives and returns list of tp2 names as well as path to main folder
        if mode is 0, extracts the archives to targetdir
        :param ToExt:
        :param dldir:
        :param targetdir:
        :param mode:
        :return:
        '''
        if ModsData is None:
            ModsData = self.ModsData

        txtdict = {0:['Extracting'], 1:['Testing']}
        if dldir is None:
            dldir = self.dldir
        if basedir is None:
            basedir = self.dir
        if mode == 0 and targetdir is None:
            targetdir = self.dir + '\Extracted'

        results = []
        for ind in ToExt:
            data = ModsData[ind]
            logging.info('{} {} : {}'.format(txtdict[mode][0], data['ID'],data['Save']))
            filename = data['Save']

            if filename=="Manual":
                results.append(-1)
                logging.warning('Skipping {} : {}'.format(data['ID'], filename))
                continue
            filepath = dldir +'\\' + filename
            if os.path.exists(filepath):
                if mode == 0:
                    res = self.ExtractMod(self, filepath, targetdir=targetdir, basedir=basedir)
                elif mode == 1:
                    res = self.TestMod(filepath, modname=data['ID'], basedir=basedir)
                else:
                    logging.ERROR('Unexpected argument for mode')
                    return 0
                results.append(res)
            else:
                logging.warning("{} doesn't exist!".format(filepath))
                results.append(2)
                continue
            logging.info('{} went fine for {} : {}'.format(txtdict[mode][0], data['ID'], filename))
        assert len(results) == len(ToExt)
        return results

    def TestMods(self, ToTest, dldir=None):
        '''
        -1:Manual
        0:CalledProcessError
        1:Success
        2:File doesn't exist
        3:Test found errors
        :param ToTest:
        :param dldir:
        :return:
        '''
        if dldir is None:
            dldir = self.dldir

        results = []
        for i in ToTest:
            logging.info('Testing {} : {}'.format(i['ID'],i['Save']))
            filename = i['Save']
            filepath = dldir + '\\' + filename
            if filename=="Manual":
                results.append(-1)
                logging.warning('Skipping {} : {}'.format(i['ID'],filepath))
                continue

            if os.path.exists(filepath):
                regexlist = [rb'(?:[^\r\n\t\f\v \\]+\\)*(?:[sS][eE][tT][uU][pP]-)?(?P<tpname>[^\r\n\t\f\v \\]*?)\.[Tt][Pp]2',
                             rb'((?:[^\r\n\t\f\v \\]+?\\)*?)(%(tpname)s)(?=\r?$)(?m)']

                res=Extract.Check_Archive(filepath,basedir=self.dir, regex=regexlist)

                if isinstance(res, int):
                    if res==0:
                        results.append(0) #Test failed
                    elif res==3:
                        results.append(3) #Test found inconsistency
                else:
                    results.append({'tpname':res[0][0],'foldpath':res[1][0]})
            else:
                logging.warning("{} doesn't exist!".format(filepath))
                results.append(2)
                continue
            logging.info("{} : {} is fine".format(i['ID'], filepath))

        assert len(results)==len(ToTest)
        return results

    def ExtractMods(self, ToExt, dldir=None, targetdir=None):
        '''
        -1:Manual
        0:CalledProcessError
        1:Success
        2:File doesn't exist
        3:Test found errors
        :param ToExt:
        :param dldir:
        :return:
        '''
        if dldir is None:
            dldir = self.dldir
        if targetdir is None:
            targetdir = self.dir + '\Extracted'

        results = []
        for i in ToExt:
            logging.info('Extracting {} : {}'.format(i['ID'],i['Save']))
            filename = i['Save']
            filepath = dldir + '\\' + filename
            if filename == "Manual":
                results.append(-1)
                logging.warning('Skipping {} : {}'.format(i['ID'],filepath))
                continue

            if os.path.exists(filepath):
                try:
                    results.append(Extract.Extract_Archive(filepath, targetdir=targetdir, basedir=self.dir))
                except subprocess.CalledProcessError:
                    logging.exception('Error in file {}'.format(filepath))
                    results.append(0)
                    continue

            else:
                logging.warning("{} doesn't exist!".format(filepath))
                results.append(2)
                continue
            logging.info("{} : {} is fine".format(i['ID'], filepath))

        assert len(results)==len(ToExt)
        return results

    def No_GUI_loop(self, file, start=0, end=-1):
        self.LoadModsData(file)
        WorkingInds=range(start, end if end!=-1 else len(self.ModsData))
        m=self.DownloadMods(WorkingInds)
        NewInds=[i for i,v in zip(WorkingInds,m) if v==1]
        n=self.ExtMods(NewInds, mode=1)

        return m,n


