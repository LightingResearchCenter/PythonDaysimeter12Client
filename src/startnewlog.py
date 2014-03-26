"""
startnewlog
Author: Jed Kundl
Creation Date: 08.07.2013
"""

import sys, os
from PyQt4 import QtGui, QtCore
from datetime import datetime
from finddaysimeter import find_daysimeter
import constants, logging

class StartNewLog(QtGui.QWidget):
    """PURPOSE: Starts a new Daysimeter log."""
    def __init__(self, parent=None):
        """Initializes Widget."""
        super(StartNewLog, self).__init__(parent)
        self.setWindowTitle('Start New Log')
        self.setFixedSize(360,180)
        
        self.info_log = logging.getLogger('daysim_log')
        
        self.day = QtGui.QComboBox()
        self.month = QtGui.QComboBox()
        self.year = QtGui.QComboBox()
        
        self.hour = QtGui.QComboBox()
        self.minute = QtGui.QComboBox()
        
        self.start = QtGui.QPushButton('Start')
        self.cancel = QtGui.QPushButton('Cancel')
        
        self.log_interval = QtGui.QComboBox()
        
        self.status = QtGui.QStatusBar()
        self.status.setSizeGripEnabled(False)
        self.info = QtGui.QStatusBar()
        self.info.setSizeGripEnabled(False)
        
        self.day.addItems([str(x) for x in range(1,32)])
        self.month.addItems([str(x) for x in range(1,13)])
        self.year.addItems([str(x) for x in range(2000, 2021)])
        
        self.hour.addItems([str(x) for x in range(24)])
        self.minute.addItems([str(x) for x in range(60)])
        
        self.log_interval.addItems(['030', '060', '090', '120', '180'])
        
        current_time = datetime.now()
        
        #Sets the comboboxes to now. User may changed date and time.
        self.day.setCurrentIndex(current_time.day - 1)
        self.month.setCurrentIndex(current_time.month - 1)
        self.year.setCurrentIndex(current_time.year - 2000)
        
        self.hour.setCurrentIndex(current_time.hour)
        self.minute.setCurrentIndex(current_time.minute)
        
        self.log_interval.setCurrentIndex(1)
        self.log_interval.currentIndexChanged.connect(self.log_duration)
        
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
        layout.addRow('Date (DD-MM-YYYY)', dmy_layout)
        layout.addRow('Time', hm_layout)
        layout.addRow('Logging Interval', self.log_interval)
        layout.addRow('Max Log Duration', self.info)
        layout.addRow(button_layout)
        layout.addRow(self.status)
        
        self.setLayout(layout)       
        
        self.start.pressed.connect(self.begin_log)
        self.cancel.pressed.connect(self.close)
        
        self.log_duration()
        self.show_self()
        
        self.info_log.info('startnewlog.py class StartNewLog func __init__: GUI initialized')

    def show_self(self):
        if not find_daysimeter():    
            self.info_log.info('startnewlog.py class StartNewLog func show_self: Daysimeter not found, closing widget')
            self.close()
        else:
            self.info_log.info('startnewlog.py class StartNewLog func show_self: Daysimeter found, showing widget')
            self.show()
    
    def log_duration(self):
        self.info_log.info('startnewlog.py class StartNewLog func log_interval: Updated log interval message')
        interval = int(self.log_interval.currentText())
        if interval == 30:
            self.info.showMessage('5.5 days with currently selected interval')
        if interval == 60:
            self.info.showMessage('11 days with currently selected interval')
        if interval == 90:
            self.info.showMessage('16.5 days with currently selected interval')
        if interval == 120:
            self.info.showMessage('22 days with currently selected interval')
        if interval == 180:
            self.info.showMessage('33 days with currently selected interval')
        
    def begin_log(self):
        """
        PURPOSE: Called when submit is clicked. Informs user that new log
        will overrite old log, and asks for confimation.
        """
        self.info_log.info('startnewlog.py class StartNewLog func begin_log: Confirming overwriting of old log')
        reply = QtGui.QMessageBox.question(self, 'Warning',
        'Starting a new log will delete current log.', QtGui.QMessageBox.Ok, \
        QtGui.QMessageBox.Cancel)
        
        if reply == QtGui.QMessageBox.Ok:
            self.info_log.info('startnewlog.py class StartNewLog func begin_log: Confirmed, old log will be erased when daysimeter ejected')
            self.start_log()
        else:
            self.info_log.info('startnewlog.py class StartNewLog func begin_log: Confirmation failed, no new log will be started')
            pass

    def start_log(self):
        """"PURPOSE: Creates new log thread."""
        self.info_log.info('startnewlog.py class StartNewLog func start_log: Creating new low thread')
        self.battery_hours()
        self.logthread = NewLogThread([str(self.day.currentText()), \
                                     str(self.month.currentText()), \
                                     str(self.year.currentText()), \
                                     str(self.hour.currentText()), \
                                     str(self.minute.currentText()), \
                                     str(self.log_interval.currentText())])
        self.logthread.done_sig.connect(self.close_self)
        self.logthread.no_daysim_sig.connect(self.disp_error)
        self.logthread.start()
        
    def close_self(self, log):
        #I'm aware that the first time this is run, the same value will be
        #recorded twice. This is fine, don't worry about it. If it keeps you
        #up at night, come find me and I will tell you why, but in person only.
        self.info_log.info('startnewlog.py class StartNewLog func close_self: Adding new log to start log')        
        if not os.path.exists('start_log.txt'):
            data = []
        else:
            with open('start_log.txt','r') as fp:
                data = fp.readlines()
                
        if len(data) > 998:
            del(data[998:])
        
        with open('start_log.txt','w') as fp:
            fp.write(log[0] + '\t' + log[1] + '\t' + log[2] + '\n')
            for x in data:
                fp.write(x)
                
        self.close()
        
        
    def disp_error(self):
        """PURPOSE: Displays an error if no Daysimeter is found."""
        QtGui.QMessageBox.question(self, 'Error',
                                   'No Daysimeter Found!', \
                                   QtGui.QMessageBox.Ok)
                                   
    def battery_hours(self):
        """PURPOSE: Sets status bar message to display battery hours logged."""
        path = find_daysimeter()
        log_filename = constants.LOG_FILENAME
        self.info_log.info('startnewlog.py class StartNewLog func battery_hours: Finding Daysimeter battery information')
        if not path:
            self.disp_error()
        else:
            with open(path + log_filename,'r') as log_fp:
                info = log_fp.readlines()
            if len(info) == 17 or len(info) == 35:
                self.status.showMessage('Number of hours logged using current battery: ' + \
                                       str(info[4]) + '/ 1680')
                if int(info[4]) >= 1680:
                    QtGui.QMessageBox.question(self, 'Message',
                                               'Your daysimeter\'s battery' + \
                                               ' should be changed soon.', \
                                               QtGui.QMessageBox.Ok)
            else:
                self.status.showMessage('Daysimeter Header Corrupt')
                self.start.setEnabled(False)
        
        
        
class NewLogThread(QtCore.QThread):
    """PURPOSE: Thread to handle starting a new log."""
    done_sig = QtCore.pyqtSignal(list)
    no_daysim_sig = QtCore.pyqtSignal()
    
    def __init__(self, args, parent=None):
        """Initializes Thread."""
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
        """What to do when start is called."""
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
                info[3] = self.log_interval + '\n'
                info[5] = '1\n'
                daysimeter_id = info[1]
                daysimeter_start = info[2]
            else:
                info[0] = '2\n'
                info[7] = self.month + '-' + self.day + '-' + self.year + \
                          ' ' + self.hour + ':' + self.minute + '\n'
                info[3] = self.log_interval + '\n'
                info[5] = '1\n'
                daysimeter_id = info[8].strip('\n')
                daysimeter_start = info[7].strip('\n')
            with open(path + log_filename, 'w') as log_fp:
                for x in info:
                    log_fp.write(x)
                    
            self.done_sig.emit([daysimeter_id, daysimeter_start, self.log_interval])


def main():
    """ PURPOSE: Creates app and runs widget """
    # Create the Qt Application
    app = QtGui.QApplication(sys.argv)
    # Create and show the form
    session = StartNewLog()
    # Run the main Qt loop
    sys.exit(app.exec_())
            
if __name__ == '__main__':
    main()