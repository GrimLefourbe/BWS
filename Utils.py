import os
import re
import stat
import logging
import shutil
import time

def onerror(func, path, exc_info):
    os.chmod(path, stat.S_IWRITE|stat.S_IWUSR)
    func(path)

def RegexBytesSeq(Regstr, bstring : bytes, keywords = None):
    '''
    Regstr is a list of bytes strings representing regex patterns. Any keywords will be fed back to
    the next elements.
    bstring if os bytes type.
    :param Regstr:
    :return:
    '''

    if keywords is None:
        keywords = {}
    groups = []
    logging.info('Base keywords : {}'.format(keywords))
    for s in Regstr:
        logging.info('Current re is {}'.format(s))
        match = re.search(s%keywords, bstring)
        if match:
            keywords.update({k.encode(): v for k, v in match.groupdict().items()})
            logging.info('New keywords : {}'.format(keywords))
            groups.append(match.groups())

    return groups

def MergeFolderTo(src, dst, samedrive=-1):
    srcl = os.listdir(src)
    dstl = os.listdir(dst)

    if samedrive == -1:
        if os.stat(src).st_dev == os.stat(dst).st_dev:
            samedrive = 1
        else:
            samedrive = 0
    copy_ok = 1
    delete_ok = 1
    for p in srcl:
        srcpath = src + '\\' + p
        if os.path.isdir(srcpath):
            if p in dstl:
                c,d = MergeFolderTo(srcpath, dst + '\\' + p, samedrive)
                copy_ok &= c
                delete_ok &= d
            elif samedrive:
                shutil.move(srcpath, dst)
            else:
                shutil.copytree(srcpath, dst + '\\' + p)
                try:
                    shutil.rmtree(srcpath, onerror=onerror)
                except PermissionError:
                    logging.exception("Error when removing {}".format(srcpath))
                    delete_ok = 0
                    continue
        else:
            srcpath = src + '\\' + p
            dstpath = dst + '\\' + p
            if p in dstl:
                RemoveFile(dstpath)
                if samedrive:
                    os.rename(srcpath, dstpath)
                else:
                    shutil.copy2(srcpath, dstpath)
                    try:
                        RemoveFile(srcpath)
                    except PermissionError:
                        logging.exception("Error when removing {}".format(srcpath))
                        delete_ok = 0
                        continue
            elif samedrive:
                os.rename(srcpath, dstpath)
            else:
                shutil.copy2(srcpath, dstpath)
                try:
                    RemoveFile(srcpath)
                except PermissionError:
                    logging.exception("Error when removing {}".format(srcpath))
                    delete_ok = 0
                    continue

    return copy_ok, delete_ok

def RemoveFile(path):
    if not os.path.isfile(path):
        logging.error("Wrong file type when trying to remove {}".format(path))
        raise FileNotFoundError
    try:
        os.remove(path)
    except PermissionError:
        os.chmod(path, stat.S_IWUSR|stat.S_IWRITE)
        try:
            os.remove(path)
        except PermissionError:
            logging.exception("Permission error when trying to remove {}".format(path))
            raise


def cleanupdir(path):
    for i in os.listdir(path):
        p = path + '\\' + i
        if os.path.isfile(p):
            try:
                os.remove(p)
            except:
                os.chmod(p, stat.S_IWRITE|stat.S_IWUSR)
                os.remove(p)
        else:
            shutil.rmtree(path + '\\' + i, onerror=onerror)
    if not len(os.listdir(path))==0:
        time.sleep(2)
        if not len(os.listdir(path))==0:
            return 0
    return 1

def listsubdir(path : str):
    s=[]
    for i in os.walk(path.rstrip(r'\/')):
        s.append(i[0])
        for j in i[2]:
            s.append(i[0] + '\\' + j)
    return s