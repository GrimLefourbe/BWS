import re

pat=re.compile("\[(?P<ID>.*?)\]"
               "(?:\nName=(?P<Name>.*?))?"
               "(?:\nRev=(?P<Rev>.*?))?"
               "(?:\nType=(?P<Type>.*?))?"
               "(?:\nLink=(?P<Link>.*?))?"
               "(?:\nDown=(?P<Down>.*?))?"
               "(?:\nSave=(?P<Save>.*?))?"
               "(?:\nSize=(?P<Size>.*?))?"
               "(?:\nTra=(?P<Tra>.*?))?"
               "(?:\nWiki=(?P<Wiki>.*?))?" "$", flags=re.MULTILINE)

def LoadMods(filename):
    with open(filename) as file:
        data= file.read()
        print(len(data))
        ModsData = pat.findall(data)
    return ModsData