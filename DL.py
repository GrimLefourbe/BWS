import os

os.chdir("C:\\Coding\\Python workshop\\BWS")

import urllib.request
import shutil

url = 'https://github.com/subtledoctor/Scales_of_Balance/archive/master.zip'
filename = "testmod"

with urllib.request.urlopen(url) as response, open(filename, 'wb') as out_file:
    shutil.copyfileobj(response, out_file)
