"""
downloadmake
Author: Jed Kundl
Creation Date: 28.06.2013
"""

import os
import sys
import struct
import logging
import time
import math
import shutil
from ConfigParser import SafeConfigParser
from datetime import datetime, timedelta
from getlogs import get_err_log
from adjactiveflag import adj_active_flag
from getcalibinfo import get_calib_info
from processconstants import process_constants
from lowpassfilter import lowpass_filter
from calccs import calc_cs
from finddaysimeter import find_daysimeter
from datetimetodatenum import dt2dn
from getconstants import get_constants
import constants as constants_
from spacepy import pycdf
from getlocaloffset import get_local_offset_s
from setdownloadflag import set_download_flag
from updateheader import update_header
from convertheader import convert_header
from PyQt4 import QtGui, QtCore

    
class DownloadMake(QtGui.QWidget):
    """
    PURPOSE: Widget that manages downloading daysimeter data and making CDF 
    or CSV files. 
    """

    last_savepath = QtCore.pyqtSignal(str)    
    
    def __init__(self, offset, parent=None, args=None):
        super(DownloadMake, self).__init__(parent)
        dl_skip_shortcut = QtGui.QShortcut(QtGui.QKeySequence('SHIFT+CTRL+G'),\
        self, self.skip_prog, self.skip_prog, QtCore.Qt.WidgetShortcut)
        if not args:
            path = find_daysimeter()
            if path:
                self.log_filename = os.path.join(path, constants_.LOG_FILENAME)
                self.data_filename = os.path.join(path, \
                                                  constants_.DATA_FILENAME)
                self.download_make = True
            else:
                sys.exit(1)
        else:
            self.log_filename = args[0]
            self.data_filename = args[1]
            self.download_make = False
        self.time_offset_index = offset
    
        
        
        
        self.daysim_log = logging.getLogger('daysim_log')
        self.err_log = logging.getLogger('err_log')
        
        self.initUI()
        
        
    def initUI(self):
        """ PURPOSE: Initialize the GUI """
        self.setFixedSize(500, 100)
        self.pbar = QtGui.QProgressBar(self)

        self.start = QtGui.QPushButton('Start Download')
        self.start.setFixedWidth(140)
        self.done = QtGui.QPushButton('Done')
        self.done.setFixedWidth(140)
        self.start.pressed.connect(self.start_download)
        self.done.pressed.connect(self.close)
        self.done.setEnabled(False)

        self.status_bar = QtGui.QStatusBar()      
        
        layout = QtGui.QVBoxLayout()
        layout.addWidget(self.pbar)
        layout.addWidget(self.start, alignment=QtCore.Qt.AlignCenter)
        layout.addWidget(self.done, alignment=QtCore.Qt.AlignCenter)
        layout.addWidget(self.status_bar)
        self.setLayout(layout)
        
        self.setWindowTitle('Daysimeter Downloader')
        self.step = 0.0
        self.pbar.setValue(self.step)
        self.pbar.hide()
        self.done.hide()        
        
        
        self.parser = SafeConfigParser()
        if not self.parser.read('daysimeter.ini') == []:
            if self.parser.has_section('Application Settings'):
                self.savedir = self.parser.get('Application Settings', \
                                               'savepath')
            else:
                self.savedir = os.getcwd()
        else:
            self.savedir = os.getcwd()
            
        self.start.hide()
        self.start_download()   
        self.show()
        
        self.daysim_log.info('downloadmake.py class DownloadMake func initUI: GUI initialized')
        
    def start_download(self):
        """ PURPOSE: Starts and manages download of data """
        self.daysim_log.info('Initializing download')
        if not find_daysimeter() and self.download_make:
            self.status_bar.showMessage('No Daysimeter plugged into this' + \
            ' computer.')
        else:
            self.daysim_log.info('downloadmake.py class DownloadMake func start_download: Daysimeter found')
            with open(self.log_filename,'r') as log_fp:
                info = log_fp.readlines()
                if len(info) == 17:
                    daysim_id = info[1].strip('\n')
                elif len(info) == 35:
                    if info[27] == 'ID number(Do Not Change)':
                        convert_header('h2')
                        log_fp.seek(0)
                        info = log_fp.readlines()
                    daysim_id = info[8].strip('\n')
                else:
                    daysim_id = 'NULL'
                now = str(datetime.now())
                default_filename = daysim_id + '-' + now[:10] \
                    + '-' + now[11:13] + '-' + now[14:16] + '-' + now[17:19]
            self.daysim_log.info('downloadmake.py class DownloadMake func start_download: Generating default filename')
            default_name = os.path.join(self.savedir, default_filename)
            self.status_bar.showMessage('')
            self.filename = str(QtGui.QFileDialog.getSaveFileName(self, \
                ('Save File'), default_name, ('CDF Files (*.cdf);; CSV Files (*.csv)')))
            if not str(self.filename) == '':
                parts = self.filename.split('/')
                del(parts[-1])
                savepath = ''
                for element in parts:
                    savepath += element + '/'
                self.last_savepath.emit(savepath)
                
                self.pbar.show()
                self.start.setText('Downloading...')
                self.status_bar.showMessage('Processing Data...')
                self.start.setEnabled(False)
                self.downloader = DownloadDaysimeter(self, [self.savedir, \
                                                     self.filename, \
                                                     self.log_filename, \
                                                     self.data_filename, \
                                                     self.download_make, \
                                                     self.time_offset_index])
                self.downloader.error.connect(self.error)
                self.connect(self.downloader, QtCore.SIGNAL('update'), \
                             self.update_progress)
                self.connect(self.downloader, QtCore.SIGNAL('fprogress'), \
                             self.fake_progress)
                self.connect(self.downloader, QtCore.SIGNAL('make'), \
                             self.make)
                self.daysim_log.info('Starting download')
                self.downloader.start()
            else:
                self.cancelled()
                
                
        
    def make(self, data):
        """
        PURPOSE: Determines filetype to be written, creates maker thread
        that actually writes data to file.
        """
        if self.filename[len(self.filename)-4:] == '.cdf':
            self.daysim_log.info('downloadmake.py class DownloadMake func make: Preparing CDF file')
            self.subjectinfo = SubjectInfo([data[1][0][0], \
                                            data[1][0][len(data[1][0]) - 1], \
                                            data[0][3]])
            self.connect(self.subjectinfo, QtCore.SIGNAL('sendinfo'), \
                         self.make_cdf)
            self.connect(self.subjectinfo, QtCore.SIGNAL('cancelled'), \
                         self.cancelled)
            self.data = data
        else:
            self.daysim_log.info('downloadmake.py class DownloadMake func make: Preparing CSV file')
            self.status_bar.showMessage('Writing CSV File...')
            self.maker = MakeCSV(self, data, self.filename)
            self.connect(self.maker, QtCore.SIGNAL('update'), \
                         self.update_progress)
            self.maker.start()
            
    def make_cdf(self, info):
        """ PURPOSE: Makes a CDF file. """
        self.daysim_log.info('downloadmake.py class DownloadMake func make_cdf: Getting CDF subject attributes')
        self.daysim_log.info('Initializing CDF file')
        if info[1] == '-':
            info[1] = 'None'
        if info[2] == '- - -':
            info[2] = 'None'
        if info[3] == '000.000':
            info[3] = 0
        self.status_bar.showMessage('Writing CDF File...')
        self.maker = MakeCDF(self, self.data, self.filename, info)
        self.connect(self.maker, QtCore.SIGNAL('update'), self.update_progress)
        self.maker.start()
        
    def cancelled(self):
        """
        PURPOSE: Sets status when the download has been cancelled, this
        usually occurs when no subject info was given.
        """
        self.daysim_log.info('downloadmake.py class DownloadMake func cancelled: Event cancelled')
        #As a side note, the ceiling started leaking again...
        self.pbar.hide()
        self.done.setText('Download Cancelled')
        self.start.hide()
        self.done.setEnabled(True)
        self.done.setText('Close')
        self.done.show()
        self.status_bar.showMessage('Download cancelled.')
        
    def error(self):
        """
        PURPOSE: Sets status when an error has occured.
        """
        self.daysim_log.info('downloadmake.py class DownloadMake func error: An error was caught, check error log for further information')
        #As a side note, the ceiling started leaking again...
        self.pbar.hide()
        self.done.setText('Close')
        self.start.hide()
        self.done.show()
        self.done.setEnabled(True)
        self.status_bar.showMessage('An error occurred.')
        
    def fake_progress(self):
        self.progresssim = ProgressSim()
        self.connect(self.progresssim, QtCore.SIGNAL('update'), \
                     self.update_progress)
        self.progresssim.start()
        
    def skip_prog(self):
        self.step = 99
        self.update_progress()
    
        
    def update_progress(self):
        """ PURPOSE: Updates progress bar when given signal to do so. """
        #it kind fakes it until it makes it
        self.step += 1
        self.pbar.setValue(self.step)
        if self.step == 100:
            self.download_done()
        
    def download_done(self):
        """ PURPOSE: Displays done message when download is complete """
        self.daysim_log.info('downloadmake.py class DownloadMake func download_done: Download completed successfully')
        self.daysim_log.info('Download complete')
        self.status_bar.showMessage('Download Complete. It is now safe ' + \
                                    'to eject your daysimeter.')
        self.start.hide()
        self.done.setEnabled(True)
        self.done.show()
        self.emit(QtCore.SIGNAL('savename'), self.filename)
        
    def keyPressEvent(self, qKeyEvent):
        if qKeyEvent.key() == QtCore.Qt.Key_Return and self.done.isEnabled(): 
            self.close()
        else:
            pass
        
class ProgressSim(QtCore.QThread):
    """
    PURPOSE: Simulates progress while daysimeter transfers data from EEPROM
    to RAM
    """
    
    def __init__(self, parent=None):
        QtCore.QThread.__init__(self, parent)
        
    def run(self):
        for x in range(99):
            time.sleep(.1515)
            self.emit(QtCore.SIGNAL('update'))
    
        
class SubjectInfo(QtGui.QWidget):
    """ PURPOSE: Creates a widget for a user to enter subject information """
    send_info_sig = QtCore.pyqtSignal(list)
    def __init__(self, args, parent=None):
        super(SubjectInfo, self).__init__(parent)
        QtGui.QMainWindow.__init__(self)
        self.setWindowTitle('Enter Subject Information')
        
        self.daysim_log = logging.getLogger('daysim_log')
        
        self.start_time = str(args[0])
        self.end_time = str(args[1])
        
        self.start_dt = datetime.strptime(self.start_time, '%Y-%m-%d %H:%M:%S')
        self.end_dt = datetime.strptime(self.end_time, '%Y-%m-%d %H:%M:%S')
        self.log_interval = int(args[2])
        
        self.subject_id = QtGui.QLineEdit()
        self.subject_sex = QtGui.QComboBox()
        self.subject_mass = QtGui.QLineEdit()
        
        self.subject_id.setMaxLength(64)
        
        self.day_dob = QtGui.QComboBox()
        self.month_dob = QtGui.QComboBox()
        self.year_dob = QtGui.QComboBox()
        
        self.day_start = QtGui.QComboBox()
        self.month_start = QtGui.QComboBox()
        self.year_start = QtGui.QComboBox()
        self.hour_start = QtGui.QComboBox()
        self.minute_start = QtGui.QComboBox()
        self.second_start = QtGui.QComboBox()
        
        self.day_end = QtGui.QComboBox()
        self.month_end = QtGui.QComboBox()
        self.year_end = QtGui.QComboBox()
        self.hour_end = QtGui.QComboBox()
        self.minute_end = QtGui.QComboBox()
        self.second_end = QtGui.QComboBox()
        
        self.subject_sex.addItems(['-', 'Male', 'Female', 'Other'])
        
        self.day_dob.addItem('-')
        self.month_dob.addItem('-')
        self.year_dob.addItem('-')
        
        self.day_dob.addItems([str(x) for x in range(1, 32)])
        self.month_dob.addItems(['January', 'February', 'March', 'April'] + \
        ['May', 'June', 'July', 'August', 'September', 'October'] + \
        ['November', 'December'])
        self.year_dob.addItems([str(x) for x in reversed(range(1900, 2021))])
        
        self.day_start.addItems([str(x) for x in range(1, 32)])
        self.month_start.addItems([str(x) for x in range(1,13)])
        self.year_start.addItems([str(x) for x in range(2013, 2021)])
        self.hour_start.addItems([str(x) for x in range(24)])
        self.minute_start.addItems([str(x) for x in range(60)])
        self.second_start.addItems(['00','30'])
        
        
        self.day_end.addItems([str(x) for x in range(1, 32)])
        self.month_end.addItems([str(x) for x in range(1,13)])
        self.year_end.addItems([str(x) for x in range(2013, 2021)])
        self.hour_end.addItems([str(x) for x in range(24)])
        self.minute_end.addItems([str(x) for x in range(60)])
        self.second_end.addItems(['00','30'])
        
        self.layout_dob = QtGui.QHBoxLayout()
        self.layout_dob.addWidget(self.day_dob)
        self.layout_dob.addWidget(self.month_dob)
        self.layout_dob.addWidget(self.year_dob)
        
        
        self.layout_start = QtGui.QHBoxLayout()
        self.layout_start.addWidget(self.day_start)
        self.layout_start.addWidget(self.month_start)
        self.layout_start.addWidget(self.year_start)
        self.layout_start.addWidget(self.hour_start)
        self.layout_start.addWidget(self.minute_start)
        self.layout_start.addWidget(self.second_start)
        
        self.layout_end = QtGui.QHBoxLayout()
        self.layout_end.addWidget(self.day_end)
        self.layout_end.addWidget(self.month_end)
        self.layout_end.addWidget(self.year_end)
        self.layout_end.addWidget(self.hour_end)
        self.layout_end.addWidget(self.minute_end)
        self.layout_end.addWidget(self.second_end)
        
        self.subject_mass.setInputMask('000.000')
        self.subject_mass.setText('000.000')
        
        self.submit = QtGui.QPushButton('Submit')
        self.cancel = QtGui.QPushButton('Cancel')
        
        button_layout = QtGui.QHBoxLayout()
        button_layout.addWidget(self.submit)
        button_layout.addWidget(self.cancel)
        
        layout = QtGui.QFormLayout()
        layout.addRow('Subject ID Number', self.subject_id)
        layout.addRow('Sex', self.subject_sex)
        layout.addRow('Date of Birth', self.layout_dob)
        layout.addRow('Mass (in kg)', self.subject_mass)
        layout.addRow('Start Date (DD/MM/YYYY HH:MM:SS)', self.layout_start)
        layout.addRow('End Date (DD/MM/YYYY HH:MM:SS)', self.layout_end)
        layout.addRow(button_layout)
        
        self.submit.setEnabled(False)
        self.submit.setDefault(True)
        
        self.setLayout(layout)
        
        self.day_start.setCurrentIndex(int(self.start_time[8:10]) - 1)
        self.month_start.setCurrentIndex(int(self.start_time[5:7]) - 1)
        self.year_start.setCurrentIndex(int(self.start_time[2:4]) - 13)
        self.hour_start.setCurrentIndex(int(self.start_time[11:13]))
        self.minute_start.setCurrentIndex(int(self.start_time[14:16]))
        self.second_start.setCurrentIndex(0 if self.start_time[17:19] == '00' else 1)
        
        self.day_end.setCurrentIndex(int(self.end_time[8:10]) - 1)
        self.month_end.setCurrentIndex(int(self.end_time[5:7]) - 1)
        self.year_end.setCurrentIndex(int(self.end_time[2:4]) - 13)
        self.hour_end.setCurrentIndex(int(self.end_time[11:13]))
        self.minute_end.setCurrentIndex(int(self.end_time[14:16]))
        self.second_end.setCurrentIndex(0 if self.end_time[17:19] == '00' else 1)
        
        self.subject_id.textChanged.connect(self.enable_submit)
        self.subject_sex.currentIndexChanged.connect(self.enable_submit)
        self.day_dob.currentIndexChanged.connect(self.enable_submit)
        self.month_dob.currentIndexChanged.connect(self.enable_submit)
        self.year_dob.currentIndexChanged.connect(self.enable_submit)
        self.day_start.currentIndexChanged.connect(self.enable_submit)
        self.month_start.currentIndexChanged.connect(self.enable_submit)
        self.year_start.currentIndexChanged.connect(self.enable_submit)
        self.hour_start.currentIndexChanged.connect(self.enable_submit)
        self.minute_start.currentIndexChanged.connect(self.enable_submit)
        self.second_start.currentIndexChanged.connect(self.enable_submit)
        self.day_end.currentIndexChanged.connect(self.enable_submit)
        self.month_end.currentIndexChanged.connect(self.enable_submit)
        self.year_end.currentIndexChanged.connect(self.enable_submit)
        self.hour_end.currentIndexChanged.connect(self.enable_submit)
        self.minute_end.currentIndexChanged.connect(self.enable_submit)
        self.second_end.currentIndexChanged.connect(self.enable_submit)
        self.subject_mass.textChanged.connect(self.enable_submit)
        
        
        self.submit.pressed.connect(self.submit_info)
        self.cancel.pressed.connect(self.closeself)
        self.success = False
        
        self.daysim_log = logging.getLogger('daysim_log')

        self.err_log = logging.getLogger('err_log')
        
        self.daysim_log.info('downloadmake.py class SubjectInfo func __init__: GUI initialized')
        self.show()
    
    def closeEvent(self, event):
        """ PURPOSE: Catches the close event, check to see if it is a 
        successful close, or an aborted close and takes appropriate action.
        """
        if self.success:
            event.accept()
        else:
            self.emit(QtCore.SIGNAL('cancelled'))
            event.accept()
            
    def closeself(self):
        """ PURPOSE: Signals that there was an unsuccessful close event. """
        self.emit(QtCore.SIGNAL('cancelled'))
        self.close()
        
    def validate_date(self):
        self.daysim_log.info('downloadmake.py class SubjectInfo func validate_date: Validating date information')
        start_time = ''
        if len(self.year_start.currentText()) == 1:
            start_time = start_time + '0' + str(self.year_start.currentText())\
            + '-'
        else:
            start_time = start_time + str(self.year_start.currentText()) + '-'
        if len(self.month_start.currentText()) == 1:
            start_time = start_time + '0' + str(self.month_start.currentText())\
            + '-'
        else:
            start_time = start_time + str(self.month_start.currentText()) + '-'
        if len(self.day_start) == 1:
            start_time = start_time + '0' + str(self.day_start.currentText())\
            + ' '
        else:
            start_time = start_time + str(self.day_start.currentText()) + ' '
        if len(self.hour_start) == 1:
            start_time = start_time + '0' + str(self.hour_start.currentText())\
            + ':'
        else:
            start_time = start_time + str(self.hour_start.currentText()) + ':'
        if len(self.minute_start) == 1:
            start_time = start_time + '0' + str(self.minute_start.currentText()) + ':'
        else:
            start_time = start_time + str(self.minute_start.currentText()) + ':'
        if len(self.second_start) == 1:
            start_time = start_time + '0' + str(self.second_start.currentText())
        else:
            start_time = start_time + str(self.second_start.currentText())
        

        end_time = ''
        if len(self.year_end.currentText()) == 1:
            end_time = end_time + '0' + str(self.year_end.currentText())\
            + '-'
        else:
            end_time = end_time + str(self.year_end.currentText()) + '-'
        if len(self.month_end.currentText()) == 1:
            end_time = end_time + '0' + str(self.month_end.currentText())\
            + '-'
        else:
            end_time = end_time + str(self.month_end.currentText()) + '-'
        if len(self.day_end) == 1:
            end_time = end_time + '0' + str(self.day_end.currentText())\
            + ' '
        else:
            end_time = end_time + str(self.day_end.currentText()) + ' '
        if len(self.hour_end) == 1:
            end_time = end_time + '0' + str(self.hour_end.currentText())\
            + ':'
        else:
            end_time = end_time + str(self.hour_end.currentText()) + ':'
        if len(self.minute_end) == 1:
            end_time = end_time + '0' + str(self.minute_end.currentText()) + ':'
        else:
            end_time = end_time + str(self.minute_end.currentText()) + ':'
        if len(self.second_end) == 1:
            end_time = end_time + '0' + str(self.second_end.currentText())
        else:
            end_time = end_time + str(self.second_end.currentText())
            
        start_dt = datetime.strptime(start_time, '%Y-%m-%d %H:%M:%S')
        end_dt = datetime.strptime(end_time, '%Y-%m-%d %H:%M:%S')
        
        start_diff = (start_dt - self.start_dt).total_seconds()
        end_diff = (self.end_dt - end_dt).total_seconds()

        if not start_diff % self.log_interval == 0:
            start_diff = (self.log_interval - (start_diff % self.log_interval))
        else:
            start_diff = 0
            
        if not end_diff % self.log_interval == 0:
            end_diff = (self.log_interval - (end_diff % self.log_interval))
        else:
            end_diff = 0
            
        bound_start = start_dt + timedelta(seconds = start_diff)
        bound_end = end_dt + timedelta(seconds = end_diff)
        
        self.day_start.setCurrentIndex(bound_start.day - 1)
        self.month_start.setCurrentIndex(bound_start.month - 1)
        self.year_start.setCurrentIndex(bound_start.year - 2013)
        self.hour_start.setCurrentIndex(bound_start.hour)
        self.minute_start.setCurrentIndex(bound_start.minute)
        self.second_start.setCurrentIndex(0 if bound_start.second == 0 else 1)
        
        self.day_end.setCurrentIndex(bound_end.day - 1)
        self.month_end.setCurrentIndex(bound_end.month - 1)
        self.year_end.setCurrentIndex(bound_end.year - 2013)
        self.hour_end.setCurrentIndex(bound_end.hour)
        self.minute_end.setCurrentIndex(bound_end.minute)
        self.second_end.setCurrentIndex(0 if bound_end.second == 0 else 1)
        
    def submit_info(self):
        """
        PURPOSE: Take user given infomation and pass it back to the main widget
        to be sent to a file maker thread.
        """
        sub_id = str(self.subject_id.text())
        sub_sex = str(self.subject_sex.currentText())
        sub_dob = str(self.day_dob.currentText()) + ' ' + \
            str(self.month_dob.currentText()) + ' ' + \
            str(self.year_dob.currentText())
        sub_mass = str(self.subject_mass.text())
        
        self.validate_date()
        
        self.daysim_log.info('downloadmake.py class SubjectInfo func submit_info: Processing data for submission')
        
        start_time = ''
        if len(self.year_start.currentText()) == 1:
            start_time = start_time + '0' + str(self.year_start.currentText())\
            + '-'
        else:
            start_time = start_time + str(self.year_start.currentText()) + '-'
        if len(self.month_start.currentText()) == 1:
            start_time = start_time + '0' + str(self.month_start.currentText())\
            + '-'
        else:
            start_time = start_time + str(self.month_start.currentText()) + '-'
        if len(self.day_start) == 1:
            start_time = start_time + '0' + str(self.day_start.currentText())\
            + ' '
        else:
            start_time = start_time + str(self.day_start.currentText()) + ' '
        if len(self.hour_start) == 1:
            start_time = start_time + '0' + str(self.hour_start.currentText())\
            + ':'
        else:
            start_time = start_time + str(self.hour_start.currentText()) + ':'
        if len(self.minute_start) == 1:
            start_time = start_time + '0' + str(self.minute_start.currentText()) + ':'
        else:
            start_time = start_time + str(self.minute_start.currentText()) + ':'
        if len(self.second_start) == 1:
            start_time = start_time + '0' + str(self.second_start.currentText())
        else:
            start_time = start_time + str(self.second_start.currentText())
        

        end_time = ''
        if len(self.year_end.currentText()) == 1:
            end_time = end_time + '0' + str(self.year_end.currentText())\
            + '-'
        else:
            end_time = end_time + str(self.year_end.currentText()) + '-'
        if len(self.month_end.currentText()) == 1:
            end_time = end_time + '0' + str(self.month_end.currentText())\
            + '-'
        else:
            end_time = end_time + str(self.month_end.currentText()) + '-'
        if len(self.day_end) == 1:
            end_time = end_time + '0' + str(self.day_end.currentText())\
            + ' '
        else:
            end_time = end_time + str(self.day_end.currentText()) + ' '
        if len(self.hour_end) == 1:
            end_time = end_time + '0' + str(self.hour_end.currentText())\
            + ':'
        else:
            end_time = end_time + str(self.hour_end.currentText()) + ':'
        if len(self.minute_end) == 1:
            end_time = end_time + '0' + str(self.minute_end.currentText()) + ':'
        else:
            end_time = end_time + str(self.minute_end.currentText()) + ':'
        if len(self.second_end) == 1:
            end_time = end_time + '0' + str(self.second_end.currentText())
        else:
            end_time = end_time + str(self.second_end.currentText())

        print start_time

        self.success = True
        self.emit(QtCore.SIGNAL('sendinfo'), [sub_id, sub_sex, sub_dob, \
        sub_mass, start_time, end_time])
        
        self.daysim_log.info('downloadmake.py class SubjectInfo func submit_info: Data formatted and sent to file maker')
        self.close()
    
   
    def enable_submit(self):
        """
        PURPOSE: Enables submit button once all fields are filled with
        valid info.
        """
        if  not self.subject_id.text() == '' and self.in_range():
            self.submit.setEnabled(True)
        else:
            self.submit.setEnabled(False)
            
    def in_range(self):
        self.daysim_log.info('downloadmake.py class SubjectInfo func in_range: Checking that timestamps are within range')
        
        start_time = ''
        if len(self.year_start.currentText()) == 1:
            start_time = start_time + '0' + str(self.year_start.currentText())\
            + '-'
        else:
            start_time = start_time + str(self.year_start.currentText()) + '-'
        if len(self.month_start.currentText()) == 1:
            start_time = start_time + '0' + str(self.month_start.currentText())\
            + '-'
        else:
            start_time = start_time + str(self.month_start.currentText()) + '-'
        if len(self.day_start) == 1:
            start_time = start_time + '0' + str(self.day_start.currentText())\
            + ' '
        else:
            start_time = start_time + str(self.day_start.currentText()) + ' '
        if len(self.hour_start) == 1:
            start_time = start_time + '0' + str(self.hour_start.currentText())\
            + ':'
        else:
            start_time = start_time + str(self.hour_start.currentText()) + ':'
        if len(self.minute_start) == 1:
            start_time = start_time + '0' + str(self.minute_start.currentText()) + ':'
        else:
            start_time = start_time + str(self.minute_start.currentText()) + ':'
        if len(self.second_start) == 1:
            start_time = start_time + '0' + str(self.second_start.currentText())
        else:
            start_time = start_time + str(self.second_start.currentText())

        end_time = ''
        if len(self.year_end.currentText()) == 1:
            end_time = end_time + '0' + str(self.year_end.currentText())\
            + '-'
        else:
            end_time = end_time + str(self.year_end.currentText()) + '-'
        if len(self.month_end.currentText()) == 1:
            end_time = end_time + '0' + str(self.month_end.currentText())\
            + '-'
        else:
            end_time = end_time + str(self.month_end.currentText()) + '-'
        if len(self.day_end) == 1:
            end_time = end_time + '0' + str(self.day_end.currentText())\
            + ' '
        else:
            end_time = end_time + str(self.day_end.currentText()) + ' '
        if len(self.hour_end) == 1:
            end_time = end_time + '0' + str(self.hour_end.currentText())\
            + ':'
        else:
            end_time = end_time + str(self.hour_end.currentText()) + ':'
        if len(self.minute_end) == 1:
            end_time = end_time + '0' + str(self.minute_end.currentText()) + ':'
        else:
            end_time = end_time + str(self.minute_end.currentText()) + ':'
        if len(self.second_end) == 1:
            end_time = end_time + '0' + str(self.second_end.currentText())
        else:
            end_time = end_time + str(self.second_end.currentText())
            
        start_dt = datetime.strptime(start_time, '%Y-%m-%d %H:%M:%S')
        end_dt = datetime.strptime(end_time, '%Y-%m-%d %H:%M:%S')
        
        start_dt_data = datetime.strptime(self.start_time, '%Y-%m-%d %H:%M:%S')
        end_dt_data = datetime.strptime(self.end_time, '%Y-%m-%d %H:%M:%S')
        
        if (start_dt - start_dt_data) >= timedelta(minutes = 0) and \
           (end_dt_data - end_dt) >= timedelta(minutes = 0):
               self.daysim_log.info('downloadmake.py class SubjectInfo func in_range: Time within range')
               return True
        else:
            return False
            
    def keyPressEvent(self, qKeyEvent):
        if qKeyEvent.key() == QtCore.Qt.Key_Return and self.submit.isEnabled(): 
            self.submit_info()
        else:
            pass
        
class DownloadDaysimeter(QtCore.QThread):
    
    error = QtCore.pyqtSignal()
    
    def __init__(self, parent, args):
        QtCore.QThread.__init__(self, parent)
        self.savedir = args[0]
        self.filename = args[1]
        self.log_filename = args[2]
        self.data_filename = args[3]
        self.move = args[4]
        self.time_offset = constants_.UTC_OFFSETS[args[5]]
        
        self.daysim_log = logging.getLogger('daysim_log')
        
        self.err_log = logging.getLogger('err_log')
        
    def run(self):
        """
        PURPOSE: Reads raw binary data, processed and packages it.
        """
        log_filename = self.log_filename
        data_filename = self.data_filename
        adj_active_flag_ = constants_.ADJ_ACTIVE_FLAG
        old_flag = constants_.OLD_FLAG
        adj_active_firm = constants_.ADJ_ACTIVE_FIRM
        #Create error log file named error.log on the desktop
        errlog_filename = get_err_log()
        if errlog_filename == '':
            self.error.emit()
            sys.exit(1)
        errlog = self.err_log

        path = find_daysimeter()
        #Open header file for reading
        self.daysim_log.info('Trying to read header file')
        try:
            logfile_fp = open(log_filename,'r')
        #Catch IO exception (if present), add to log and quit
        except IOError:
            errlog.error('Could not open logfile')
            self.error.emit()
            sys.exit(1)
        else:
            #Read each line of the header and put it into a list
            #called info.
            #info[0] is status, info[1] is device ID, et cetera
            info = [x.strip('\n') for x in logfile_fp.readlines()]        
        #Close the logfile
        finally:
            logfile_fp.close()
        self.daysim_log.info('Header file read')
        #If we are using an old format, set flag to True
        if len(info) > 17:
            old_flag = False
        
        #Find the daysimeter device ID
        if old_flag:
            daysimeter_id = int(info[1])
            device_model = constants_.DEVICE_MODEL
            device_sn = constants_.DEVICE_VERSION + info[1]
        else:
            daysimeter_id = int(info[8])
            device_model = info[2]
            device_sn = info[2].lstrip('abcdefghijklmnopqrstuvwxyz') + info[8]
        #Get calibration info
        if not old_flag:
            calib_const = [float(x) for x in info[9].strip('\n').split('\t')]
            calib_info = \
            [daysimeter_id, calib_const[0], calib_const[1], calib_const[2]]
        else:
            calib_info = get_calib_info(daysimeter_id)
        
        if not calib_info:
            self.err_log.error('Calibration infromation was not found')
            self.error.emit()
            sys.exit(1)
            
        self.daysim_log.info('Trying to read data file')
        #Open binary data file for reading
        try:
            self.emit(QtCore.SIGNAL('fprogress'))
            datafile_fp = open(data_filename,'rb')
        #Catch IO exception (if present), add to log and quit
        except IOError:
            errlog.error('Could not open datafile')
            self.error.emit()
            sys.exit(1)
        else:
            #Read entire file into a string called data
            data = datafile_fp.read()
        #Close the datafile
        finally:
            datafile_fp.close()
            
        self.daysim_log.info('Data file read')
    
    #####It is assumed that time is formatted correctly, if not this
        #part of the code will not work. Time format is as follows:
        #mm-dd-yy HH:MM
    
        #Converts a time string into a float representing seconds
        #since epoch (UNIX)
        if not old_flag:
            struct_time = time.strptime(info[7], "%m-%d-%y %H:%M")
        else:
            struct_time = time.strptime(info[2], "%m-%d-%y %H:%M")
            
        epoch_time = datetime.fromtimestamp(time.mktime(struct_time)) + self.time_offset
        #log_interval is interval that the Daysimeter took measurements at.
        #Since python uses seconds since epoch, cast as int
        log_interval = int(info[3])
        
        #Determine the number of of logged entries. Why divded by 8?
        #I'm glad you asked! There are 4 things that are logged, and
        #each item takes up 2 bytes. So, we take the total number of
        #bytes (len(data)) and dived by 2*4. It makes so much sense!
        #I will admit, I only figure that out during debugging...
        num_entries = int(math.floor(len(data)/8))
        #Create lists for raw Red, Green, Blue, and Activity
        red = [-1] * num_entries
        green = [-1] * num_entries
        blue = [-1] * num_entries
        activity = [-1] * num_entries
        #Iteratively seperate data into raw R,G,B,A
        #struct.unpack unpacks binary data given a format.
        #>H is an unsigned short (16 bit unsigned integer) in big
        #endian notation.
        self.daysim_log.info('Unpacking binary data')
        for x in range(0, num_entries):
            #If value is 65278 the daysimeter reset, skip and leave
            #the value at -1
            if struct.unpack('>H', data[x*8:x*8+2])[0] == 65278:
                continue
            #If value is 65535 there are no more entires to be
            #read. Remove 'empty' entries and break
            elif struct.unpack('>H', data[x*8:x*8+2])[0] == 65535:
                del red[x:]
                del green[x:]
                del blue[x:]
                del activity[x:]
                break
            red[x] = struct.unpack('>H', data[x*8:x*8+2])[0]
            green[x] = struct.unpack('>H', data[x*8+2:x*8+4])[0]
            blue[x] = struct.unpack('>H', data[x*8+4:x*8+6])[0]
            activity[x] = struct.unpack('>H', data[x*8+6:x*8+8])[0]
        
        self.daysim_log.info('Finished upacking data')
        #Create array to keep track of resets; resets[x] = y means
        #there have been y resets before point x.
        resets = [-1] * len(red)
        
        #Remove reamining -1s (reset entires) from raw R,G,B,A
        #Note: calling len(red) 100,000 times runs this portion
        #of the code in a fraction of a second.
        self.daysim_log.info('Removing resets')
        x = y = 0
        while x < len(red):
            if red[x] == -1:
                del red[x]
                del green[x]
                del blue [x]
                del activity[x]
                y += 1
                continue
            resets[x] = y
            x += 1
        self.daysim_log.info('Resets removed')
        
        #If there were resets, R,G,B,A are now shorter than resets,
        #so we shall resize it.
        del resets[len(red):]
        
        #As of right now this uses either daysimeter_id (bad) or
        #firmware version (good). Once all daysimeters use a F1.x 
        #header or above, this code can be reduced to just the 
        #elif statement (as an if, of course )
        if old_flag:    
            if (daysimeter_id >= 54 and daysimeter_id <= 69) or \
            daysimeter_id >= 83:
                adj_active_flag_ = True
        elif float(info[1]) in adj_active_firm:
            adj_active_flag_ = True
        
        #If we are using the firmware version where the LSB of
        #activity is actually a monitor for RGB values rolling over
        #we need to adjust the values accordingly.
        if adj_active_flag_:
            adjusted_rgb = adj_active_flag(red, green, blue, activity)
            #Unpack adjusted values
            red = adjusted_rgb[0]
            green = adjusted_rgb[1]
            blue = adjusted_rgb[2]
            
        #Create list for time called times (because time is
        #a python module)
        times = [-1] * len(red)
        mat_times = [-1] * len(red)
        #Iteratively 'generate' timestamps and place into times
        for x in range(0, len(times)):
            times[x] = epoch_time + timedelta(seconds=log_interval*x)
            mat_times[x] = dt2dn(times[x])
            
        #Activity is captured on the daysimeter as a mean squared
        #value (i.e. activity = x^2 + y^2 + z^2) and is measured in
        #counts. To get the number of g's, calculate the root mean
        #square (RMS) value and multiple by .0039 (the number of g's
        #per count) *4. The *4 comes from "four right shifts in the 
        #souce code." Basically, there is some bit shifting to maximize
        #storage space in the EEPROM, and we 'un-shift' it.
        activity = [math.sqrt(x)*.0039*4 for x in activity]
        
        self.daysim_log.info('Adjusting raw data based on calibration information')
        #Apply calibration constants to raw data
        red = [x*calib_info[1] for x in red]
        green = [x*calib_info[2] for x in green]
        blue = [x*calib_info[3] for x in blue]
        #If new fireware, find constants in the header, process them, and
        #calculate lux and cla
        self.daysim_log.info('Calculating Luc and CLA')
        if not old_flag:
            constants = process_constants(info[14], info[13], info[12], \
            info[11], info[10], info[15])
            temp = self.calc_lux_cla(red, green, blue, constants)
        #Else, search for a constants file, process constants, and calculate
        #lux and cla
        else:
            temp = self.calc_lux_cla(red, green, blue)
        #Unpack lux and cla
        lux = temp[0]
        cla = temp[1]
    
        del(temp)
        #Apply a zero phase shift filter to cla and activity
        self.daysim_log.info('Applying zero phase shift filter to data')
        cla = lowpass_filter(cla, log_interval)
        activity = lowpass_filter(activity, log_interval)
        #Calculate cs
        cs = calc_cs(cla)
        self.daysim_log.info('Readying data to be written to file')
        self.emit(QtCore.SIGNAL('make'),([device_model, device_sn, \
        calib_info, log_interval], [times, mat_times, red, green, blue, lux, \
        cla, cs, activity, resets]))
        
        
        if self.move:
            self.daysim_log.info('Backing up raw data from daysimeter')
            shutil.copy(os.path.join(path, constants_.LOG_FILENAME), \
                        self.savedir)
            shutil.copy(os.path.join(path, constants_.DATA_FILENAME), \
                        self.savedir)
            os.rename(os.path.join(self.savedir, constants_.LOG_FILENAME), \
                      os.path.join(self.savedir, \
                      self.filename[:len(self.filename) - 4] + '-LOG.txt'))
            os.rename(os.path.join(self.savedir, constants_.DATA_FILENAME), \
                      os.path.join(self.savedir, \
                      self.filename[:len(self.filename) - 4] + '-DATA.txt'))
        
    def calc_lux_cla(self, *args):
        """ PURPOSE: Calculates CS and CLA. """
        
        if len(args) == 3:
            red = args[0]
            green = args[1]
            blue = args[2]
            #Constants is a list of lists, with hardware specific constants
            constants = get_constants()
        elif len(args) == 4:
            red = args[0]
            green = args[1]
            blue = args[2]
            constants = args[3]
        else:
            self.err_log.warning('Invalid usage of calc_lux_cla')
            sys.exit(1)
            
        loop_max = num_entries = len(red)
        
        #Create lux list and allocate space
        lux = [-1] * num_entries
        #Calculate and fill lux
        for x in range(0, loop_max):
            lux[x] = constants[4][0]*red[x] + constants[4][1]*green[x] + \
            constants[4][2]*blue[x]
            
        #Create lists and allocate space for each list
        scone_macula = [-1] * num_entries
        v_lamda_macula =  [-1] * num_entries
        melanopsin =  [-1] * num_entries
        v_prime =  [-1] * num_entries
        cla = [-1] * num_entries
        
        #Following is lots of fancy math which I do not understand the
        #reasoning for. I based it off the MatLab code, with some exceptions
        #to optimize code for python
        for x in range(0, loop_max):
            scone_macula[x] = constants[0][0]*red[x] + \
            constants[0][1]*green[x] + constants[0][2]*blue[x]
            v_lamda_macula[x] = constants[1][0]*red[x] + \
            constants[1][1]*green[x] + constants[1][2]*blue[x]
            melanopsin[x] = constants[2][0]*red[x] + \
            constants[2][1]*green[x] + constants[2][2]*blue[x]
            v_prime[x] = constants[3][0]*red[x] + constants[3][1]*green[x] + \
            constants[3][2]*blue[x]
            
            if scone_macula[x] > v_lamda_macula[x] * constants[5][2]:
                #Some super fancy math. I wish I knew what was going on here...
                cla[x] = melanopsin[x] + constants[5][0] * (scone_macula[x] - \
                v_lamda_macula[x] * constants[5][2]) - \
                constants[5][1]*683*(1 - 2.71**(-(v_prime[x]/(683*6.5))))
            else:
                cla[x] = melanopsin[x]
            
        cla = [0 if x < 0 else x for x in cla]
            
        return [lux, cla]
        
class MakeCDF(QtCore.QThread):
    
    def __init__(self, parent, data, filename, info):
        QtCore.QThread.__init__(self, parent)
        self.data = data
        self.filename = filename
        self.info = info
        self.logical_array(info[4], info[5])
        
        
        self.daysim_log = logging.getLogger('daysim_log')

        self.err_log = logging.getLogger('err_log')
        
    def logical_array(self, start, end):
        start_dt = datetime.strptime(start, '%Y-%m-%d %H:%M:%S')
        end_dt = datetime.strptime(end, '%Y-%m-%d %H:%M:%S')
        start_index = self.data[1][0].index(start_dt)
        end_index = self.data[1][0].index(end_dt)
        
        self.logical_arr = [False] * len(self.data[1][0])
        
        for x in range(start_index, end_index):
            self.logical_arr[x] = True
        
    def run(self):
        """ PURPOSE: Makes a CDF file from data. """
        
        sub_info = self.info
        if not sub_info[2] == 'None':
            struct_time = time.strptime(sub_info[2], '%d %B %Y')
            sub_info[2] = datetime.fromtimestamp(time.mktime(struct_time))

        filename = self.filename

        if os.path.isfile(filename):
            os.remove(filename)
        data = self.data
        self.daysim_log.info('Writing data to CDF file')
        with pycdf.CDF(filename,'') as cdf_fp:
            #Set global attributes
            cdf_fp.attrs['creationDate'] = datetime.now()
            cdf_fp.attrs['deviceModel'] = data[0][0]
            cdf_fp.attrs['deviceSN'] = data[0][1]
            cdf_fp.attrs['redCalibration'] = data[0][2][1]
            cdf_fp.attrs['greenCalibration'] = data[0][2][2]
            cdf_fp.attrs['blueCalibration'] = data[0][2][3]
    #########The following global attributes either do not exist yet, or
    #########have no available source to pull the information from
    #        cdf_fp.attrs['uvCalibration'] = 
    #        cdf_fp.attrs['illuminanceCalibration'] =
            cdf_fp.attrs['subjectID'] = sub_info[0]
            cdf_fp.attrs['subjectSex'] = sub_info[1]
            cdf_fp.attrs['subjectDateOfBirth'] = sub_info[2]
            cdf_fp.attrs['subjectMass'] = sub_info[3]
            
            
            #Set variables
            cdf_fp['time'] = data[1][0]
#            cdf_fp.new('matTime', type=pycdf.const.CDF_REAL8)
#            cdf_fp['matTime'] = data[1][1]
            cdf_fp.new('timeOffset', get_local_offset_s(), \
            pycdf.const.CDF_INT4, False)
            cdf_fp['logicalArray'] = self.logical_arr
            cdf_fp['red'] = data[1][2]
            cdf_fp['green'] = data[1][3]
            cdf_fp['blue'] = data[1][4]
            cdf_fp['illuminance'] = data[1][5]
            cdf_fp['CLA'] = data[1][6]
            cdf_fp['CS'] = data[1][7]
            cdf_fp['activity'] = data[1][8]
            
    #        cdf_fp['xAcceleration'] =
    #        cdf_fp['yAcceleration'] =
    #        cdf_fp['zAcceleration'] =
    #        cdf_fp['uvIndex'] =
    #        cdf_fp['temperature'] =
    #        cdf_fp['longitude'] =
    #        cdf_fp['latitude'] =
    #        cdf_fp['event'] =
            
            #Set variable attributes for time
            cdf_fp['time'].attrs['description'] = 'UTC in CDF Epoch format,' + \
            ' milliseconds since 1-Jan-0000'
            cdf_fp['time'].attrs['unitPrefix'] = 'm'
            cdf_fp['time'].attrs['baseUnit'] = 's'
            cdf_fp['time'].attrs['unitType'] = 'baseSI'
            cdf_fp['time'].attrs['otherAttributes'] = ''
            
            #Set variable attributes for matTime
#            cdf_fp['matTime'].attrs['description'] = 'UTC in MATLAB serial' + \
#            ' date format, days since 1-Jan-0000'
#            cdf_fp['matTime'].attrs['unitPrefix'] = ''
#            cdf_fp['matTime'].attrs['baseUnit'] = 'days'
#            cdf_fp['matTime'].attrs['unitType'] = 'nonSI'
#            cdf_fp['matTime'].attrs['otherAttributes'] = ''
            
            #Set variable attributes for timeOffset
            cdf_fp['timeOffset'].attrs['description'] = 'Localized offset ' + \
            'from UTC'
            cdf_fp['timeOffset'].attrs['unitPrefix'] = ''
            cdf_fp['timeOffset'].attrs['baseUnit'] = 's'
            cdf_fp['timeOffset'].attrs['unitType'] = 'baseSI'
            cdf_fp['timeOffset'].attrs['otherAttributes'] = ''
            
            #Set variable attributes for logical array
            cdf_fp['logicalArray'].attrs['description'] = ''
            cdf_fp['logicalArray'].attrs['unitPrefix'] = ''
            cdf_fp['logicalArray'].attrs['baseUnit'] = ''
            cdf_fp['logicalArray'].attrs['unitType'] = ''
            cdf_fp['logicalArray'].attrs['otherAttributes'] = ''
            
            #Set variable attributes for red
            cdf_fp['red'].attrs['description'] = ''
            cdf_fp['red'].attrs['unitPrefix'] = ''
            cdf_fp['red'].attrs['baseUnit'] = 'lx'
            cdf_fp['red'].attrs['unitType'] = 'namedSI'
            cdf_fp['red'].attrs['otherAttributes'] = ''
            
            #Set variable attributes for green
            cdf_fp['green'].attrs['description'] = ''        
            cdf_fp['green'].attrs['unitPrefix'] = ''
            cdf_fp['green'].attrs['baseUnit'] = 'lx'
            cdf_fp['green'].attrs['unitType'] = 'namedSI'
            cdf_fp['green'].attrs['otherAttributes'] = ''
            
            #Set variable attributes for blue
            cdf_fp['blue'].attrs['description'] = ''
            cdf_fp['blue'].attrs['unitPrefix'] = ''
            cdf_fp['blue'].attrs['baseUnit'] = 'lx'
            cdf_fp['blue'].attrs['unitType'] = 'namedSI'
            cdf_fp['blue'].attrs['otherAttributes'] = ''
            
            #Set variable attributes for illuminance
            cdf_fp['illuminance'].attrs['description'] = ''
            cdf_fp['illuminance'].attrs['unitPrefix'] = ''
            cdf_fp['illuminance'].attrs['baseUnit'] = 'lx'
            cdf_fp['illuminance'].attrs['unitType'] = 'namedSI'
            cdf_fp['illuminance'].attrs['otherAttributes'] = ''
            
            #Set variable attributes for CLA
            cdf_fp['CLA'].attrs['description'] = 'Circadian Light'
            cdf_fp['CLA'].attrs['unitPrefix'] = ''
            cdf_fp['CLA'].attrs['baseUnit'] = 'CLA'
            cdf_fp['CLA'].attrs['unitType'] = 'nonSI'
            cdf_fp['CLA'].attrs['otherAttributes'] = 'model'
            
            #Set variable attributes for CS
            cdf_fp['CS'].attrs['description'] = 'Circadian Stimulus'
            cdf_fp['CS'].attrs['unitPrefix'] = ''
            cdf_fp['CS'].attrs['baseUnit'] = 'CS'
            cdf_fp['CS'].attrs['unitType'] = 'nonSI'
            cdf_fp['CS'].attrs['otherAttributes'] = 'model'
            
            #Set variable attributes for activity
            cdf_fp['activity'].attrs['description'] = 'Activity index in g' + \
            '-force (acceleration in m/2^2 over standard gravity 9.80665 m/s^2)'
            cdf_fp['activity'].attrs['unitPrefix'] = ''
            cdf_fp['activity'].attrs['baseUnit'] = 'g_n'
            cdf_fp['activity'].attrs['unitType'] = 'nonSI'
            cdf_fp['activity'].attrs['otherAttributes'] = 'method'
            
            #Set variable attributes for xAcceleration
    #        cdf_fp['xAcceleration'].attrs['description'] = 'Acceleration ' + \
    #        'in the x-axis relative to the accelerometer'
    #        cdf_fp['xAcceleration'].attrs['unitPrefix'] = ''
    #        cdf_fp['xAcceleration'].attrs['baseUnit'] = 'm/s^2'
    #        cdf_fp['xAcceleration'].attrs['unitType'] = 'derivedSI'
    #        cdf_fp['xAcceleration'].attrs['otherAttributes'] = ''
            
            #Set variable attributes for yAcceleration
    #        cdf_fp['yAcceleration'].attrs['description'] = 'Acceleration ' + \ 
    #        'in the y-axis relative to the accelerometer'
    #        cdf_fp['yAcceleration'].attrs['unitPrefix'] = ''
    #        cdf_fp['yAcceleration'].attrs['baseUnit'] = 'm/s^2'
    #        cdf_fp['yAcceleration'].attrs['unitType'] = 'derivedSI'
    #        cdf_fp['yAcceleration'].attrs['otherAttributes'] = ''
            
            #Set variable attributes for zAcceleration
    #        cdf_fp['zAcceleration'].attrs['description'] = 'Acceleration ' + \
    #        'in the z-axis relative to the accelerometer'
    #        cdf_fp['zAcceleration'].attrs['unitPrefix'] = ''
    #        cdf_fp['zAcceleration'].attrs['baseUnit'] = 'm/s^2'
    #        cdf_fp['zAcceleration'].attrs['unitType'] = 'derivedSI'
    #        cdf_fp['zAcceleration'].attrs['otherAttributes'] = ''
            
            #Set variable attributes for uvIndex
    #        cdf_fp['uvIndex'].attrs['description'] = 'Ultraviolet index'
    #        cdf_fp['uvIndex'].attrs['unitPrefix'] = ''
    #        cdf_fp['uvIndex'].attrs['baseUnit'] = 'uvIndex'
    #        cdf_fp['uvIndex'].attrs['unitType'] = 'nonSI'
    #        cdf_fp['uvIndex'].attrs['otherAttributes'] = ''
            
            #Set variable attributes for temperature
    #        cdf_fp['temperature'].attrs['description'] = 'Ambient air ' + \
    #        'temperature in degrees Kelvin'
    #        cdf_fp['temperature'].attrs['unitPrefix'] = ''
    #        cdf_fp['temperature'].attrs['baseUnit'] = 'K'
    #        cdf_fp['temperature'].attrs['unitType'] = 'baseSI'
    #        cdf_fp['temperature'].attrs['otherAttributes'] = ''
            
            #Set variable attributes for longitude
    #        cdf_fp['longitude'].attrs['description'] = 'Longitude in ' + \
    #        'decimal degrees'
    #        cdf_fp['longitude'].attrs['unitPrefix'] = ''
    #        cdf_fp['longitude'].attrs['baseUnit'] = 'deg'
    #        cdf_fp['longitude'].attrs['unitType'] = 'nonSI'
    #        cdf_fp['longitude'].attrs['otherAttributes'] = ''
            
            #Set variable attributes for latitude
    #        cdf_fp['latitude'].attrs['description'] = 'Latitude in ' + \
    #        'decimal degrees'
    #        cdf_fp['latitude'].attrs['unitPrefix'] = ''
    #        cdf_fp['latitude'].attrs['baseUnit'] = 'deg'
    #        cdf_fp['latitude'].attrs['unitType'] = 'nonSI'
    #        cdf_fp['latitude'].attrs['otherAttributes'] = ''
            
            #Set variable attributes for event
    #        cdf_fp['event'].attrs['description'] = 'Event marker'
    #        cdf_fp['event'].attrs['unitPrefix'] = ''
    #        cdf_fp['event'].attrs['baseUnit'] = ''
    #        cdf_fp['event'].attrs['unitType'] = ''
    #        cdf_fp['event'].attrs['otherAttributes'] = 'event code definition'
            
        #Set download flag to true (0)
        self.daysim_log.info('All data written to CDF file')
        if not find_daysimeter():
            pass
        else:
            set_download_flag()
        
        self.emit(QtCore.SIGNAL('update'))

class MakeCSV(QtCore.QThread):
    
    def __init__(self, parent, data, filename):
        QtCore.QThread.__init__(self, parent)
        self.data = data
        self.filename = filename

        self.daysim_log = logging.getLogger('daysim_log')

        self.err_log = logging.getLogger('err_log')
        
    def run(self):
        """ PURPOSE: Makes a CSV file from data. """
    
        filename = self.filename
        self.daysim_log.info('Writing data to CSV file')
        with open(filename,'w') as csv_fp:
            csv_fp.write('time,red,green,blue,lux,CLA,CS,activity,resets\n')
            for x in range(len(self.data[1][0])):
                csv_fp.write(str(self.data[1][0][x]) + ',' + \
                str(self.data[1][2][x]) + ',' + str(self.data[1][3][x]) + ',' \
                + str(self.data[1][4][x]) + ',' +  str(self.data[1][5][x]) + \
                 ',' +  str(self.data[1][6][x]) + ',' + \
                 str(self.data[1][7][x]) + ',' + str(self.data[1][8][x]) + \
                 ',' + str(self.data[1][9][x]) + '\n')
        set_download_flag()
        self.daysim_log.info('All data written to CSV file')
        self.emit(QtCore.SIGNAL('update'))

def main():
    """ PURPOSE: Creates app and runs widget """
    # Create the Qt Application
    app = QtGui.QApplication(sys.argv)
    # Create and show the form
    session = DownloadMake()
    # Run the main Qt loop
    sys.exit(app.exec_())
            
if __name__ == '__main__':
    main()          