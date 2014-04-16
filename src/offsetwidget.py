# -*- coding: utf-8 -*-
"""
Created on Wed Apr 09 09:50:59 2014

@author: kundlj
"""

from PyQt4 import QtGui, QtCore
import sys, logging

class OffsetWidget(QtGui.QWidget):
    """
    PURPOSE: Widget to apply UTC offset to data
    """
    
    send = QtCore.pyqtSignal(int, bool)    
    
    def __init__(self, parent=None, default=None):
        """ default - the default UTC offset """
        super(OffsetWidget, self).__init__(parent)
        if default:
            self.default = default
        else:
            self.default = 15
        self.daysim_log = logging.getLogger('daysim_log')
        self.err_log = logging.getLogger('err_log')
        self.initUI()
        
    def initUI(self):
        self.daysim_log.info('offsetwidget.py class Offsetwidget func initUI: Initializing GUI')
        self.setWindowTitle('UTC Offset')
        self.setFixedSize(200, 100)        
        self.submit = QtGui.QPushButton('Submit')
        self.cancel = QtGui.QPushButton('Cancel')
        self.offset = QtGui.QComboBox()
        items = ['UTC-12:00', 'UTC-11:00', 'UTC-10:00', 'UTC-09:30', \
                 'UTC-09:00', 'UTC-08:00', 'UTC-07:00', 'UTC-06:00', \
                 'UTC-05:00', 'UTC-04:30', 'UTC-04:00', 'UTC-03:30', \
                 'UTC-03:00', 'UTC-02:00', 'UTC-01:00', 'UTC+00:00', \
                 'UTC+00:00', 'UTC+01:00', 'UTC+02:00', 'UTC+03:00', \
                 'UTC+03:30', 'UTC+04:00', 'UTC+04:30', 'UTC+05:00', \
                 'UTC+05:30', 'UTC+05:45', 'UTC+06:00', 'UTC+06:30', \
                 'UTC+07:00', 'UTC+08:00', 'UTC+08:45', 'UTC+09:00', \
                 'UTC+09:30', 'UTC+10:00', 'UTC+10:30', 'UTC+11:00', \
                 'UTC+11:30', 'UTC+12:00', 'UTC+12:45', 'UTC+13:00', \
                 'UTC+14:00']
        self.daysim_log.info('offsetwidget.py class Offsetwidget func initUI: Offsets Loaded')
        self.offset.addItems(items)
        self.offset.setCurrentIndex(self.default)
        self.make_default = QtGui.QCheckBox('Remember my offset')
        
        button_layout = QtGui.QHBoxLayout()
        button_layout.addWidget(self.submit)
        button_layout.addWidget(self.cancel)
        
        layout = QtGui.QVBoxLayout()
        layout.addWidget(self.offset)
        layout.addWidget(self.make_default)
        layout.addLayout(button_layout)
        self.daysim_log.info('offsetwidget.py class Offsetwidget func initUI: Setting layout')
        self.setLayout(layout)
        self.daysim_log.info('offsetwidget.py class Offsetwidget func initUI: Connecting signals to sockets')
        self.submit.pressed.connect(self.close_self)
        self.cancel.pressed.connect(self.close)
        self.daysim_log.info('offsetwidget.py class Offsetwidget func initUI: Widget visable')
        
    def close_self(self):
        self.daysim_log.info('offsetwidget.py class Offsetwidget func close_self: Emitting signal')
        self.send.emit(self.offset.currentIndex(), self.make_default.isChecked())
        self.close()
        

def main():
    """ PURPOSE: Creates app and runs widget """
    # Create the Qt Application
    app = QtGui.QApplication(sys.argv)
    # Create and show the form
    session = OffsetWidget()
    # Run the main Qt loop
    sys.exit(app.exec_())
            
if __name__ == '__main__':
    main()