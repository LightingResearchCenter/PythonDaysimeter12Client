# -*- coding: utf-8 -*-
"""
Created on Mon Jul 22 09:55:45 2013

@author: kundlj
"""

import sys, os
sys.path.insert(0, os.pardir)
import time
from src.finddaysimeter import find_daysimeter
import src.constants as constants_
from PyQt4 import QtGui, QtCore

class StatusWidget(QtGui.QWidget):
    
    def __init__(self, parent=None):
        super(StatusWidget, self).__init__(parent)
        self.standby = StandbyStatus(self)
        self.new = NewStatus(self)
        self.resume = ResumeStatus(self)
        self.no_daysim = NoDaysimeter(self)
        self.corrupt = Corrupt(self)

        
        layout = QtGui.QHBoxLayout()
        layout.addWidget(self.standby)
        layout.addWidget(self.new)
        layout.addWidget(self.resume)
        layout.addWidget(self.no_daysim)
        layout.addWidget(self.corrupt)
        self.setLayout(layout)
        
        self.find_status()
        self.set_status()
        
    def set_standby(self):
        self.new.hide()
        self.resume.hide()
        self.no_daysim.hide()
        self.standby.show()
        self.corrupt.hide()
        self.setFixedSize(166, 30)
        
    def set_new(self):
        self.new.show()
        self.resume.hide()
        self.no_daysim.hide()
        self.standby.hide()
        self.corrupt.hide()
        self.setFixedSize(234, 30)
        
    def set_resume(self):
        self.new.hide()
        self.resume.show()
        self.no_daysim.hide()
        self.standby.hide()
        self.corrupt.hide()
        self.setFixedSize(252, 30)
        
    def set_not_found(self):
        self.new.hide()
        self.resume.hide()
        self.no_daysim.show()
        self.standby.hide()
        self.corrupt.hide()
        self.setFixedSize(198, 30)
        
    def set_corrupt(self):
        self.new.hide()
        self.resume.hide()
        self.no_daysim.hide()
        self.standby.hide()
        self.corrupt.show()
        self.setFixedSize(192, 30)
        
    def set_status(self):
        self.status_watcher = SetStatus(self)
        self.status_watcher.connected.connect(self.find_status)
        self.status_watcher.not_connected.connect(self.set_not_found)
        self.status_watcher.start()
        
    def find_status(self):
        lens = {17,35}
        if not find_daysimeter():
            self.set_not_found()
        else:
            path = find_daysimeter()
            filename = constants_.LOG_FILENAME
            if path:
                with open(path + filename, 'r') as log_fp:
                    info = log_fp.readlines()
                if not len(info) in lens:
                    self.set_corrupt()
                elif int(info[0]) == 0:
                    self.set_standby()
                elif int(info[0]) == 2:
                    self.set_new()
                elif int(info[0]) == 4:
                    self.set_resume()
                else:
                    self.set_corrupt()
            
        
class StandbyStatus(QtGui.QWidget):
    
    def __init__(self, parent=None):
        super(StandbyStatus, self).__init__(parent)
        
    def paintEvent(self, e):
        painter = QtGui.QPainter()
        painter.begin(self)
        painter.setRenderHint(QtGui.QPainter.Antialiasing, True)        
        painter.setPen(QtGui.QColor(0, 0, 0))
        painter.drawText(e.rect(), QtCore.Qt.AlignLeft, \
                         'Daysimeter is in standby mode.')
        painter.end()
        
class NewStatus(QtGui.QWidget):
    
    def __init__(self, parent=None):
        super(NewStatus, self).__init__(parent)
        
    def paintEvent(self, e):
        painter = QtGui.QPainter()
        painter.begin(self)
        painter.setRenderHint(QtGui.QPainter.Antialiasing, True)        
        painter.setPen(QtGui.QColor(0, 0, 0))
        painter.drawText(0, 10, \
                         'Daysimeter will start a new log when ejected.')
        painter.end()
        
        
class ResumeStatus(QtGui.QWidget):
    
    def __init__(self, parent=None):
        super(ResumeStatus, self).__init__(parent)
        
    def paintEvent(self, e):
        painter = QtGui.QPainter()
        painter.begin(self)
        painter.setRenderHint(QtGui.QPainter.Antialiasing, True)        
        painter.setPen(QtGui.QColor(0, 0, 0))
        painter.drawText(0, 10, \
                         'Daysimeter will resume current log when ejected.')
        painter.end()
        
    
class NoDaysimeter(QtGui.QWidget):
    
    def __init__(self, parent=None):
        super(NoDaysimeter, self).__init__(parent)
        
    def paintEvent(self, e):
        painter = QtGui.QPainter()
        painter.begin(self)
        painter.setRenderHint(QtGui.QPainter.Antialiasing, True)        
        painter.setPen(QtGui.QColor(0, 0, 0))
        painter.drawText(0, 10, \
                         'No Daysimeter plugged into computer.')
        painter.end()
        
class Corrupt(QtGui.QWidget):
    
    def __init__(self, parent=None):
        super(Corrupt, self).__init__(parent)
        
    def paintEvent(self, e):
        painter = QtGui.QPainter()
        painter.begin(self)
        painter.setRenderHint(QtGui.QPainter.Antialiasing, True)        
        painter.setPen(QtGui.QColor(0, 0, 0))
        painter.drawText(0, 10, \
                         'ERROR: Daysimeter Header corrupt.')
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
    status = StatusWidget()
    status.show()
    sys.exit(app.exec_())
        
if __name__ == '__main__':
    main()