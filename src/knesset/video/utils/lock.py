# simple queue based process locking facility

import time, uuid, os
from django.conf import settings

class Lock:
    
    def __init__(self,queueFileName,ttl):
        self._queueFileName=queueFileName
        self._ttl=ttl
        
    def _getUuid(self):
        return str(uuid.uuid4())
    
    def _getCurTime(self):
        return int(time.time())
    
    def _getDataRoot(self):
        return getattr(
            settings, 
            'DATA_ROOT', 
            os.path.join(
                settings.PROJECT_ROOT, 
                os.path.pardir, 
                os.path.pardir, 
                'data'
            )
        )
    
    def _getQueueFileName(self):
        return self._getDataRoot()+'/'+self._queueFileName
    
    def _fileAppend(self,fn,content):
        open(fn,'a').write(content)
    
    def _fileGetLines(self,fn):
        lines=[]
        for line in open(fn,'r'):
            lines.append(line)
        return lines
    
    def _isValidLine(self,line_uuid,line_time):
        if self._getCurTime()-10<line_time:
            return True
        else:
            return False
    
    def _fileGetValidLines(self,fn):
        validLines=[]
        lines=self._fileGetLines(fn)
        for strLine in lines:
            line=strLine.strip().split(' ')
            if len(line)>1:
                line_uuid=line[0]
                line_time=int(line[1])
                if self._isValidLine(line_uuid,line_time):
                    validLines.append((line_uuid,line_time))
        return validLines
    
    def _fileWrite(self,fn,new_content):
        open(fn,'w').write(new_content)
            
    
    def lock(self):
        uuid=self._getUuid();
        curtime=self._getCurTime()
        fn=self._getQueueFileName()
        self._fileAppend(fn,uuid+' '+str(curtime)+"\n")
        lines=self._fileGetValidLines(fn)
        if len(lines)>0 and lines[0][0]==uuid:
            return lines[0][0]
        else:
            return False
        
    def releaseLock(self,uuid):
        fn=self._getQueueFileName()
        lines=self._fileGetValidLines(fn)
        if len(lines)>0 and lines[0][0]==uuid:
            new_content=''
            for line in lines:
                if line[0]!=uuid:
                    new_content+=str(line[0])+' '+str(line[1])+"\n"
            self._fileWrite(fn,new_content)
        return True