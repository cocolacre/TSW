import sip
import gc
sip.setapi('QString', 1)
from PyQt4 import QtCore, QtGui, QtTest,QtSql
import queue, copy
import sys,time
from PyQt4.QtCore import *
from PyQt4.QtGui import *
import subprocess as sp
import os,ctypes
import datetime
import sqlite3
import cv2
import screen,keyboard
import uuid
from ctypes import wintypes as wt
import clr
import System.Diagnostics

class WindowsWatcher(QtCore.QObject):
    def __init__(self):
        super(QtCore.QObject, self).__init__()
        self.running =True
        self.dataPortion = 10
        self.timer = QtCore.QTimer()
        self.interval = 1000 #milliseconds
        #self.timer.setInterval(1000)
        self.dbg = True
        
    @pyqtSlot()
    def start_windows_watcher(self):
        #self.timer.start()
        prev_window = 0
        prev_window_text = ''
        while self.running:
            QtTest.QTest.qWait(self.interval)
            hwnd = ctypes.windll.user32.GetForegroundWindow()
            window_text_length = ctypes.windll.user32.GetWindowTextLengthW(hwnd)
            buff = ctypes.create_unicode_buffer(window_text_length+1)
            res = ctypes.windll.user32.GetWindowTextW(hwnd, buff,window_text_length+1)
            #path_len = 200
            #path_buff = ctypes.create_unicode_buffer(path_len+1)
            #res = ctypes.windll.user32.GetWindowModuleFileNameW(hwnd, path_buff,path_len)
            pid = ctypes.c_uint()
            res = ctypes.windll.user32.GetWindowThreadProcessId(hwnd, ctypes.byref(pid))
            #print(pid.value)
            process = System.Diagnostics.Process.GetProcessById(pid.value)
            name = process.MainModule.FileName
            if self.dbg:
                if prev_window != hwnd or prev_window_text != str(buff.value):
                    prev_window = hwnd
                    prev_window_text = str(buff.value)
                    #print(hwnd, window_text_length,buff.value, path_buff.value)
                    print("["+str(buff.value)+"] ["+name+"]")
                    del buff
                    #del path_buff
                    del hwnd
ww = WindowsWatcher()
ww.start_windows_watcher()
