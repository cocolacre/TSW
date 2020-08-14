import gc
import sip
sip.setapi('QString', 1)
from PyQt4 import QtCore, QtGui,QtSql, QtTest
#from PyQt4 import QtCore, QtGui, QtTest,QtSql
from PyQt4 import Qt as _Qt
import queue, copy
import sys,time
from PyQt4.QtCore import *
from PyQt4.QtGui import *
import subprocess as sp
import os,ctypes
import random
import datetime
import sqlite3
import cv2
import uuid
from ctypes import wintypes as wt

import screen,keyboard
from StorageQt import StorageQt
from Task import Task
from ScreenCapturer import ScreenCapturer
from KeyboardLog import KeyboardLog
from Camera import Camera
from Sound import Sound
from TabSettingsWidget import TabSettingsWidget
from NewTaskDialog import NewTaskDialog
from ReminderJackWidget import ReminderJackWidget
from BreakReasonDialog import BreakReasonDialog
from BehaviourJournal import BehaviourJournal
from Timeline import Timeline


POINT = wt.POINT

GetSystemMetrics = ctypes.windll.user32.GetSystemMetrics
GetMonitorInfo = ctypes.windll.user32.GetMonitorInfoA
GetAsyncKeyState = ctypes.windll.user32.GetAsyncKeyState

myappid = u'cocolacre.TaskStackWidget'
ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID(myappid)

#class regularTable(QObject):
    
class FocusOutFilter(QObject):
    focusOut = pyqtSignal()

    def eventFilter(self, widget, event):
        #print(widget)
        if event.type() == QEvent.FocusOut:
            self.focusOut.emit()
            return False
        else:
            return False
            
class KeyPressFilter(QObject):
    f2_pressed = pyqtSignal()
    #app = ''
    def eventFilter(self, widget, event):
        if event.type() == QEvent.ShortcutOverride:
            #print('KeyPressFilter: event.type:', event.type())
            #print('event.nativeScanCode(), event.key():',event.nativeScanCode(), event.key())
            # TAB: 15 16777217 
            if event.nativeScanCode() == 15: #TAB
                #print('TAB PRESSED: ', widget,widget.app)
                focusWidget = widget.app.focusWidget()
                classname = focusWidget.metaObject().className()
                if classname not in ["QGraphicsView","QTreeWidget"]:
                    return True
                elif classname == "QGraphicsView":
                    print('TAB pressed within QGraphicsView')
                    #widget.treeWidget.setFocus()
                    return True
                elif classname == "QTreeWidget":
                    print('TAB pressed within QTreeWidget')
                    #widget.TimeLine.view.setFocus()
                    
                return True
            else:
                return False
                
        if event.type() == QEvent.KeyPress: #TAB not registered.
            print('KeyPressFilter: ', event.key(), event.nativeScanCode())
            print('treeWidget has focus: ', widget.treeWidget.hasFocus())
            keys = {'F2':60}
            if widget.treeWidget.hasFocus() and event.nativeScanCode() == keys['F2']:
                print('Emitting f2_pressed')
                self.f2_pressed.emit()
                #return False
            return False
        else:
            return False
        
class TimeLineGraphicsScene(QtGui.QGraphicsScene):
    pass
    #def __init__(self):
    #    su
class TimeLineWidget(QtGui.QWidget):
    pass
    #self.scene=TimeLineScene(

class ScrollKeeper(QtGui.QTextEdit):
    autosave_signal = pyqtSignal()
    def __init__(self, text=''):
        super(QtGui.QTextEdit, self).__init__(text)
        self.setFocusPolicy(QtCore.Qt.ClickFocus)
        self.focusOutFilter = FocusOutFilter()
        self.installEventFilter(self.focusOutFilter)
        self.focusOutFilter.focusOut.connect(self.focusLost)
        self.textChanged.connect(self.autosave)
        self.taskDescriptionEditCounter = 0
    def autosave(self):
        self.taskDescriptionEditCounter +=1
        if self.taskDescriptionEditCounter % 10 == 0:
            self.autosave_signal.emit()
    def focusLost(self):
        print('THE ENEMY HAS TAKEN CONTROL OF THE FOCUS!') # ;)
        
class TaskStackWidget(QtGui.QTabWidget):
    keyPressed = QtCore.pyqtSignal(QtCore.QEvent)
    updateLoopJack = QtCore.pyqtSignal()
    
    def __init__(self,parent=None,app=None):
        super(TaskStackWidget, self).__init__()
        self.app = app
        
        self.setFocusPolicy(QtCore.Qt.ClickFocus)
        self.setWindowTitle("Task Stack")
        self.setWindowIcon(QtGui.QIcon('resources/48x48.png'))
        self.move(-10,0)
        self.H = 600 #TODO: get taskbar height. Get monitor handle etc.
        ###### Main window settings ########
        alpha = 0.999
        self.W = int(GetSystemMetrics(0)*alpha)
        self.H = GetSystemMetrics(1)-50
        self.resize(self.W, self.H)
        self.setWindowFlags(QtCore.Qt.CustomizeWindowHint)
        self.time_started = time.time()
        self.tasksWidget = QtGui.QWidget(parent=self)
       
        self.storage = StorageQt()
        self.q = self.storage.q
        self.main_table = 'tasks'
        self.reminders = []
        #### <SOUNDS> ####
        self.sound = Sound()
        #### </SOUNDS> ####
        
        #### taskData ####
        self.taskData = QtGui.QWidget(parent=self.tasksWidget)
        self.taskData.setFocusPolicy(QtCore.Qt.ClickFocus)
        self.taskData.setContentsMargins(0,0,0,0)
        #style = "margin: 0px 0px 0px 0px; background-color: honeydew; border-style : solid;"
        style = "background-color: honeydew; border-style : solid;"
        self.taskData.setStyleSheet(style)

        #### taskDataBox ####
        self.taskDataBox = QtGui.QVBoxLayout()
        self.taskDataBox.setSpacing(0)
        self.taskDataBox.setContentsMargins(0,0,0,0)

        #### taskControl ####
        self.taskControl = QtGui.QWidget(parent=self.tasksWidget)
        self.taskControl.setFocusPolicy(QtCore.Qt.ClickFocus)
        style = "background-color: #ffffff; border-style : solid;"
        #self.taskControl.setStyleSheet(style)
        alpha = 0.45 #taskControl and taskData widgets width ratio.
        self.taskControl.resize(int(self.W * alpha), self.H)
        #self.taskControl.setFixedWidth(int(self.W * alpha)+200)
        
        self.taskData.resize(int(self.W * (1.0-alpha)), self.H)
        self.taskData.setMinimumWidth(int(self.W*(1-alpha)))
        self.taskData.setFixedSize(int(self.W*(1-alpha)), self.H)
        style = "border: 0"
        self.taskData.setStyleSheet(style)        
        
        #### taskData.name ####
        self.taskData.name = QtGui.QLabel('Name')
        self.taskData.name.move(0,0)
        self.taskData.name.setFixedSize(200,15)
        style = "background-color: #ffa500; border-style : solid; border-width : 1px"
        self.taskData.name.setStyleSheet(style)

        #### taskData.descriptionLabel ####
        self.taskData.descriptionLabel = QtGui.QLabel('Description:')
        style = "background-color: ghostwhite; border-style : solid; border-width : 1px"
        style = style + '; color : gray'
        self.taskData.descriptionLabel.setFixedSize(100,15)
        self.taskData.descriptionLabel.setStyleSheet(style)

        #### taskData.description ####
        #self.taskData.description = ScrollKeeper(parent = self.taskData)
        self.taskData.description = ScrollKeeper()
        self.taskData.description.autosave_signal.connect(self.save_task_description)
        #self.taskDescriptionEditCounter = 0
        self.taskData.description.setFixedSize(330,350)
        self.taskData.description.setAcceptRichText(False)
        oca = QtGui.QIcon(QtCore.QString('resources/oca.gif'))
        inv = QtGui.QIcon(QtCore.QString('resources/folder-2.png'))
        self.taskData.saveDescriptionButton=QtGui.QPushButton(oca,'Save',parent=self.taskData)
        self.taskData.bigOpenTaskFolderButton=QtGui.QPushButton(inv,'Folder',parent=self.taskData)
        self.taskData.bigOpenTaskFolderButton.setIconSize(QtCore.QSize(27,27))
        style = "background-color: lightgreen; border-style : solid; border-width : 1px"
        style = "background-color: snow; border: 1px; border-style : solid;"
        self.taskData.description.setStyleSheet(style)
        self.taskData.description.setText('?'*256)
        self.taskData.description.move(0,30)
        self.taskData.description.focusOutFilter.focusOut.connect(self.save_task_description)

        #### taskData.saveDescriptionButton ####
        self.taskData.saveDescriptionButton.setStyleSheet(style)
        self.taskData.bigOpenTaskFolderButton.setStyleSheet(style)
        self.taskData.saveDescriptionButton.setFixedSize(70,30)
        self.taskData.bigOpenTaskFolderButton.setFixedSize(70,30)
        self.taskData.saveDescriptionButton.clicked.connect(self.save_task_description)
        self.taskData.bigOpenTaskFolderButton.clicked.connect(self.open_task_folder)

        self.taskDataBox.addWidget(self.taskData.name)
        #self.taskData.name.move(0,0)
        #self.taskDataBox.addWidget(self.taskData.descriptionLabel)
        self.taskDataControls = QtGui.QWidget()
        style = "background-color: lightgreen; border-style : solid; border-width : 1px"
        self.taskDataControls.setStyleSheet(style)
        self.taskDataControlsBox = QtGui.QHBoxLayout()
        #self.taskDataControlsBox.addWidget(self.openTaskFolderButton)
        #self.taskDataControlsBox.addWidget(self.taskData.saveDescriptionButton)
        self.taskDataControlsBox.setSpacing(0)
        self.taskDataControls.setMaximumWidth(330)
        self.taskDataControlsBox.addWidget(self.taskData.bigOpenTaskFolderButton)
        self.taskDataControlsBox.addWidget(self.taskData.saveDescriptionButton)
        self.taskDataControlsBox.setContentsMargins(0,0,0,0)
        self.taskDataControlsBox.setSpacing(0)
        self.taskDataControls.setLayout(self.taskDataControlsBox)
        #self.taskDataBox.addWidget(self.taskData.saveDescriptionButton)
        self.taskDataBox.addWidget(self.taskData.description)
        self.taskDataBox.addWidget(self.taskDataControls)
        self.taskDataBox.setContentsMargins(0,0,0,0)
        self.taskDataBox.setSpacing(0)


        #### OUTPUT ############
        self.output = QtGui.QWidget()
        #### OUTPUT ############
        #### tasksWidgetBox ####
        self.tasksWidgetBox = QtGui.QHBoxLayout()
        self.tasksWidgetBox.setContentsMargins(0,0,0,0)
        self.taskDataBox.setSpacing(0)
        self.tasksWidgetBox.setSpacing(0)
        self.taskDataBox.addStretch()
        self.tasksWidgetBox.addWidget(self.taskControl)
        self.taskDataBox.addStretch()
        self.tasksWidgetBox.addWidget(self.taskData)
        self.taskDataBox.addStretch()
        self.tasksWidgetBox.addWidget(self.output)
        self.taskDataBox.addStretch()
        
        self.tasksWidget.setLayout(self.tasksWidgetBox)
        self.taskData.setLayout(self.taskDataBox)
        self.taskDataBox.setSpacing(0)
        
        ### timeline widget
        #self.TimeLineViewPort = QtGui.QWidget()
        #set temp style
        #self.TimeLine.setStyleSheet("background-color : rgb(40,40,40);")
        #self.TimeLine.setFixedHeight(150)
        #self.TimeLine = Timeline(self.TimeLineViewPort)
        #self.TimeLineBox = QtGui
        self.TimeLine = Timeline()
        #self.TimeLine.load_pixmaps()
        #self.TimeLineViewPort.setFixedHeight(150)
        ###
        
        ### set vertical layout here. 
        # specimen advance progress\process\procedure interactive engagement and navigation system.
        # (sorry this is dumb)
        self.SAP = QtGui.QWidget(parent=self) #specimen advance panel
        self.SAPBox = QtGui.QVBoxLayout()
        self.SAPBox.addWidget(self.tasksWidget)
        #self.SAPBox.addWidget(self.TimeLineViewPort)
        self.SAPBox.addWidget(self.TimeLine.view)
        self.SAP.setLayout(self.SAPBox)
        ###
        
        self.tab2 = QtGui.QWidget()
        #self.addTab(self.tasksWidget, "tasks")
        self.addTab(self.SAP, "SAP")
        self.addTab(self.tab2, "tab2")
        self.settingsWidget = TabSettingsWidget()
        self.addTab(self.settingsWidget, "ϾϓϿ")
        #self.H = GetMonitorInfo.rcWork #spectroWidth, spectroHeight
        
        #### treeWidget ####
        self.treeWidget = QtGui.QTreeWidget()
        #self.treeWidget.
        self.KeyPressFilter = KeyPressFilter()
        self.installEventFilter(self.KeyPressFilter)
        self.KeyPressFilter.f2_pressed.connect(self.f2_edit_item)
        #self.treeWidget.setSelectionMode(QtGui.QAbstractItemView.MultiSelection)
        self.treeWidget.setSelectionMode(QtGui.QAbstractItemView.ExtendedSelection)
        self.treeWidget.setColumnCount(8)        
        self.treeWidget.headerItem().setText(0,'Name')
        self.treeWidget.setColumnWidth(0,280)
        self.treeWidget.headerItem().setText(1,'№')
        self.treeWidget.setColumnWidth(1,30)
        self.treeWidget.headerItem().setText(2,'Age')
        self.treeWidget.setColumnWidth(2,53)
        self.treeWidget.headerItem().setText(3,'Status')
        self.treeWidget.setColumnWidth(3,60)
        self.treeWidget.headerItem().setText(4,'')
        self.treeWidget.headerItem().setIcon(4,QtGui.QIcon(QtCore.QString('resources/priorities.png')))
        self.treeWidget.setColumnWidth(4,25)
        self.treeWidget.headerItem().setText(5,'Lead T')
        self.treeWidget.setColumnWidth(5,53)
        self.treeWidget.headerItem().setText(6,'Spent T')
        self.treeWidget.setColumnWidth(6,49)
        self.treeWidget.headerItem().setText(7,'Pred. T')
        self.treeWidget.setColumnWidth(7,49)
        self.treeWidget.itemChanged.connect(self.updateTaskItem)
        self.treeWidget.currentItemChanged.connect(self.currentItemChanged)
        self.treeWidget.itemDoubleClicked.connect(self.edit_item)
        self.temporalControlWidget = QtGui.QWidget()
        style = "background-color: rgb(240,240,255); border-width : 1px;"
        self.temporalControlWidget.setStyleSheet(style)
        self.temporalControlWidgetBox = QtGui.QHBoxLayout(self.temporalControlWidget)
        self.temporalControlWidgetBox.setContentsMargins(0,0,0,0)
        self.temporalControlWidgetBox.setSpacing(0)
        #self.temporalControlWidgetBox.addStretch()
        style = "border-width : 1px; border-style : solid;"
        self.tsl = QtGui.QLabel('Task stack')
        self.tsl.setStyleSheet(style)
        self.tsl.setFixedWidth(66)
        self.temporalControlAfkLabel=QtGui.QLabel()
        self.temporalControlAfkLabel.setStyleSheet(style)
        self.temporalControlAfkLabel.setFixedWidth(66)
        self.temporalControlWorkButton = QtGui.QPushButton('ТРУД')
        self.temporalControlAfkLabel.setStyleSheet(style)
        self.temporalControlWorkLabel=QtGui.QLabel()
        self.temporalControlWorkLabel.setFixedWidth(66)
        self.temporalControlWorkLabel.setStyleSheet(style)
        self.temporalControlSlackButton = QtGui.QPushButton('ПЕРЕРЫВ')
        self.temporalControlSlackLabel=QtGui.QLabel()
        self.temporalControlSlackLabel.setFixedWidth(66)
        self.temporalControlWidgetBox.addWidget(self.tsl)
        self.temporalControlWidgetBox.addWidget(self.temporalControlAfkLabel)
        self.temporalControlWidgetBox.addWidget(self.temporalControlSlackButton)
        self.temporalControlWidgetBox.addWidget(self.temporalControlSlackLabel)
        self.temporalControlWidgetBox.addWidget(self.temporalControlWorkButton)
        self.temporalControlWidgetBox.addWidget(self.temporalControlWorkLabel)
        #################################
        ###      STATUS LABEL         ###
        #################################
        self.statusLabel = QtGui.QLabel('Status label')
        self.statusWarningPixmap = QtGui.QPixmap(QtCore.QString('resources/warning-small.png'))
        self.statusIcon = QtGui.QLabel('')
        self.statusIcon.setPixmap(self.statusWarningPixmap)
        self.statusLabel.setStyleSheet('background-color: rgb(200,200,200)') 
        #################################
        self.temporalControlWidgetBox.addWidget(self.statusLabel)
        self.temporalControlWidgetBox.addWidget(self.statusIcon)
        self.temporalControlWorkButton.setStyleSheet('font-weight: bold; color: rgb(170,15,236)')
        self.temporalControlSlackButton.setStyleSheet('font-weight: bold; color: rgb(170,15,236)')
        self.temporalControlWidgetBox.addStretch()
        self.temporalControlWorkButton.clicked.connect(self.toogle_activity)
        self.temporalControlSlackButton.clicked.connect(self.toogle_activity)
        self.activity = 'work'
        self.prev_activity = 'slack'
        self.activityTimer = QtCore.QTimer()
        self.activityTimer.setInterval(1000)
        self.activityWorkPeriod = 0
        self.activitySlackPeriod = 0
        self.activityAfkPeriod = 0
        self.activityTimer.timeout.connect(self.update_activity_timers)
        
        ### TRAY ###
        new_tray = True
        #new_tray = not True
        if new_tray:
            from AnimatedTray import AnimatedTray
            self.tray = AnimatedTray()
            self.tray.activity = 'slack'
            self.activityTimer.timeout.connect(self.tray.switchFrame)
            self.tray.enable()
        else:
            self.trayIcon = QtGui.QIcon(QtCore.QString('resources/card-2.png'))
            self.tray = QtGui.QSystemTrayIcon(self.trayIcon)
            self.trayMenu = QtGui.QMenu(QtCore.QString('Hey!'))
            self.tray.show()
        
        self.prev_activity_timer_timeout = time.time() - 2 #hack
        self.activityTimer.start()
        
        ##############################################        
        ###     TARGET\CURRENT TASKS TASK LABEL    ###
        ##############################################        
        
        ### <OLD> ###
        self.targetTasksWidgetBox = QtGui.QVBoxLayout()
        self.targetTasksWidget = QtGui.QWidget()
        self.targetTasksWidget.setFixedHeight(90)
        #self.targetTasksList = QtGui.QLabel('placeholder for QListWidget for targetetd tasks')
        self.targetTasksList = QtGui.QListWidget()
        self.targetTasksWidgetBox.setContentsMargins(0,0,0,0)
        self.targetTasksWidgetBox.setSpacing(0)
        self.targetTasksWidgetBox.addWidget(self.targetTasksList)    
        self.targetTasksList.setFixedHeight(88)
        self.targetTasksWidget.setLayout(self.targetTasksWidgetBox)
        ### </OLD> ###
        
        ### <NEW> ###
        #self.targetTaskTableWidget=QtGui.QTableWidget(1,6)
        #self.targetTaskTableWidget.setColumnWidth(0,270)
        #self.targetTaskTableWidget.setColumnWidth(1,30)
        #self.targetTaskTableWidget.setColumnWidth(2,90)
        #self.targetTaskTableWidget.setColumnWidth(3,90)
        #
        #self.targetTaskTableWidget.setRowHeight(0,22)
        #
        #self.targetTaskTableWidget.setFixedHeight(120)
        #self.targetTaskTableWidget.verticalHeader().setVisible(False)
        #
        #
        #self.targetTaskHeaderName = QtGui.QTableWidgetItem()
        #self.targetTaskHeaderName.setText('Name')
        ##self.targetTaskHeaderName.setFixedWidth(265)
        #self.targetTaskTableWidget.setHorizontalHeaderItem(0,self.targetTaskHeaderName)
        #
        #self.targetTaskHeaderNumber = QtGui.QTableWidgetItem()
        #self.targetTaskHeaderNumber.setText('№')
        #self.targetTaskTableWidget.setHorizontalHeaderItem(1,self.targetTaskHeaderNumber)
        #
        #self.targetTaskHeaderAge = QtGui.QTableWidgetItem()
        #self.targetTaskHeaderAge.setText('Age')
        #self.targetTaskTableWidget.setHorizontalHeaderItem(2,self.targetTaskHeaderAge)
        #
        #self.targetTaskHeaderSpent = QtGui.QTableWidgetItem()
        #self.targetTaskHeaderSpent.setText('Spent')
        #self.targetTaskTableWidget.setHorizontalHeaderItem(3,self.targetTaskHeaderSpent)
        #
        #self.targetTaskTableWidget.horizontalHeader().setFixedHeight(20)
        
        self.loopJack = QtGui.QWidget()
        self.loopJackBox = QtGui.QHBoxLayout()
        self.sumAfkText = QtGui.QLabel('Total AFK:')
        self.sumAfkText.setFixedWidth(48)
        self.sumWorkText = QtGui.QLabel('Total work:')
        self.sumWorkText.setFixedWidth(53)
        self.sumSlackText = QtGui.QLabel('Total slack:')
        self.sumSlackText.setFixedWidth(53)
        self.sumAfk = QtGui.QLabel('?')
        self.sumAfk.setFixedWidth(42)
        self.sumWork = QtGui.QLabel('?')
        self.sumWork.setFixedWidth(42)
        self.sumSlack = QtGui.QLabel('?')
        self.sumSlack.setFixedWidth(42)
        
        for widget in [
                       self.sumWorkText  , self.sumWork,
                       self.sumSlackText , self.sumSlack,
                       self.sumAfkText   , self.sumAfk
                      ]:
            self.loopJackBox.addWidget(widget)
        self.reminderJack = ReminderJackWidget(parent=self)
        #self.reminderJack.load_reminders()
        self.loopJackBox.addWidget(self.reminderJack)
        self.loopJack.setLayout(self.loopJackBox)
        self.target16x16 = QtGui.QIcon(QtCore.QString("resources/target16x16.png"))
        
        self.targeted_task = ''
        ### </NEW> ###
        
        
        
        self.addTaskIcon = QtGui.QIcon(QtCore.QString('resources/add.png'))
        self.addChildIcon = QtGui.QIcon(QtCore.QString('resources/child.png'))
        self.removeTaskIcon = QtGui.QIcon(QtCore.QString('resources/remove.png'))
        self.completeTaskIcon = QtGui.QIcon(QtCore.QString('resources/complete.png'))
        self.upTaskIcon = QtGui.QIcon(QtCore.QString('resources/up.png'))
        self.downTaskIcon = QtGui.QIcon(QtCore.QString('resources/down.png'))
        self.LoadIcon = QtGui.QIcon(QtCore.QString('resources/load.png'))
        self.targetIcon = QtGui.QIcon(QtCore.QString('resources/target.png'))
        #camera button
        self.CameraIcon = QtGui.QIcon(QtCore.QString('resources/camera.png'))
        self.CameraStartIcon = QtGui.QIcon(QtCore.QString('resources/camera-start.png'))
        self.CameraStopIcon = QtGui.QIcon(QtCore.QString('resources/camera-stop.png'))
        #screen 
        self.ScreenIcon = QtGui.QIcon(QtCore.QString('resources/screen.png'))
        self.ScreenStartIcon = QtGui.QIcon(QtCore.QString('resources/screen-start.png'))
        self.ScreenStopIcon = QtGui.QIcon(QtCore.QString('resources/screen-stop.png'))
        self.CloseIcon = QtGui.QIcon(QtCore.QString('resources/close.png'))
        self.SleepIcon = QtGui.QIcon(QtCore.QString('resources/clip.png'))
        
        self.FingersIcon = QtGui.QIcon(QtCore.QString('resources/fingers.png'))
        self.FingersStartIcon = QtGui.QIcon(QtCore.QString('resources/fingers-start.png'))
        self.FingersStopIcon = QtGui.QIcon(QtCore.QString('resources/fingers-stop.png'))
        self.SettingsIcon = QtGui.QIcon(QtCore.QString('resources/settings.png'))
        self.EvilBoneIcon = QtGui.QIcon(QtCore.QString('resources/EvilBone.gif'))
        self.taskDescriptionIcon = QtGui.QIcon(QtCore.QString('resources/jelly.png'))
        self.filterEditIcon = QtGui.QIcon(QtCore.QString('resources/identify.png'))
        self.priorityUpIcon = QtGui.QIcon(QtCore.QString('resources/priority-up.png'))
        self.priorityDownIcon = QtGui.QIcon(QtCore.QString('resources/priority-down.png'))
        self.InventoryIcon = QtGui.QIcon(QtCore.QString('resources/folder-2.png'))
        self.RestartIcon = QtGui.QIcon(QtCore.QString('resources/restart.gif'))
        self.QuickTaskIcon = QtGui.QIcon(QtCore.QString('resources/quick-task-note.png'))
        self.MicrophoneIcon = QtGui.QIcon(QtCore.QString('resources/mic-1.png'))
        self.SpellsIcon= QtGui.QIcon(QtCore.QString('resources/book-1.gif'))
        self.spellBooksIcons = [QtGui.QIcon(QtCore.QString('resources/book-%s.gif'%i)) for i in range(1,7)]
        self.clearTargetsIcon =QtGui.QIcon(QtCore.QString('resources/nv_basic.gif'))
        self.cmdIcon =QtGui.QIcon(QtCore.QString('resources/cmd.png'))
        self.forehexIcon = QtGui.QIcon(QtCore.QString('resources/asc_breaker.png'))

        self.closeApp = QtGui.QPushButton(self.CloseIcon, '')
        self.cmd = QtGui.QPushButton(self.cmdIcon, '')
        self.addTask = QtGui.QPushButton(self.addTaskIcon, '')
        self.addChild = QtGui.QPushButton(self.addChildIcon, '')
        self.removeTask = QtGui.QPushButton(self.removeTaskIcon, '')
        self.completeTask = QtGui.QPushButton(self.completeTaskIcon, '')
        self.upTask = QtGui.QPushButton(self.upTaskIcon, '')
        self.downTask = QtGui.QPushButton(self.downTaskIcon, '')
        self.loadTasks = QtGui.QPushButton(self.LoadIcon, '')
        self.targetTask = QtGui.QPushButton(self.targetIcon, '')
        self.editTaskDescription = QtGui.QPushButton(self.taskDescriptionIcon, '')
        self.filterEdit = QtGui.QPushButton(self.filterEditIcon, '')
        self.priorityUp = QtGui.QPushButton(self.priorityUpIcon, '')
        self.priorityDown = QtGui.QPushButton(self.priorityDownIcon, '')
        self.openTaskFolderButton = QtGui.QPushButton(self.InventoryIcon, '')
        self.restartAppButton = QtGui.QPushButton(self.RestartIcon,'')
        self.quickTaskButton = QtGui.QPushButton(self.QuickTaskIcon,'')
        self.microphoneButton = QtGui.QPushButton(self.MicrophoneIcon,'')
        self.sleepButton = QtGui.QPushButton(self.SleepIcon,'')
        self.clearTargets = QtGui.QPushButton(self.clearTargetsIcon,'')
        self.forehex = QtGui.QPushButton(self.forehexIcon, '')
        self.spellsButton = QtGui.QPushButton(self.SpellsIcon,'')
        self.spellButtonTimer = QtCore.QTimer()
        self.spellButtonTimer.setInterval(1000)
        self.spellButtonTimer.timeout.connect(self.spellbook_cycle)
        self.spellButtonTimer.start()
        QSize30 = QtCore.QSize(30,30)
        QSize33 = QtCore.QSize(33,33)
        QSize34 = QtCore.QSize(34,34)
        QSize35 = QtCore.QSize(35,35)
        QSize40 = QtCore.QSize(40,40)
        
        
        ####################################
        #### FIX ICON SIZE HERE if needed  #
        ####################################
        
        self.closeApp.setIconSize(QSize30)
        self.addTask.setIconSize(QSize30)
        self.addChild.setIconSize(QSize30)
        self.removeTask.setIconSize(QSize30)
        self.completeTask.setIconSize(QSize30)
        self.upTask.setIconSize(QSize30)
        self.downTask.setIconSize(QSize30)
        self.loadTasks.setIconSize(QSize30)
        self.targetTask.setIconSize(QSize30)
        self.editTaskDescription.setIconSize(QSize30)
        self.filterEdit.setIconSize(QSize30)
        self.priorityUp.setIconSize(QSize30)
        self.priorityDown.setIconSize(QSize30)
        self.openTaskFolderButton.setIconSize(QSize30)
        self.restartAppButton.setIconSize(QSize30)
        self.quickTaskButton.setIconSize(QSize30)
        self.microphoneButton.setIconSize(QSize30)
        self.spellsButton.setIconSize(QSize30)
        self.sleepButton.setIconSize(QSize30)
        self.clearTargets.setIconSize(QSize30)
        self.cmd.setIconSize(QSize30)
        self.forehex.setIconSize(QSize30)

        #self.openTaskFolderButton.setFixedSize(30,30)
        self.box = QtGui.QVBoxLayout()
        self.box.setSpacing(0)
        self.box.setContentsMargins(0,0,0,0)
        #WATCH OUT
        self.buttonPanel = QtGui.QWidget()
        self.buttonPanelBox = QtGui.QHBoxLayout()
        self.buttonPanelBox.setSpacing(0)
        self.buttonPanelBox.setContentsMargins(0,0,0,0)
        #self.buttonPanelBox.addStretch()
        self.buttonPanelBox.addWidget(self.upTask)
        self.buttonPanelBox.addWidget(self.downTask)
        self.buttonPanelBox.addWidget(self.addTask)
        self.buttonPanelBox.addWidget(self.addChild)
        self.buttonPanelBox.addWidget(self.removeTask)
        self.buttonPanelBox.addWidget(self.completeTask)
        self.buttonPanelBox.addWidget(self.loadTasks)
        self.buttonPanelBox.addWidget(self.targetTask)
        self.buttonPanelBox.addWidget(self.editTaskDescription)
        self.buttonPanelBox.addWidget(self.filterEdit)
        self.buttonPanelBox.addWidget(self.priorityUp)
        self.buttonPanelBox.addWidget(self.priorityDown)
        self.buttonPanelBox.addWidget(self.restartAppButton)
        self.buttonPanelBox.addWidget(self.sleepButton)
        self.buttonPanelBox.addWidget(self.clearTargets)
        #self.buttonPanel.resize(550,40)
        #this does not solve GAP problem.
        self.buttonPanelBox.setSpacing(0)
        #setSpacing(N) sets the minimum number of pixels that the QBoxLayout must place between items.
        self.buttonPanelBox.addStretch()
        self.buttonPanel.setLayout(self.buttonPanelBox)
        
        self.connect(self.closeApp, QtCore.SIGNAL('clicked()'), self.kill_all)
        self.connect(self.sleepButton, QtCore.SIGNAL('clicked()'), self.sleep)
        self.connect(self.addTask, QtCore.SIGNAL('clicked()'), self.add_task_proc)
        self.connect(self.addChild, QtCore.SIGNAL('clicked()'), self.add_child_proc)
        self.connect(self.removeTask, QtCore.SIGNAL('clicked()'), self.remove_task_proc)
        self.connect(self.loadTasks, QtCore.SIGNAL('clicked()'), self.load_tasks)
        self.connect(self.completeTask, QtCore.SIGNAL('clicked()'), self.complete_task)
        self.connect(self.targetTask, QtCore.SIGNAL('clicked()'), self.target_task)
        self.connect(self.editTaskDescription, QtCore.SIGNAL('clicked()'), self.description_edit)
        self.connect(self.filterEdit, QtCore.SIGNAL('clicked()'),self.filter_edit)
        self.connect(self.priorityUp, QtCore.SIGNAL('clicked()'), self.priority_up)
        self.connect(self.priorityDown, QtCore.SIGNAL('clicked()'), self.priority_down)
        self.connect(self.restartAppButton, QtCore.SIGNAL('clicked()'), self.restart_application)
        self.connect(self.openTaskFolderButton, QtCore.SIGNAL('clicked()'), self.open_task_folder)
        self.connect(self.clearTargets, QtCore.SIGNAL('clicked()'), self.clear_targeted_tasks)


        #### taggAdder ##########
        self.checkboxes = QtGui.QWidget()
        # CREATE TABLE IF NOT EXISTS tags 
        # CREATE TABLE IF NOT EXISTS selected_tags 
        #cmd = "SELECT * from tags"
        #self.query.ex(cmd)
        #cmd = "SELECT * from selected_tags"
        #self.query.ex(cmd)
		
		
		#########################
		
        #### taskFilterPanel ####
        self.taskFilterPanel = QtGui.QWidget()
        self.taskFilterPanelBox = QtGui.QHBoxLayout()
        self.taskFilterPanelBox.setSpacing(0)
        self.taskFilterPanelBox.setContentsMargins(0,0,0,0)
        self.taskFilterEdit =QtGui.QLineEdit()
        self.taskFilterEdit.setMinimumWidth(100)
        #self.taskFilterLabel = QtGui.QLabel('filter: ')
        self.taskFilterTumbler = QtGui.QCheckBox('filter: ')
        self.taskFilterHideDone = QtGui.QCheckBox('hide DONE')
        self.taskPriorityFilter = QtGui.QComboBox()
        self.taskPriorityFilter.addItem(QtCore.QString('0'))
        self.taskPriorityFilter.addItem(QtCore.QString('1'))
        self.taskPriorityFilter.addItem(QtCore.QString('2'))
        self.taskPriorityFilter.setMinimumWidth(50)
        self.taskPriorityFilter.setMaximumWidth(90)
        self.taskFilterPanelBox.addWidget(self.taskFilterHideDone)
        self.taskFilterHideDone.stateChanged.connect(self.hide_done)
        self.taskFilterPanelBox.addWidget(self.taskFilterTumbler)
        self.taskFilterPanelBox.addWidget(self.taskFilterEdit)
        self.taskFilterPanelBox.addWidget(self.taskPriorityFilter)
        
        #self.taskFilterPanelBox.addWidget(self.taggAdder)
        self.taskSortKey = QtGui.QComboBox()
        self.taskSortKey.setMinimumWidth(100)
        self.taskSortKey.addItem(QtCore.QString('id'))
        self.taskSortKey.addItem(QtCore.QString('priority'))
        self.taskSortKey.addItem(QtCore.QString('age'))
        self.taskSortKey.currentIndexChanged.connect(self.sort_index_changed)
        self.taskFilterPanelBox.addWidget(self.taskSortKey)
        #05:55
        style = "background-color: lightsteelblue; border-width : 1px; border-style : solid;"
        self.taskFilterPanel.setStyleSheet(style)
        self.taskFilterPanel.setLayout(self.taskFilterPanelBox)
        self.taskFilterPanel.setFixedWidth(200)
        self.taskFilterEdit.textChanged.connect(self.apply_filter)
        
        ### LOG BUTTONS
        self.toogleCameraButton=QtGui.QPushButton(self.CameraStartIcon,'')
        self.startCameraButton=QtGui.QPushButton(self.CameraStartIcon,'')
        self.stopCameraButton=QtGui.QPushButton(self.CameraStopIcon,'')
        
        self.toogleScreenLogButton=QtGui.QPushButton(self.ScreenIcon,'')
        self.toogleInputLogButton=QtGui.QPushButton(self.FingersIcon,'')
        self.settingsButton=QtGui.QPushButton(self.SettingsIcon,'')
        ####
        self.EvilBoneButton=QtGui.QPushButton(self.EvilBoneIcon,'')
        ####
        self.settingsButton.setIconSize(QSize33)
        self.settingsButton.setFixedSize(QSize35)
        self.toogleCameraButton.setIconSize(QSize33)
        self.toogleCameraButton.setFixedSize(QSize35)
        self.toogleScreenLogButton.setIconSize(QSize33)
        self.toogleScreenLogButton.setFixedSize(QSize35)
        self.toogleInputLogButton.setIconSize(QSize33)
        self.toogleInputLogButton.setFixedSize(QSize35)
        self.EvilBoneButton.setIconSize(QSize33)
        self.EvilBoneButton.setFixedSize(QSize35)
        
        self.connect(self.toogleScreenLogButton, QtCore.SIGNAL('clicked()'), self.toogle_capturer)
        self.connect(self.toogleCameraButton, QtCore.SIGNAL('clicked()'), self.toogle_webcam_capturer)
        self.connect(self.toogleInputLogButton, QtCore.SIGNAL('clicked()'), self.toogle_fingerlog)
        
        self.LogControlPanel = QtGui.QWidget()
        self.LogControlPanelBox = QtGui.QHBoxLayout()
        self.LogControlPanelBox.setSpacing(0)
        self.LogControlPanelBox.setContentsMargins(0,0,0,0)
        self.LogControlPanelBox.addWidget(self.toogleCameraButton)
        self.LogControlPanelBox.addWidget(self.toogleScreenLogButton)
        self.LogControlPanelBox.addWidget(self.toogleInputLogButton)
        self.LogControlPanelBox.addWidget(self.microphoneButton)
        self.LogControlPanelBox.addWidget(self.settingsButton)
        self.LogControlPanelBox.addWidget(self.EvilBoneButton)
        self.LogControlPanelBox.addWidget(self.spellsButton)
        self.LogControlPanelBox.addWidget(self.closeApp)
        self.LogControlPanelBox.addWidget(self.openTaskFolderButton)
        self.LogControlPanelBox.addWidget(self.quickTaskButton)
        self.LogControlPanelBox.addWidget(self.cmd)
        #TODO: move the following button to a better place.
        self.LogControlPanelBox.addWidget(self.forehex)
        #DELETE ME LATER  -for task#1547
        #self.toogleSortingEnabled = QtGui.QPushButton('tge')
        #self.toogleSortingEnabled.setFixedSize(35,35)
        #self.LogControlPanelBox.addWidget(self.toogleSortingEnabled)
        #self.toogleSortingEnabled.clicked.connect(self.toogle_sorting_enabled)
        
        self.LogControlPanelBox.setSpacing(0)
        self.LogControlPanelBox.addStretch()
        self.LogControlPanel.setLayout(self.LogControlPanelBox)
        
        self.taskControl.setLayout(self.box)
        self.box.addWidget(self.temporalControlWidget)
        #self.box.addWidget(self.targetTasksWidget)
        #self.box.addWidget(self.targetTaskTableWidget)
        self.box.addWidget(self.loopJack)
        self.box.addWidget(self.LogControlPanel)
        self.box.addWidget(self.buttonPanel)
        self.box.addWidget(self.taskFilterPanel)
        self.box.addWidget(self.treeWidget)
        
        self.statusBar = QtGui.QWidget()
        self.statusBarBox = QtGui.QHBoxLayout()
        self.statusBar.setLayout(self.statusBarBox)
        self.statusBarBox.setContentsMargins(0,0,0,0)
        self.statusBarBox.setSpacing(0)
        
        self.bytesLabel = QtGui.QLabel('0 bytes written')
        self.bytesLabel.setMaximumWidth(200)
        self.bytesLabel.setStyleSheet('background-color: #d3d3d3;')
        self.statusBarLabel = QtGui.QLabel('STATUS:[var1]=val1 var2=val2 var3=val3')
        
        #self.statusBarBox.addStretch()
        self.statusBarBox.addWidget(self.bytesLabel)
        self.statusBarBox.addWidget(self.statusBarLabel)
        self.statusBarBox.addStretch()
        self.box.addWidget(self.statusBar)
        
        self.backup_queue = queue.LifoQueue()
        print('TODO: add DB for tasks and backup!')
        self.debug = True
        self.running = True
        self.timer = QtCore.QTimer()
        self.capture_interval = 5
        self.timer.setInterval(self.capture_interval)
        self.thread = None
        self.capturer = None
        self.captured_bytes = 0
        self.webcam_capturer_state = False
        self.screen_capturer_state = False
        self.input_capturer_state = False

        ################################
        ########    SHORTCUTS    #######
        ################################
        self.shortcutExit = QtGui.QShortcut(QtGui.QKeySequence("Alt+Q"),self)
        self.shortcutExit.activated.connect(self.kill_all)
        self.shortcutAltA = QtGui.QShortcut(QtGui.QKeySequence("Alt+A"),self)
        self.shortcutAltA.activated.connect(self.add_task_hotkey_pressed)
        self.shortcutAltB = QtGui.QShortcut(QtGui.QKeySequence("Alt+B"),self)
        self.shortcutAltB.activated.connect(self.add_branch_hotkey_pressed)
        self.shortcutAltD = QtGui.QShortcut(QtGui.QKeySequence("Alt+D"),self)
        self.shortcutAltD.activated.connect(self.delete_task_hotkey_pressed)
        self.shortcutAltC = QtGui.QShortcut(QtGui.QKeySequence("Alt+C"),self)
        self.shortcutAltC.activated.connect(self.complete_task_hotkey_pressed)
        self.shortcutAltL = QtGui.QShortcut(QtGui.QKeySequence("Alt+L"),self)
        self.shortcutAltL.activated.connect(self.clear_targeted_tasks)
        self.shortcutAltT = QtGui.QShortcut(QtGui.QKeySequence("Alt+T"),self)
        self.shortcutAltT.activated.connect(self.target_task)
        self.shortcutAltS = QtGui.QShortcut(QtGui.QKeySequence("Alt+S"),self)
        self.shortcutAltS.activated.connect(self.sort_column_cycle)
        self.shortcutAltF = QtGui.QShortcut(QtGui.QKeySequence("Alt+F"),self)
        self.shortcutAltF.activated.connect(self.filter_edit)
        self.shortcutAltE = QtGui.QShortcut(QtGui.QKeySequence("Alt+E"),self)
        self.shortcutAltE.activated.connect(self.description_edit)
        self.shortcutAltR = QtGui.QShortcut(QtGui.QKeySequence("Alt+R"),self)
        self.shortcutAltR.activated.connect(self.open_task_folder) #open multiple folders if needed
        self.shortcutAltPlus = QtGui.QShortcut(QtGui.QKeySequence("Alt+="),self)
        self.shortcutAltPlus.activated.connect(self.priority_up)        
        self.shortcutAltMinus = QtGui.QShortcut(QtGui.QKeySequence("Alt+-"),self)
        self.shortcutAltMinus.activated.connect(self.priority_down)
        self.shortcutHide = QtGui.QShortcut(QtGui.QKeySequence("Alt+H"),self)
        self.shortcutHide.activated.connect(self.hide_done_checkbox_toogle)
        self.shortcutAltU = QtGui.QShortcut(QtGui.QKeySequence("Alt+U"), self)
        self.shortcutAltU.activated.connect(self.restart_application)
        self.shortcutAltV = QtGui.QShortcut(QtGui.QKeySequence("Alt+V"), self)
        self.shortcutAltV.activated.connect(self.open_task_folder_cmd)
        self.shortcutAltP = QtGui.QShortcut(QtGui.QKeySequence("Alt+P"), self)
        self.shortcutAltP.activated.connect(self.sleep)
        self.shortcutAltW = QtGui.QShortcut(QtGui.QKeySequence("Alt+W"), self)
        self.shortcutAltW.activated.connect(self.toogle_activity)
        #self.shortcutF1 = QtGui.QShortcut(self,QtCore.Qt.Key_F1, context=QtCore.Qt.WidgetShortcut)
        self.shortcutF1 = QtGui.QShortcut(QtCore.Qt.Key_F1,self)
        self.shortcutF1.activated.connect(self.open_behaviour_journal)
        ### !!! TODO: Fix this using slot-signal pattern and tab indexes
        self.shortcutAlt1 = QtGui.QShortcut(QtGui.QKeySequence("Alt+1"), self)
        self.shortcutAlt1.activated.connect(self.switchTab1)
        self.shortcutAlt2 = QtGui.QShortcut(QtGui.QKeySequence("Alt+2"), self)
        self.shortcutAlt2.activated.connect(self.switchTab2)
        self.shortcutAlt3 = QtGui.QShortcut(QtGui.QKeySequence("Alt+3"), self)
        self.shortcutAlt3.activated.connect(self.switchTab3)
        self.shortcutAltO = QtGui.QShortcut(QtGui.QKeySequence("Alt+O"),self)
        self.shortcutAltO.activated.connect(self.TimeLine.add_expected_behaviour_record_empty)
        
        #self.shortcutHide.activated.connect(self.hide_done)
        #starting keyboard logger
        self.toogle_fingerlog()
        
        #watch for AFK state.
        self.afkTimeout = 0.5
        self.afkTimer = QtCore.QTimer()
        self.afkTimer.setInterval(self.afkTimeout*1000)
        self.afkTimer.timeout.connect(self.check_afk)
        self.prevMouseMovementTime = 0
        self.prevMousePosition = (0,0)
        self.prevKeyboardEventTime = 0
        self.afkTimer.start()
        self.afkPeriod = 0
        self.afkMax = 240 #not seconds, but number of 2Hz afk-checks.
        
        
        self.tasks = [] # refs to Task objects or UUIDs?
        self.tasks_dict = {}
        self.done_hidden = False
        self.metadata = {}
        self.load_tasks()
        self.activity_log=[]
        self.daily_stats = []
        self.behaviour_records = []
        self.load_activity_log()
        self.load_behaviour_journal()
        self.load_metadata()
        
        self.current_task_id = 1
        self.previousFocus = self.tasks[len(self.tasks)-1]
        self.treeWidget.setSortingEnabled(True)
        #self.treeWidget.sortByColumn(1, 0)
        self.treeWidget.sortByColumn(1,0)
        self.currentTab = 0
        self.listWidgetItemNames = []
        self.lastBehaviourTimeCompleted = ''
        #timeline init.
        #for record in self.activity_log[-5500:]:
        for record in self.activity_log:
            self.TimeLine.add_activity_rect(record)
        #load tasks data to timeline within load_tasks.
        print('LOADING BEHAVIOUR RECORDS(and icons)):', len(self.behaviour_records))
        
        for record in self.behaviour_records:
            self.TimeLine.add_bj_record_icon(record)
        
        self.TimeLine.add_daily_stats(self.daily_stats)
        
        #self.regular_table_timer = QtCore.QTimer()
        #self.regular_table_timer.setInterval(3600*1000)
        #self.regular_table_timer.timeout.connect(self.open_regular_table)
        #self.regular_table_timer.start()
        
    def open_regular_table(self):
        #os.system('"c:\\Program Files (x86)\\OpenOffice 4\\program\\scalc.exe" "C:\\Users\\2\\Documents\\Task-Stack-Widget\\task-data\\2216\\regular_table.ods"')
        pass
        
    def make_widget(self, base=QtGui.QWidget, parent=None,focus_policy=QtCore.Qt.ClickFocus):
        widget = base(parent=parent)
        widget.setFocusPolicy(focus_policy)
        return widget
        
        
    def display(self):
        print('DISPLAY(SELF):')
        self.app.focusChanged.connect(self.report_focus_change)
        self.show()
        self.TimeLine.view.show()
        #for record in self.activity_log[-5500:]:
        #    self.TimeLine.add_activity_rect(record)
        #self.TimeLine.view.centerOn(0,0)
        
    def switchTab1(self):
        self.setCurrentIndex(0)
    def switchTab2(self):
        self.setCurrentIndex(1)
    def switchTab3(self):
        self.setCurrentIndex(2)    
    
    def load_activity_log(self):
        """
        Load activity_log table in a form of a list of lists\tuples\dicts?
        Let it be list of lists.
        So we can generate records' durations.
        
        """
        format_code = "%Y-%m-%d %H:%M:%S"

        #TODO: select initial record (replace 5500 with smth meaningful.
        #TODO: measure perfomance of Timeline rendering.
        #self.activity_log
        prev_record = None
        #cmd = "SELECT * FROM activity_log WHERE id > 5500"
        cmd = "SELECT * FROM activity_log WHERE id > 1"
        self.storage.ex(cmd)
        query = self.storage.q
        print('load_activity_log: query size:', query.size()) #-1
        
        while query.next():
            record = []
            record.append(query.value(0)) #id
            record.append(str(query.value(1))) #time
            record.append(0) #duration placeholder.
            record.append(str(query.value(2))) #name
            #record.append(int(time.mktime(time.strptime(record[1],format_code)))) #time_started(epoch)
            self.activity_log.append(record)
            #prev_record = record
        print('load_activity_log: len(self.activity_log):', len(self.activity_log)) #
        format_code = "%Y-%m-%d %H:%M:%S"
        for i in range(len(self.activity_log)-1):
            record = self.activity_log[i]
            record_time = str(record[1])
            next_record = self.activity_log[i+1]
            next_record_time = str(next_record[1]) #string
            #convert time string to seconds.
            #strptime : string -> tuple
            #mktime: tuple -> float(seconds)
            record_time_seconds = time.mktime(time.strptime(record_time,format_code))
            next_record_time_seconds = time.mktime(time.strptime(next_record_time,format_code))
            record_duration = next_record_time_seconds - record_time_seconds
            record[2] = record_duration
        print('load_activity_log: last 10 records:\n')
        for record in self.activity_log[-10:]:
            print(record)
        
        
        ATTENTION = """
        THE FOLLOWING CODE IS INCORRECT. FIX LATER. This is just to try drawing some stata.
        """
        prev_day = self.activity_log[0][1].split(' ')[0]
        day_work_sum = 0
        day_non_work_sum = 0
        day_poweroff_sum = 0
        daily_work_ratio = 0
        for record in self.activity_log[1:]:
            day = record[1].split(' ')[0]
            if day == prev_day:
                if record[3] == 'work':
                    day_work_sum += record[2] #add duration.
                elif record[3] == 'afk' or record[3] == 'slack':
                    day_non_work_sum += record[2]
                else:
                    day_poweroff_sum += record[2]
            else:
                day_stats = {'day': day,'work':int(day_work_sum), 'non-work':int(day_non_work_sum),
                'power off':int(day_poweroff_sum), 'work_to_nonwork':int(100*day_work_sum/(day_non_work_sum+0.001))}
                self.daily_stats.append(dict(day_stats))
                day_stats = {'day': day,'work':0, 'non-work':0,'power off':0,'work_to_nonwork':0}
                
                prev_day = day
                if record[3] == 'work':
                    #day_work_sum = record[2]
                    day_work_sum = 0
                elif record[3] == 'afk' or record[3] == 'slack':
                    #day_non_work_sum = record[2]
                    day_non_work_sum = 0
                elif record[3] == 'power off':
                    #day_poweroff_sum = record[2]
                    day_poweroff_sum = 0
        
    def load_metadata(self):
        self.metadata['targeted_task'] = ''
        cmd = "SELECT key, value FROM metadata"
        self.storage.ex(cmd)
        query = self.storage.q
        while query.next():
            self.metadata[str(query.value(0))]=str(query.value(1))
        #set targeted task.
        print('DEBUG load_metadata:')
        print(self.metadata)
        
        if 'targeted_task' in self.metadata and self.metadata['targeted_task'] != '':
            task_item = self.tasks_dict[self.metadata['targeted_task']]
            self.treeWidget.scrollToItem(task_item)
            self.treeWidget.setCurrentItem(task_item, 0)
            self.treeWidget.setItemSelected(task_item, True)
            task_item.setSelected(True)
            self.treeWidget.scrollToItem(task_item)
            self.target_task()
            time.sleep(0.5)
            self.treeWidget.scrollToItem(task_item, hint = QtGui.QAbstractItemView.EnsureVisible)
        
        #load loop jack data.
        cmd = "SELECT value FROM metadata WHERE key='work_time_sum'"
        work_sum = int(str(self.storage.fetch(cmd)))
        cmd = "SELECT value FROM metadata WHERE key='slack_time_sum'"
        slack_sum = int(str(self.storage.fetch(cmd)))
        cmd = "SELECT value FROM metadata WHERE key='afk_time_sum'"
        afk_sum = int(str(self.storage.fetch(cmd)))
        self.sumWork.setText(str(work_sum))
        self.sumSlack.setText(str(slack_sum))
        self.sumAfk.setText(str(afk_sum))
       
    def log_slack_reason(self):
        result = self.open_behaviour_journal()
        print("log_slack_reason:")
        if result != 0:
            # replace print with verbose logging print.
            print("result: != 0")
        else:
            print("log_slack_reason: result=0")
    
    def open_behaviour_journal(self):
        bj = BehaviourJournal(parent=self)
        bj.TimeLine = self.TimeLine
        bj.app = self.app
        result = bj.exec_()
        return result
    
    def load_behaviour_journal(self):
        cmd = "SELECT behaviour_classes.name, behaviour_journal.behaviourId,behaviour_journal.time_started, behaviour_journal.duration FROM behaviour_classes,behaviour_journal WHERE behaviour_classes.id=behaviour_journal.behaviourId"
        query = self.storage.q
        self.storage.ex(cmd)
        
        while query.next():
            record = type('',(dict,),{})()
            record.name = str(query.value(0))
            record.id = int(query.value(1))
            record.time_started = str(query.value(2))
            record.duration = int(query.value(3))
            self.behaviour_records.append(record)

    def get_total_slack(self, with_afk=True):
        if with_afk:
            cmd = "SELECT sum(strftime('%s',b.time) - strftime('%s',a.time)) FROM activity_log a, activity_log b WHERE b.rowid = a.rowid + 1 AND (a.activity = 'slack' OR (a.activity = 'afk' AND b.activity = 'slack'))"
        else:
            cmd = "SELECT sum(strftime('%s',b.time) - strftime('%s',a.time)) FROM activity_log a, activity_log b WHERE b.rowid = a.rowid + 1 AND a.activity = 'slack'"
        total_slack = self.storage.fetch(cmd)
        return total_slack
            
    def get_total_work(self):
        cmd = "SELECT sum(strftime('%s',b.time) - strftime('%s',a.time)) FROM activity_log a, activity_log b WHERE b.rowid = a.rowid + 1 AND a.activity = 'work'"
        total_work = self.storage.fetch(cmd)
        return total_work
    def open_task_folder_cmd(self):
        if self.current_task_id not in os.listdir('task-data'):
            os.system('mkdir task-data\{0}'.format(self.current_task_id))
        print('start cmd /K cd task-data\{0}'.format(self.current_task_id))
        sp.Popen('start cmd /K cd task-data\{0}'.format(self.current_task_id), shell=True)
        #os.system('cmd /K cd task-data\%d'%self.current_task_id)      
    def filter_edit(self):
        # https://forum.qt.io/topic/80019/find-which-widget-had-focus-when-menu-item-is-clicked/4
        # This is the function you're looking for.
        # 
        if self.taskFilterEdit.hasFocus():
            self.previousFocus.setFocus()
        else:
            self.previousFocus = self.app.focusWidget()
            self.taskFilterEdit.setFocus()

        # HIDDEN OPTION:
    def apply_filter(self, newtext):
        lower = str.lower
        newtext=lower(str(newtext))
        print(newtext)
        keywords = [str(keyword).strip() for keyword in newtext.lower().split(' ')]
        for task in self.tasks:
            if str(newtext)=='':
                self.treeWidget.setItemHidden(task, False)
                continue
            show = False
            for kw in [keyword.strip() for keyword in keywords]:
                show = show or str(task.name).lower().__contains__(kw)
                if show:
                    continue
            hide = not show
            self.treeWidget.setItemHidden(task, hide)

    def add_task_hotkey_pressed(self):
        self.add_task_proc()
    def add_branch_hotkey_pressed(self):
        self.add_child_proc()
    def delete_task_hotkey_pressed(self):
        self.remove_task_proc()
    def complete_task_hotkey_pressed(self):
        self.complete_task()
    def load_tasks_hotkey_pressed(self):
        """
        Add parameters to this method call 
        for task display filtering.
        """
        self.load_tasks()
    def open_task_folder(self):
        self.sound.open_stash()
        task_data_files = os.listdir('task-data')
        if str(self.current_task_id) not in task_data_files:
            # replace subprocess call with something better.
            #os.execlp('mkdir', 'task-data\%s'%str(self.current_task_id))
            res = sp.check_output('mkdir task-data\%s'%str(self.current_task_id), shell=True)
        #os.execlp('explorer', 'task-data\%s'%str(self.current_task_id))
        res = sp.check_output('explorer task-data\%s'%str(self.current_task_id))
    
    #def switch_mode(self):
    #    self.toogle_activity()

    def toogle_activity(self):
        self.activityTimer.stop()
        self.dbg_print('CURRENT activity:', self.activity)
        self.dbg_print('Previous activity:', self.prev_activity)
        if self.activity == 'afk':
            self.temporalControlSlackButton.setEnabled(True)
            self.temporalControlWorkButton.setEnabled(True)
            self.temporalControlAfkLabel.setStyleSheet('font-weight: bold; color: green')
            self.temporalControlSlackLabel.setStyleSheet('font-weight: normal; color: black')
            self.temporalControlWorkLabel.setStyleSheet('font-weight: normal; color: black')
            self.activity = str(self.prev_activity)
            self.prev_activity = 'afk'
        
        elif self.activity == 'work':
            #work--> slack
            self.sound.inhibit()
            self.dbg_print('work-->slack')
            self.activity = 'slack'
            self.prev_activity = 'work'
            #cmd = "INSERT INTO activity_log VALUES(NULL,'{0}','{1}')"
            #cmd = cmd.format(time.strftime("%Y-%m-%d %H:%M:%S"), self.activity)
            #self.storage.ex(cmd)
            self.add_new_current_activity_record()
            
            self.temporalControlSlackButton.setStyleSheet('font-weight: bold; color: grey')
            self.temporalControlWorkButton.setStyleSheet('font-weight: bold; color: rgb(170,15,236)')
            self.temporalControlSlackButton.setEnabled(False)
            self.temporalControlWorkButton.setEnabled(True)
            self.temporalControlSlackLabel.setStyleSheet('font-weight: bold; color: green')
            self.temporalControlWorkLabel.setStyleSheet('font-weight: normal; color: black')
            self.temporalControlAfkLabel.setStyleSheet('font-weight: normal; color: black')
            
            if not self.activityTimer.isActive():
                self.activityTimer.start()
            
            print('calling log_slack_reason !!!')
            self.log_slack_reason()
            print('toogle_activity: log_slack_reason call returned.')
            
            
        elif self.activity == 'slack':
            self.sound.initiate()
            self.dbg_print('slack-->work')
            #slack --> work
            self.activity = 'work'
            self.prev_activity = 'slack'
            
            #cmd = "INSERT INTO activity_log VALUES(NULL,'{0}','{1}')"
            #cmd = cmd.format(time.strftime("%Y-%m-%d %H:%M:%S"), self.activity)
            #self.storage.ex(cmd)
            self.add_new_current_activity_record()
            
            self.temporalControlWorkButton.setStyleSheet('font-weight: bold; color: grey')
            self.temporalControlSlackButton.setStyleSheet('font-weight: bold; color: rgb(170,15,236)')
            self.temporalControlWorkButton.setEnabled(False)
            self.temporalControlSlackButton.setEnabled(True)
            self.temporalControlWorkLabel.setStyleSheet('font-weight: bold; color: green')
            self.temporalControlSlackLabel.setStyleSheet('font-weight: normal; color: black')
            self.temporalControlAfkLabel.setStyleSheet('font-weight: normal; color: black')
        else:
            self.dbg_print('AFK activity detected on toogle.')
        self.dbg_print('After toogle(current):', self.activity)
        self.dbg_print('After toogle(prev):', self.prev_activity)
        if not self.activityTimer.isActive():
            self.activityTimer.start()
            self.lastBehaviourTimeCompleted = ''
    
    def get_last_actvity_record_id(self):
        pre_last_record_id = self.activity_log[-1:][0]
        cmd = "SELECT id FROM activity_log WHERE id > {0}".format(pre_last_record_id)
        last_record_id = self.storage.fetch(cmd)
        return last_record_id
        
    def update_activity_timers(self):
        
        ### determining if there was a machine shutdown\sleep. 
        current_time = time.time()
        activity_timer_delta = current_time - self.prev_activity_timer_timeout
        #if activity_timer_delta > self.activityTimer.interval() + 3
        if activity_timer_delta > 15:
            #log sleep activity interval.
            #determing the moment when self.activityTimer stopped.
            #convert time float to time string.
            format_code = "%Y-%m-%d %H:%M:%S"
            sleep_started = time.strftime(format_code, time.localtime(self.prev_activity_timer_timeout))
            print('update_activity_timers: SLEEP DELAY DETECTED!', sleep_started,' - ', time.ctime())

            cmd = "INSERT INTO activity_log VALUES(NULL,'{0}','{1}')"
            cmd = cmd.format(sleep_started, 'power off')
            self.storage.ex(cmd)
            #new_id = self.get_last_actvity_record_id()
            #
            new_record_id = self.activity_log[-1:][0][0]+1
            duration = int(activity_timer_delta)
            self.activity_log.append([new_record_id,sleep_started,duration,'power off'])
            
            cmd = "INSERT INTO activity_log VALUES(NULL,'{0}','{1}')"
            current_time_string = time.strftime("%Y-%m-%d %H:%M:%S")
            cmd = cmd.format(current_time_string, self.activity)
            self.storage.ex(cmd)
            self.activity_log.append([new_record_id+1,current_time_string,0,self.activity])

        self.prev_activity_timer_timeout  = current_time
        ### determined if there was a sleep\power off.
        
        
        if self.activity == 'afk':
            self.activityAfkPeriod+=1
            self.temporalControlAfkLabel.setText(self.format_time(self.activityAfkPeriod))
            self.sumAfk.setText(str(int(str(self.sumAfk.text()))+1))
            
            if self.activityAfkPeriod % 20 == 0: #update sum in db every 20 seconds
                cmd = "SELECT value FROM metadata WHERE key='afk_time_sum'"
                afk_sum = int(str(self.storage.fetch(cmd)))
                afk_sum += 20
                cmd = "UPDATE metadata SET value = {0} WHERE key = '{1}'".format(afk_sum, 'afk_time_sum')
                self.storage.ex(cmd)
                #self.updateLoopJack.emit()

        if self.activity == 'work':
            self.activityWorkPeriod+=1
            self.temporalControlWorkLabel.setText(self.format_time(self.activityWorkPeriod))
            self.sumWork.setText(str(int(str(self.sumWork.text()))+1))
            
            if self.metadata['targeted_task'] != '':
                self.tasks_dict[self.metadata['targeted_task']].time_spent = int(self.tasks_dict[self.metadata['targeted_task']].time_spent)+1
                if self.tasks_dict[self.metadata['targeted_task']].time_spent % 5 == 0:
                    self.update_spent_time()
            
            if self.activityWorkPeriod % 20 == 0: #update sum in db every 20 seconds
                cmd = "SELECT value FROM metadata WHERE key='work_time_sum'"
                res = self.storage.fetch(cmd)
                print('update_activity_timers:', self.activityWorkPeriod, res)
                work_sum = int(str(res))
                work_sum += 20
                cmd = "UPDATE metadata SET value = {0} WHERE key = '{1}'".format(work_sum, 'work_time_sum')
                self.storage.ex(cmd)
                #self.updateLoopJack.emit()

        if self.activity == 'slack':
            self.activitySlackPeriod+=1
            self.temporalControlSlackLabel.setText(self.format_time(self.activitySlackPeriod))
            self.sumSlack.setText(str(int(str(self.sumSlack.text()))+1))
            
            if self.activitySlackPeriod % 20 == 0: #update sum in db every 20 seconds
                cmd = "SELECT value FROM metadata WHERE key='slack_time_sum'"
                slack_sum = int(str(self.storage.fetch(cmd)))
                slack_sum += 20
                cmd = "UPDATE metadata SET value = {0} WHERE key = '{1}'".format(slack_sum, 'slack_time_sum')
                self.storage.ex(cmd)
                #self.updateLoopJack.emit()
                
        self.tray.activity = self.activity
    
    def update_last_activity_record(self):
        #last_record = self.activity_log[-1:]
        self.activity_log[-1:][2]+=1
        
    def update_spent_time(self):
        task_item = self.tasks_dict[self.metadata['targeted_task']]
        
        cmd = "UPDATE tasks SET time_spent = {0} WHERE uuid = '{1}'"
        cmd = cmd.format(task_item.time_spent, task_item.uuid)
        self.storage.ex(cmd)
        
        task_item.setText(6, str(task_item.time_spent))
    
    def format_time(self,seconds):
        t = int(seconds)
        D = int(t / 86400)
        t = int(t % 86400)        
        H = int(t / 3600)
        t = int(t % 3600)
        M = int(t / 60)
        S = int(t % 60)
        time_string = ''
        for i, item in enumerate([D,H,M,S]):
            if len(str(item)) == 1:
                time_string+='0'+str(item)+':'
            elif len(str(item)) == 2:
                time_string+=str(item)+':'
            else:
                time_string+=str(item)+'!ERROR!'
        time_string = time_string[:-1]
        return time_string

    def check_afk(self):
        pos = self.gcp()
        if pos != self.prevMousePosition:
            self.prevMousePosition = pos
            mouse_moved = True
        else:
            mouse_moved = False
        
        if self.finger_logger and self.finger_logger.running:
            if time.time() - self.finger_logger.prev_cap_time > self.afkTimeout:
                keyboard_pressed = False
            else:
                keyboard_pressed = True
        else:
            keyboard_pressed = False #since we do not actually know that.
        afk = not mouse_moved and not keyboard_pressed
        #if no user action was registered within 1 second
        if afk:
            self.afkPeriod +=1
            #if no user action was registered within "afkMax" period - toogle activity!
            if self.afkPeriod > self.afkMax and self.afkPeriod < self.afkMax+3:
                if self.capturer:
                    pass
                    #self.toogle_capturer()
                if self.activity != 'afk':
                    self.prev_activity = str(self.activity)
                    self.activity = 'afk'
                    
                    #cmd = "INSERT INTO activity_log VALUES(NULL,'{0}','{1}')"
                    #cmd = cmd.format(time.strftime("%Y-%m-%d %H:%M:%S"), self.activity)
                    #self.storage.ex(cmd)
                    # previous 3 lines are replaced with the following:
                    self.add_new_current_activity_record()
                    
                    self.tsl.setText('AFK['+self.prev_activity+']')
                    self.tsl.setStyleSheet('font-weight: bold; color: red')
                    self.temporalControlAfkLabel.setStyleSheet('font-weight: bold; color: green')
                    self.temporalControlSlackLabel.setStyleSheet('font-weight: normal; color: black')
                    self.temporalControlWorkLabel.setStyleSheet('font-weight: normal; color: black')
        else:
            self.afkPeriod = 0
            if self.activity == 'afk':
                if not self.capturer:
                    pass
                    # capturer auto-toogled here.
                    #self.toogle_capturer()
                self.dbg_print('Back from AFK. Restoring activity state afk-->%s'%self.prev_activity)
                self.activity = str(self.prev_activity)
                self.add_new_current_activity_record()
                self.prev_activity = 'afk'
                if self.activity == 'work':
                    self.temporalControlWorkLabel.setStyleSheet('font-weight: bold; color: green')
                    self.temporalControlSlackLabel.setStyleSheet('font-weight: normal; color: black')
                    self.temporalControlAfkLabel.setStyleSheet('font-weight: normal; color: black')
                elif self.activity == 'slack':
                    self.temporalControlSlackLabel.setStyleSheet('font-weight: bold; color: green')
                    self.temporalControlAfkLabel.setStyleSheet('font-weight: normal; color: black')
                    self.temporalControlWorkLabel.setStyleSheet('font-weight: normal; color: black')
                
                #returning from afk and switching back activity. 
                #adding new record.
                opt = 2 #see above ~ 12 lines.
                if opt == 0:
                    record_time = time.strftime("%Y-%m-%d %H:%M:%S"),
                    cmd = "INSERT INTO activity_log VALUES(NULL,'{0}','{1}')"
                    cmd = cmd.format(record_time, self.activity)
                    self.storage.ex(cmd)
                    new_record_id = self.activity_log[-1:][0]+1
                    record=[new_record_id, record_time,0,self.activity]
                    #cmd = "SELECT id FROM activity_log WHERE id > {0} and time='{1}'"
                    #cmd = cmd.format(self.activity_log[:-1][0], record_time)
                    #new_record_id = self.storage.fetch(cmd)
                    self.activity_log.append(record)
                elif opt == 1:
                    self.add_new_current_activity_record()
    
    def str_time_delta(self, first,second):
        """
        first, second - time strings with format="%Y-%m-%d %H:%M:%S"
        returns int(difference)
        """
        #TODO: add check for proper format.
        format_code = "%Y-%m-%d %H:%M:%S"
        first_tuple = time.strptime(first,format_code)
        second_tuple = time.strptime(second,format_code)
        first_int = time.mktime(first_tuple)
        second_int = time.mktime(second_tuple)
        delta = int(abs(first_int - second_int)) # no matter which is bigger.
        return delta
        
    def add_new_current_activity_record(self):
        print('add_new_current_activity_record called: ', self.activity)
        record_time = time.strftime("%Y-%m-%d %H:%M:%S")
        cmd = "INSERT INTO activity_log VALUES(NULL,'{0}','{1}')"
        cmd = cmd.format(record_time, self.activity)
        self.storage.ex(cmd)
        new_record_id = self.activity_log[-1:][0][0]+1
        record=[new_record_id, record_time,0,self.activity]
        #cmd = "SELECT id FROM activity_log WHERE id > {0} and time='{1}'"
        #cmd = cmd.format(self.activity_log[:-1][0], record_time)
        #new_record_id = self.storage.fetch(cmd)
        self.activity_log.append(record)
        
        #prev_duration = self.str_time_delta(
        #OH. I don't need it - we are already incrementing duration via timer.
        
    def kill_all(self):
        """
        Add cleanup here. 
        As of now, just kill the process.
        
        """
        #add state saving before process is killed (to DB)
        self.tray.hide()
        pid = os.getpid()
        os.system('taskkill /f /pid %d'%pid)
        
    def dbg_print(self, *data):
        if self.debug:
            print(data)
            
    def toogle_capturer(self):
        if self.screen_capturer_state:
            self.toogleScreenLogButton.setIcon(self.ScreenStartIcon)
            self.capturer.running = False
            self.kill_capturer()
            self.screen_capturer_state = False
        else:
            self.run_capturer()
            self.toogleScreenLogButton.setIcon(self.ScreenStopIcon)
            self.screen_capturer_state = True
        if self.debug:
            print('toogle screen log:', self.screen_capturer_state)

        
    def toogle_fingerlog(self):
        if self.input_capturer_state:
            self.toogleInputLogButton.setIcon(self.FingersStartIcon)
            self.input_capturer_state = False
            self.kill_finger_logger()
            self.dbg_print('[3]Toogling(off) keyboard logging')
        else:
            self.input_capturer_state = True
            self.toogleInputLogButton.setIcon(self.FingersStopIcon)
            self.run_fingerlog()
        if self.debug:
            print('toogle fingers log:', self.input_capturer_state)
    
    def toogle_webcam_capturer(self):
    
        if self.webcam_capturer_state:
            self.toogleCameraButton.setIcon(self.CameraStartIcon)
            self.webcam_capturer_state = False
            self.kill_webcam()
        else:
            self.toogleCameraButton.setIcon(self.CameraStopIcon)
            self.webcam_capturer_state = True
            self.run_webcam()
        if self.debug:
            print('toogle webcam log:', self.webcam_capturer_state)
            
    def run_fingerlog(self):
        self.thread_fingers = QtCore.QThread()
        self.finger_logger = KeyboardLog()
        self.finger_logger.finished_sig.connect(self.kill_all)
        self.finger_logger.moveToThread(self.thread_fingers)
        self.finger_logger.finished_sig.connect(self.kill_finger_logger)
        self.thread_fingers.started.connect(self.finger_logger.start_keyboard_logging)
        self.finger_logger.activate_sig.connect(self.activate_window)
        self.thread_fingers.start()
        if self.debug:
            print('running fingers log')
            
    def run_capturer(self):
        self.thread = QtCore.QThread()
        self.capturer = ScreenCapturer()
        self.capturer.moveToThread(self.thread)
        self.capturer.finished_sig.connect(self.kill_capturer)
        self.capturer.bytes_written_sig.connect(self.update_bytes_written)
        self.thread.started.connect(self.capturer.start_capturing)
        self.thread.start()
        if self.debug:
            print('started capturing...')
    
    
    @pyqtSlot()
    def run_webcam(self):
        self.thread_webcam = QtCore.QThread()
        self.webcam = Camera()
        self.webcam.moveToThread(self.thread_webcam)
        self.webcam.finished_sig.connect(self.kill_webcam)
        self.thread_webcam.started.connect(self.webcam.start_camera)
        self.thread_webcam.start()
        if self.debug:
            print('started webcam...')
            
    @pyqtSlot(int)
    def update_bytes_written(self, nBytes):
        self.captured_bytes+=nBytes
        elapsed = time.time() - self.time_started
        rate = int(self.captured_bytes/elapsed)
        self.bytesLabel.setText('Writting data:%s kB\\sec'%str(int(rate/1000.0)))


    @pyqtSlot()
    def kill_webcam(self):
        self.webcam.running = False
        self.thread_webcam.quit()
        self.thread_webcam.wait()
        if self.debug:
            print('Done killing webcamera')
        del self.webcam
        del self.thread_webcam
        self.thread_webcam=None
        self.webcam=None
        gc.collect()
        
    @pyqtSlot()
    def kill_capturer(self):
        self.thread.running = False
        self.thread.quit()
        self.thread.wait()
        if self.debug:
            print('Done killing capturer')
        del self.thread
        del self.capturer
        self.thread = None
        self.capturer = None
        gc.collect()
    
    @pyqtSlot()
    def kill_finger_logger(self):
        self.finger_logger.finished_sig.disconnect(self.kill_all)
        self.finger_logger.stop_keyboard_logging()
        self.dbg_print('Disconnected toogleInputLogButton signal') 
        self.finger_logger.requesting_stop = True
        counter = 0
        max_attempts = 50
        self.dbg_print('Quitting thread_fingers')
        self.thread_fingers.quit()
        while self.finger_logger.hooked and counter < max_attempts:
            self.dbg_print('Attempting to stop keyboard-logger thread')
            time.sleep(0.001)
            counter+=1
        del self.thread_fingers
        del self.finger_logger
        self.thread_fingers = None
        self.finger_logger = None
        gc.collect()
    
    def sleep(self):
        self.sound.phase_change()
        os.system('rundll32.exe powrprof.dll,SetSuspendState 0,1,0')
           
    def add_child_proc(self):
        parent = self.treeWidget.currentItem()
        task_item = Task( level = parent.level+1,parent = parent)
        parent.addChild(task_item)
    
    def add_task_proc(self):
        self.sound.jump()
        task_item = Task(popup=False)
        name = 'New task...'
        task_item.name = name
        
        #task_item.setFlags(task_item.flags() | QtCore.Qt.ItemIsEditable)
        task_item.setFlags(task_item.flags() & ~QtCore.Qt.ItemIsEditable)
        
        self.treeWidget.setSortingEnabled(True)
        self.treeWidget.addTopLevelItem(task_item)
        #nTasks = len(self.tasks)
        #lastTask = self.tasks[nTasks-1]
        #lastTaskIndex = self.treeWidget.indexFromItem(lastTask)
        #belowIndex = self.treeWidget.indexBelow(lastTaskIndex)
        #self.treeWidget.insertTopLevelItem(belowIndex.row()+1, task_item)
        #print('add_task_proc:')
        #print(nTasks, lastTaskIndex,lastTaskIndex.row(), belowIndex, belowIndex.row())

        self.treeWidget.scrollToItem(task_item)
        
        opt = 1
        if opt == 0:
            self.treeWidget.editItem(task_item, 0)
            time.sleep(0.3)        
            #time.sleep(0.3)        
            keyboard.send('ctrl+a')        
            # problem fix 1: via while loop.
            new_name_check_interval = 0.25
            new_name_wait_period = 10
            editor_started = time.time()
            while str(task_item.text(0)) == name:
                #time.sleep(new_name_check_interval)
                QtTest.QTest.qWait(new_name_check_interval*1000)
                if time.time() - editor_started > new_name_wait_period:
                    #task_item.setText(0, str(task_item.id))
                    task_item.setText(0, task_item.id)
                    #self.treeWidget.closePersistentEditor(task_item, 0)
                    break
            # problem fix 2: via openPersistentEditor.
        elif opt == 1:
            dialog = NewTaskDialog()
            result = dialog.exec_()
            if result != 0:
                #name = dialog.name
                task_item.name = str(dialog.nameEdit.text())
                task_item.time_spent_prediction = dialog.prediction
            else:
                task_item.time_spent_prediction = 15
                
            
        task_item.setText(0,task_item.name)
        
        #task_item.setText(7,str(task_item.time_spent_prediction)+' m')
        #time_spent_prediction_sec = task_item.time_spent_prediction*60
        task_item.setText(7,str(task_item.time_spent_prediction*60))
        
        name = task_item.text(0)
        query = self.storage.q
        cmd = "INSERT INTO {main_table} VALUES(NULL, '{0}','{1}',{2},'{3}','{4}','{5}',{6},'{7}', '{8}',{9},{10})".format(task_item.name, 
                                                       task_item.uuid,
                                                       task_item.level,
                                                       task_item.parent,
                                                       task_item.time_created, 
                                                       task_item.status,
                                                       task_item.priority,
                                                       task_item.description,
                                                       task_item.time_completed,
                                                       task_item.time_spent,
                                                       task_item.time_spent_prediction,
                                                       main_table=self.main_table)
        print('INSERT CMD: \n', cmd)
        self.storage.ex(cmd)
        self.dbg_print('Add error handling for db interaction code')
        self.last_created_tree_widget_item = task_item
        self.tasks.append(task_item)
        self.tasks_dict[task_item.uuid]=task_item
        cmd = "SELECT id FROM {main_table} WHERE uuid = '{0}'".format(task_item.uuid,
        main_table=self.main_table)
        id = self.storage.fetch(cmd)
        task_item.id = str(id) #correct id.
        self.current_task_id = str(id)
        print('add_task_proc:', id)
        task_item.setSortData(1,int(id))
        # REPLACE THIS WITH a descriptor logic later.
        task_item.setText(1,str(id))
        self.treeWidget.scrollToItem(task_item)
        self.treeWidget.setItemSelected(task_item, True)
        self.treeWidget.setCurrentItem(task_item)
        #self.treeWidget.setSortingEnabled(True)

    #def toogle_sorting_enabled(self):
    #    self.treeWidget.setSortingEnabled(not self.treeWidget.isSortingEnabled())
        
    def set_time_spent_prediction(self,task_item):
        dialog = NewTaskDialog()
        result = dialog.exec_()
        if result != 0:
            task_item.time_spent_prediction = dialog.prediction
            print('Predicted: ',task_item.time_spent_prediction)
        else:
            print('TimeSpentPredictionDialog canceled; prediction=',task_item.time_spent_prediction)
    
    def clear_targeted_tasks(self):
        cmd = "DELETE from targeted_tasks"
        self.storage.ex(cmd)
        for i in range(self.targetTasksList.count()):
            self.targetTasksList.takeItem(0)
    def target_task_OLD(self):
        """
        
        """
        nTargeted = self.targetTasksList.count()
        #nTargeted = 
        print('Amount of targeted tasks: ', nTargeted)
        nSelected = 0
        for task_item in self.treeWidget.selectedItems():
            nSelected+=1
            print(task_item)

        task_item  = self.treeWidget.currentItem()
        self.listWidgetItemNames = []
        if self.targetTasksList.count() > 0:
            for index in range(0,self.targetTasksList.count()):
                self.listWidgetItemNames.append(str(self.targetTasksList.item(index).text()))
                
        if task_item.name in self.listWidgetItemNames and task_item.status == 'ACTIVE':
            #print('ERROR!')
            # DELETE from ListBox by name.
            cmd = "DELETE from targeted_tasks WHERE name = '{0}'".format(
                                                          task_item.name)
            self.storage.ex(cmd)
            nTargeted = self.targetTasksList.count()
            for i in range(nTargeted):
                if str(self.targetTasksList.item(i).text()) == task_item.name:
                    res = self.targetTasksList.takeItem(i)
                    
            self.sound.poof()
        else:
            if nTargeted > 4:
                print('ERROR! There are already 5 targeted tasks! Can not target more!')
                return
            self.targetTasksList.addItem(QtCore.QString(task_item.name))
            self.sound.open_stash()
            cmd = "INSERT INTO targeted_tasks VALUES({0}, '{1}', '{2}', {3})".format(
                         task_item.id,
                         task_item.name,
                         task_item.uuid,
                         self.targetTasksList.count()
                        )
            self.storage.ex(cmd)
            
    def target_task(self):
        task_item = self.treeWidget.currentItem()
        if not task_item.targeted:
            #self.sound.target.play()
            if self.metadata['targeted_task'] != '':
                prev_targeted_task = self.tasks_dict[self.metadata['targeted_task']]
                prev_targeted_task.targeted = False
                prev_targeted_task.setIcon(0,QtGui.QIcon())
                #self.sound.target()
            
            task_item.setIcon(0,self.target16x16)
            task_item.targeted = True
            self.metadata['targeted_task'] = task_item.uuid
            print('DEBUG target_task: %s'%(task_item.uuid))
            cmd = "UPDATE metadata SET value = '{0}' WHERE key = 'targeted_task'".format(task_item.uuid)
            self.storage.ex(cmd)
            self.sound.target()
            
        else:
            task_item.setIcon(0,QtGui.QIcon())
            task_item.targeted = False
            self.metadata['targeted_task']=''
            cmd = "UPDATE metadata SET value = '' WHERE key = 'targeted_task'"
            self.storage.ex(cmd)
            
    def load_tasks(self, from_date='', status = '', priproty = '', limit = 9999):
        """
        Load tasks from DB to our TaskStackWidget as Task objects.
        Max columns taken from task attributes count.
        """
        query = self.storage.q
        
        cmd = "PRAGMA table_info({main_table})".format(main_table=self.main_table)
        self.storage.ex(cmd)
        fields = [] #Names of table fields        
        while query.next():
            field = str(query.value(1)) #"tasks" table row names.
            fields.append(field)
        tasks = []
        
        cmd = "SELECT * from {main_table} LIMIT {0}".format(limit, main_table=self.main_table)
        self.storage.ex(cmd)
        while query.next():
            field = 'field'
            fid = 0
            values = []
            task_dict = {}
            while fid < len(fields):
                value = query.value(fid)
                if type(value) is QtCore.QString:
                    value = str(value)
                if type(value) is QtCore.QPyNullVariant:
                    value=''
                values.append(value)
                task_dict[fields[fid]] = value
                fid+=1
            
            #self.dbg_print(task_dict)
            task_item = Task(**task_dict)
            #if task_item.status == 'CURRENT':
                #place task_item on the targeted list
            if not task_dict['id']:
                sys.exit()
            #else:
            #    print('So where does ID go?')
            task_item.setFlags(task_item.flags() & ~QtCore.Qt.ItemIsEditable)
            self.tasks.append(task_item)
            self.tasks_dict[task_item.uuid]=task_item
            self.treeWidget.addTopLevelItem(task_item)
            #add task_created icon to timeline.
            self.TimeLine.add_task_creation_icon(task_item)
            self.TimeLine.add_task_completion_icon(task_item)
            
        #self.treeWidget.resizeColumnToContents(0)
        self.treeWidget.scrollToItem(task_item)
        self.treeWidget.setCurrentItem(task_item, 0)
        self.treeWidget.setItemSelected(task_item, True)
        task_item.setSelected(True)
        
    @pyqtSlot()
    def f2_edit_item(self):
        task_item = self.treeWidget.currentItem()
        column = 0
        self.edit_item(task_item, column)
    @pyqtSlot(int,int)
    def edit_item(self, task_item, column):
        editable_columns = [0,4,7]
        if column in editable_columns:
            print('edit_item:', column,task_item.columns[column])
            column = task_item.columns[column]
            dialog = NewTaskDialog(task_item,focus=column)
            result = dialog.exec_()
            if result != 0:
                #name = dialog.name
                task_item.name = str(dialog.nameEdit.text())
                cmd = "UPDATE {main_table} SET {0} = '{1}' WHERE uuid = '{2}'".format('name',task_item.name, task_item.uuid, main_table=self.main_table)
                self.storage.ex(cmd)
                task_item.setText(0, task_item.name)
                
                task_item.time_spent_prediction = dialog.prediction
                cmd = "UPDATE {main_table} SET {0} = {1} WHERE uuid = '{2}'".format('time_spent_prediction',task_item.time_spent_prediction, task_item.uuid, main_table=self.main_table)
                self.storage.ex(cmd)
                
                #task_item.setText(7,str(task_item.time_spent_prediction)+' m')
                
                task_item.setText(7,str(task_item.time_spent_prediction*60))
                
            print('edit_item:')
            print(bin(task_item.flags().__int__()))
        else:
            pass
        #else:
        #    task_item.time_spent_prediction = 15
        
    
    @pyqtSlot(int,int)
    def currentItemChanged(self, current,previous):
        self.sound.short_click()
        print('currentItemChanged: PREV: ',previous.name, 'CURRENT: ', current.name, current.id)
        self.current_task_id = current.id # -1 
        self.taskData.name.setText(current.name)
        if type(current.description) == QtCore.QPyNullVariant:
            current.description = '...'
        self.taskData.description.setText(current.description)
        self.treeWidget.scrollToItem(current)

    @pyqtSlot(int)
    def updateTaskItem(self, task_item, field):
        """
        UPDATE db record based on new treeWidgetItem columns.
        
        """
        fields = {0:'name', 
                  1:'id', 
                  2:'time_created',
                  3:'status', 
                  4:'priority',
                  5:'time_completed',
                  6:'time_spent',
                  7:'time_spent_prediction'}
        if field in [1,4,5,6,7]: #if we're dealing with time_completed column.
            return False
        if not task_item:
            task_item = self.last_created_tree_widget_item
        res = task_item.__setattr__(fields[field], task_item.text(field))
        cmd = "UPDATE {main_table} SET {0} = '{1}' WHERE uuid = '{2}'".format(fields[field],task_item.text(field), task_item.uuid, main_table=self.main_table)
        ### change Status field color.
        green = QtGui.QColor(0,255,0)
        yellow = QtGui.QColor(255,242,0)
        red = QtGui.QColor(255,0,0)
        if fields[field] == 'status':
            status_color = {'ACTIVE':yellow, 'DONE':green, 'CURRENT':red}
            task_item.setBackgroundColor(3,status_color[str(task_item.status)])
        self.storage.ex(cmd)
        self.treeWidget.setItemSelected(task_item, True)
        self.treeWidget.setCurrentItem(task_item)
        
        
    def complete_task(self):
        """
        Wrong function name.
        We <cycle> task status here, but we do not set the "complete" status.
        """
        task_item = self.treeWidget.currentItem()
        #Bad name. Why "task item" instead of "task" or "task object" ?
        if task_item.status == 'ACTIVE':
            self.sound.complete()
            task_item.status = 'DONE'
            task_item.setText(task_item.columns['status'],task_item.status)
            task_item.setText(task_item.columns['priority'], '0')
            task_item.priority = 0
            task_item.setBackgroundColor(task_item.columns['status'],QtGui.QColor(0,255,0))
            cmd = "UPDATE {main_table} SET {0} = '{1}' WHERE uuid = '{2}'".format('status',task_item.status, task_item.uuid, main_table=self.main_table)
            self.storage.ex(cmd)
            cmd = "UPDATE {main_table} SET {0} = '{1}' WHERE uuid = '{2}'".format('priority',task_item.priority, task_item.uuid, main_table=self.main_table)
            self.storage.ex(cmd)
            
            task_item.time_completed = time.strftime("%Y-%m-%d %H:%M:%S")
            cmd = "UPDATE {main_table} SET {0} = '{1}' WHERE uuid = '{2}'".format('time_completed',task_item.time_completed, task_item.uuid, main_table=self.main_table)
            self.storage.ex(cmd)
            task_item.setText(5, task_item.get_lead_time())
            #task_item.setText(5, task_item.time_completed)
            #task_item.set_status('DONE')
            if self.done_hidden:
                task_item.setHidden(True) 
            
        #if task_item.status == 'DONE':    - ERROR!!
        elif task_item.status == 'DONE':    
            task_item.status = 'ACTIVE'
            task_item.setHidden(False) 
            task_item.time_completed = ''
            task_item.setText(task_item.columns['status'],task_item.status)
            cmd = "UPDATE {main_table} SET {0} = '{1}' WHERE uuid = '{2}'".format('time_completed','', task_item.uuid, main_table=self.main_table)
            self.storage.ex(cmd)
            cmd = "UPDATE {main_table} SET {0} = '{1}' WHERE uuid = '{2}'".format('status',task_item.status, task_item.uuid, main_table=self.main_table)
            self.storage.ex(cmd)
            task_item.setBackgroundColor(task_item.columns['status'],QtGui.QColor(255,255,0))
            task_item.setText(5, '')

            return None
            
            
    def priority_up(self):
        self.sound.hop_up()
        for task_item in self.treeWidget.selectedItems():
            uuid = task_item.uuid
            priority = int(str(task_item.priority)) + 1
            cmd = "UPDATE {main_table} set priority = {1} WHERE uuid = '{0}'".format(uuid, priority, main_table=self.main_table)
            self.storage.ex(cmd)
            print('Changing {main_table} {2} priority from {0} to {1}'.format(task_item.priority, priority, task_item.id,main_table=self.main_table))
            task_item.priority = priority
            task_item.setText(4, str('{:02d}'.format(task_item.priority)))
        self.treeWidget.scrollToItem(task_item)

    def priority_down(self):
        self.sound.hop_down()
        for task_item in self.treeWidget.selectedItems():
            uuid = task_item.uuid
            priority = int(str(task_item.priority)) - 1
            cmd = "UPDATE {main_table} set priority = {1} WHERE uuid = '{0}'".format(uuid, priority, main_table=self.main_table)
            self.storage.ex(cmd)
            print('Changing task {2} priority from {0} to {1}'.format(task_item.priority, priority, task_item.id))
            task_item.priority = priority
            task_item.setText(4, str('{:02d}'.format(task_item.priority)))        
        self.treeWidget.scrollToItem(task_item)

    def remove_task_proc(self):
        #verify dialog
        verify = QtGui.QMessageBox()
        res = verify.question(self,'','Confirm removal', verify.Yes | verify.No)
        if res == verify.Yes:
            root = self.treeWidget.invisibleRootItem()
            for task_item in self.treeWidget.selectedItems():
                self.backup_queue.put(task_item.clone())
                root.removeChild(task_item)
                uuid = task_item.uuid
                print('Removing task with UUID:', uuid)
                cmd = "DELETE FROM {main_table} WHERE uuid = '{0}'".format(uuid, main_table=self.main_table)
                self.storage.ex(cmd)
                cmd = "INSERT INTO tasks_trash VALUES(NULL, '{0}','{1}',{2},'{3}','{4}','{5}',{6},'{7}')".format(task_item.name, 
                                                   task_item.uuid,
                                                   task_item.level,
                                                   task_item.parent,
                                                   task_item.time_created, 
                                                   task_item.status,
                                                   task_item.priority,
                                                   task_item.description)
                self.storage.ex(cmd)
                self.tasks.remove(task_item)
            self.sound.deleted()
                #(item.parent() or root).removeChild(item)
        else:
            verify.information('')

    def description_edit(self):
        """
        Alt+E
            switch focus to taskData.description QTextEdit widget.
            upon pressing again - save description and return focus to
            previous widget.
            
        """
        self.sound.hit()
        if self.taskData.description.hasFocus():
            self.previousFocus.setFocus()#if this is not None! otherwise *add code*
            self.save_task_description()
        else:
            self.previousFocus = self.app.focusWidget() #if this is not None! otherwise *add code*
            self.taskData.description.setFocus()

    def save_task_description(self):
        task_item = self.treeWidget.currentItem()
        task_item.description = str(self.taskData.description.toPlainText())
        cmd = "UPDATE {main_table} SET {0} = '{1}' WHERE uuid = '{2}'".format('description',task_item.description, task_item.uuid, main_table=self.main_table)
        self.storage.ex(cmd)
    
    def hide_done_checkbox_toogle(self):
        #self.hide_done()
        state = self.taskFilterHideDone.checkState()
        #not checked
        print('taskFilterHideDone: ', state)
        #if state == 0:
        if self.taskFilterHideDone.isChecked():
            self.taskFilterHideDone.setChecked(0)
        else:
            self.taskFilterHideDone.setChecked(2)
        
    def hide_done(self):
        print('hiding DONE tasks')
        self.done_hidden = not self.done_hidden
        for task_item in self.tasks:
            if str(task_item.status) == 'DONE':
                task_item.setHidden(not task_item.isHidden())
                

    def sort_column_cycle(self):
        """
        Cycle through sort keys and apply them.
    
        """
        self.sound.sort_cycle()
        cycle = {0:1,1:2,2:0}
        print('SORT CYCLE')
        sort_column = self.treeWidget.sortColumn()
        #4
        columns = {1:'id', 4:'priority', 2:'age'}
        keys = {'id':0, 'priority':1, 'age':2}
        sort_key = keys[columns[sort_column]]
        # keys[columns[4]]=keys['priority']= 1 = sortKey
        N_keys = self.taskSortKey.count()
        #new_sort_key = (sort_key+1) % N_keys
        new_sort_key = cycle[sort_key] # = cycle[1] = 2
        text_old = self.taskSortKey.itemText(sort_key)
        text_new = self.taskSortKey.itemText(new_sort_key)
        print('sort_column_cycle: ', sort_key,text_old,'-->', new_sort_key, text_new) 
        self.taskSortKey.setCurrentIndex(new_sort_key)
        temp = self.treeWidget.scrollToItem(self.treeWidget.currentItem())
        
        
    @pyqtSlot(int)
    def sort_index_changed(self,data):
        #self.treeWidget.setSortingEnabled(True)
        indexes = {0:'id', 1:'priority', 2:'age'}
        name = indexes[data]
        # date - new index, name - new sort key! 
        print('sort_index_changed: ', data, name)
        
        columns = {'id':1, 'priority':4, 'age':2}
        if name in columns.keys():
            col = columns[name]
            #self.treeWidget.sortByColumn(col, 1)
            self.treeWidget.sortByColumn(col, 0)
        else:
            print('sort_index_changed: name NOT in column.keys')
        
    def block_text_append(self):
        """
        
        """
        print('Task description length limit exceeded!')
    
    def spellbook_cycle(self):
        # TODO LOGGER!
        book_id = int(time.time()) % len(self.spellBooksIcons)
        #print('spellbook_cycle:' ,book_id)
        self.spellsButton.setIcon(self.spellBooksIcons[book_id])
    
    
    def restart_application(self):
        self.tray.hide()
        self.sound.restart()
        time.sleep(1.5) # let the sound play :)
        python = sys.executable
        os.execl(python, python, * sys.argv)
        self.kill_all()

    def activate_window(self):
        self.setWindowState(self.windowState() & ~QtCore.Qt.WindowMinimized | QtCore.Qt.WindowActive)
        self.activateWindow()
        self.dbg_print(self.windowState().__int__())

    def gcp(self):
        p = POINT()
        res = ctypes.windll.user32.GetCursorPos(ctypes.byref(p))
        return (p.x, p.y)
    
    @pyqtSlot(int,int)
    def report_focus_change(self, old, new ):
        print('REPORT_FOCUS_CHANGE: OLD:', old)
        print('REPORT_FOCUS_CHANGE: new:',new)
        
        QtGui.QApplication.instance().new = new
        QtGui.QApplication.instance().old = old
        ### for BreakReasonDialog. TODO: refine later.
        ### use eventFilter instead!
        ### This causes unwanted hard-coded cross-connections between modules.
        Qt
        if new and old:
            if new.objectName()=='behaviourClassSelector' and old.objectName() != 'behaviourClassSelectorView':
                if not new.opened:
                    new.opened = True
                    new.showPopup()
                else:
                    new.opened = False
            if old.objectName() == 'behaviourClassSelector' and new.objectName() != 'behaviourClassSelectorView':
                old.opened = False
        #if new and new.objectName() == ('behaviourStartedEdit' or 'behaviourCompletedEdit'):
        if new and new.objectName() in ('behaviourStartedEdit' , 'behaviourCompletedEdit'):
            new.setCurrentSection(QtGui.QDateTimeEdit.MinuteSection)
            new.setSelectedSection(QtGui.QDateTimeEdit.MinuteSection)
        ###
        
if __name__ == "__main__":
    import sys
    pid = os.getpid()
    app = QtGui.QApplication(sys.argv)
    win_main = TaskStackWidget(app=app)
    #win_main.app = app
    
    #win_main.show()
    win_main.display()
    #win_main.treeWidget.scrollToBottom()
    win_main.treeWidget.setFocus()
    print(win_main.pos().x())
    #sys.exit(app.exec_())
    app.exec_()
    os.system('taskkill /f /PID %d'%pid)