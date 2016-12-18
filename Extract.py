import os
import subprocess
import logging

'''
ext_tools['bar']['foo'] is a list of tuples with a command used to extract files of extension .foo on the platform bar and a command used to test integrity of files
ext_tools['bar']['foo'][i][0] is used to extract, ext_tools['bar']['foo'][i][1] is used to test.
'''
ext_tools = {
    'win32': {'exe': [("{basedir}\\Tools\\7z.exe x {filename} -o{targetdir} -aoa", "{basedir}\\Tools\\7z.exe t {filename}")],
              'rar': [("{basedir}\\Tools\\7z.exe x {filename} -o{targetdir} -aoa", "{basedir}\\Tools\\7z.exe t {filename}")],
              'zip': [("{basedir}\\Tools\\7z.exe x {filename} -o{targetdir} -aoa", "{basedir}\\Tools\\7z.exe t {filename}")],
              '7z' : [("{basedir}\\Tools\\7z.exe x {filename} -o{targetdir} -aoa", "{basedir}\\Tools\\7z.exe t {filename}")]},
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

def Check_Archive(filepath, basedir='', regex = None, ext_tool=None):
    '''
    Checks the integrity of the contents of filepath
    basedir is used to find the path of the ext_tool
    ext_tool can be used to override the defaults ext_tool, it should be
    [command to use to extract archive, command to use to test archive].
    The command will be affected by format(filename=filepath, basedir=basedir)
    Returns 3 if the extracting tool found an error, else returns the results of regex in a list or 1 if regex was not given.
    :param filepath:
    :param basedir:
    :param ext_tool:
    :return:
    '''
    startupinfo = subprocess.STARTUPINFO()
    startupinfo.dwFlags |= subprocess.STARTF_USESHOWWINDOW


    if ext_tool is None:
        ext_tool = SelectTool(filepath)

    logging.info('Selected ext_tool is {}'.format(ext_tool))
    command = ext_tool[1].format(filename=filepath, basedir=basedir)
    logging.info('Command is {}'.format(command))
    # uses the extraction tool to check the validity of the archive and its contents
    try:
        res = subprocess.check_output(command, startupinfo=startupinfo)
    except subprocess.CalledProcessError:
        logging.exception('Returning 0 due to exception during the execution of {}'.format(command))
        return 0
    logging.info('ext_tool executed without error')

    s = CheckPat.findall(res)

    # Checks if Everything is Ok
    if b'Everything is Ok' not in s[0]:
        logging.debug('ext_tool found an issue.\n'
                      's={}\n'
                      'ext_tool output :\n{}'.format(s, res))
        return 3

    if regex is None:
        results = 1
    else:
        results = RegexBytesSeq(regex, res)

    logging.info('Testing was successful for {}'.format(filepath))

    return results




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
    # uses the extraction tool to check the validity of the archive and its contents
    try:
        res = subprocess.check_output(command, startupinfo=startupinfo)
    except subprocess.CalledProcessError:
        logging.exception('Returning 0 due to exception during the execution of {}'.format(command))
        return 0

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
