import sip
sip.setapi("QString", 1)
from PyQt4 import QtCore, QtGui
from PyQt4.QtCore import *

import time
class _MyDateTimeEdit(QtGui.QDateTimeEdit):
    def event(self,e):
        if e.type() == 6: #KeyPress
            return False
        else:
            return super().event(e)
class MySlider(QtGui.QSlider):
    def keyPressEvent(self,e):
        if e.type() == 6:
            scanCode = e.nativeScanCode()
            if scanCode == 328: #UP ARROW
                shift = QtCore.Qt.ShiftModifier
                keyPress = QtGui.QKeyEvent(e.type(),QtCore.Qt.Key_Tab, QtCore.Qt.KeyboardModifiers(shift))
                QtGui.QApplication.sendEvent(self,keyPress)
            elif scanCode == 336: #DOWN ARROW
                keyPress = QtGui.QKeyEvent(e.type(),QtCore.Qt.Key_Tab, QtCore.Qt.KeyboardModifiers())
                QtGui.QApplication.sendEvent(self,keyPress)
            else:
                super().keyPressEvent(e)
                
class MyDateTimeEdit(QtGui.QDateTimeEdit):
    tilda_pressed = pyqtSignal() #to focus on comboBox. EXTEND!
    letters_scancodes = set(list(range(16,26))+list(range(30,39))+list(range(44,52))+[41,])
    def keyPressEvent(self,e):
        if e.type() == 6: #KeyPress
            scanCode = e.nativeScanCode()
            print('KeyPress: ', scanCode)
            #scanCode: left = 331, right = 333
            #event.type = 6
            if scanCode == 333:
                keyPress = QtGui.QKeyEvent(e.type(),QtCore.Qt.Key_Tab, QtCore.Qt.KeyboardModifiers())
                QtGui.QApplication.sendEvent(self,keyPress)
                self.setSelectedSection(self.currentSection())
            elif scanCode == 331:
                shift = QtCore.Qt.ShiftModifier
                keyPress = QtGui.QKeyEvent(e.type(),QtCore.Qt.Key_Tab, QtCore.Qt.KeyboardModifiers(shift))
                QtGui.QApplication.sendEvent(self,keyPress)
                #self.setSelectedSection(self.currentSection())
            elif scanCode in self.letters_scancodes: # tilda
                self.tilda_pressed.emit()
                
        super().keyPressEvent(e)

class DateTimeEditFilter(QObject):
    """
        !!! Attention !!!
    PyQT has a bug when focus event messes up DateTimeEdit's current section,
    so the filter+signal combination does not work.
    Quick fix applied within TSW's report_focus_change method.
    """
    focusIn = pyqtSignal()
    focusOut = pyqtSignal()
    
    def eventFilter(self,widget,event):
        #if event.type() == QEvent.FocusOut:
            #self.focusOut.emit()
        if event.type() == QEvent.FocusIn:
            print('DateTimeEditFilter: focusIn!')
            print('widget.name:', widget.objectName())
            print('widget.currentSection:', widget.currentSection())
            widget.setCurrentSection(QtGui.QDateTimeEdit.MinuteSection)
            widget.setSelectedSection(QtGui.QDateTimeEdit.MinuteSection)
            widget.setCurrentSectionIndex(2)
            print('widget.currentSection:', widget.currentSection())
            
            #self.focusIn.emit()
        return False
        
class KeyPressFilter(QObject):
    f1_pressed = pyqtSignal()
    f2_pressed = pyqtSignal()
    f3_pressed = pyqtSignal()
    tilda_pressed = pyqtSignal()
    hostWidget = ''
    kids = []
    offspring=[]
    digits_scancodes = set([2,3,4,5,6,7,8,9,10,11])
    disallows_selector_focus_on_keyEvent = []
    allow_selector_focus_on_keyEvent = ['behaviourCompletedEdit',
                                        'behaviourStartedEdit',
                                        'durationSlider',
                                        'behaviourQualityEdit',
                                        'behaviourDurationVarianceEdit',
                                        'behaviourRecordDetailsWidget',
                                        'behaviourRecordDetailsWidgetLeft'
                                        'behaviourRecordDetailsBoxLeft',
                                        'behaviourRecordDetailsBox',
                                        'durationGroupBox',
                                        'durationGroupBoxLayout',
                                        ]
                                        
    def eventFilter(self, widget, event):
        infos = """
        When focused on comboBox - we stop registering keyPresses IF 
        alfanumeric keys  or UP\DOWN arrows are pressed. Other keypresses generate KeyEvents.
            1) When focus is within ComboBox - the events generated are not KeyEvents?
                KeyEvents, *but not* KeyPress events!
            2) Does this depend on ComboBox.setAutoCompletion ?
                
            3) What are the events?
                KeyEvent! (not KeyPressEvent!)
                QEvent.UpdateRequest	77	The widget should be repainted.
                QEvent.Paint	12	Screen update necessary 
                QEvent.ShortcutOverride	51	Key press in child, for overriding shortcut key handling (QKeyEvent).
                    [no documentation on this event]
                Shortcut 117
                ShortcutOverride 51
                
                
            4) Are there ANY events registered for alphanumeric keypresses at all?
            5) Установлен фильтр в диалог.
               В диалоге - слайдер и дейтТаймЕдит.
               Фокус в слайдере - принимает 6й эвент.
               Фокус в ДТЕ - не принимает.
               If obj.event() returns false - event is passed to the parent.
               https://stackoverflow.com/questions/5941730/event-propagation-in-qt
               То есть фокус в ДТЕ, ДТЕ при нажатии клавиш получает евенты нажатия, которые не доходят до фильтра диалога. Значит ДТЕ - принимает евент и его метод евент() возвращает Тру.
               А те виджеты (слайдер), которые не принимают ивент, возвращают фолс - и кутэ ядро передает ивент родителю.
               Значит нам нужно либо вставить фильтры в ДТЕ и техтЕдит, либо изменить их метод .евент(), чтобы тот возвращал фолс.
               DTE = type('MyDTE',(QtDTE,),{'event': lambda e: not super(DTE,self)
            =========
            Pressing tilds:
                classSelector: event.type = 51
                datetimeedit = 77,12,7
                
        """
        # Outer IF: one of the following *two*:
        #if widget.objectName() is not None:
        #if event.type() == QEvent.KeyPress:
        
        #Pay attention: this may refer to previously focused widget.
        focusWidget = QtGui.QApplication.focusWidget()
        
        print(event.type())
        #stop processing and pass the event if it *is not* a keyPressEvent.
        opt = 0
        
        if opt == 1 and event.type() == QEvent.InputEvent and focusWidget:
            try:
                if event.nativeScanCode() == 41:
                    if focusWidget.objectName() in self.allow_selector_focus_on_keyEvent:
                        print('event.nativeScanCode():',event.nativeScanCode())
                        self.tilda_pressed.emit()
                        return False
                else:
                    x = 1
            except Exception as _e:
                pass
                #print(str(_e))
        #if event.type() not in [7,12,77]
        if event.type() != QEvent.KeyPress and focusWidget:
            #if QtGui.QApplication.focusWidget().objectName() == 'behaviourClassSelector':
            if focusWidget.objectName() == 'behaviourClassSelector':
                print('catched behaviourClassSelector event!:')
                print('event.type:', event.type())
            #elif event.type() in [12,51,77]:
            #    print('event.type:', event.type(), 'focusWidget', focusWidget)
            #return False
        #if event.type() not in [12,77, QEvent.KeyPress] and focusWidget:
        #    print('Voodoo! event.type():', event.type())
        #    print('focusWidget:', focusWidget)
            
        if opt == 1 and event.type() == QEvent.KeyPress:
            print('QEvent.KeyPress:', event.type())
            print('event.nativeScanCode: ', event.nativeScanCode())
            print('event.text:', event.text())
            
        if opt == 1 and QtGui.QApplication.focusWidget() is None: #if_8
            print('QtGui.QApplication.focusWidget():',QtGui.QApplication.focusWidget())
            #print('objectName:',QtGui.QApplication.focusWidget().)
        
        if QtGui.QApplication.focusWidget() is not None: #if_0
            #if focusWidget.objectName() == 'behaviourClassSelector':
            #    focusWidget.showPopup()
            
            #if event.type() == QEvent.KeyPress: #if_1
            #    #print('event.nativeVirtualKey:', event.nativeVirtualKey())
            #    print('event.nativeScanCode: ', event.nativeScanCode())
            #    print('event.text:', event.text())
    
            #if event.type() == QEvent.KeyPress: #if_2
            #    print('focusWidget:', QtGui.QApplication.focusWidget().objectName())
            
            #if widget.focusWidget().objectName() == 'behaviourStartedEdit':
            #if widget.objectName() is not None and str(widget.objectName()) not in self.disallows_selector_focus_on_keyEvent: #if_3
                
            
            # HOTKEY TO START SELECTING BEHAVIOUR CLASS (or add tags).
            #if event.type() == QEvent.KeyPress and event.nativeScanCode() in self.digits_scancodes: #if_4
            #    #focus on b.class selector.
            #    
            #    # *widget* is the widget that RECIEVES THE EVENT!
            #    #print('widget.children():', len(widget.children()),widget.children())
            #    
            #    print('focusWidget.children():', len(QtGui.QApplication.focusWidget().children()),QtGui.QApplication.focusWidget().children())

            #if focusWidget and event.type() == QEvent.KeyPress and event.nativeScanCode() in [41] and focusWidget.objectName() in self.allow_selector_focus_on_keyEvent: #if_9
            #    # ` pressed. [TILDA]
            #    self.tilda_pressed.emit()
                
            if event.type() == QEvent.KeyPress and event.nativeScanCode() in [59,60,61]: #if_5
                # 59,60,61 => F1,F2,F3 # TODO: platform-independent keycodes.
                #if self.hostWidget == '': #when capturing first event.
                #if True:#Why did we have this here? Anyway:
                if self.hostWidget == '':
                
                    print('if self.hostWidget == "" :')
                    self.hostWidget = widget
                    self.offspring = []
                    kids = self.hostWidget.children()
                    for kid in kids:
                        self.offspring.append(kid)
                        grandKids = kid.children()
                        if len(grandKids) == 0: #if_6
                            continue
                        else:# len(grandKids) 
                            for grandKid in grandKids:
                                self.offspring.append(grandKid)
                                print('grandKid: ',grandKid, grandKid.objectName())
    
                keys = {'F1':59, 'F2':60,'F3':61}
                kids_focused = any([kid.hasFocus() for kid in self.offspring if hasattr(kid, 'hasFocus')])
                print('kids_focused:',kids_focused)
                """BROKEN KIDS' FOCUS"""
                #if kids_focused: #if_7
                if True:
                    scanCode = event.nativeScanCode()
                    if scanCode == keys['F1']:
                        self.f1_pressed.emit()
                    elif scanCode == keys['F2']:
                        self.f2_pressed.emit()
                    elif scanCode == keys['F3']:
                        self.f3_pressed.emit()
                
                return False
            else:
                return False
        else: #if widget.objectName is NONE (focus not within app window already (i.e. alt+tab))
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
        

class BehaviourJournal(QtGui.QDialog):
    """
    Планируемое поведение - тоже задачи!
    ТО есть изначальная ситуация: различные нейрогруппы инициируют разнообразное (импульсивное) поведение, нацеленное на удовлетворение спонтанно возникающих потребностей. 
    Но сам по себе образ создаваемого виджета утверждает иную траекторию принятия во внимание процесса смены поведения и поведения в целом.
    Первоначально была идея фиксации данных о произошедшем торможении рабочего процесса и о !причине! возникшего !прерывания! - то есть форма, в которой я бы по памяти записывал бы произошедшее, так сказать, поведение - в момент возврата к работе. Попробуем ЗАРАНЕЕ вводить причину перерыва - при остановке рабочего процесса. То есть "захотелось отдохнуть\поесть\и тп" - ВНОСИМ ОЖИДАЕМОЕ ПОВЕДЕНИЕ.
    
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
        self.setObjectName('BehaviourJournal')
        self.lastBehaviourTimeCompleted = parent.lastBehaviourTimeCompleted
        self.behaviour_classes = {}
                   
        #buttons.
        self.buttonsBox = QtGui.QHBoxLayout()
        self.buttonsBox.setObjectName('buttonsBox')
        self.buttonsWidget = QtGui.QWidget()
        self.buttonsWidget.setObjectName('buttonsWidget')
        
        self.addBehaviorClass = QtGui.QPushButton("[F2]Add behaviour class",parent=self)
        self.addBehaviorClass.clicked.connect(self.add_behaviour_class)
        self.addBehaviorClass.setObjectName('addBehaviorClass')
        
        #self.behaviourClassSelector = QtGui.QComboBox()
        self.behaviourClassSelector = QtGui.QComboBox(parent=self)
        self.behaviourClassSelector.setObjectName('behaviourClassSelector')
        self.behaviourClassSelector.setAutoCompletion(True)
        self.behaviourClassSelector.opened = False
        self.behaviourClassSelector.view().setObjectName('behaviourClassSelectorView')
        
        
        self.addBehaviorRecord = QtGui.QPushButton('[F1] Save record',parent=self)
        self.addBehaviorRecord.setObjectName('addBehaviorRecord')
        self.addBehaviorRecord.clicked.connect(self.add_behaviour)
        
        self.ok = QtGui.QPushButton('[F3] Ok',parent=self)
        self.ok.setObjectName('ok')
        self.ok.clicked.connect(self.finish)
        
        self.buttonsBox.addWidget(self.addBehaviorRecord)
        self.buttonsBox.addWidget(self.behaviourClassSelector)
        self.buttonsBox.addWidget(self.addBehaviorClass)
        self.buttonsBox.addWidget(self.ok)
        
        ### FOCUS PROXY
        #quick solution for disabling buttons, so pressing tab sends focus from comboBox to dateTimeEdit.
        self.buttons = [self.addBehaviorRecord,self.ok, self.addBehaviorClass]
        for button in self.buttons: button.setEnabled(False)
        ### /FOCUS PROXY
        
        self.buttonsWidget.setLayout(self.buttonsBox)
        self.buttonsWidget.setObjectName('buttonsWidget')
        #behaviour record details.
        self.behaviourRecordDetailsWidget = QtGui.QWidget()
        self.behaviourRecordDetailsWidget.setObjectName('behaviourRecordDetailsWidget')
        self.behaviourRecordDetailsBox = QtGui.QHBoxLayout()
        self.behaviourRecordDetailsBox.setObjectName('behaviourRecordDetailsBox')
        
        ######### LEFT WIDGET (behaviour details)###############
        
        #left half: time_started,time_completed, quality, variance
        self.behaviourRecordDetailsBoxLeft = QtGui.QVBoxLayout()
        self.behaviourRecordDetailsBoxLeft.setObjectName('behaviourRecordDetailsBoxLeft')
        self.behaviourRecordDetailsWidgetLeft = QtGui.QWidget()
        self.behaviourRecordDetailsWidgetLeft.setObjectName('behaviourRecordDetailsWidgetLeft')
        
        if self.lastBehaviourTimeCompleted == '':
            datetime_started = QtCore.QDateTime.currentDateTime()
        else:
            #extract time_completed of the last record.
            datetime_started = self.lastBehaviourTimeCompleted
            
        #self.behaviourStartedEdit = QtGui.QDateTimeEdit(datetime_started)
        self.behaviourStartedEdit = MyDateTimeEdit(datetime_started)
        
        self.behaviourStartedEdit.setObjectName('behaviourStartedEdit')
        self.behaviourStartedEdit.setDisplayFormat("yyyy-MM-dd hh:mm:ss")
        self.behaviourStartedEdit.setWrapping(True)
        self.behaviourStartedEdit.tilda_pressed.connect(self.behaviourClassSelector.setFocus)
        #self.behaviourStartedEditFocusFilter = DateTimeEditFilter()
        #self.behaviourStartedEdit.installEventFilter(self.behaviourStartedEditFocusFilter)
        #self.behaviourStartedEditFocusFilter.focusIn.connect(self.select_minutes_section)
        #self.behaviourStartedEdit.setSelectedSection(QtGui.QDateTimeEdit.MinuteSection)

        
        #self.behaviourStartedEdit.setObjectName('behaviourStartedEdit')
        #("%Y-%m-%d %H:%M:%S")
        #### duration ####
        self.durationGroupBox = QtGui.QGroupBox(QtCore.QString("Behaviour duration"))
        self.durationGroupBox.setObjectName('durationGroupBox')
        self.durationGroupBoxLayout = QtGui.QVBoxLayout()
        self.durationGroupBoxLayout.setObjectName('durationGroupBoxLayout')
        
        #self.durationSlider = QtGui.QSlider(QtCore.Qt.Horizontal)
        self.durationSlider = MySlider(QtCore.Qt.Horizontal)
        self.durationSlider.setObjectName('durationSlider')
        self.durationSlider.setFixedWidth(600)
        self.durationSlider.setRange(1,720)
        self.durationSlider.setSingleStep(1)
        DEFAULT_BEHAVIOUR_DURATION = 5
        self.durationSlider.setValue(DEFAULT_BEHAVIOUR_DURATION) #Get default duration for each behaviour class!!
        self.durationSlider.setPageStep(5)
        self.durationSlider.setTickInterval(10)
        self.durationSlider.setTickPosition(QtGui.QSlider.TicksBelow)
        self.durationSlider.valueChanged.connect(self.set_duration)
        
        #self.behaviourCompletedEdit = QtGui.QDateTimeEdit(datetime_started.addSecs(60*int(self.durationSlider.value())))
        self.behaviourCompletedEdit = MyDateTimeEdit(datetime_started.addSecs(60*int(self.durationSlider.value())))
        self.behaviourCompletedEdit.setObjectName('behaviourCompletedEdit')
        self.behaviourCompletedEdit.setWrapping(True)
        #self.behaviourCompletedEditFocusFilter = DateTimeEditFilter()
        #self.behaviourCompletedEdit.installEventFilter(self.behaviourCompletedEditFocusFilter)
        #self.behaviourCompletedEditFocusFilter.focusIn.connect(self.select_minutes_section)

        self.behaviourCompletedEdit.setDisplayFormat("yyyy-MM-dd hh:mm:ss")
        self.durationGroupBoxLayout.addWidget(self.durationSlider)
        self.durationGroupBoxLayout.addWidget(self.behaviourCompletedEdit)
        self.durationGroupBox.setLayout(self.durationGroupBoxLayout)
        #### /duration ####
        
        self.behaviourQualityEdit = QtGui.QSlider(QtCore.Qt.Horizontal)
        self.behaviourQualityEdit.setObjectName('behaviourQualityEdit')
        self.behaviourQualityEdit.setRange(0,10)
        self.behaviourQualityEdit.setSingleStep(1)
        self.behaviourQualityEdit.setValue(5) #Get default behaviour quality.
        self.behaviourQualityLabel = QtGui.QLabel("Quality: " + str(self.behaviourQualityEdit.value()))
        self.behaviourQualityEdit.valueChanged.connect(self.set_quality)
        
        self.behaviourDurationVarianceEdit = QtGui.QSlider(QtCore.Qt.Horizontal)
        self.behaviourDurationVarianceEdit.setObjectName('behaviourDurationVarianceEdit')
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
        
        #self.behaviourCommentEditLabel = QtGui.QLabel('Comment:')
        self.behaviourCommentEdit = QtGui.QTextEdit()
        self.behaviourCommentEdit.setObjectName('behaviourCommentEdit')
        ######### /RIGHT WIDGET (behaviour comment)###############
        
        ######## TOP WIDGET (contains left and right widgets) #######
        self.behaviourRecordDetailsBox.addWidget(self.behaviourRecordDetailsWidgetLeft)
        #self.behaviourRecordDetailsBox.addWidget(self.behaviourCommentEditLabel)
        self.behaviourRecordDetailsBox.addWidget(self.behaviourCommentEdit)
        self.behaviourRecordDetailsWidget.setLayout(self.behaviourRecordDetailsBox)
        ######## /TOP WIDGET (contains left and right widgets) #######
        
        ######## behaviour list widget #################
        self.behaviourRecords = QtGui.QListWidget()
        self.behaviourRecords.setObjectName('behaviourRecords')
        
        ######## compose behaviour input widget. ################
        self.addBehaviorBox = QtGui.QVBoxLayout()
        self.addBehaviorBox.setObjectName('addBehaviorBox')
        self.addBehaviorBox.addWidget(self.buttonsWidget)
        self.addBehaviorBox.addWidget(self.behaviourRecordDetailsWidget)
        self.addBehaviorBox.addWidget(self.behaviourRecords)
        self.setLayout(self.addBehaviorBox)
            
        self.KeyPressFilter = KeyPressFilter()
        self.installEventFilter(self.KeyPressFilter)
        self.KeyPressFilter.f1_pressed.connect(self.add_behaviour)
        self.KeyPressFilter.f2_pressed.connect(self.add_behaviour_class)
        self.KeyPressFilter.f3_pressed.connect(self.finish)
        self.KeyPressFilter.tilda_pressed.connect(self.behaviourClassSelector.setFocus)
        self.shortcutAltE = QtGui.QShortcut(QtGui.QKeySequence("Alt+E"),self)

        self.shortcutAltE.activated.connect(self.comment_edit)

        
        self.prev_duration = 0
        self.bCND = ''
        self.behaviour_records = []
        self.load_behaviour_classes()
    
    def select_minutes_section(self):
        """ useless as of now."""
        self.app.focusWidget().setSelectedSection(QtGui.QDateTimeEdit.MinuteSection)
    
    @pyqtSlot(int)
    def set_duration(self,duration):                  
        #self.behaviourCompletedEdit.setDateTime(self.behaviourCompletedEdit.dateTime().addSecs(60*int(self.durationSlider.value())))
        self.behaviourCompletedEdit.setDateTime(self.behaviourStartedEdit.dateTime().addSecs(60*duration))
        #self.prev_duration = durat
    
    def comment_edit(self):
        print('comment_edit!')
        if self.behaviourCommentEdit.hasFocus():
            self.previousFocus = QtGui.QApplication.instance().old
            self.previousFocus.setFocus()
            self.save_comment()
        else:
            self.previousFocus = QtGui.QApplication.focusWidget()
            #self.previousFocus = QtGui.QApplication.instance().old
            self.behaviourCommentEdit.setFocus()

            

    def save_comment(self):
        print('save_comment:')

    def set_quality(self):
        self.behaviourQualityLabel.setText("Quality: " + str(self.behaviourQualityEdit.value()))
        
    def set_variance(self):
        """
        This is for plotting (blurring element borders) and operation research.
        """
        pass
        
        
    def add_behaviour(self):
        """Improve later:Add UUID.
        TableWidget or TreeWidget."""
        #later we can improve the format of description of the process.
        
        
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
        #'Started: '
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
        #refactor later.
        cmd=cmd.format(b.behaviourId, b.comment, b.time_created, b.time_started,b.predicted_duration,
        b.duration, b.quality, b.source, b.variance)
        self.storage.ex(cmd)
        record = b.name + '\tStarted: ' + b.time_started + ' \tDuration:' + str(b.duration) + 'm'
        self.behaviourRecords.addItem(QtCore.QString(record))
        
        self.behaviourStartedEdit.setDateTime(self.behaviourCompletedEdit.dateTime())
        self.behaviourCompletedEdit.setDateTime(self.behaviourCompletedEdit.dateTime().addSecs(self.durationSlider.value()*60))
        #if self.lastBehaviourTimeCompleted == '':
        #    #"%Y-%m-%d %H:%M:%S"-> secs.
        #    #mktime(strptime()
        #    #self.behaviourCompletedEdit
        self.lastBehaviourTimeCompleted = self.behaviourCompletedEdit.dateTime()
        self.parent().lastBehaviourTimeCompleted = self.behaviourCompletedEdit.dateTime()
    
    def load_behaviour_journal(self):
        #cmd = "SELECT * FROM behaviour_journal"
        cmd = "SELECT behaviour_classes.name, behaviour_journal.behaviourId,behaviour_journal.time_started, behaviour_journal.duration FROM behaviour_classes,behaviour_journal WHERE behaviour_classes.id=behaviour_journal.behaviourId"
        query = self.storage.q
        self.storage.ex(cmd)
        
        while query.next():
            record = type('',(dict,),{})()
            record.name = str(query(value(0)))
            record.id = int(query(1))
            record.time_started = str(query(2))
            record.duration = int(query(3))
            self.behaviour_records.append(record)
        
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
        self.done(1)