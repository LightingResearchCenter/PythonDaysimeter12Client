"""
startnewlog
Author: Jed Kundl
Creation Date: 08.07.2013
"""

import sys
from PyQt4 import QtGui, QtCore
from datetime import datetime
from finddaysimeter import find_daysimeter
import constants

class StartNewLog(QtGui.QWidget):
    
    def __init__(self, parent=None):
        super(StartNewLog, self).__init__(parent)
        self.setWindowTitle('Start New Log')
        self.setFixedSize(350,150)
        
        self.day = QtGui.QComboBox()
        self.month = QtGui.QComboBox()
        self.year = QtGui.QComboBox()
        
        self.hour = QtGui.QComboBox()
        self.minute = QtGui.QComboBox()
        
        self.start = QtGui.QPushButton('Start')
        self.cancel = QtGui.QPushButton('Cancel')
        
        self.log_interval = QtGui.QComboBox()
        
        self.status = QtGui.QStatusBar()
        
        self.day.addItems([str(x) for x in range(1,32)])
        self.month.addItems([str(x) for x in range(1,13)])
        self.year.addItems([str(x) for x in range(2000, 2021)])
        
        self.hour.addItems([str(x) for x in range(24)])
        self.minute.addItems([str(x) for x in range(60)])
        
        self.log_interval.addItems(['030', '060', '090', '120', '150', '180'])
        
        current_time = datetime.now()
        
        self.day.setCurrentIndex(current_time.day - 1)
        self.month.setCurrentIndex(current_time.month - 1)
        self.year.setCurrentIndex(current_time.year - 2000)
        
        self.hour.setCurrentIndex(current_time.hour)
        self.minute.setCurrentIndex(current_time.minute)
        
        self.log_interval.setCurrentIndex(1)
        
        self.battery_hours()
        
        dmy_layout = QtGui.QHBoxLayout()
        dmy_layout.addWidget(self.day)
        dmy_layout.addWidget(self.month)
        dmy_layout.addWidget(self.year)
        
        hm_layout = QtGui.QHBoxLayout()
        hm_layout.addWidget(self.hour)
        hm_layout.addWidget(self.minute)
        
        button_layout = QtGui.QHBoxLayout()
        button_layout.addWidget(self.start)
        button_layout.addWidget(self.cancel)
        
        layout = QtGui.QFormLayout()
        layout.addRow('Date', dmy_layout)
        layout.addRow('Time', hm_layout)
        layout.addRow('Logging Interval', self.log_interval)
        layout.addRow(button_layout)
        layout.addRow(self.status)
        
        self.setLayout(layout)
        
        self.start.pressed.connect(self.begin_log)
        self.cancel.pressed.connect(self.close)
        
    def begin_log(self):
        reply = QtGui.QMessageBox.question(self, 'Warning',
        'Starting a new log will delete current log.', QtGui.QMessageBox.Ok, \
        QtGui.QMessageBox.Cancel)
        
        if reply == QtGui.QMessageBox.Ok:
            self.start_log()
        else:
            pass

    def start_log(self):
        self.logthread = NewLogThread([str(self.day.currentText()), \
                                     str(self.month.currentText()), \
                                     str(self.year.currentText()), \
                                     str(self.hour.currentText()), \
                                     str(self.minute.currentText()), \
                                     str(self.log_interval.currentText())])
        self.logthread.done_sig.connect(self.close)
        self.logthread.no_daysim_sig.connect(self.disp_error)
        self.logthread.start()
        
    def disp_error(self):
        QtGui.QMessageBox.question(self, 'Error',
                                   'No Daysimeter Found!', \
                                   QtGui.QMessageBox.Ok)
                                   
    def battery_hours(self):
        path = find_daysimeter()
        log_filename = constants.LOG_FILENAME
        
        if not path:
            self.no_daysim_sig.emit()
        else:
            with open(path + log_filename,'r') as log_fp:
                info = log_fp.readlines()
            if len(info) == 17:
                self.status.showMessage('Number of hours logged using current battery: ' + \
                                       str(info[4]))
            else:
                self.status.showMessage('Number of hours logged using current battery: ' + \
                                       str(info[6]))
        
        
        
class NewLogThread(QtCore.QThread):
    done_sig = QtCore.pyqtSignal()
    no_daysim_sig = QtCore.pyqtSignal()
    
    def __init__(self, args, parent=None):
        QtCore.QThread.__init__(self, parent)
        
        self.day = args[0]
        self.month = args[1]
        self.year = args[2][2:]
        
        self.hour = args[3]
        self.minute = args[4]
        
        self.log_interval = args[5]
        
        if len(self.day) == 1:
            self.day = '0' + self.day
        if len(self.month) == 1:
            self.month = '0' + self.month
        
        if len(self.hour) == 1:
            self.hour = '0' + self.hour
        if len(self.minute) == 1:
            self.minute = '0' + self.minute
        
    def run(self):
        path = find_daysimeter()
        log_filename = constants.LOG_FILENAME
        
        if not path:
            self.no_daysim_sig.emit()
        else:
            with open(path + log_filename,'r') as log_fp:
                info = log_fp.readlines()
            if len(info) == 17:
                info[0] = '2\n'
                info[2] = self.month + '-' + self.day + '-' + self.year + \
                          ' ' + self.hour + ':' + self.minute + '\n'
                info[3] = self.log_interval
                info[5] = '1\n'
            else:
                info[0] = '2\n'
                info[4] = self.month + '-' + self.day + '-' + self.year + \
                          ' ' + self.hour + ':' + self.minute + '\n'
                info[5] = self.log_interval
                info[7] = '1\n'
            with open(path + log_filename, 'w') as log_fp:
                for x in info:
                    log_fp.write(x)
                    
            self.done_sig.emit()


def main():
    """ PURPOSE: Creates app and runs widget """
    # Create the Qt Application
    app = QtGui.QApplication(sys.argv)
    # Create and show the form
    session = StartNewLog()
    session.show()
    # Run the main Qt loop
    sys.exit(app.exec_())
            
if __name__ == '__main__':
    main()