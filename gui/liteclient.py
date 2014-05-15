# -*- coding: utf-8 -*-
"""
Created on Wed Apr 23 12:19:34 2014

@author: kundlj
"""
import sys, os
sys.path.insert(0, os.pardir)
import time
import math
from PyQt4 import QtGui, QtCore
from datetime import datetime 
from functools import partial
from ConfigParser import ConfigParser
from src.downloadmake import DownloadMake
from src.offsetwidget import OffsetWidget
from src.logfunc import stop_log
from src.logfunc import resume_log
from src.finddaysimeter import find_daysimeter
import src.constants as constants_
from src.startnewlog import StartNewLog
from statuslight import StatusLight
from statuswidget import StatusWidget
from startloginfo import StartLogInfo
from src.getlogs import get_err_log, get_daysim_log, setup_logger
import logging

class DaysimeterClientLITE(QtGui.QWidget):
    
    def __init__(self, parent=None):
        super(DaysimeterClientLITE, self).__init__(parent)
        
        setup_logger('daysim_log', get_daysim_log())
        self.daysim_log = logging.getLogger('daysim_log')

        setup_logger('err_log', get_err_log())
        self.err_log = logging.getLogger('err_log')
        
        self.disconnected = True
        
        self.load_config()        
        self.initUI()
        self.make_shortcuts()
        self.make_enabler()
        
    def initUI(self):
        self.setFixedSize(300, 120)        
        
        self.new_log_button = QtGui.QPushButton('Start New Log')
        self.stop_log_button = QtGui.QPushButton('Stop Logging')
        self.download_button = QtGui.QPushButton('Download Data')
        
        self.new_log_button.pressed.connect(self.start_log)
        self.stop_log_button.pressed.connect(self.stop_log)
        self.download_button.pressed.connect(self.download_data_UTC)
        
        self.status = QtGui.QStatusBar()
        self.status.setSizeGripEnabled(False)
        
        self.setWindowTitle('Daysimeter Client - LITE')
        
        self.status_light = StatusLight(self)
        self.status_widget = StatusWidget(self)
        
        status_layout = QtGui.QHBoxLayout()
        status_layout.addWidget(self.status_light)
        status_layout.addWidget(self.status_widget)
        
        button_layout = QtGui.QHBoxLayout()
        button_layout.addWidget(self.new_log_button)
        button_layout.addWidget(self.stop_log_button)
        button_layout.addWidget(self.download_button)
        
        all_layout = QtGui.QVBoxLayout()
        all_layout.addLayout(status_layout)
        all_layout.addLayout(button_layout)
        all_layout.addWidget(self.status)
        
        self.setLayout(all_layout)
        self.show()
        
    def load_config(self, update=None, args=None):
        """Loads the info from the ini file if it exists, otherwise creates it
        
        update - a string that lets the function know if it's the initial run
                 or if it's just updating a value from the program
        
        """
        # Get the path of the file and open it
        dir_path = os.getcwd()
        file_path = os.path.join(dir_path, 'daysimeter.ini')
        # Parse the ini file
        self.init = ConfigParser()
        if os.path.isfile(file_path):
            init_file = open(file_path, mode='r')
            self.init.readfp(init_file)
            init_file.close()
            init_file = open(file_path, mode='w')
        else:
            init_file = open(file_path, mode='w')
            self.set_save_path()
        # Update the Application settings
        if update == 'savepath':
            self.set_save_path()
        if update == 'utc':
            self.update_utc(args)
        self.init.write(init_file)
        init_file.close()
    
    def update_utc(self, index):
        if self.init.has_section('UTC Settings'):
            pass
        else:
            self.init.add_section('UTC Settings')
        self.init.set('UTC Settings', 'default', index)
        
    def set_default_savepath(self, path):
        dir_path = os.getcwd()
        file_path = os.path.join(dir_path, 'daysimeter.ini')
        # Parse the ini file
        self.init = ConfigParser()
        if os.path.isfile(file_path):
            init_file = open(file_path, mode='r')
            self.init.readfp(init_file)
            init_file.close()
            init_file = open(file_path, mode='w')
        else:
            init_file = open(file_path, mode='w')
            self.set_save_path()
            
        if os.path.isdir(path):
            if self.init.has_section("Application Settings"):
                self.init.set("Application Settings", 'savepath', path)
            else:
                self.init.add_section("Application Settings")
                self.init.set("Application Settings", 'savepath', path)
        self.init.write(init_file)
        init_file.close()
        
    def set_save_path(self):
        """Create a dialog to set the savepath and set it in the ini file"""
        if self.init.has_section("Application Settings"):
            dir_name = str(QtGui.QFileDialog.getExistingDirectory(self,
                       directory=self.init.get('Application Settings', \
                                               'savepath')))
        else:
            dir_name = str(QtGui.QFileDialog.getExistingDirectory(self,
                       directory=os.getcwd()))
        
        if dir_name:
            if self.init.has_section("Application Settings"):
                self.init.set("Application Settings", 'savepath', dir_name)
            else:
                self.init.add_section("Application Settings")
                self.init.set("Application Settings", 'savepath', dir_name)
                
    def start_log(self):
        """ Starts a new log on the Daysimeter """
        self.new_log = StartNewLog()
    
    def stop_log(self):
        """ Stops current log """
        if stop_log():
            self.status.showMessage("Current Log Stopped", 2000)
        else:
            QtGui.QMessageBox.question(self, 'Error',
                                   'No Daysimeter Found!', \
                                   QtGui.QMessageBox.Ok)
            
        
               
    def download_data_UTC(self):
        
        path = find_daysimeter()
        log_filename = constants_.LOG_FILENAME
        
        with open(path + log_filename, 'r') as fp:
            info = fp.readlines()
        
        if len(info) == 17:
            if info[1] == '1.1\n' or '1.2\n':
                self.send_offset(15, False)
            else:
                if self.init.has_section('UTC Settings'):
                    offset = int(self.init.get('UTC Settings', 'default'))
                    self.offsetter = OffsetWidget(default=offset)
                else:
                    self.offsetter = OffsetWidget(self)
                self.offsetter.send.connect(self.send_offset)
                self.offsetter.show()
                
        else:
            if self.init.has_section('UTC Settings'):
                offset = int(self.init.get('UTC Settings', 'default'))
                self.offsetter = OffsetWidget(default=offset)
            else:
                self.offsetter = OffsetWidget(self)
            self.offsetter.send.connect(self.send_offset)
            self.offsetter.show()
    
    def send_offset(self, index, update):
        if update:
            self.load_config(update='utc', args=index)
        self.download_data(index)
        
    def download_data(self, index=None):
        """Creates a widget to download data from the Daysimeter"""
        self.daysim_log.info('Creating download wdiget')
        if index:
            self.download = DownloadMake(offset=index)
        else:
            self.download = DownloadMake()
        self.download.last_savepath.connect(self.set_default_savepath)
            
    def make_shortcuts(self):
        """ Creates the keyboard shortcuts for the Daysimeter Client """
        download_shortcut = QtGui.QShortcut(QtGui.QKeySequence('CTRL+D'), \
        self, self.download_data_UTC, self.download_data_UTC, QtCore.Qt.WidgetShortcut)
        
        quit_shortcut = QtGui.QShortcut(QtGui.QKeySequence('CTRL+Q'), \
        self, self.close, self.close, QtCore.Qt.WidgetShortcut)
        
        set_save_shortcut = QtGui.QShortcut(QtGui.QKeySequence('SHIFT+CTRL+S'), \
        self, partial(self.load_config, update='savepath'), \
        partial(self.load_config, update='savepath'), QtCore.Qt.WidgetShortcut)
        
        new_log_shortcut = QtGui.QShortcut(QtGui.QKeySequence('CTRL+N'), \
        self, self.start_log, self.start_log, QtCore.Qt.WidgetShortcut)

        reset_batt_shortcut = QtGui.QShortcut(QtGui.QKeySequence('SHIFT+CTRL+R'), \
        self, self.reset_battery, self.reset_battery, QtCore.Qt.WidgetShortcut)
        
        fix_head_shortcut = QtGui.QShortcut(QtGui.QKeySequence('SHIFT+CTRL+F'), \
        self, self.fix_header, self.fix_header, QtCore.Qt.WidgetShortcut)
        
        
        start_log_shortcut = QtGui.QShortcut(QtGui.QKeySequence('SHIFT+CTRL+L'), \
        self, self.get_start_log, self.get_start_log, QtCore.Qt.WidgetShortcut)
        
    def get_start_log(self):
        """
        Creates a widget that allows a user to search the start log for the
        time and date it was started, and the log interval used.
        """
        self.start_log = StartLogInfo()
        
    def reset_battery(self):
        """ Resets the "number of logged hours" line in a Daysimeter's Header """
        reply = QtGui.QMessageBox.question(self, 'Message',
                                   'Confirm Battery Reset.', \
                                   QtGui.QMessageBox.Ok, QtGui.QMessageBox.Cancel)        
        
        if reply == QtGui.QMessageBox.Ok:
            path = find_daysimeter()
            log_filename = constants_.LOG_FILENAME
            if not path:
                QtGui.QMessageBox.question(self, 'Error',
                                       'No Daysimeter Found!', \
                                       QtGui.QMessageBox.Ok)
            else:
                with open(path + log_filename, 'r') as log_fp:
                    info = log_fp.readlines()
                info[4] = '0\n'
                with open(path + log_filename, 'w') as log_fp:
                    for x in info:
                        log_fp.write(x)
                self.statusBar().showMessage('Logging hours reset.', 2000)
        else:
            self.statusBar().showMessage('Reset Cancelled.', 2000)
            
    def resume_log(self):
        """ Resumes teh current log from where it left off """
        duration = datetime.now() - self.time_connected
        duration = duration.total_seconds()
        total_time = ''
        
        if math.floor(duration/(24*60*60)) > 0:
            if math.floor(duration/(24*60*60)) > 1:
                total_time = total_time + str(int(math.floor(duration/(24*60*60)))) + \
                ' days'
            else:
                total_time = total_time + str(int(math.floor(duration/(24*60*60)))) + \
                ' day'
            duration = duration % (24 * 60 * 60)
            
            if math.floor(duration/(60*60)) > 0:
                if math.floor(duration/(60*60)) > 1:
                    if math.floor((duration%(60*60))/60) == 0:
                        total_time = total_time + ' and ' + \
                        str(int(math.floor(duration/(60*60)))) + ' hours'
                    else: 
                        total_time = total_time + ', ' + \
                        str(int(math.floor(duration/(60*60)))) + ' hours and ' + \
                        str(int(math.floor((duration%(60*60))/60))) + ' minutes'
                else:
                    if math.floor((duration%(60*60))/60) == 0:
                        total_time = total_time + ' and ' + \
                        str(int(math.floor(duration/(60*60)))) + ' hour'
                    elif math.floor((duration%(60*60))/60) == 1: 
                        total_time = total_time + ', ' + \
                        str(int(math.floor(duration/(60*60)))) + ' hour and ' + \
                        str(int(math.floor((duration%(60*60))/60))) + ' minute'
                    else:
                        total_time = total_time + ', ' + \
                        str(int(math.floor(duration/(60*60)))) + ' hour and ' + \
                        str(int(math.floor((duration%(60*60))/60))) + ' minutes'
            elif math.floor((duration%(60*60))/60) > 0:
                if math.floor((duration%(60*60))/60) > 1:
                    total_time = total_time + ' and' + \
                    str(int(math.floor((duration%(60*60))/60))) + ' minutes'
                else:
                    total_time = total_time + ' and' + \
                    str(int(math.floor((duration%(60*60))/60))) + ' minute'
        elif math.floor(duration/(60*60)):
            if math.floor((duration%(60*60))/60) == 0:
                if math.floor((duration%(60*60))/60) == 1:
                    total_time = total_time + \
                    str(int(math.floor(duration/(60*60)))) + ' hour'
                else:
                    total_time = total_time + \
                    str(int(math.floor(duration/(60*60)))) + ' hours'
            elif math.floor(duration/(60*60)) == 1 and \
                 math.floor((duration%(60*60))/60) == 1: 
                total_time = total_time + \
                str(int(math.floor(duration/(60*60)))) + ' hour and ' + \
                str(int(math.floor((duration%(60*60))/60))) + ' minute'
            elif math.floor(duration/(60*60)) == 1 and \
                 math.floor((duration%(60*60))/60) > 1: 
                total_time = total_time + \
                str(int(math.floor(duration/(60*60)))) + ' hour and ' + \
                str(int(math.floor((duration%(60*60))/60))) + ' minutes'
            elif math.floor(duration/(60*60)) > 1 and \
                 math.floor((duration%(60*60))/60) == 1: 
                total_time = total_time + \
                str(int(math.floor(duration/(60*60)))) + ' hours and ' + \
                str(int(math.floor((duration%(60*60))/60))) + ' minute'   
            else: 
                total_time = total_time + \
                str(int(math.floor(duration/(60*60)))) + ' hours and ' + \
                str(int(math.floor((duration%(60*60))/60))) + ' minutes'
        elif math.floor(duration/60) > 0:
            if math.floor(duration/60) > 1:
                total_time = total_time + \
                             str(int(math.floor(duration/60))) + ' minutes'
            else:
                total_time = total_time + \
                             str(int(math.floor(duration/60))) + ' minute'
            
        if total_time == '':
            if resume_log():
                self.statusBar().showMessage("Current Log Resumed", 2000)
            else:
                QtGui.QMessageBox.question(self, 'Error',
                                   'No Daysimeter Found!', \
                                   QtGui.QMessageBox.Ok)
            
        else:
            reply = QtGui.QMessageBox.question(self, 'Warning',
                                       'Daysimeter has been plugged in for ' \
                                       + total_time + '.\nAre you sure you want to resume current log?',
                                       QtGui.QMessageBox.Yes, QtGui.QMessageBox.No)
            
            if reply == QtGui.QMessageBox.Yes:
                if resume_log():
                    self.statusBar().showMessage("Current Log Resumed", 2000)
                else:
                    QtGui.QMessageBox.question(self, 'Error',
                                           'No Daysimeter Found!', \
                                           QtGui.QMessageBox.Ok)
    
    def fix_header(self):
        """
        Attempts to fix header file. If unable displays status informing user 
        """
        path = find_daysimeter()
        if path:
            with open(path + constants_.LOG_FILENAME, 'r') as log_fp:
                info = log_fp.readlines()
            for x in info:
                if x[:len(constants_.BATTERY_STRING)] == constants_.BATTERY_STRING:
                    index = info.index(x)
                    break
            temp = info[:index+1]
            if len(temp) == 17:
                info = temp
                with open(path + constants_.LOG_FILENAME, 'w') as log_fp:
                    for x in info:
                        log_fp.write(x)
            else:
                self.statusBar().showMessage('Could not fix header file.', 2000)
                
    def make_enabler(self):
        """
        Makes an enabler to determine whether daysimeter functions should be
        enabled or disabled.
        
        enabler - thread that constantly checks to see if a Daysimeter is
        attached to computer
        """
        self.enabler = EnableButtons(self)
        self.enabler.connected.connect(self.enable_selection)
        self.enabler.not_connected.connect(self.disable_selection)
        self.enabler.start()
        
    def enable_selection(self):
        """
        Enables daysimeter functions
        """
        if not self.status_widget.corrupt.isVisible():
            self.new_log_button.setEnabled(True)
            self.stop_log_button.setEnabled(True)
            self.download_button.setEnabled(True)
            self.status_light.set_green()
            if self.disconnected:
                self.time_connected = datetime.now()
                self.disconnected = False
        else:
            self.status_light.set_yellow()
            self.new_log_button.setEnabled(True)
            self.stop_log_button.setEnabled(True)
            self.download_button.setEnabled(True)
    
    def disable_selection(self):
        """
        Disables Daysimeter functions.
        """
        self.new_log_button.setEnabled(False)
        self.stop_log_button.setEnabled(False)
        self.download_button.setEnabled(False)
        self.status_light.set_red()
        self.status.showMessage('No Daysimeter plugged into computer.', \
                                     500)
        self.disconnected = True
        
class EnableButtons(QtCore.QThread):
    """
    Constantly checks to see if a Daysimeter is attached to the computer
    """
    connected = QtCore.pyqtSignal()
    not_connected = QtCore.pyqtSignal()    
    
    def __init__(self, parent=None):
        """Initializes Thread."""
        QtCore.QThread.__init__(self, parent)
        
    def run(self):
        """ Runs the thread """
        while True:
            if not find_daysimeter():
                self.not_connected.emit()
            else:
                self.connected.emit()
            time.sleep(1)
        
def main():
    """ PURPOSE: Creates app and runs widget """
    # Create the Qt Application
    app = QtGui.QApplication(sys.argv)
    # Create and show the form
    session = DaysimeterClientLITE()
    # Run the main Qt loop
    sys.exit(app.exec_())
            
if __name__ == '__main__':
    main() 