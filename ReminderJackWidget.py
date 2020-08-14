import sip
import random
sip.setapi("QString", 1)
from PyQt4 import QtCore, QtGui
import time
import uuid

class ReminderJackWidget(QtGui.QWidget):
    #Typical use is to call cooperative superclass method [???]
    def __init__(self,parent,mode = 'QLabel'):
        #super(self).__init__()
        super(QtGui.QWidget, self).__init__(parent=parent)
        self.storage = self.parent().storage
        self.reminders = self.parent().reminders
        self.load_reminders()
        self.current = self.reminders[random.randint(0,len(self.reminders)-1)]
        self.setFixedWidth(300)
        self.jack = QtCore.QTimer()
        self.jackFreq = 300
        self.jack.setInterval(self.jackFreq)
        self.jack.timeout.connect(self.jack_flash)
        self.jack.start()
        #self.add_reminder(name='Do sports.')
        
        if mode == 'QLabel':
            self.jackLabelFlashTimer = QtCore.QTimer()
            self.jackLabelFlashTimer.setInterval(777)
            self.jackLabelFlashTimer.timeout.connect(self.jack_label_flash)
            self.jackLabel = QtGui.QLabel(parent=self)
            self.jackLabelFlashTimer.start()
            #self.jackLabel.setText("Do not forget to not forget.")
            self.jackLabel.setText("Do remind to remind.")
            self.jackLabel.setFixedWidth(300)
            
    def jack_flash(self):
        #print('jack_flash:')
        pass
    def jack_label_flash(self):
        self.jackLabelFlashTimer.stop()
        new_interval = 5000+random.random()*5000
        self.jackLabelFlashTimer.setInterval(new_interval)
        self.jackLabelFlashTimer.start()
        #new_bg_color = QtGui.QColor(random.randint(0,255),random.randint(0,255),random.randint(0,255))
        #new_text_color = QtGui.QColor(random.randint(0,255),random.randint(0,255),random.randint(0,255))
        
        #self.jackLabel.setBackgroundColor(new_bg_color)
        #self.jackLabel.setStyleSheet('background-color: rgb({0},{1},{2}); color: rgb({3},{4},{5})'.format(random.randint(240,255),random.randint(240,255),random.randint(240,255),random.randint(0,255),random.randint(0,255),random.randint(0,255))) 
        self.jackLabel.setStyleSheet('font-weight: bold; background-color: rgb({0},{1},{2})'.format(random.randint(140,255),random.randint(140,255),random.randint(140,255)))
        self.current = self.reminders[random.randint(0,len(self.reminders)-1)]
        self.jackLabel.setText(self.current.name)
        #self.jackLabel.setBackgroundColor(new_bg_color)
        #self.jackLabel.setTextColor(new_text_color)
    def load_reminders(self):
        # cmd = "CREATE TABLE IF NOT EXISTS reminders(id integer primary key autoincrement, name varchar(100), uuid varchar(36), time_created varchar(24), status varchar, mode varchar(32), description varchar(2048), times_reminded int)"
        #reminders = []
        fields = [] #Names of table fields        
        query = self.storage.q
        cmd = "PRAGMA table_info(reminders)"
        self.storage.ex(cmd)
        while query.next():
            field = str(query.value(1))
            fields.append(field)
        
        cmd = "SELECT * FROM reminders"
        self.storage.ex(cmd)
        while query.next():
            reminder = type('',(dict,),{})()
            reminder.fields=list(fields)
            fid = 0
            values = []
            #reminder = {}
            while fid < len(fields):
                value = query.value(fid)
                if type(value) is QtCore.QString:
                    value = str(value)
                if type(value) is QtCore.QPyNullVariant:
                    value=''
                values.append(value)
                reminder[fields[fid]] = value
                reminder.__setattr__(fields[fid],value)
                fid+=1
                self.reminders.append(reminder)
    
    def add_reminder(self,name='New reminder'):
        #reminder = {}
        reminder = type('',(dict,),{})()
        #reminder['name'] = 'New reminder...'
        #reminder.__setattr__
        reminder.name = name
        reminder.time_created = time.strftime("%Y-%m-%d %H:%M:%S")
        reminder.uuid = uuid.uuid4()
        reminder.status = 'ACTIVE'
        reminder.mode = 'cron: *,*,*,*,*'
        reminder.description = 'Note this. Do that. Ask about some thing'
        reminder.times_reminded = 0
        cmd = "INSERT INTO reminders VALUES"\
              "(NULL, '{0}','{1}','{2}','{3}','{4}','{5}',{6})".format(
                                                            reminder.name,
                                                            reminder.uuid,
                                                            reminder.time_created,
                                                            reminder.status,
                                                            reminder.mode,
                                                            reminder.description,
                                                            reminder.times_reminded
                                                            )
        self.storage.ex(cmd)