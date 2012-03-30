from django.test import TestCase
from knesset.video.utils.lock import Lock

class Lock_test(Lock):
    
    def __init__(self,queueFileName,ttl,testCase,fileGetLinesReturn):
        self._testCase=testCase
        self._fileGetLinesReturn=fileGetLinesReturn
        self.fileAppendLog=[]
        self.fileWriteLog=[]
        Lock.__init__(self,queueFileName,ttl)
    
    def _getUuid(self):
        return 'uuid'
    
    def _getCurTime(self):
        return 10000
    
    def _getDataRoot(self):
        return 'data'
    
    def _fileAppend(self,fn,content):
        self.fileAppendLog.append((fn,content))
        
    def _fileGetLines(self,fn):
        self._testCase.assertIn(fn,self._fileGetLinesReturn)
        return self._fileGetLinesReturn[fn]
    
    def _fileWrite(self,fn,new_content):
        self.fileWriteLog.append((fn,new_content))

class testLock(TestCase):
    
    def testLock(self):
        # invalid
        lock=Lock_test('test',50,self,fileGetLinesReturn={'data/test':[]})
        uuid=lock.lock()
        self.assertEquals(lock.fileAppendLog,[('data/test',"uuid 10000\n")])
        self.assertEquals(lock.fileWriteLog,[])
        self.assertFalse(uuid)
        # valid
        lock=Lock_test('test',50,self,fileGetLinesReturn={'data/test':["uuid 10000\n"]})
        uuid=lock.lock()
        self.assertEquals(lock.fileAppendLog,[('data/test',"uuid 10000\n")])
        self.assertEquals(lock.fileWriteLog,[])
        self.assertEquals(uuid,'uuid')
        self.assertTrue(lock.releaseLock(uuid))
        self.assertEquals(lock.fileWriteLog,[('data/test',"")])
        self.assertEquals(lock.fileAppendLog,[('data/test',"uuid 10000\n")])
        # more comples scenario
        # invalid
        lock=Lock_test('test',50,self,fileGetLinesReturn={'data/test':[
            "expired_uuid 5000\n",
            "valid_uuid 10000\n",
        ]})
        uuid=lock.lock()
        self.assertEquals(lock.fileAppendLog,[('data/test',"uuid 10000\n")])
        self.assertEquals(lock.fileWriteLog,[])
        self.assertFalse(uuid)
        # valid
        lock=Lock_test('test',50,self,fileGetLinesReturn={'data/test':[
            "expired_uuid 5000\n",
            "another_expired_uuid 6000\n",
            "uuid 10000\n",
            "other_uuid 9999\n",
            "another_uuid 9998\n",
        ]})
        uuid=lock.lock()
        self.assertEquals(lock.fileAppendLog,[('data/test',"uuid 10000\n")])
        self.assertEquals(lock.fileWriteLog,[])
        self.assertEquals(uuid,'uuid')
        self.assertTrue(lock.releaseLock(uuid))
        self.assertEquals(lock.fileWriteLog,[('data/test',"other_uuid 9999\nanother_uuid 9998\n")])
        self.assertEquals(lock.fileAppendLog,[('data/test',"uuid 10000\n")])
        
        
        
        
        
        
        