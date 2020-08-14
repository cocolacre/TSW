from PyQt4 import QtCore, QtGui, QtTest,QtSql
import time, os, sys, random



#QIcon
#icon.pixmap
#QIcon.addPixmap(pixmap, mode,state)
#     
# MK 0
# Just a flashing little circle on a black background.     
#class AnimatedTray(QtGui.QSystemTrayIcon):
class AnimatedTray():
    def __init__(self):
        self.black = QtGui.QIcon(QtCore.QString("resources/black16x16.png"))
        self.red = QtGui.QIcon(QtCore.QString("resources/red16x16.png"))
        self.green = QtGui.QIcon(QtCore.QString("resources/green16x16.png"))
        self.yellow = QtGui.QIcon(QtCore.QString("resources/yellow16x16.png"))
        self.tray = QtGui.QSystemTrayIcon(self.yellow)
        #super(QtGui.QSystemTrayIcon, self).__init__(self.black)
        #self.trayMenu
        #self.timer = QtCore.QTimer()
        #self.timer.setInterval(1000)
        #self.timer.timeout.connect(self.switchFrame)
        #self.timer.start()
        self.currentFrame = 0
        self.activity = 'slack'
        
    def switchFrame(self):
        if self.currentFrame == 0:
            self.currentFrame = 1
            if self.activity == 'slack':
                self.tray.setIcon(self.red)
            elif self.activity == 'work':
                self.tray.setIcon(self.green)
            elif self.activity == 'afk':
                self.tray.setIcon(self.yellow)
        elif self.currentFrame == 1:
            self.tray.setIcon(self.black)
            self.currentFrame = 0
        self.tray.show()
        #print('updating tray icon...')
    def enable(self):
        self.tray.show()
    def hide(self):
        self.tray.hide()
        
########## 
#########        
