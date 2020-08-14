import sys,time
import sip
#sip.setapi('QString', 1)
from PyQt4 import QtCore, QtGui, QtTest,QtSql
from PyQt4.QtCore import *
from PyQt4.QtGui import *
import keyboard
import subprocess as sp

class KeyboardLog(QtCore.QObject):
    finished_sig = QtCore.pyqtSignal()
    activate_sig = QtCore.pyqtSignal()
    def __init__(self):
        super(QtCore.QObject, self).__init__()
        self.time_started = time.time()
        self.running = True
        self.counter = 0
        self.max = 10000
        self.requesting_stop = False
        self.debug = True
        self.hooked = False
        self.prev_name = ''
        self.prev_cap_time = 0
        self.hotkeys = []
        
    def dbg_print(self,text):
        if self.debug:
            print(text)
    
    @pyqtSlot()
    def start_keyboard_logging(self): 
        keyboard.hook(self.print_pressed_keys)
        self.hooked = False
        self.install_hotkeys()
        keyboard.wait()
    
    def install_hotkeys(self):
        """
        Put hotkeys for an app here.
        """
        #hotkey = keyboard.add_hotkey('alt+q',self.exit_hotkey)
        hotkey = keyboard.add_hotkey('alt+`',self.activate_window)
        hotkey_cmd = keyboard.add_hotkey('windows+enter', self.open_cmd)
        hotkey_paste_time = keyboard.add_hotkey('right ctrl+windows',self.paste_time_ctrl_v)
        self.hotkeys.append(hotkey)
        return None
    def paste_time_ctrl_v(self):
        t = time.strftime("%H:%M:%S")
        #keyboard.send(
        #keyboard.write(t, exact=True)
        keyboard.write(t)
        keyboard.send('left ctrl')
    def open_cmd(self):
        sp.Popen('start cmd /K cd %USERPROFILE%\Documents', shell=True)
    def activate_window(self):
        self.activate_sig.emit()
        
    def exit_hotkey(self):
        for h in self.hotkeys:
            keyboard.remove_hotkey(h)
        self.stop_keyboard_logging()
        self.finished_sig.emit()

    def print_pressed_keys(self,e):
        line = ', '.join(str(code) for code in keyboard._pressed_events)
        # '\r' and end='' overwrites the previous line.
        if e.name != self.prev_name or (time.time()-self.prev_cap_time) > 0.2:
            self.prev_cap_time = time.time()
            self.prev_name = e.name
            #print(e.name, end="", flush=True)
            #print(e.name,e.time)
            # !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
            #print(e.scan_code,e.name,time.strftime("%H:%M:%S"))
            #print(e.name, e.scan_code, end="", flush=True)

    @pyqtSlot()
    def stop_keyboard_logging(self):
        self.running = False
        self.dbg_print('[0]Unhooking')
        keyboard.unhook_all()
        self.dbg_print('[1]Unhooked')
        self.hooked = False