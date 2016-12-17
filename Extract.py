import os
import subprocess
import logging

'''
ext_tools['bar']['foo'] is a list of tuples with a command used to extract files of extension .foo on the platform bar and a command used to test integrity of files
ext_tools['bar']['foo'][i][0] is used to extract, ext_tools['bar']['foo'][i][1] is used to test.
'''
ext_tools = {
    'win32': {'exe': [("{basedir}\\Tools\\7z.exe x {filename} -o{targetdir}", "{basedir}\\Tools\\7z.exe t {filename}")],
              'rar': [("{basedir}\\Tools\\7z.exe x {filename} -o{targetdir}", "{basedir}\\Tools\\7z.exe t {filename}")],
              'zip': [("{basedir}\\Tools\\7z.exe x {filename} -o{targetdir}", "{basedir}\\Tools\\7z.exe t {filename}")],
              '7z' : [("{basedir}\\Tools\\7z.exe x {filename} -o{targetdir}", "{basedir}\\Tools\\7z.exe t {filename}")]},
    'darwin': {'exe': [],
               'rar': [],
               'zip': [("unzip -o {filename}", "unzip -to {filename}")],
               '7z': []},
    'linux': {
        'exe': [("{basedir}\\Tools\\7z.exe x {filename -o{targetdir}", "{basedir}\\Tools\\7z.exe t {filename}")],
        'rar': [],
        'zip': [("{basedir}\\Tools\\7z.exe x {filename -o{targetdir}", "{basedir}\\Tools\\7z.exe t {filename}")],
        '7z' : [("{basedir}\\Tools\\7z.exe x {filename} -o{targetdir}", "{basedir}\\Tools\\7z.exe t {filename}")]},
    'linux2': {
        'exe': [("{basedir}\\Tools\\7z.exe x {filename} -o{targetdir}", "{basedir}\\Tools\\7z.exe t {filename}")],
        'rar': [],
        'zip': [("{basedir}\\Tools\\7z.exe x {filename} -o{targetdir}", "{basedir}\\Tools\\7z.exe t {filename}")],
        '7z' : [("{basedir}\\Tools\\7z.exe x {filename} -o{targetdir}", "{basedir}\\Tools\\7z.exe t {filename}")]}}

import re

CheckPat = re.compile(b"(Everything is Ok)|(?P<fieldname>\w+): *(?P<value>\d+)\r")


def Check_Archive(filepath, basedir='', regex = None,ext_tool=None):
    '''
    Checks the integrity of the contents of filepath
    basedir is used to find the path of the ext_tool
    ext_tool can be used to override the defaults ext_tool, it should be
    [command to use to extract archive, command to use to test archive].
    The command will be affected by format(filename=filepath, basedir=basedir)
    :param filepath:
    :param basedir:
    :param ext_tool:
    :return:
    '''
    startupinfo = subprocess.STARTUPINFO()
    startupinfo.dwFlags |= subprocess.STARTF_USESHOWWINDOW

    if regex is None:
        regex = []

    if ext_tool is None:
        ext_tool = SelectTool(filepath)

    logging.info('Selected ext_tool is {}'.format(ext_tool))
    command = ext_tool[1].format(filename=filepath, basedir=basedir)
    logging.info('Command is {}'.format(command))
    # uses the 7z-like extraction tool to check the validity of the archive and its contents
    res = subprocess.check_output(command, startupinfo=startupinfo)

    logging.info('ext_tool executed without error')

    for Pat in regex:
        Pat.search(res)

    s = CheckPat.findall(res)

    # Checks if Everything is Ok
    if b'Everything is Ok' not in s[0]:
        logging.debug('ext_tool found an issue.\n'
                      's={}\n'
                      'ext_tool output :\n{}'.format(s, res))
        return 3
    logging.info('Testing was successful for {}'.format(filepath))

    return res




def SelectTool(filename):
    from sys import platform
    platform_tools = ext_tools[platform]
    ext = filename.rsplit('.')[-1]
    if ext in platform_tools:
        return platform_tools[ext][0]

def Extract_Archive(filepath, targetdir=None, basedir='', ext_tool=None):
    if targetdir is None:
        targetdir = filepath.rsplit(sep='.', maxsplit=1)
        os.makedirs(targetdir, exist_ok=True)

    if ext_tool is None:
        ext_tool = SelectTool(filepath)

    # Stops the console window from popping
    startupinfo = subprocess.STARTUPINFO()
    startupinfo.dwFlags |= subprocess.STARTF_USESHOWWINDOW

    ext_tool = SelectTool(filepath)

    logging.info('Selected ext_tool is {}'.format(ext_tool))
    command = ext_tool[0].format(filename=filepath, basedir=basedir, targetdir=targetdir)
    logging.info('Command is {}'.format(command))
    # uses the 7z-like extraction tool to check the validity of the archive and its contents
    res = subprocess.check_output(command, startupinfo=startupinfo)

    logging.info('ext_tool executed without error')

    s = CheckPat.findall(res)

    # Checks if Everything is Ok
    if b'Everything is Ok' not in s[0]:
        logging.debug('ext_tool found an issue.\n'
                      's={}\n'
                      'ext_tool output :\n{}'.format(s, res))
        return 3
    logging.info('Testing was successful for {}'.format(filepath))
    return 1
