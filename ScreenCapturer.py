import sys,time,os
import sip
#sip.setapi('QString', 1)
from PyQt4 import QtCore, QtGui, QtTest,QtSql
from PyQt4.QtCore import *
from PyQt4.QtGui import *
import screen,keyboard
import cv2

class ScreenCapturer(QtCore.QObject):
    #captured_sig = QtCore.pyqtSignal()
    finished_sig = QtCore.pyqtSignal()
    bytes_written_sig = QtCore.pyqtSignal(int)
    
    def __init__(self):
        super(QtCore.QObject, self).__init__()
        self.running = True
        self.delay = 5
        self.counter = 0
        self.max = 5000
        self.debug = True
        self.bytes_written = 0
        
    @pyqtSlot()
    def start_capturing(self):
        prev_capture = 0
        def fmt(data):
            if len(str(data)) == 1:
                return('0'+str(data))
            else:
                return str(data)        
        while self.running:
            
            if (time.time() - prev_capture) >= self.delay:
                prev_capture = time.time()
                lt = time.localtime()
                d = fmt(lt.tm_mday)
                h = fmt(lt.tm_hour)
                m = fmt(lt.tm_min)
                s = fmt(lt.tm_sec)
                mon = fmt(lt.tm_mon)
                current_task = 'TASK_PLACEHOLDER'
                filename='screen-log/%s-%s__%s-%s-%s-%s.png'%(mon,d,h,m,s,current_task)
                img = screen.capture()
                res = cv2.imwrite(filename, img)
                fsize = int(os.stat(filename).st_size)
                self.bytes_written +=fsize
                
                self.bytes_written_sig.emit(fsize)
                if self.debug:
                    print('[Screenshooter]:Writing %s bytes'%str(int(fsize/1000.0)))
                
                self.counter+=1
                if self.counter > self.max:
                    self.running = False
                    self.finished_sig.emit()
                    break
            #code below is for faster thread shutdown. Cleanup is working fine.
            QtTest.QTest.qWait(50)
            if not self.running:
                break