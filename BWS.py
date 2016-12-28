import ModInfo
import Extract
import Utils
import Net
import os
import sys
import time
import re
import logging
import subprocess
import shutil
import stat
import tempfile


#NTotSC 2 in 1??


def loginit(logdir):
    '''
    Taken from Python Logging Cookbook
    :param logdir:
    :return:
    '''
    logging.basicConfig(level=logging.DEBUG,
                        format='%(asctime)s %(name)-12s %(levelname)-8s %(message)s',
                        datefmt='%m-%d %H:%M',
                        filename=logdir + '/' + time.strftime('BWS_%Y_%m_%d_%H_%M.log'),
                        filemode='w')
    console = logging.StreamHandler()
    console.setLevel(logging.DEBUG)
    formatter = logging.Formatter('%(name)-12s: %(levelname)-8s %(message)s')
    console.setFormatter(formatter)
    logging.getLogger('').addHandler(console)

class BWS:
    def __init__(self, dir=None, dldir=None, logsdir=None, no_gui=True, configdir=None, tmpdir=None, gamedir=None,
                 start=0, end=-1):
        if dir is None:
            self.dir = sys.path[0].replace('\\', '/')
        else:
            self.dir = dir
        os.chdir(self.dir)
        if dldir is None:
            self.dldir = self.dir + '/Downloads'
        else:
            self.dldir = dldir
        if logsdir is None:
            self.logsdir = self.dir + '/Logs'
        else:
            self.logsdir = logsdir
        if configdir is None:
            self.config = self.dir + '/Config'
        else:
            self.config = logsdir
        if tmpdir is None:
            self.tmpdir = self.dir + '/Temp'
        else:
            self.tmpdir = tmpdir
        if gamedir is None:
            self.gamedir = self.dir + '/Game'
        else:
            self.gamedir = gamedir
        os.makedirs(self.tmpdir, exist_ok=True)
        os.makedirs(self.config, exist_ok=True)
        os.makedirs(self.dldir, exist_ok=True)
        os.makedirs(self.logsdir, exist_ok=True)
        os.makedirs(self.gamedir, exist_ok=True)
        loginit(self.logsdir)
        logging.info('basedir is {}, dldir is {}, logsdir is {}'.format(self.dir,self.dldir, self.logsdir))
        self.ModsData = []

        if no_gui:
            inifile = self.config + r'/BG2EE.ini'
            self.No_GUI_loop(inifile, start=start, end=end)
    def LoadModsData(self, inifile=None):
        if inifile is None:
            inifile = self.dir + '/Mod.ini'

        if os.path.isfile(inifile):

            logging.info('Loading {}'.format(inifile))
            ModsData=ModInfo.ModList(inifile)
            logging.info('{} mods loaded'.format(len(ModsData)))

            for i in ModsData:
                logging.info('Converting {}'.format(i['ID']))
                if 'Size' in i:
                    try:
                        i['Size'] = int(i['Size'])
                    except ValueError:
                        logging.warning('Could not convert {} to int'.format(i['Size']))
                else:
                    logging.warning('No size specified')
            self.ModsData += ModsData
            return self.ModsData
        else:
            logging.warning("{} is not a file".format(inifile))

    def LoadModsComponents(self, inifile=None, ModsData=None):
        if inifile is None:
            inifile = self.config + '/WeiDU-EN.ini'
        if ModsData is None:
            ModsData = self.ModsData
        if os.path.isfile(inifile):
            logging.info('Loading components from {}'.format(inifile))
            ModInfo.ModComp(inifile, ModsData=ModsData)
            logging.info('Done loading components')
        else:
            logging.warning("{} is not a file".format(inifile))
        return ModsData

    def DeleteMods(self, ToDel, dldir=None):
        '''
        ModsToDel should be the list of index of the mods to delete from the download directory
        :param ToDel:
        :return:
        '''
        if dldir is None:
            dldir = self.dldir

        for i in ToDel:
            filename = dldir + '/' + i['Save']
            if os.path.exists(filename):
                logging.info('Deleting file {}'.format(filename))
                try:
                    os.remove(filename)
                except PermissionError:
                    logging.exception('Error when trying to remove file {}'.format(filename))
                    raise
            else:
                logging.info('Could not find the file {}'.format(filename))

    def TestPresentMods(self, ToTest=None, ModsData=None, dldir=None):
        if ModsData is None:
            ModsData = self.ModsData
        if dldir is None:
            dldir = self.dldir
        if ToTest is None:
            ToTest = range(len(ModsData))
        results = []
        logging.info("Testing present mods in {}".format(dldir))
        for ind in ToTest:
            filepath = dldir + '/' + ModsData[ind]['Save']
            logging.info("Looking for file {}".format(filepath))
            if os.path.isfile(filepath):
                if os.path.getsize(filepath)==ModsData[ind]['Size']:
                    results.append(1)
                else:
                    results.append(2)
            else:
                results.append(0)

        return results

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
            code, size = Net.DownloadFile(url.rstrip('/'), dldir + '/' + filename)

            if code != 200:
                logging.warning('Received {} code when downloading file {} from {}'.format(code, filename, url))

                results.append(code)
                continue

            #size = os.path.getsize(dldir+'/' + filename)
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

        #regexlist = [rb'(?:[^\r\n\t\f\v /]+/)*(?:[sS][eE][tT][uU][pP]-)?(?P<tpname>[^\r\n\t\f\v /]*?)\.[Tt][Pp]2',
        #             rb'((?:[^\r\n\t\f\v /]+?/)*?)(%(tpname)s)(?=\r?$)(?m)']
        if isinstance(modname,str):
            modname=modname.encode('ascii')
        regexlist = [rb'((?:[^\r\n\t\f\v /]+?/)*?)(%s)(?:/backup\r?$)?(?=\r?$)(?mi)' % modname]

        res = Extract.Check_Archive(filepath,basedir=self.dir, regex=regexlist)

        logging.info('Check_Archive returned {}'.format(res))
        if isinstance(res, int):
            return res
        else:
            return res

    def TestMods(self, ToExt, dldir = None, basedir=None, ModsData=None):
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


        results = []
        for ind in ToExt:
            data = ModsData[ind]
            logging.info('{} {} : {}'.format(txtdict[1][0], data['ID'],data['Save']))
            filename = data['Save']

            if filename=="Manual":
                results.append(-1)
                logging.warning('Skipping {} : {}'.format(data['ID'], filename))
                continue
            filepath = dldir +'/' + filename
            if os.path.exists(filepath):
                res = self.TestMod(filepath, modname=data['ID'], basedir=basedir)
                results.append(res)
            else:
                logging.warning("{} doesn't exist!".format(filepath))
                results.append(2)
                continue
            logging.info('{} went fine for {} : {}'.format(txtdict[1][0], data['ID'], filename))
        assert len(results) == len(ToExt)
        return results

    #for very special cases
    DataPDict ={}
    #for when there's a second archive inside the first
    SecArcPat = re.compile(r'^(/?(?:[^\r\n\t\f\v/]+?/)*?(?:[^\r\n\t\f\v/]+?\.(?:exe|zip|rar|7z)))$(?im)')

    def PrepMod(self, filepath, moddict, targetdir=None, tmpdir=None, basedir=None):
        '''

        :param filepath:
        :param tmpdir:
        :param basedir:
        :return:
        '''

        if basedir is None:
            basedir = self.dir
        if tmpdir is None:
            tmpdir=self.tmpdir

        tmpdirobj = tempfile.TemporaryDirectory(prefix=tmpdir + '/')
        tmpdir = tmpdirobj.name

        if targetdir is None:
            targetdir = self.gamedir

        logging.info('Starting preparation of {} located at {}'.format(moddict['ID'],filepath))
        logging.info('tmp dir is {}, target dir is {}, basedir is {}'.format(tmpdir, targetdir, basedir))

        if len(os.listdir(tmpdir)) != 0:
            logging.error("Something went wrong, tmpdir isn't empty, skipping {}".format(moddict['ID']))
            return 0

        res = Extract.Extract_Archive(filepath, targetdir=tmpdir, basedir=basedir)
        if res != 1:
            logging.warning("Something went wrong during extraction, skipping {}".format(moddict['ID']))
            return 2

        ID = moddict['ID']
        files = Utils.listsubdir(tmpdir)

        tp2Pat = re.compile(r"(^/?(?:[^\r\n\t\f\v/]+?/)*?(?:setup-)?{}.tp2)$(?mi)".format(ID))
        logging.info('tp2pat is {}'.format(tp2Pat))
        s = '\n'.join(files)
        tp2match = tp2Pat.search(s)

        if not tp2match:
            logging.warning("Could not find tp2 on first try")
            Arc2match = BWS.SecArcPat.search(s)
            if Arc2match:
                res = Extract.Extract_Archive(Arc2match.group(1),targetdir=tmpdir+'/2', basedir=basedir)
                if res != 1:
                    logging.warning("unsuccessful extraction of {}, skipping {]".format(Arc2match.group(1), ID))
                    Utils.cleanupdir(tmpdir)
                    return 0
                files = Utils.listsubdir(tmpdir+'/2')
                s = '\n'.join(files)
                tp2match = tp2Pat.search(s)
                if not tp2match:
                    logging.warning("Could not find tp2 on 2nd try, skipping {}".format(ID))
                    Utils.cleanupdir(tmpdir)
                    return 0
            else:
                logging.warning("Could not find secondary archive, skipping {}".format(ID))
                Utils.cleanupdir(tmpdir)
                return 0

        tp2path = tp2match.group(1)
        logging.info("Found tp2 path {} : {}".format(ID, tp2path))

        if tp2path.split('/')[-2].lower() == ID.lower():
            datapath = tp2path.rsplit('/', 1)[0]
        else:
            dataPat = re.compile(r"(^/?(?:[^\r\n\t\f\v/]+?/)*?(?:(?<=/)|(?<=^))({}))(?(2)|backup)$(?mi)".format(ID))
            logging.info("dataPat is {}".format(dataPat))
            datamatch = dataPat.search(s)
            if datamatch:
                logging.debug("match is {}".format(datamatch))
                datapath = datamatch.group(1)
            else:
                logging.info("Did not match, now looking through tp2")
                with open(tp2path, 'rb') as f:
                    tmps=f.readline().lower()
                    while b'backup' not in tmps and tmps != b'':
                        tmps=f.readline().lower()

                logging.debug('tmps is {}'.format(tmps))
                if tmps != b'':
                    tmps = tmps.replace(b'\\', b'/')
                    tmps = tmps.split(b'~')[1].decode()
                    logging.debug('tmps is {}'.format(tmps))
                    tmps = tmps.rsplit('/', 1)[0]
                    dataPat = re.compile(r"^(/?(?:[^\r\n\t\f\v/]+?/)*?{})$(?mi)".format(tmps.rsplit('/', 1)[0]))
                    logging.info('New dataPat is {}'.format(dataPat))
                    datapath = dataPat.search(s).group(1)
                else:
                    logging.warning('{} : Data folder not found, rare exception'.format(ID))
                    datapath = BWS.DataPDict[ID]

        logging.info('Found tp2 and folder {} | {}'.format(tp2path, datapath))

        if datapath in tp2path:
            src = datapath.rsplit('/', 1)[0]
            res = Utils.MergeFolderTo(src, targetdir)
        else:
            src = datapath.rsplit('/', 1)[0]
            res = Utils.MergeFolderTo(src, targetdir)
            targettp2 = targetdir + '/' + tp2path.rsplit('/',1)[1]
            if not os.path.exists(targettp2):
                shutil.move(tp2path, targettp2)

        try:
            Utils.cleanupdir(tmpdir)
        except PermissionError:
            logging.exception("Could not delete tmpdir for {}".format(ID))

        return res

    def PrepMods(self, ToPrep, dldir=None, targetdir=None, tmpdir=None, basedir=None, ModsData=None):
        if dldir is None:
            dldir = self.dldir
        if targetdir is None:
            targetdir = self.gamedir
        if tmpdir is None:
            tmpdir = self.tmpdir
        if basedir is None:
            basedir = self.dir
        if ModsData is None:
            ModsData = self.ModsData

        return [self.PrepMod(dldir + '/' + ModsData[i]['Save'], ModsData[i], tmpdir=tmpdir, targetdir=targetdir,
                             basedir=basedir) for i in ToPrep]

    def No_GUI_loop(self, file, start=0, end=-1):
        self.LoadModsData(file)
        loaded = len(self.ModsData)
        self.ModsData = self.LoadModsComponents(self.config + '/WeiDU-EN.ini')
        WorkingInds = range(start, end if end != -1 else len(self.ModsData))
        selected = len(WorkingInds)
        m = self.DownloadMods(WorkingInds)
        #m = self.TestPresentMods(ToTest=WorkingInds)
        NewInds = [i for i,v in zip(WorkingInds,m) if v == 1]
        downloaded = len(NewInds)
        #n = self.ExtMods(NewInds, mode=1)
        Utils.cleanupdir(self.tmpdir)
        n = self.PrepMods(NewInds, dldir=self.dldir, targetdir=self.gamedir, basedir=self.dir, ModsData=self.ModsData)
        extracted = len([i for i in n if isinstance(i, tuple)])
        logging.info("{} mods loaded, {} selected, {} downloaded or found, {} properly extracted".format(loaded, selected, downloaded, extracted))
        return m, n


