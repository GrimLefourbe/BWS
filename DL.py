import urllib.request
import shutil


def DownloadFile(url, filename=None):
    print("Starting download of {} to {}".format(url, filename))
    with urllib.request.urlopen(url) as response, open(filename, 'wb') as out_file:
        shutil.copyfileobj(response, out_file)
    print("Download finished for {}".format(filename))

    return 1


if __name__ == '__main__':
    url = 'https://github.com/subtledoctor/Scales_of_Balance/archive/master.zip'
    filename = "testmod"
