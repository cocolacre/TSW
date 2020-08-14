# auto-cycling-widget.py
class AutoCyclingLabel(QtGui.QLabel):
    keyPressed = QtCore.pyqtSignal(QtCore.QEvent)
    def __init__(self,parent=None):
        super(QtGui.QLabel, self).__init__()
        self.setWindowTitle("Autocycling label")
        self.move(-10,0)
        self.H = 600 #TODO: get taskbar height. Get monitor handle etc.
        #############################
        
        self.W = 256
        self.H = 32
        self.resize(self.W, self.H)
        self.time_started = time.time()
        self.activityTimer = QtCore.QTimer()
        self.activityTimer.setInterval(3000)
        # strategy 1:
        # several aulChannels QLabels 
        # several QLabel.icons
        # 
        # self.channels=[] 
        # Channel2 = QtGui.QLabel('Channel 2')
        # Channel1 = QtGui.QLabel('Channel 1')
        # self.channels.append(Channel1)
        # self.channels.append(Channel2) #USE DICTS!!!
        # self.activityTimer.timeout.connect(self.switch_channel)
        # self.activityTimer.start()
        # 
        # 
        # 
        # def switch_channel(self):
        # self.setChannel((chn.index()+1)/self.nChannels())
        # self.display.setWidget(self.channels[self.currentChannel()+1)/self.nChannels()
        # 
        # 
        # 
        
        
        