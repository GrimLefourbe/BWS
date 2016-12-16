import ModInfo
import Extract
import Net
import os
import sys
import time
import traceback
import logging
import subprocess

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
    def __init__(self, dir=None, dldir=None, logsdir=None):
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
        os.makedirs(self.dldir, exist_ok=True)
        os.makedirs(self.logsdir, exist_ok=True)
        loginit(self.logsdir)

        self.ModsData = []


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

    def DownloadMods(self, ToDl, dldir=None):
        '''
        ModsToDl should be a list of dicts with entries for Save, Down and Size
        Size can be None, it will then be ignored
        :param dldir:
        :param ToDl:
        :return:
        '''
        if dldir is None:
            dldir = self.dldir

        results = []
        for data in ToDl:
            url, filename, esize = data['Down'], data['Save'], data['Size']
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
            if size != esize:
                logging.warning('Incorrect download size when downloading {} from {},'
                                ' found size of {} and expected {}'.format(filename, url, size, esize))
                results.append(2)
                continue

            logging.info('Download of {} from {} went as expected'.format(filename, url))
            results.append(0)

        logging.info('Download of {} files finished'.format(len(ToDl)))
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

        cwd=os.getcwd()
        os.chdir(dldir)

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
                try:
                    results.append(Extract.Check_Archive(filepath,basedir=self.dir))
                except subprocess.CalledProcessError:
                    logging.exception('Error in file {}'.format(filepath))
                    results.append(0)
                    continue

            else:
                logging.warning("{} doesn't exist!".format(filepath))
                results.append(2)
                continue
            logging.info("{} : {} is fine".format(i['ID'], filepath))
        os.chdir(cwd)
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



