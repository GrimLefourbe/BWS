import re
import configparser

ModListPat=re.compile("\[(?P<ID>.*?)\]"
               "(?:\n *Name=(?P<Name>.*?))?"
               "(?:\n *(?:(?:Rev=)|(?:Version=))(?P<Rev>.*?))?"
               "(?:\n *Type=(?P<Type>.*?))?"
               "(?:\n *Link=(?P<Link>.*?))?"
               "(?:\n *NOTLATEST_Down=(?P<NOTLATEST_Down>.*?))?"
               "(?:\n *Down=(?P<Down>.*?))?"
               "(?:\n *Save=(?P<Save>.*?))?"
               "(?:\n *Size=(?P<Size>.*?))?"
               "(?:\n *Tra=(?P<Tra>.*?))?"
               "(?:\n *Wiki=(?P<Wiki>.*?))?" "$", flags=re.MULTILINE)

def ModList_old(filename):
    with open(filename) as file:
        ModsData = [match.groupdict() for match in ModListPat.finditer(file.read())]
    return ModsData

def ModList(filename):
    P = configparser.ConfigParser(interpolation=None)
    P.optionxform = lambda x:x
    with open(filename) as f:
        P.read_file(f)
    ModsData = []
    iterP = iter(P.values())
    iterP.__next__()
    for i in iterP: #this excludes the DEFAULT section
        print(i)
        d = dict(i)
        d['ID'] = i.name
        ModsData.append(d)
    return ModsData