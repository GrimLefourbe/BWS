import os
os.chdir("C:\\Coding\\Python workshop\\BWS")

import subprocess

extracting_tools = ["C:\\Games\\BWS\\BigWorldSetup-bigworldsetup-2148d38ef306\\BiG World Setup\\Tools\\7z.exe","7z1604-extra\\7za.exe"]

import re

CheckPat = re.compile("(Everything is Ok)|(?P<fieldname>\w+): *(?P<value>\d+)\r")
def Check_Archive(filename, ext_tool = None):
    startupinfo = subprocess.STARTUPINFO()
    startupinfo.dwFlags |= subprocess.STARTF_USESHOWWINDOW

    if ext_tool is None:
        ext_tool = SelectTool(filename)

    #uses the 7z-like extraction tool to check the validity of the archive and its contents
    try:
        res = subprocess.check_output([ext_tool, 't', filename], startupinfo=startupinfo)
    except subprocess.CalledProcessError:
        print("CalledProcessError")
        raise
    res = res.decode()
    s=CheckPat.findall(res)

    #Checks if Everything is Ok
    if not 'Everything is Ok' in s[0]:
        print("Erreur")
        print(s)
        return
    
    #Put the results into a more usable format
    resdict = {i[1]:int(i[2]) for i in s[1:]}
    return res
def SelectTool(filename):
    return extracting_tools[0]

def Extract_Archive(filename,targetdir=None):
    if targetdir is None:
        targetdir = filename.rsplit(sep = '.',maxsplit = 1)
        os.mkdir(targetdir)

    #Stops the console window from popping
    startupinfo = subprocess.STARTUPINFO()
    startupinfo.dwFlags |= subprocess.STARTF_USESHOWWINDOW

    ext_tool = SelectTool(filename)

    try:
        res = subprocess.check_output([ext_tool, "x", filename, "-o"+dirname], startupinfo=startupinfo)
    except subprocess.CalledProcessError:
        print("CalledProcessError")
        raise

    return res

