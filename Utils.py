import os
import re
import stat
import logging

def onerror(func, path, exc_info):
    """
    Error handler for ``shutil.rmtree``.

    If the error is due to an access error (read only file)
    it attempts to add write permission and then retries.

    If the error is for another reason it re-raises the error.

    Usage : ``shutil.rmtree(path, onerror=onerror)``
    """
    # Is the error an access error ?
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

def listsubdir(path : str):
    s=[]
    for i in os.walk(path.rstrip(r'\/')):
        s.append(i[0])
        for j in i[2]:
            s.append(i[0] + '\\' + j)
    return s