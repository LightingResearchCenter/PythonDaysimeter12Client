# -*- coding: utf-8 -*-
"""
Created on Wed Jun 12 15:34:13 2013

@author: pentla
"""

import sys, os
sys.path.insert(0, os.pardir)
import time
import math
from PyQt4 import QtGui, QtCore
from numpy import genfromtxt, core, asscalar
from datetime import datetime 
import graphingwidget as gw
from ConfigParser import ConfigParser, SafeConfigParser
from functools import partial
from spacepy import pycdf
from re import sub
from src.downloadmake import DownloadMake
from src.offsetwidget import OffsetWidget
from src.logfunc import stop_log
from src.logfunc import resume_log
from src.finddaysimeter import find_daysimeter
from src.startnewlog import StartNewLog
from src.getversion import get_current_version
import src.constants as constants_
from statuslight import StatusLight
from statuswidget import StatusWidget
from startloginfo import StartLogInfo
import subprocess
from src.getlogs import get_err_log, get_daysim_log, setup_logger
import logging

QT_APP = QtGui.QApplication(sys.argv) 
 
class LayoutExample(QtGui.QMainWindow):
    """The main window for the daysimeter download client. It opens daysimeter
    data files and displays a central widget"""
    def __init__(self):
        """Initialize the daysimeter client with a placeholder widget
        
        Creates the main window, creates the menus, and loads info from the
        ini file        
        """
        QtGui.QMainWindow.__init__(self)
        
        setup_logger('daysim_log', get_daysim_log())
        self.daysim_log = logging.getLogger('daysim_log')

        setup_logger('err_log', get_err_log())
        self.err_log = logging.getLogger('err_log')
        
        self.setWindowTitle('Daysimeter Download Client')
        self.setMinimumSize(600, 400)
        self.main_widget = gw.GraphingWidget(self)
        self.setCentralWidget(self.main_widget)
        self.init = None
        self.statusBar()
        self.make_toolbar()
#        self.create_menus()
        self.load_config()
        self.update_check()
        self.make_enabler()
#        self.daysimeter_status()
        self.disconnected = True
        self.make_shortcuts()
        

        
        
        self.show()
        
        
        
#    def daysimeter_status(self):
#        self.status_widget = StatusWidget(self)
#        self.daysim_status = QtGui.QDockWidget('Status', self.status_widget)
#        self.daysim_status.setAllowedAreas(QtCore.Qt.TopDockWidgetArea)
#        self.daysim_status.setFeatures(QtGui.QDockWidget.NoDockWidgetFeatures)
#        self.addDockWidget(QtCore.Qt.TopDockWidgetArea, self.daysim_status)

        
    def get_daysim_log(self):
        return self.daysim_log
        
    def go_print(self):
        """ Prints the graph and metadata """
        self.daysim_log.info('Initializing printer')
        printer = QtGui.QPrinter(QtGui.QPrinter.PrinterResolution)
        printer.setOrientation(QtGui.QPrinter.Landscape)
        printer.setResolution(300)
        printer.setFullPage(True)
        reply = QtGui.QPrintDialog(printer, self)
        if reply.exec_() == QtGui.QDialog.Accepted:
            painter = QtGui.QPainter(printer)
            printer_width = printer.pageRect().width()
            printer_height = printer.pageRect().height()
            self.print_widget = self.main_widget
            reset_size = self.main_widget.size()
            self.print_widget.resize(1200, 900)
            xscale = printer_width  / self.print_widget.plot.width()
            yscale = printer_height  / self.print_widget.plot.height()
            painter.scale(xscale, yscale)
            self.print_widget.plot.render(painter, QtCore.QPoint\
            ((printer.paperRect().width() - printer.pageRect().width())/4,0))
            xoff = int(printer.pageRect().width() - \
                       self.print_widget.metadata.width() * xscale)/xscale
            yoff = int(printer.pageRect().height() - \
                       self.print_widget.metadata.height() * yscale)/yscale
            self.print_widget.metadata.render(painter, \
                                              QtCore.QPoint(xoff, yoff))
            painter.end()
            self.print_widget.resize(reset_size)
        self.daysim_log.info('Job ready to be printed')
            
    def make_shortcuts(self):
        """ Creates the keyboard shortcuts for the Daysimeter Client """
        download_shortcut = QtGui.QShortcut(QtGui.QKeySequence('CTRL+D'), \
        self, self.download_data_UTC, self.download_data_UTC, QtCore.Qt.WidgetShortcut)
        
        open_shortcut = QtGui.QShortcut(QtGui.QKeySequence('CTRL+L'), \
        self, self.open_file, self.open_file, QtCore.Qt.WidgetShortcut)
        
        quit_shortcut = QtGui.QShortcut(QtGui.QKeySequence('CTRL+Q'), \
        self, self.close, self.close, QtCore.Qt.WidgetShortcut)
        
        print_shortcut = QtGui.QShortcut(QtGui.QKeySequence('CTRL+P'), \
        self, self.go_print, self.go_print, QtCore.Qt.WidgetShortcut)
        
        set_save_shortcut = QtGui.QShortcut(QtGui.QKeySequence('SHIFT+CTRL+S'), \
        self, partial(self.load_config, update='savepath'), \
        partial(self.load_config, update='savepath'), QtCore.Qt.WidgetShortcut)
        
        new_log_shortcut = QtGui.QShortcut(QtGui.QKeySequence('CTRL+N'), \
        self, self.start_log, self.start_log, QtCore.Qt.WidgetShortcut)

        reset_batt_shortcut = QtGui.QShortcut(QtGui.QKeySequence('SHIFT+CTRL+R'), \
        self, self.reset_battery, self.reset_battery, QtCore.Qt.WidgetShortcut)
        
        fix_head_shortcut = QtGui.QShortcut(QtGui.QKeySequence('SHIFT+CTRL+F'), \
        self, self.fix_header, self.fix_header, QtCore.Qt.WidgetShortcut)
        
        process_shortcut = QtGui.QShortcut(QtGui.QKeySequence('SHIFT+CTRL+P'), \
        self, self.process_data, self.process_data, QtCore.Qt.WidgetShortcut)
        
        start_log_shortcut = QtGui.QShortcut(QtGui.QKeySequence('SHIFT+CTRL+L'), \
        self, self.get_start_log, self.get_start_log, QtCore.Qt.WidgetShortcut)
        
        toggle_show_shortcut = QtGui.QShortcut(QtGui.QKeySequence('SHIFT+CTRL+T'), \
        self, self.toggle_show, self.toggle_show, QtCore.Qt.WidgetShortcut)
        
        
    def make_toolbar(self):
        """ Creates the top toolbar where all the functions are located """
        self.top_toolbar = QtGui.QToolBar()
        self.top_toolbar.setAllowedAreas(QtCore.Qt.TopToolBarArea)
        self.top_toolbar.setMovable(False)
        
        open_act = QtGui.QAction("&Open Processed File", 
                              self,
                              statusTip="Open a processed daysimeter file",
                              shortcut=QtGui.QKeySequence.Open,
                              triggered=self.open_file)
        quit_act = QtGui.QAction("&Quit", 
                              self,
                              shortcut=QtGui.QKeySequence.Quit,
                              triggered=sys.exit)
        print_act = QtGui.QAction("&Print", 
                              self,
                              statusTip="Print Graph",
                              triggered=self.go_print)
                              
        set_savepath = QtGui.QAction("&Set Save Path", 
                                  self,
                                  statusTip="Set the save path for the " + \
                                  "processed Daysimeter data file",
                                  triggered=partial(self.load_config, 
                                                    update='savepath'))
        self.make_download = QtGui.QAction("&Download Data", 
                                  self,
                                  statusTip="Download daysimeter data " +  \
                                  "and write to file",
                                  triggered=self.download_data_UTC)
                                  
        self.data_process = QtGui.QAction("&Process Data", 
                                  self,
                                  statusTip="Processes downloaded Daysimeter files",
                                  triggered=self.process_data)
                                  
        self.stop_logging = QtGui.QAction('&Stop Current Log', self, statusTip='Stop ' + \
                                  'current log', triggered=self.stop_log)
                                  
        self.resume_logging = QtGui.QAction('&Resume Current Log', self, statusTip='Resumes ' + \
                                  'current log', triggered=self.resume_log)
                                  
        self.start_logging = QtGui.QAction('&Start New Log', self, statusTip='Starts'+\
                                   ' a new data log', triggered=self.start_log)
        
        self.reset_batt = QtGui.QAction('&Reset Logged Hours', self, statusTip='Sets'+\
                                   ' logged hours to 0', triggered=self.reset_battery)
                                   
        # Adds the options to the menu
        file_actions = [open_act, set_savepath, self.data_process, print_act, quit_act]
        daysimeter_actions = [self.make_download, self.start_logging, \
                              self.stop_logging, self.resume_logging, \
                              self.reset_batt]
        
        self.status_light = StatusLight(self)
        self.top_toolbar.addWidget(self.status_light)
        self.top_toolbar.addSeparator()
        self.status_widget = StatusWidget(self)
        self.top_toolbar.addWidget(self.status_widget)
        self.top_toolbar.addSeparator()
        
        self.top_toolbar.addActions(file_actions)
        self.top_toolbar.addSeparator()
       
        self.top_toolbar.addActions(daysimeter_actions)
            
        self.addToolBar(self.top_toolbar)
        
        
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
            
        
    def create_menus(self):
        """Create the menus"""
        self.create_file_menu()
        self.create_daysimeter_menu()
    
        
    def create_file_menu(self):
        """Creates the file menu"""
        file_menu = self.menuBar().addMenu('&File')
        # Makes menu options
        actions = []
        open_act = QtGui.QAction("&Open...", 
                              self,
                              statusTip="Open a processed daysimeter file",
                              shortcut=QtGui.QKeySequence.Open,
                              triggered=self.open_file)
        quit_act = QtGui.QAction("&Quit", 
                              self,
                              shortcut=QtGui.QKeySequence.Quit,
                              triggered=sys.exit)
        # Adds the options to the menu
        actions.extend([open_act, quit_act])
        for action in actions:
            file_menu.addAction(action)
            
    def create_daysimeter_menu(self):
        """Creates the daysimeter menu"""
        daysim_menu = self.menuBar().addMenu('&Daysimeter')
        # Makes menu options
        actions = []
        set_savepath = QtGui.QAction("&Set Save Path", 
                                  self,
                                  statusTip="Set the save path for the " + \
                                  "processed Daysimeter data file",
                                  triggered=partial(self.load_config, 
                                                    update='savepath'))
        make_download = QtGui.QAction("&Download Data", 
                                  self,
                                  statusTip="Download daysimeter data " +  \
                                  "and write to file",
                                  triggered=self.download_data_UTC)
                                  
        stop_logging = QtGui.QAction('&Stop Current Log', self, statusTip='Stop ' + \
                                  'current log', triggered=self.stop_log)
                                  
        resume_logging = QtGui.QAction('&Resume Current Log', self, statusTip='Resumes ' + \
                                  'current log', triggered=self.resume_log)
                                  
        start_logging = QtGui.QAction('&Start New Log', self, statusTip='Starts'+\
                                   ' a new data log', triggered=self.start_log)
        # Adds the options to the menu
        log_menu = QtGui.QMenu(daysim_menu)
        log_menu.setTitle('Log')
        log_list = [start_logging, stop_logging, resume_logging]
        for item in log_list:
            log_menu.addAction(item)
        actions.extend([make_download, set_savepath])
        for action in actions:
            daysim_menu.addAction(action)
        daysim_menu.addMenu(log_menu)
        
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
    
    def start_log(self):
        """ Starts a new log on the Daysimeter """
        self.new_log = StartNewLog()
    
    def stop_log(self):
        """ Stops current log """
        if stop_log():
            self.statusBar().showMessage("Current Log Stopped", 2000)
        else:
            QtGui.QMessageBox.question(self, 'Error',
                                   'No Daysimeter Found!', \
                                   QtGui.QMessageBox.Ok)
            
        
    def resume_log(self):
        """ Resumes teh current log from where it left off """
        duration = datetime.now() - self.time_connected
        duration = duration.total_seconds()
        total_time = ''
        
        duration_days = duration/(24*60*60)
        if math.floor(duration_days) > 0:
            if math.floor(duration_days) > 1:
                total_time = total_time + str(int(math.floor(duration_days))) + \
                ' days'
            else:
                total_time = total_time + str(int(math.floor(duration_days))) + \
                ' day'
            duration = duration % (24 * 60 * 60)
            
            duration_hours = math.floor(duration/(60*60))
            duration_mins = math.floor((duration%(60*60))/60)
            if duration_hours > 0:
                if duration_hours > 1:
                    if duration_mins == 0:
                        total_time = total_time + ' and ' + \
                        str(int(duration_hours)) + ' hours'
                    else: 
                        total_time = total_time + ', ' + \
                        str(int(duration_hours)) + ' hours and ' + \
                        str(int(duration_mins)) + ' minutes'
                else:
                    if duration_mins == 0:
                        total_time = total_time + ' and ' + \
                        str(int(duration_hours)) + ' hour'
                    elif duration_mins == 1: 
                        total_time = total_time + ', ' + \
                        str(int(duration_hours)) + ' hour and ' + \
                        str(int(duration_mins)) + ' minute'
                    else:
                        total_time = total_time + ', ' + \
                        str(int(duration_hours)) + ' hour and ' + \
                        str(int(duration_mins)) + ' minutes'
            elif duration_mins > 0:
                if duration_mins > 1:
                    total_time = total_time + ' and' + \
                    str(int(duration_mins)) + ' minutes'
                else:
                    total_time = total_time + ' and' + \
                    str(int(duration_mins)) + ' minute'
        elif duration_hours:
            if duration_mins == 0:
                if duration_mins == 1:
                    total_time = total_time + \
                    str(int(duration_hours)) + ' hour'
                else:
                    total_time = total_time + \
                    str(int(duration_hours)) + ' hours'
            elif duration_hours == 1 and \
                 duration_mins == 1: 
                total_time = total_time + \
                str(int(duration_hours)) + ' hour and ' + \
                str(int(duration_mins)) + ' minute'
            elif duration_hours == 1 and \
                 duration_mins > 1: 
                total_time = total_time + \
                str(int(duration_hours)) + ' hour and ' + \
                str(int(duration_mins)) + ' minutes'
            elif duration_hours > 1 and \
                 duration_mins == 1: 
                total_time = total_time + \
                str(int(duration_hours)) + ' hours and ' + \
                str(int(duration_mins)) + ' minute'   
            else: 
                total_time = total_time + \
                str(int(duration_hours)) + ' hours and ' + \
                str(int(duration_mins)) + ' minutes'
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
                                           
    def download_data_UTC(self):
        log_filename = constants_.LOG_FILENAME
        
        prev_info = []
        # Remount the daysimeter until the data equals the previous data
        while True:
            # Find daysim path and read the data
            path = find_daysimeter()
            with open(path + log_filename, 'r') as fp:
                info = fp.readlines()

            # Stop loop if the data equals the previous data
            if info and prev_info == info:
                break
            self.remount(path)
            prev_info = info

        
        if len(info) != 17:
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
            self.send_offset(15, False)

    def remount(self, drive):
      diskpart_data = "change-drive.txt"
      with open(diskpart_data, 'w') as f:
          diskpart = "".join(["select volume=", drive, "\nremove\n", "assign\n", "exit\n"])
          f.write(diskpart)
      subprocess.call (['diskpart',  '/s', diskpart_data])

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
        self.connect(self.download, QtCore.SIGNAL('savename'), self.read_data)
        
    def get_start_log(self):
        """
        Creates a widget that allows a user to search the start log for the
        time and date it was started, and the log interval used.
        """
        self.start_log = StartLogInfo()
        
    def process_data(self):
        """ Process already downloaded daysimeter files """
        self.daysim_log.info('Initizling data processor')
        self.parser = SafeConfigParser()
        if not self.parser.read('daysimeter.ini') == []:
            if self.parser.has_section('Application Settings'):
                self.savedir = self.parser.get('Application Settings', 'savepath')
            else:
                self.savedir = os.getcwd()
        else:
            self.savedir = os.getcwd()
            
        log_filename = QtGui.QFileDialog.getOpenFileName(self, \
        'Select Header File', self.savedir, ('Text Files (*.txt)'))
        
        for x in reversed(range(len(log_filename))):
            if log_filename[x] == '/':
                samedir = log_filename[:x+1]
                break
        
        if log_filename:
            data_filename = QtGui.QFileDialog.getOpenFileName(self, \
            'Select Data File', samedir, ('Text Files (*.txt)'))
            
            if data_filename:
                self.download = DownloadMake(args=[log_filename, data_filename])
                self.connect(self.download, QtCore.SIGNAL('savename'), self.read_data)
        
    def read_data(self, filename):
        """Reads the data from a txt or cdf and graphs it
        
        filename - a string of the file name
        
        """
        # Gets the file extension of the file
        ext = os.path.splitext(filename)[1].lower()
        # Reads the data based on the file type
        if ext == '.txt':
            self.update_header(filename)
            timestamps, daysim_data, filetype = self.read_txt_data(filename)
        elif ext == '.cdf':
            timestamps, daysim_data, filetype = self.read_cdf_data(filename)
        else:
            return
        # Sets the data in the graphing widget
        self.main_widget.set_data(timestamps, daysim_data, filetype)
        
    def open_file(self):
        """Opens and read a cdf or txt file and pass its data"""
        if self.init.get('Application Settings', 'savepath'):
            def_dir = self.init.get('Application Settings', 'savepath')
        else:
            def_dir = './'
        filename = str(QtGui.QFileDialog.getOpenFileName(self,
                                                       directory=def_dir,
                                                       filter="Data File (*.cdf *.txt)"))
        if not filename:
            return
            
        self.read_data(filename)
    
    def read_txt_data(self, filename):
        """Reads the data from a daysimeter txt file
        
        filename - the string filename of the file
        
        returns an array of timestamps, a recarray of daysim_data, and txt (
        the filetype)
        
        """
        # Parses the data from the file into an recarray
        daysim_data = genfromtxt(filename, 
                                 dtype=['S11', 'S8', 'f8', 'f8', 'f8', 'f8'],
                                 names=True)
        # Concatenates the dates and times
        daysim_data['Date'] = core.defchararray.add(daysim_data['Date'],
                                                         ' ')
        datetime_str = core.defchararray.add(daysim_data['Date'],
                                                daysim_data['Time'])
        # Converts the string timestamps to datetime objects
        timestamps = [datetime.strptime(datetime_str[x], "%m/%d/%Y %H:%M:%S")
                      for x in range(len(datetime_str))]
        # Removes the dates/times from the data (prevents program from 
        # trying to graph the dates/times)
        daysim_data = self.remove_datetime_fields(daysim_data)
        return timestamps, daysim_data, 'txt'
        
    def read_cdf_data(self, filename):
        """Reads the data from a daysimeter cdf file
        
        filename - the string filename of the file
        
        returns an array of timestamps, a dict of daysim_data, and txt (
        the filetype)
        
        """
        # Opens and parses the cdf file 
        with pycdf.CDF(filename) as daysim_data:
            daysim_data = daysim_data.copy()
            timestamps = [daysim_data['time'][x] for x in \
                          range(len(daysim_data['time'])) if \
                          daysim_data['logicalArray'][x] == True]
            # Removes any data in the cdf related to time
            daysim_data = self.slicedict(daysim_data, 'time')
            daysim_data = self.trim_data(daysim_data)
        return timestamps, daysim_data, 'cdf'
        
    def trim_data(self, cdf_dict):
        """ Trims data using the logical array """
        omit = {'time', 'timeOffset', 'matTime', 'attrs'}
        list_dict = {}        
        
        for key in cdf_dict.keys():
            if key in omit:
                pass
            else:
                list_dict[key] = [asscalar(x) for x in cdf_dict[key]]
            
        for key in list_dict.keys():
            if key == 'logicalArray':
                pass
            else:
                list_dict[key] = [list_dict[key][x] for x in \
                                  range(len(list_dict[key])) if \
                                  list_dict['logicalArray'][x] == True]

        list_dict['attrs'] = cdf_dict['attrs']
            
        return list_dict
        
    def slicedict(self, cdf_dict, substr):
        """Removes the keys containing substr from cdf_dict
        
        cdf_dict - dict
        substr - substring to be removed
        
        returns the dict with the keys removed
        
        """
        # Saves the global attributes of the cdf
        attrs = cdf_dict.attrs
        # Removes any keys that contain the string substr
        cdf_dict = {k:v for k, v in cdf_dict.iteritems() 
                    if substr not in k.lower()}
        # Adds a key for the attributes of the cdf into the data
        cdf_dict['attrs'] = attrs
        return cdf_dict
        
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
                
    def update_check(self):
        if self.init.has_section('Version Settings'):
            if not self.init.get('Version Settings', 'show') == 'false':
                version = self.init.get('Version Settings', 'version')
                if not get_current_version(version) == version:
                    QtGui.QMessageBox.question(self, 'Message',
                                               'There is a newer version of the' + \
                                               ' daysimeter client available.', \
                                               QtGui.QMessageBox.Ok)
                                               
    def toggle_show(self):
        if self.init.has_section('Version Settings'):
            show_status = self.init.get('Version Settings', 'show')
            if show_status == 'true':
                self.init.set('Version Settings', 'show', 'false')
                self.statusBar().showMessage('Version pop-up disabled.', 2000)
                self.update_config()
            elif show_status == 'false':
                self.init.set('Version Settings', 'show', 'true')
                self.statusBar().showMessage('Version pop-up enabled.', 2000)
                self.update_config()
                
    def update_config(self):
        dir_path = os.getcwd()
        file_path = os.path.join(dir_path, 'daysimeter.ini')
        if os.path.isfile(file_path):
            init_file = open(file_path, mode='w')
            self.init.write(init_file)
            init_file.close()
        
    def update_header(self, filename):
        """Updates the header of the older daysimeter txt data files
        
        filename - the string filename of the file
        
        """
        # Opens the file and parses it
        with open(filename, 'r') as txt_file:
            lines = txt_file.readlines()
            # If Date is at the beginning of the first line, it is replaced 
            # with date and time so it can be read by read_txt
            lines[0] = sub('^Date', '#Date Time', lines[0])
            # If the line was changed,then write the file
            if lines[0]:
                open(filename, 'w').write(''.join(lines))
        
    def remove_datetime_fields(self, data_array):
        """Removes the dates/times from the daysimeter data
        
        data_array - recarray of the daysimeter data
        
        returns the daysimeter data without the date/times
        
        """
        # Makes a list of the differnent fields in the daysimeter data
        names = list(data_array.dtype.names)
        # Ignores the first 2 fields
        new_names = names[2:]
        return data_array[new_names]
        
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
            self.make_download.setEnabled(True)
            self.stop_logging.setEnabled(True)
            self.resume_logging.setEnabled(True)
            self.start_logging.setEnabled(True)
            self.reset_batt.setEnabled(True)
            self.status_light.set_green()
            if self.disconnected:
                self.time_connected = datetime.now()
                self.disconnected = False
        else:
            self.status_light.set_yellow()
            self.make_download.setEnabled(False)
            self.stop_logging.setEnabled(False)
            self.resume_logging.setEnabled(False)
            self.start_logging.setEnabled(False)
            self.reset_batt.setEnabled(False)
    
    def disable_selection(self):
        """
        Disables Daysimeter functions.
        """
        self.make_download.setEnabled(False)
        self.stop_logging.setEnabled(False)
        self.resume_logging.setEnabled(False)
        self.start_logging.setEnabled(False)
        self.reset_batt.setEnabled(False)
        self.status_light.set_red()
        self.statusBar().showMessage('No Daysimeter plugged into computer.', \
                                     500)
        self.disconnected = True
                                     
    def run(self):
        """Runs the main window"""
        self.show()
        sys.exit(QT_APP.exec_())

        
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

if __name__ == '__main__':    
    print "Running client"
    APP = LayoutExample()
    APP.run()