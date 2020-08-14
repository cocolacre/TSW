import sys,time,os
import sip
#sip.setapi('QString', 1)
from PyQt4 import QtCore, QtGui, QtTest,QtSql
from PyQt4.QtCore import *
from PyQt4.QtGui import *
import screen,keyboard
import cv2

class Camera(QtCore.QObject):
    """
    TODO:
        1)Add captured images to db in relation with the current task if one is present.
    
    """
    finished_sig = QtCore.pyqtSignal()
    bytes_written_sig = QtCore.pyqtSignal(int)
    
    def __init__(self):
        super(QtCore.QObject, self).__init__()
        self.time_started = time.time()
        self.running = True
        self.counter = 0
        self.max = 10000
        self.debug = True
        self.delay = 300
        self.bytes_written=0
        
    @pyqtSlot()
    def start_camera(self):
        prev_cap_time = 0
        def fmt(data):
            if len(str(data)) == 1:
                return('0'+str(data))
            else:
                return str(data)        
        
        while self.running and self.counter < self.max:
            QtGui.QApplication.processEvents() 
            if (time.time() - prev_cap_time) >= self.delay:
                prev_cap_time = time.time()
                vc = cv2.VideoCapture(0)
                lt = time.localtime()
                d = fmt(lt.tm_mday)
                h = fmt(lt.tm_hour)
                m = fmt(lt.tm_min)
                s = fmt(lt.tm_sec)
                mon = fmt(lt.tm_mon)
                filename='webcam-log/%s-%s__%s-%s-%s.jpg'%(mon,d,h,m,s)
                if vc.isOpened(): # try to get the first frame
                    rval, frame = vc.read()
                    vc.release()
                    cv2.imwrite(filename, frame)
                    
                else:
                    vc.release()
                    rval = False
                if self.debug: print('releasing webcam')
                if self.debug: print('done releasing webcam.')
                fsize = int(os.stat(filename).st_size)
                self.bytes_written +=fsize
                self.bytes_written_sig.emit(fsize)
                if self.debug:
                    print('[WEBCAM]: Writing %s bytes'%str(int(fsize/1000.0)))
            if not self.running:
                break
            QtTest.QTest.qWait(50)