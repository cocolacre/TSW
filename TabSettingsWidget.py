import sip
#sip.setapi('QString', 1)
from PyQt4 import QtCore, QtGui, QtTest,QtSql
from PyQt4 import Qt as _Qt
import queue, copy
import sys,time
from PyQt4.QtCore import *
from PyQt4.QtGui import *
import subprocess as sp
import os,ctypes

class TabSettingsWidget(QtGui.QWidget):
    def __init__(self,parent=None):
        super(TabSettingsWidget, self).__init__()
        self.grid = QtGui.QGridLayout(self)
        self.gridLabel1 = QtGui.QLabel('gridLabel1')
        self.gridLabel2 = QtGui.QLabel('gridLabel2')
        self.gridLineEdit = QtGui.QLineEdit()
        self.grid.addWidget(self.gridLabel1)
        self.grid.addWidget(self.gridLabel2)
        self.grid.addWidget(self.gridLineEdit)
        self.setLayout(self.grid)
        