import urllib.request

def DownloadFile(url, filename=None, reporthook=None):
    print("Starting download of {} to {}".format(url, filename))
    with urllib.request.urlopen(url) as response, open(filename, 'wb') as out_file:
        #In case download isn't possible
        if response.code !=200:
            print("Error in {}".format(url))
            print(response.code)
            return 0
        if reporthook==None:
            #Temp solution while no GUI
            ln = response.getheader('Content-length')
            if ln:
                ln=int(ln)
                def reporthook(n):
                    print('\r{:.2f}% complete'.format(100*n/ln),end='',flush=True)
            else:
                def reporthook(n):
                    print('\r{:.0f} kb downloaded'.format(n/1000),end='',flush=True)
        downloaded = 0
        while 1:

            chunk=response.read(16*1024)
            #read returns None when the stream is closed so we can test it
            if not chunk:
                break

            downloaded += len(chunk)
            out_file.write(chunk)
            reporthook(downloaded)

    print("\nDownload finished for {}, {} bytes downloaded".format(filename, downloaded))

    return 1


if __name__ == '__main__':
    url = 'https://github.com/subtledoctor/Scales_of_Balance/archive/master.zip'
    filename = "testmod"
