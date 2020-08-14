import sip
sip.setapi("QString", 1)
from PyQt4 import QtCore, QtGui
import time

#class TimeSpentPredictionDialog(QtGui.QDialog):
class NewTaskDialog(QtGui.QDialog):
    def __init__(self,task_item='',focus='name'):
        super(QtGui.QDialog, self).__init__()
        self.setWindowFlags(QtCore.Qt.CustomizeWindowHint)
        if task_item == '': 
            self.name = 'New task...'
            self.prediction = 15
        else:
            self.name = task_item.name
            if task_item.time_spent_prediction == '':
                self.prediction = 0
            else:
                self.prediction = int(task_item.time_spent_prediction)
        self.vbox = QtGui.QVBoxLayout()
        
        self.info1=QtGui.QLabel('Task name:')
        self.nameEdit = QtGui.QLineEdit()
        self.nameEdit.setText(self.name)
        self.nameEdit.editingFinished.connect(self.setName)
        
        self.slider = QtGui.QSlider(QtCore.Qt.Horizontal)
        self.slider.setRange(5,720)
        self.slider.setSingleStep(5)
        self.slider.setValue(self.prediction)
        self.slider.setPageStep(60)
        self.slider.setTickInterval(10)
        self.slider.setTickPosition(QtGui.QSlider.TicksBelow)
        self.slider.valueChanged.connect(self.set_prediction)
        
        self.info2 = QtGui.QLabel('Predict completion time for the task:')
        
        self.predictionLabel = QtGui.QLabel(str(self.prediction)+ ' minutes')
        
        self.ok = QtGui.QPushButton('Ok')
        self.ok.clicked.connect(self.finish)
        
        #self.buttons=QtGui.QDialogButtonBox(QtGui.QDialogButtonBox.Ok|
        #self.buttons=QtGui.QDialogButtonBox(QtGui.QDialogButtonBox.Ok|
        #                                    QtGui.QDialogButtonBox.Cancel)
        #self.buttons.clicked.connect(self.finish)
        
        self.vbox.addWidget(self.info1)
        self.vbox.addWidget(self.nameEdit)
        self.vbox.addWidget(self.info2)
        self.vbox.addWidget(self.slider)
        self.vbox.addWidget(self.predictionLabel)
        #self.vbox.addWidget(self.buttons)
        self.vbox.addWidget(self.ok)
        
        self.setLayout(self.vbox)
        if focus == 'name':
            self.nameEdit.selectAll()
        elif focus == 'time_spent_prediction':
            self.slider.setFocus()
            
    def finish(self):
        self.done(1)
        
    def setName(self):
        self.name = str(self.nameEdit.text())
        
    def set_prediction(self):
        self.prediction = self.slider.value()
        self.predictionLabel.setText(str(self.prediction) + ' minutes')
        
        