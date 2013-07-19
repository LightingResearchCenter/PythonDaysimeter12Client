# -*- coding: utf-8 -*-
"""
Created on Wed Jul 17 14:19:29 2013

@author: kundlj
"""

import sys, os
sys.path.insert(0, os.pardir)
import time
from src.finddaysimeter import find_daysimeter
from PyQt4 import QtGui, QtCore

class StatusLight(QtGui.QWidget):
    
    def __init__(self, parent=None):
        super(StatusLight, self).__init__(parent)
#        self.setFixedSize(22,22)
        
        self.green = GreenLight(self)
        self.green_text = GreenText(self)
        self.yellow = YellowLight(self)
        self.red = RedLight(self)
        
        green_layout = QtGui.QHBoxLayout()
        green_layout.addWidget(self.green)
        green_layout.addWidget(self.green_text)
        
        
        
        layout = QtGui.QVBoxLayout()
        layout.addLayout(green_layout)
        layout.addWidget(self.yellow)
        layout.addWidget(self.red)
        
        self.setLayout(layout)
        self.green.hide()
        self.red.hide()
        
        self.set_status()
        
    def set_status(self):
        self.status_watcher = SetStatus(self)
        self.status_watcher.connected.connect(self.set_green)
        self.status_watcher.not_connected.connect(self.set_red)
        self.status_watcher.start()
        
    def set_green(self):
        self.yellow.hide()
        self.red.hide()
        self.green.show()
        
    def set_red(self):
        self.yellow.hide()
        self.green.hide()
        self.red.show()
        
class GreenLight(QtGui.QWidget):
    
    def __init__(self, parent=None):
        super(GreenLight, self).__init__(parent)
        self.setFixedSize(22,22)
        self.green = QtGui.QColor(44, 173, 9)
        
    def paintEvent(self, e):
        painter = QtGui.QPainter()
        painter.begin(self)
        painter.setRenderHint(QtGui.QPainter.Antialiasing, True)        
        painter.setPen(self.green)
        painter.setBrush(self.green)
        painter.drawEllipse(1, 1, 20, 20)
        painter.end()
        
class GreenText(QtGui.QWidget):
    
    def __init__(self, parent=None):
        super(GreenText, self).__init__(parent)
#        self.setFixedSize(22,22)
        
    def paintEvent(self, e):
        painter = QtGui.QPainter()
        painter.begin(self)
        painter.setRenderHint(QtGui.QPainter.Antialiasing, True)        
        painter.setPen(QtGui.QColor(0, 0, 0))
        painter.drawText(e.rect(), QtCore.Qt.AlignLeft, 'Daysimeter Status: Okay')
        painter.end() 

class YellowLight(QtGui.QWidget):
    
    def __init__(self, parent=None):
        super(YellowLight, self).__init__(parent)
        self.setFixedSize(22,22)
        self.yellow = QtGui.QColor(237, 242, 97)
        
    def paintEvent(self, e):
        painter = QtGui.QPainter()
        painter.begin(self)
        painter.setRenderHint(QtGui.QPainter.Antialiasing, True)        
        painter.setPen(self.yellow)
        painter.setBrush(self.yellow)
        painter.drawEllipse(1, 1, 20, 20)
        painter.end()
        
        
class RedLight(QtGui.QWidget):
    
    def __init__(self, parent=None):
        super(RedLight, self).__init__(parent)
        self.setFixedSize(22,22)
        self.red = QtGui.QColor(184, 18, 27)
        
    def paintEvent(self, e):
        painter = QtGui.QPainter()
        painter.begin(self)
        painter.setRenderHint(QtGui.QPainter.Antialiasing, True)        
        painter.setPen(self.red)
        painter.setBrush(self.red)
        painter.drawEllipse(1, 1, 20, 20)
        painter.end()
        
class SetStatus(QtCore.QThread):
    connected = QtCore.pyqtSignal()
    not_connected = QtCore.pyqtSignal()    
    
    def __init__(self, args, parent=None):
        """Initializes Thread."""
        QtCore.QThread.__init__(self, parent)
        
    def run(self):
        while True:
            if not find_daysimeter():
                self.not_connected.emit()
            else:
                self.connected.emit()
            time.sleep(1)
    
        
def main():
    app = QtGui.QApplication(sys.argv)
    light = StatusLight()
    light.show()
    sys.exit(app.exec_())
        
if __name__ == '__main__':
    main()