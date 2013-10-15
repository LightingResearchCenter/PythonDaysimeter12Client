# -*- coding: utf-8 -*-
"""
Created on Mon Aug 05 16:33:14 2013

@author: kundlj
"""
import sys
from PyQt4 import QtGui

class StartLogInfo(QtGui.QWidget):
    
    def __init__(self, parent=None):
        super(StartLogInfo, self).__init__(parent)
        
        self.setWindowTitle('Log History Utility')
        
        self.daysimeter_id = QtGui.QStatusBar()
        self.start_date = QtGui.QStatusBar()
        self.log_interval = QtGui.QStatusBar()
        
        self.daysimeter_id.setSizeGripEnabled(False)
        self.start_date.setSizeGripEnabled(False)
        self.log_interval.setSizeGripEnabled(False)
        
        self.input = QtGui.QLineEdit()
        
        self.find = QtGui.QPushButton('Find')
        self.find_next = QtGui.QPushButton('Find Older')
        self.find_prev = QtGui.QPushButton('Find Newer')
        
        self.status = QtGui.QStatusBar()
        self.status.setSizeGripEnabled(False)
        
        self.input.setInputMask('0009')
        self.input.setText('0000')
        
        input_layout = QtGui.QHBoxLayout()
        input_layout.addWidget(self.input)
        input_layout.addWidget(self.find)

        button_layout = QtGui.QHBoxLayout()
        button_layout.addWidget(self.find_prev)
        button_layout.addWidget(self.find_next)        
        
        layout = QtGui.QFormLayout()
        layout.addRow(input_layout)
        layout.addRow('Daysimeter ID:', self.daysimeter_id)
        layout.addRow('Start Date/Time:', self.start_date)
        layout.addRow('Log Interval', self.log_interval)
        layout.addRow(button_layout)
        layout.addRow(self.status)
        
        self.setLayout(layout)
        
        self.find_next.setEnabled(False)
        self.find_prev.setEnabled(False)
        
        self.find.pressed.connect(self.find_val)
        self.find_next.pressed.connect(self.next_val)
        self.find_prev.pressed.connect(self.prev_val)
        
        with open('start_log.txt', 'r') as fp:
            data = fp.readlines()
        
        self.data = [x.strip('\n').split('\t') for x in data]
        
        self.setFixedSize(self.sizeHint())
        self.show()
        
    def find_val(self):
        self.val_index = []
        self.val_index_index = 0
        val = int(self.input.text())
        
        for x in range(len(self.data)):
            if int(self.data[x][0]) == val:
                self.val_index.append(x)
        
        if len(self.val_index) > 0:
            self.status.showMessage('Log ' + str(self.val_index_index + 1) + \
                                    ' of ' + str(len(self.val_index)))
            self.daysimeter_id.showMessage(self.data[0][0])
            self.start_date.showMessage(self.data[0][1])
            self.log_interval.showMessage(self.data[0][2])
            
        else:
            self.status.showMessage('No Entires Found', 5000)
            self.daysimeter_id.showMessage('')
            self.start_date.showMessage('')
            self.log_interval.showMessage('')
            self.find_next.setEnabled(False)
            self.find_prev.setEnabled(False)
            
        if len(self.val_index) > 2:
            self.find_next.setEnabled(True)
            
    def next_val(self):
        self.val_index_index += 1
        
        self.daysimeter_id.showMessage(self.data[self.val_index[self.val_index_index]][0])
        self.start_date.showMessage(self.data[self.val_index[self.val_index_index]][1])
        self.log_interval.showMessage(self.data[self.val_index[self.val_index_index]][2])
        
        self.find_prev.setEnabled(True)
        
        self.status.showMessage('Log ' + str(self.val_index_index + 1) + \
                                    ' of ' + str(len(self.val_index)))
        
        if self.val_index_index == len(self.val_index) - 1:
            self.find_next.setEnabled(False)
        
    def prev_val(self):
        self.val_index_index -= 1
        
        self.daysimeter_id.showMessage(self.data[self.val_index[self.val_index_index]][0])
        self.start_date.showMessage(self.data[self.val_index[self.val_index_index]][1])
        self.log_interval.showMessage(self.data[self.val_index[self.val_index_index]][2])
        
        self.find_next.setEnabled(True)
        
        self.status.showMessage('Log ' + str(self.val_index_index + 1) + \
                                    ' of ' + str(len(self.val_index)))
        
        if self.val_index_index == 0:
            self.find_prev.setEnabled(False)
            
def main():
    """ PURPOSE: Creates app and runs widget """
    # Create the Qt Application
    app = QtGui.QApplication(sys.argv)
    # Create and show the form
    session = StartLogInfo()
    session.show()
    # Run the main Qt loop
    sys.exit(app.exec_())
            
if __name__ == '__main__':
    main()    
    