from PyQt4 import QtCore, QtGui

class BetterTextEdit(QtGui.QTextEdit):
    def __init__(self, parent = None):
        QtGui.QTextEdit.__init__(self, parent)
                 
    def canInsertFromMimeData(mimedata):
        if mimedata.hasImage():
            return True
        else:
            QtGui.QTextEdit.canInsertFromMimeData(mimedata)
	
    def insertFromMimeData(self, mimedata):
        if mimedata.hasImage():
		    image = QtGui.
        QtGui.QTextEdit.insertFromMimeData(self, mimedata)