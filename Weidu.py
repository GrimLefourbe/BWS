import subprocess
from sys import platform
import logging
import shlex
import os

def FindTP2path(tpname, gamefolder):
    gamefolder = gamefolder.rstrip("/")
    t = gamefolder + '/setup-' + tpname + '.tp2'
    if os.path.exists(t):
        return t
    t = "{}/{}/setup-{}.tp2".format(gamefolder, tpname, tpname)
    if os.path.exists(t):
        return t
    t = "{}/{}/{}.tp2".format(gamefolder, tpname, tpname)
    if os.path.exists(t):
        return t
    return 0

def formatComp(compstring : str):
    try:
        int(compstring.lstrip('@'))
    except ValueError:
        return ''
    return compstring.lstrip('@')

class Weidu_Handler:
    def __init__(self, weidupath, gamepath, lang=None):
        self.weidupath = weidupath
        self.gamepath = gamepath

        self.ConfigWeidu(lang=lang)

    def ConfigWeidu(self, lang=None):
        if lang is not None:
            subprocess.call([self.weidupath, "--use-lang", lang], cwd=self.gamepath)
        return 1

    def ExecTP2(self, tppath, lang, ToIns=None, ToUnins=None,
                stdin=None, stdout=None, stderr=None, gamepath=None, weidupath=None, *weiduargs, **popenargs):
        if weidupath is None:
            weidupath = self.weidupath
        if gamepath is None:
            gamepath = self.gamepath
        if stdin is None:
            stdin = subprocess.PIPE
        if stdout is None:
            stdout = subprocess.PIPE
        if stderr is None:
            stderr = subprocess.PIPE
        elif stderr is 1:
            stderr = subprocess.STDOUT

        command = [weidupath, tppath, "--language", lang, "--no-exit-pause"]
        if ToIns is not None and len(ToIns) != 0:
            command.append("--force-install-list")
            for i in ToIns:
                t = formatComp(i)
                if t != '':
                    command.append(t)
        if ToUnins is not None and len(ToUnins) != 0:
            command.append("--force-uninstall-list")
            for i in ToUnins:
                t = formatComp(i)
                if t != '':
                    command.append(t)

        for i in weiduargs:
            command.append(str(i))

        logging.info("Command is {}".format(command))

        w = subprocess.Popen(command, cwd=gamepath, stdin=stdin, stdout=stdout, stderr=stderr, **popenargs)

        logging.info("Popen object created")

        return w


    def Install_mod(self, tpname, ToIns = None, ToUnins = None, lang = None, stdin = None, stdout = None, stderr = None,
                    gamepath = None, weidupath = None):
        if lang is None:
            lang = "0"
        if weidupath is None:
            weidupath = self.weidupath
        if gamepath is None:
            gamepath = self.gamepath
        if stdin is None:
            stdin = subprocess.PIPE
        if stdout is None:
            stdout = subprocess.PIPE
        if stderr is None:
            stderr = subprocess.PIPE
        elif stderr is 1:
            stderr = subprocess.STDOUT


        logging.info("Preparing install of {}".format(tpname))
        tppath = FindTP2path(tpname, gamepath)
        logging.info("Found tppath is {}".format(tppath))
        w = self.ExecTP2(tppath, lang, ToIns=ToIns, ToUnins=ToUnins, stdin=stdin, stdout=stdout, stderr=stderr,
                         gamepath=gamepath, weidupath=weidupath)
        return w
