import re

pat=re.compile("\[(?P<ID>.*?)\]"
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
    with open(filename) as file:
        ModsData = [match.groupdict() for match in pat.finditer(file.read())]
    return ModsData