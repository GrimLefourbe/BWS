import os
import threading
import io
import sys

class ReaderThread(threading.Thread):
    def __init__(self, piperead = None, pipewrite=None, endtag=b'', outstream=None, group=None, name=None, daemon=None):
        super().__init__(group=group, target=self.work, name=name, daemon=daemon)
        if isinstance(piperead, int):
            self.filer = os.fdopen(piperead, 'rb')
        elif hasattr(piperead, "readline"):
            self.filer = piperead
        elif piperead is None:
            pass
        else:
            raise NotImplementedError
        if isinstance(pipewrite, int):
            self.filew = os.fdopen(pipewrite, 'wb')
        elif hasattr(pipewrite, "write"):
            self.filew = piperead
        elif pipewrite is None:
            pass
        else:
            raise NotImplementedError
        if outstream is None:
            self.outstream = io.BytesIO()
        else:
            self.outstream = outstream
        self.die = False
        self.tag = endtag + b'\n'
        self.go = threading.Event()
        self.go.set()
        self.sent = threading.Event()
        self.n = 0
        self.lastn = 0

    def getfds(self):
        r, w = os.pipe()
        self.filew = os.fdopen(w, 'wb')
        self.filer = os.fdopen(r, 'rb')

        return r, w

    def instock(self):
        return self.n

    def work(self):
        for l in self.filer:
            self.n += self.outstream.write(l)
            self.sent.set()
            self.go.wait()
            self.sent.clear()
            if self.die:
                break
        self.outstream.close()
        self.filer.close()
        self.filew.close()

    def close(self):
        self.die = True
        self.filew.write(self.tag)
        self.filew.flush()

    def read(self):
        if self.outstream.closed:
            return ''
        if not self.n:
            return None
        s = sys.getswitchinterval()
        sys.setswitchinterval(1000)
        self.go.clear()
        self.filew.write(self.tag)
        self.filew.flush()
        self.sent.wait()
        b = self.outstream.getvalue()
        i = b.rfind(self.tag)
        self.outstream.truncate(0)
        self.outstream.seek(0)
        n = self.n
        self.n = 0
        sys.setswitchinterval(s)
        self.go.set()

        return b[:i] + b[i+len(self.tag):n]