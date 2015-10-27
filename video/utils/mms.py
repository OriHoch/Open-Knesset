try:
    from libmimms2 import libmms,core as mimms
except OSError:
    print "You need to install mms support library: sudo apt-get install libmms-dev"
    exit()

class _options():
    def __init__(self,url,filename,time_limit,resume=False):
        self.time=time_limit
        self.bandwidth=1e6
        self.url=url
        self.filename=filename
        self.quiet=True
        self.resume=True
        self.clobber=False
        self.connections_count=1

def get_size(url):
    stream=libmms.Stream(url, 1e6)
    return stream.length()
    
def download(url,filename,time_limit):
    isDone=False
    try:
        mimms.download(_options(url,filename,time_limit))
        isDone=True
    except mimms.Timeout: pass
    except KeyboardInterrupt: pass 
    return isDone
    
def resume_download(url,filename,time_limit):
    isDone=False
    try:
        mimms.download(_options(url,filename,time_limit))
        isDone=True
    except mimms.Timeout: pass
    except KeyboardInterrupt: pass
    return isDone

