import urllib.request
import shutil

def DownloadFile(url, filename=None, reporthook=None):
    print("Starting download of {} to {}".format(url, filename))
    with urllib.request.urlopen(url) as response, open(filename, 'wb') as out_file:
        if response.code !=200:
            print("Error in {}".format(url))
            print(response.code)
            return 0
        if reporthook==None:
            ln = response.getheader('Content-length')
            if ln:
                ln=int(ln)
                def reporthook(n):
                    print('{}% complete'.format(100*n/ln))
            else:
                def reporthook(n):
                    print('{} bytes downloaded'.format(n))
        downloaded = 0
        while 1:
            chunk=response.read(16*1024)
            if not chunk:
                break
            downloaded += len(chunk)
            out_file.write(chunk)
            reporthook(downloaded)

    print("Download finished for {}, {} bytes downloaded".format(filename, downloaded))

    return 1


if __name__ == '__main__':
    url = 'https://github.com/subtledoctor/Scales_of_Balance/archive/master.zip'
    filename = "testmod"
