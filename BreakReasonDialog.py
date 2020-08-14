import sip
sip.setapi("QString", 1)
from PyQt4 import QtCore, QtGui
from PyQt4.QtCore import *

import time

class KeyPressFilter(QObject):
    f1_pressed = pyqtSignal()
    f2_pressed = pyqtSignal()
    f3_pressed = pyqtSignal()
    hostWidget = ''
    kids = []
    offspring=[]
    def eventFilter(self, widget, event):
        
        if event.type() == QEvent.KeyPress and event.nativeScanCode() in [59,60,61]:
            #if self.hostWidget == '': #when capturing first event.
            
            if True:#when capturing first event.
                self.hostWidget = widget
                self.offspring = []
                kids = self.hostWidget.children()
                for kid in kids:
                    self.offspring.append(kid)
                    grandKids = kid.children()
                    if len(grandKids) == 0:
                        continue
                    else:# len(grandKids) 
                        for grandKid in grandKids:
                            self.offspring.append(grandKid)
            #print(self.offspring)
            #[print(kid, kid.objectName()) for kid in self.offspring]
            #print('offspring:', self.offspring
            #offsprint should never equal ''

            keys = {'F1':59, 'F2':60,'F3':61}

            kids_focused = any([kid.hasFocus() for kid in self.offspring if hasattr(kid, 'hasFocus')])
            #print('kids_focused:', kids_focused)
            if kids_focused:
                sCode = event.nativeScanCode()
                
                if sCode == keys['F1']:
                    self.f1_pressed.emit()
                elif sCode == keys['F2']:
                    self.f2_pressed.emit()
                elif sCode == keys['F3']:
                    self.f3_pressed.emit()
            
            return False
        else:
            return False


class behaviourClassNameDialog(QtGui.QDialog):
    def __init__(self):
        super(QtGui.QDialog, self).__init__()
        self.setWindowFlags(QtCore.Qt.CustomizeWindowHint)
        self.box = QtGui.QVBoxLayout()
        self.nameEditor = QtGui.QLineEdit()
        self.nameEditor.setText('New behaviour class name...')
        self.descriptionEditor = QtGui.QLineEdit()
        self.descriptionPlaceholder = 'Behaviour class description...'
        self.descriptionEditor.setText(self.descriptionPlaceholder)

        
        self.ok = QtGui.QPushButton('Ok')
        self.ok.clicked.connect(self.finish)
        
        self.box.addWidget(self.nameEditor)
        self.box.addWidget(self.descriptionEditor)
        self.box.addWidget(self.ok)
        self.setLayout(self.box)
    
    def finish(self):
        self.done(1)

class BehaviourDetailsDialog(QtGui.QDialog):
    def __init__(self,parent,option=None):
        super(QtGui.QDialog,self).__init__(parent=parent)
        

class BreakReasonDialog(QtGui.QDialog):
    """
    изначальная ситуация: различные нейрогруппы инициируют разнообразное (импульсивное) поведение, нацеленное на удовлетворение спонтанно возникающих потребностей. 
    Но сам по себе образ создаваемого виджета утверждает иную траекторию принятия во внимание процесса смены поведения и поведения в целом.

    Нам нужно так же делать запись при :
       - возврате с перерыва\афк, в начале которого не было сделано фиксации.
      -  в целом - при отсутствии недавних записей в журнале.
      -  при наличии пустот в  таймлайне (то есть наличии окон неконтролируемого интеллектом поведенеия).
      -  по инициативе пользователя в любое время.
        
    ===
    хоткеи?
    ===
    
    """
    def __init__(self,parent,focus='name'):
        super(QtGui.QDialog, self).__init__(parent=parent)
        self.storage = self.parent().storage
        #self.setWindowFlags(QtCore.Qt.CustomizeWindowHint)
        #self.behaviour_classes = []
        self.behaviour_classes = {}
        opt = 2
        if opt == 1:
            self.Vbox = QtGui.QVBoxLayout()
            #self.mainWidget = QtGui.QWidget(parent=self)
            
            self.rightWidget = QtGui.QWidget()
            self.fluke = QtGui.QLabel('What are you going to do?')
            self.addBehaviorClass = QtGui.QPushButton("[F2]Add behaviour class",parent=self)
            self.addBehaviorClass.clicked.connect(self.add_behaviour_class)
            
            #self.behaviourClassSelector = QtGui.QSpinBox()
            #self.behaviourClassSelector = BehaviourClassSelector(parent=self)
    
            self.behaviourClassSelector = QtGui.QComboBox()
            self.behaviourClassSelector.setAutoCompletion(True)
            
            self.addBehaviorRecord = QtGui.QPushButton('[F1] Add reason',parent=self)
            self.addBehaviorRecord.clicked.connect(self.add_behaviour)
            
            self.ok = QtGui.QPushButton('[F3] Ok',parent=self)
            self.ok.clicked.connect(self.finish)
            
            self.Hbox = QtGui.QHBoxLayout()
            self.Hbox.addWidget(self.addBehaviorClass)
            self.Hbox.addWidget(self.addBehaviorRecord)
            self.Hbox.addWidget(self.behaviourClassSelector)
            self.Hbox.addWidget(self.ok)
            
            self.leftWidget = QtGui.QWidget(parent=self)
            self.leftWidget.setLayout(self.Hbox)
            
            #self.rightWidget = QtGui.QWidget(parent=self)
            #self.rightWidget = QtGui.QLabel("Slack records list")
            
            self.rightWidget = QtGui.QListWidget()
            
            self.Vbox.addWidget(self.fluke)
            self.Vbox.addWidget(self.leftWidget)
            self.Vbox.addWidget(self.rightWidget)
            self.setLayout(self.Vbox)
        elif opt == 2:
            
            #buttons.
            self.buttonsBox = QtGui.QHBoxLayout()
            self.buttonsWidget = QtGui.QWidget()
            
            self.addBehaviorClass = QtGui.QPushButton("[F2]Add behaviour class",parent=self)
            self.addBehaviorClass.clicked.connect(self.add_behaviour_class)
            
            self.behaviourClassSelector = QtGui.QComboBox()
            self.behaviourClassSelector.setAutoCompletion(True)
            
            self.addBehaviorRecord = QtGui.QPushButton('[F1] Add reason',parent=self)
            self.addBehaviorRecord.clicked.connect(self.add_behaviour)
            
            self.ok = QtGui.QPushButton('[F3] Ok',parent=self)
            self.ok.clicked.connect(self.finish)
            
            self.buttonsBox.addWidget(self.addBehaviorRecord)
            self.buttonsBox.addWidget(self.behaviourClassSelector)
            self.buttonsBox.addWidget(self.addBehaviorClass)
            self.buttonsBox.addWidget(self.ok)
            self.buttonsWidget.setLayout(self.buttonsBox)
            
            #behaviour record details.
            self.behaviourRecordDetailsWidget = QtGui.QWidget()
            self.behaviourRecordDetailsBox = QtGui.QHBoxLayout()
            
            ######### LEFT WIDGET (behaviour details)###############
            
            #left half: time_started,time_completed, quality, variance
            self.behaviourRecordDetailsBoxLeft = QtGui.QVBoxLayout()
            self.behaviourRecordDetailsWidgetLeft = QtGui.QWidget()
            
            datetime_now = QtCore.QDateTime.currentDateTime()
            self.behaviourStartedEdit = QtGui.QDateTimeEdit(datetime_now)
            #("%Y-%m-%d %H:%M:%S")
            self.behaviourStartedEdit.setDisplayFormat("yyyy-MM-dd hh:mm:ss")
            #### duration ####
            self.durationGroupBox = QtGui.QGroupBox(QtCore.QString("Behaviour duration"))
            self.durationGroupBoxLayout = QtGui.QVBoxLayout()
            
            self.durationSlider = QtGui.QSlider(QtCore.Qt.Horizontal)
            self.durationSlider.setRange(1,120)
            self.durationSlider.setSingleStep(1)
            DEFAULT_BEHAVIOUR_DURATION = 5
            self.durationSlider.setValue(DEFAULT_BEHAVIOUR_DURATION) #Get default duration for each behaviour class!!
            self.durationSlider.setPageStep(5)
            self.durationSlider.setTickInterval(10)
            self.durationSlider.setTickPosition(QtGui.QSlider.TicksBelow)
            self.durationSlider.valueChanged.connect(self.set_duration)
            
            self.behaviourCompletedEdit = QtGui.QDateTimeEdit(datetime_now.addSecs(60*int(self.durationSlider.value())))
            self.behaviourCompletedEdit.setDisplayFormat("yyyy-MM-dd hh:mm:ss")
            self.durationGroupBoxLayout.addWidget(self.durationSlider)
            self.durationGroupBoxLayout.addWidget(self.behaviourCompletedEdit)
            self.durationGroupBox.setLayout(self.durationGroupBoxLayout)
            #### /duration ####
            
            self.behaviourQualityEdit = QtGui.QSlider(QtCore.Qt.Horizontal)
            self.behaviourQualityEdit.setRange(0,10)
            self.behaviourQualityEdit.setSingleStep(1)
            self.behaviourQualityEdit.setValue(5) #Get default behaviour quality.
            self.behaviourQualityLabel = QtGui.QLabel("Quality: " + str(self.behaviourQualityEdit.value()))
            self.behaviourQualityEdit.valueChanged.connect(self.set_quality)
            
            self.behaviourDurationVarianceEdit = QtGui.QSlider(QtCore.Qt.Horizontal)
            self.behaviourDurationVarianceEdit.setRange(0,10)
            self.behaviourDurationVarianceEdit.setSingleStep(1)
            self.behaviourDurationVarianceEdit.setValue(3)
            self.behaviourDurationVarianceEdit.valueChanged.connect(self.set_variance)
            
            self.behaviourRecordDetailsBoxLeft.addWidget(self.behaviourStartedEdit)
            #self.behaviourRecordDetailsBoxLeft.addWidget(self.durationSlider)
            #self.behaviourRecordDetailsBoxLeft.addWidget(self.behaviourCompletedEdit)
            self.behaviourRecordDetailsBoxLeft.addWidget(self.durationGroupBox)
            self.behaviourRecordDetailsBoxLeft.addWidget(self.behaviourDurationVarianceEdit)
            self.behaviourRecordDetailsBoxLeft.addWidget(self.behaviourQualityLabel)
            self.behaviourRecordDetailsBoxLeft.addWidget(self.behaviourQualityEdit)
            
            self.behaviourRecordDetailsWidgetLeft.setLayout(self.behaviourRecordDetailsBoxLeft)
            ######### /LEFT WIDGET (behaviour details)###############
            ######### RIGHT WIDGET (behaviour comment)###############
            
            self.behaviourCommentEdit = QtGui.QTextEdit()
            ######### /RIGHT WIDGET (behaviour comment)###############
            
            ######## TOP WIDGET (contains left and right widgets) #######
            self.behaviourRecordDetailsBox.addWidget(self.behaviourRecordDetailsWidgetLeft)
            self.behaviourRecordDetailsBox.addWidget(self.behaviourCommentEdit)
            self.behaviourRecordDetailsWidget.setLayout(self.behaviourRecordDetailsBox)
            ######## /TOP WIDGET (contains left and right widgets) #######
            
            ######## behaviour list widget #################
            self.behaviourRecords = QtGui.QListWidget()
            
            ######## compose behaviour input widget. ################
            self.addBehaviorBox = QtGui.QVBoxLayout()
            self.addBehaviorBox.addWidget(self.buttonsWidget)
            self.addBehaviorBox.addWidget(self.behaviourRecordDetailsWidget)
            self.addBehaviorBox.addWidget(self.behaviourRecords)
            self.setLayout(self.addBehaviorBox)
            
        self.KeyPressFilter = KeyPressFilter()
        self.installEventFilter(self.KeyPressFilter)
        self.KeyPressFilter.f1_pressed.connect(self.add_behaviour)
        self.KeyPressFilter.f2_pressed.connect(self.add_behaviour_class)
        self.KeyPressFilter.f3_pressed.connect(self.finish)
        
        self.prev_duration = 0
        self.bCND = ''
        self.load_behaviour_classes()
        #01-11 10:11
        #self.behaviourClassSelector.showPopup()
    
    @pyqtSlot(int)
    def set_duration(self,duration):                  
        #self.behaviourCompletedEdit.setDateTime(self.behaviourCompletedEdit.dateTime().addSecs(60*int(self.durationSlider.value())))
        self.behaviourCompletedEdit.setDateTime(self.behaviourStartedEdit.dateTime().addSecs(60*duration))
        #pass
        #self.prev_duration = durat
    def set_quality(self):
        self.behaviourQualityLabel.setText("Quality: " + str(self.behaviourQualityEdit.value()))
        
    def set_variance(self):
        
        pass
        
        
    def add_behaviour(self):
        #later we can improve the format of description of the process.
        opt = 1 #opt == 2 or 3 - when we implement the timeline.
        if opt == 0:
            self.queue = []
            t = time.strftime("%Y-%m-%d %H:%M:%S")
            name = str(self.behaviourClassSelector.currentText())
            record = t+'\t' + name
            print('add_behaviour:' ,record)
            #self.rightWidget.addItem(QtCore.QString(record))
            self.behaviourRecords.addItem(QtCore.QString(record))
        elif opt == 1:
            # CREATE TABLE IF NOT EXISTS behaviour_log(id integer primary key autoincrement, behaviourId int, comment varchar(2048), time_created varchar(24), time_started varchar(24), predicted_duration int, duration int, quality int, source varchar(256),  variance REAL DEFAULT 0.5)
            #behaviour_journal(id integer primary key autoincrement, 
            #{0}    behaviourId int, 
            #{1}    comment varchar(2048), 
            #{2}    time_created varchar(24), 
            #{3}    time_started varchar(24), 
            #{4}    predicted_duration int, 
            #{5}    duration int, 
            #{6}    quality int, 
            #{7}    source varchar(256),  
            #{8}    variance REAL DEFAULT 0.5)"
            
            # форма редактирования полей записи в журнал (или в план?).
            # журнал и план. журнал - это лог. план - это ожидание конкретной последовательности записей журнала.
            
            #behaviourId int
            b =type("behaviour_record", (dict,),{})
            b.name = str(self.behaviourClassSelector.currentText())
            b.behaviourId = self.behaviour_classes[b.name] 
            b.comment = str(self.behaviourCommentEdit.toPlainText())
            time_format = "%Y-%m-%d %H:%M:%S"
            b.time_created = time.strftime(time_format)
            b.time_started = str(self.behaviourStartedEdit.text())
            b.predicted_duration = str(self.durationSlider.value()) #MINUTES
            b.duration = self.durationSlider.value()
            b.quality = self.behaviourQualityEdit.value()
            b.variance = self.behaviourDurationVarianceEdit.value()
            b.source = 'neuroclassified'
            cmd = "INSERT INTO behaviour_journal VALUES(NULL,{0},'{1}','{2}','{3}',{4},{5},{6},'{7}',{8})"
            cmd=cmd.format(b.behaviourId, b.comment, b.time_created, b.time_started,b.predicted_duration,
            b.duration, b.quality, b.source, b.variance)
            self.storage.ex(cmd)
            record = b.name + ' ' + b.time_started + ' \tDuration:' + str(b.duration) + 'm\t'
            self.behaviourRecords.addItem(QtCore.QString(record))
            #started_at_default = 1 # 
            
            
    def load_behaviour_classes(self):
        cmd = "SELECT * FROM behaviour_classes"
        query = self.storage.q
        self.storage.ex(cmd)
        
        while query.next():
            b = type('',(dict,),{})()
            b.id =              int(str(query.value(0)))
            b.name =            str(query.value(1))
            b.description =     str(query.value(2))
            b.attribute =       str(query.value(3))
            #self.behaviour_classes.append(b.name)
            self.behaviour_classes[str(b.name)]=b.id
            print("load_behaviour_classes: \n",b.id,b.name,b.description,b.attribute)
            self.behaviourClassSelector.addItem(str(b.name))
            
    def add_behaviour_class(self):
        self.bCND = behaviourClassNameDialog()
        result = self.bCND.exec_()
        print('add_behaviour_class:')
        print('result:',result)
        if result != 0:
            b = self.save_behaviour_class()
            print(self.behaviour_classes)
            
           
    def save_behaviour_class(self):
        behaviourName = str(self.bCND.nameEditor.text())
        print('save_behaviour_class: ', behaviourName)
        behaviourClassDescription = str(self.bCND.descriptionEditor.text())
        if behaviourClassDescription == self.bCND.descriptionPlaceholder:
            behaviourClassDescription = ''
            
        behaviourClassAttribute = '' #placeholder for something, like rating or frequency
        cmd = "INSERT INTO behaviour_classes VALUES(NULL, '{name}', '{description}', '{attribute}')".format(name=behaviourName,
                               description=behaviourClassDescription,
                               attribute=behaviourClassAttribute
                               )
        self.storage.ex(cmd)
        behaviour = type('behaviour_class', (dict,),{})()
        behaviour.name = behaviourName
        behaviour.description = behaviourClassDescription
        behaviour.attribute = behaviourClassAttribute
        #self.behaviour_classes.append(behaviour.name)
        cmd = "SELECT id FROM behaviour_classes WHERE name='{0}'".format(behaviourName)
        behaviourId = int(str(self.storage.fetch(cmd)))
        self.behaviour_classes[behaviourName]=behaviourId
        self.behaviourClassSelector.addItem(str(behaviour.name))
        #self.bCND = ''
        return behaviour
        
        
    def set_behaviour(self):
        
        pass
    def finish(self):
        print("BreakReasonDialog: finish()")
        self.done(1)