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
    """
    Status indicator light for daysimeter device.
    """
    def __init__(self, parent=None):
        """ Creates the "lights" and adds them to the layout. """
        super(StatusLight, self).__init__(parent)
#        self.setFixedSize(22,22)
        
        self.green = GreenLight(self)
        self.yellow = YellowLight(self)
        self.red = RedLight(self)
        
        layout = QtGui.QVBoxLayout()
        layout.addWidget(self.green)
        layout.addWidget(self.yellow)
        layout.addWidget(self.red)
        
        self.setLayout(layout)
        self.green.hide()
        self.red.hide()
        
        self.set_status()
        
    def set_status(self):
        """ Creates a watcher to determine whether a daysimeter is attached """
        self.status_watcher = SetStatus(self)
        self.status_watcher.connected.connect(self.set_green)
        self.status_watcher.not_connected.connect(self.set_red)
        self.status_watcher.start()
        
    def set_green(self):
        """ Sets the green light """
        self.yellow.hide()
        self.red.hide()
        self.green.show()
        
    def set_red(self):
        """ sets the red light """
        self.yellow.hide()
        self.green.hide()
        self.red.show()
    
    def set_yellow(self):
        """ sets the yellow light """
        self.green.hide()
        self.red.hide()
        self.yellow.show()
        
class GreenLight(QtGui.QWidget):
    """ Creates a green circle """
    def __init__(self, parent=None):
        """ Initializes circle with fixed size and color """
        super(GreenLight, self).__init__(parent)
        self.setFixedSize(22, 22)
        self.green = QtGui.QColor(44, 173, 9)
        
    def paintEvent(self, e):
        """ Draws the circle """
        painter = QtGui.QPainter()
        painter.begin(self)
        painter.setRenderHint(QtGui.QPainter.Antialiasing, True)        
        painter.setPen(self.green)
        painter.setBrush(self.green)
        painter.drawEllipse(1, 1, 20, 20)
        painter.end()

class YellowLight(QtGui.QWidget):
    """ Creates a yellow circle """
    def __init__(self, parent=None):
        """ Initializes circle with fixed size and color """
        super(YellowLight, self).__init__(parent)
        self.setFixedSize(22, 22)
        self.yellow = QtGui.QColor(227, 227, 93)
        
    def paintEvent(self, e):
        """ Draws the circle """
        painter = QtGui.QPainter()
        painter.begin(self)
        painter.setRenderHint(QtGui.QPainter.Antialiasing, True)        
        painter.setPen(self.yellow)
        painter.setBrush(self.yellow)
        painter.drawEllipse(1, 1, 20, 20)
        painter.end()
        
        
class RedLight(QtGui.QWidget):
    """ Creates a red circle """
    def __init__(self, parent=None):
        """ Initializes circle with fixed size and color """
        super(RedLight, self).__init__(parent)
        self.setFixedSize(22, 22)
        self.red = QtGui.QColor(184, 18, 27)
        
    def paintEvent(self, e):
        """ Draws the circle """
        painter = QtGui.QPainter()
        painter.begin(self)
        painter.setRenderHint(QtGui.QPainter.Antialiasing, True)        
        painter.setPen(self.red)
        painter.setBrush(self.red)
        painter.drawEllipse(1, 1, 20, 20)
        painter.end()
        
class SetStatus(QtCore.QThread):
    """ Determines whether a daysimeter is attached or not """
    connected = QtCore.pyqtSignal()
    not_connected = QtCore.pyqtSignal()    
    
    def __init__(self, args, parent=None):
        """Initializes Thread."""
        QtCore.QThread.__init__(self, parent)
        
    def run(self):
        """ runs the thread """
        while True:
            if not find_daysimeter():
                self.not_connected.emit()
            else:
                self.connected.emit()
            time.sleep(1)
    
        
def main():
    """ runs the status indicator """
    app = QtGui.QApplication(sys.argv)
    light = StatusLight()
    light.show()
    sys.exit(app.exec_())
        
if __name__ == '__main__':
    main()