import urllib.request
import urllib.error
import logging

def DownloadFile(url, filename=None, reporthook=None):
    logging.info('Sending request to {}'.format(url))
    with urllib.request.urlopen(url) as response, open(filename, 'wb') as out_file:
        #In case download isn't possible
        if response.code !=200:
            return response.code, 0
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
        logging.info('Done downloading from {} to {}, {} bytes downloaded'.format(url,filename,downloaded))

    return response.code, downloaded


if __name__ == '__main__':
    url = 'https://github.com/subtledoctor/Scales_of_Balance/archive/master.zip'
    filename = "testmod"
