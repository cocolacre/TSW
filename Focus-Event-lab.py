import gc
import sip
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
import uuid
from ctypes import wintypes as wt

import screen,keyboard
from StorageQt import StorageQt
from Task import Task




class FocusOutFilter(QObject):
    focusOut = pyqtSignal()

    def eventFilter(self, widget, event):
        if event.type() == QEvent.FocusOut:
            print("--eventFilter() focus_out on " + widget.objectName())
            self.focusOut.emit()
            return event.type()
        else:
            print('Other event', event.type())
            return event.type()

#class SignalOnFocus(QWidget):
#    def __init__(self):
#        ...    
#        self.focusOutFilter = FocusOutFilter()
#        self.inputLineEdit1.installEventFilter(self.focusOutFilter)
#        self.focusOutFilter.focusOut.connect(self.focusLost)

class MyEdit(QtGui.QLineEdit):
    def __init__(self, text=''):
        super(QtGui.QLineEdit, self).__init__(text)
        self.focusOutFilter = FocusOutFilter()
        self.installEventFilter(self.focusOutFilter)
        self.focusOutFilter.focusOut.connect(self.focusLost)
    def focusLost(self):
        print('THE ENEMY HAS TAKEN CONTROL OF THE FOCUS!') # ;)

    #should be class method?
    #def eventFilter(self, event):
    #    print('eventFilter works')
    #    if event.type() == QtCore.QEvent.FocusOut:
    #        print('FOCUS event occured')
    #    if event.lostFocus():
    #        print('Widget has lost focus')
    #        print('Need to save Description state')
    #    else:
    #        print('Hello, you are working in this widget.')
			
			
class LabelGapsolution(QtGui.QWidget):
    """
    
    """
    def __init__(self):
        super(QtGui.QWidget, self).__init__()
        hbox = QtGui.QHBoxLayout()
        #hbox.setSpacing(0)
        hbox.setContentsMargins(0,0,0,0)
        self.resize(300,300)
        self.setFixedSize(300,300)
        vwbox = QtGui.QVBoxLayout()
        #vwbox.setSpacing(0)
        vwbox.setContentsMargins(0,0,0,0)
        vw = QtGui.QWidget(parent = self)
        vw.setContentsMargins(0,0,0,0)
        style = "padding: 0px; margin: 0px 0px 0px 0px; border-style: solid; background-color: lawngreen;"
        #vw.setStyleSheet("background-color: azure")
        vw.setStyleSheet(style)
        hw = QtGui.QWidget()
        #lab = QtGui.QLabel(parent = hw, 'above buttons')
        lab = QtGui.QLabel('there must be no green color below')
        style = "padding: 0px; margin: 0px 0px 0px 0px; border-style: solid; background-color: salmon;"
        lab.setStyleSheet(style)
        b1 = QtGui.QPushButton('b1')
        style = "background-color: yellow; border-style : solid;"
        style = style + " " + "border-color : black"
        ###################
        style = "border: 5px solid red"
        style = "margin: 1px 1px 1px 1px"
        style = "padding: 0px; margin: 0px 0px 0px 0px; border-style: solid; background-color: yellow;"
        #b1.setStyleSheet(style)
        #b1.setStyleSheet("border-style : solid")
        b2 = QtGui.QPushButton('b2')
        b2.setStyleSheet(style)
        #b2.setStyleSheet("background-color: red")
        hbox.addWidget(b1)
        hbox.addWidget(b2)
        bw = QtGui.QWidget()
        bw.setStyleSheet(style)
        bw.setLayout(hbox)
        my = MyEdit('hi!')
        vwbox.addWidget(lab)
        vwbox.addWidget(bw)
        vwbox.addWidget(my)
        
        vw.setLayout(vwbox)
        self.show()
    
    #def eventFilter(event):
		
if __name__ == "__main__":
    app = QtGui.QApplication(sys.argv)
    win = LabelGapsolution()
    win.show()
    sys.exit(app.exec_())