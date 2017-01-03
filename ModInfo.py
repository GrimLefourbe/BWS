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

def ModList(filename):
    P = configparser.ConfigParser(interpolation=None)
    P.optionxform = lambda x: x
    with open(filename, encoding='cp1252') as f:
        P.read_file(f)
    ModsData = []
    iterP = iter(P.values())
    iterP.__next__()
    for i in iterP: #this excludes the DEFAULT section
        d = dict(i)
        d['ID'] = i.name
        ModsData.append(d)
    return ModsData

def ModComp(filename, ModsData=None):
    P = configparser.ConfigParser(interpolation=None)
    P.optionxform = lambda x: x
    with open(filename, encoding='cp1252') as f:
        P.read_file(f)

    if ModsData is None:
        return P
    for d in ModsData:
        complist = []
        try:
            c = P[d['ID']]
            for k, v in c.items():
                if k == "Tra":
                    continue

                complist.append((k, v))
        except KeyError:
            continue
        d["Comp"] = complist
    return ModsData
