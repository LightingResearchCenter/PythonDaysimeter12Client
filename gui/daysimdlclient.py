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
from numpy import genfromtxt, core
from datetime import datetime 
import graphingwidget as gw
from ConfigParser import ConfigParser
from functools import partial
from spacepy import pycdf
from re import sub
from src.downloadmake import DownloadMake
from src.logfunc import stop_log
from src.logfunc import resume_log
from src.finddaysimeter import find_daysimeter
from src.startnewlog import StartNewLog
import src.constants as constants_
from statuslight import StatusLight
from statuswidget import StatusWidget

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
        self.setWindowTitle('Daysimeter Download Client')
        self.setMinimumSize(600, 400)
        self.main_widget = gw.GraphingWidget(self)
        self.setCentralWidget(self.main_widget)
        self.init = None
        self.statusBar()
        self.make_toolbar()
#        self.create_menus()
        self.load_config()
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
        
    def go_print(self):
        printer = QtGui.QPrinter(QtGui.QPrinter.PrinterResolution)
        printer.setOrientation(QtGui.QPrinter.Landscape)
        printer.setResolution(300)
        printer.setFullPage(True)
        reply = QtGui.QPrintDialog(printer, self)
        if reply.exec_() == QtGui.QDialog.Accepted:
            painter = QtGui.QPainter(printer)
            printerWidth = printer.pageRect().width()
            printerHeight = printer.pageRect().height()
            self.print_widget = self.main_widget
            reset_size = self.main_widget.size()
            self.print_widget.resize(1200, 900)
            xscale = printerWidth  / self.print_widget.plot.width()
            yscale = printerHeight  / self.print_widget.plot.height()
            painter.scale(xscale, yscale)
            self.print_widget.plot.render(painter, QtCore.QPoint((printer.paperRect().width() - printer.pageRect().width())/4,0))
            xoff = int(printer.pageRect().width() - self.print_widget.metadata.width() * xscale)/xscale
            yoff = int(printer.pageRect().height() - self.print_widget.metadata.height() * yscale)/yscale
            self.print_widget.metadata.render(painter, QtCore.QPoint(xoff, yoff))
            painter.end()
            self.print_widget.resize(reset_size)
            
    def make_shortcuts(self):
        download_shortcut = QtGui.QShortcut(QtGui.QKeySequence('CTRL+D'),\
        self, self.download_data, self.download_data, QtCore.Qt.WidgetShortcut)
        
        open_shortcut = QtGui.QShortcut(QtGui.QKeySequence('CTRL+O'),\
        self, self.open_file, self.open_file, QtCore.Qt.WidgetShortcut)
        
        quit_shortcut = QtGui.QShortcut(QtGui.QKeySequence('CTRL+Q'),\
        self, self.close, self.close, QtCore.Qt.WidgetShortcut)
        
        print_shortcut = QtGui.QShortcut(QtGui.QKeySequence('CTRL+P'),\
        self, self.go_print, self.go_print, QtCore.Qt.WidgetShortcut)
        
        set_save_shortcut = QtGui.QShortcut(QtGui.QKeySequence('CTRL+S'),\
        self, partial(self.load_config, update='savepath'), partial(self.load_config, update='savepath'), QtCore.Qt.WidgetShortcut)
        
        new_log_shortcut = QtGui.QShortcut(QtGui.QKeySequence('CTRL+N'),\
        self, self.start_log, self.start_log, QtCore.Qt.WidgetShortcut)

        reset_batt_shortcut = QtGui.QShortcut(QtGui.QKeySequence('CTRL+R'),\
        self, self.reset_battery, self.reset_battery, QtCore.Qt.WidgetShortcut)
        
    def make_toolbar(self):
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
                                  triggered=self.download_data)
                                  
        self.stop_logging = QtGui.QAction('&Stop Current Log', self, statusTip='Stop ' + \
                                  'current log', triggered=self.stop_log)
                                  
        self.resume_logging = QtGui.QAction('&Resume Current Log', self, statusTip='Resumes ' + \
                                  'current log', triggered=self.resume_log)
                                  
        self.start_logging = QtGui.QAction('&Start New Log', self, statusTip='Starts'+\
                                   ' a new data log', triggered=self.start_log)
        
        self.reset_batt = QtGui.QAction('&Reset Logged Hours', self, statusTip='Sets'+\
                                   ' logged hours to 0', triggered=self.reset_battery)
                                   
        # Adds the options to the menu
        file_actions = [open_act, set_savepath, print_act, quit_act]
        daysimeter_actions = [self.make_download, self.start_logging, self.stop_logging, self.resume_logging, self.reset_batt]
        
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
        
        
    def load_config(self, update=None):
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
        self.init.write(init_file)
        init_file.close()

    def set_save_path(self):
        """Create a dialog to set the savepath and set it in the ini file"""
        if self.init.has_section("Application Settings"):
            dir_name = str(QtGui.QFileDialog.getExistingDirectory(self,
                       directory=self.init.get('Application Settings', 'savepath')))
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
                                  triggered=self.download_data)
                                  
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
            self.statusBar().showMessage('Logging hours reset', 2000)
    
    def start_log(self):
        self.new_log = StartNewLog()
    
    def stop_log(self):
        if stop_log():
            self.statusBar().showMessage("Current Log Stopped", 2000)
        else:
            QtGui.QMessageBox.question(self, 'Error',
                                   'No Daysimeter Found!', \
                                   QtGui.QMessageBox.Ok)
            
        
    def resume_log(self):
        duration = datetime.now() - self.time_connected
        print datetime.now(), self.time_connected, duration
        duration = duration.total_seconds()
        print duration
        total_time = ''
        
        if math.floor(duration/(24*60*60)) > 0:
            if math.floor(duration/(24*60*60)) > 1:
                total_time = total_time + str(int(math.floor(duration/(24*60*60)))) + \
                ' days'
            else:
                total_time = total_time + str(int(math.floor(duration/(24*60*60)))) + \
                ' day'
            duration = duration%(24*60*60)
            
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
            elif math.floor(duration/(60*60)) == 1 and math.floor((duration%(60*60))/60) == 1: 
                total_time = total_time + \
                str(int(math.floor(duration/(60*60)))) + ' hour and ' + \
                str(int(math.floor((duration%(60*60))/60))) + ' minute'
            elif math.floor(duration/(60*60)) == 1 and math.floor((duration%(60*60))/60) > 1: 
                total_time = total_time + \
                str(int(math.floor(duration/(60*60)))) + ' hour and ' + \
                str(int(math.floor((duration%(60*60))/60))) + ' minutes'
            elif math.floor(duration/(60*60)) > 1 and math.floor((duration%(60*60))/60) == 1: 
                total_time = total_time + \
                str(int(math.floor(duration/(60*60)))) + ' hours and ' + \
                str(int(math.floor((duration%(60*60))/60))) + ' minute'   
            else: 
                total_time = total_time + \
                str(int(math.floor(duration/(60*60)))) + ' hours and ' + \
                str(int(math.floor((duration%(60*60))/60))) + ' minutes'
        elif math.floor(duration/60) > 0:
            if math.floor(duration/60) > 1:
                total_time = total_time + str(int(math.floor(duration/60))) + ' minutes'
            else:
                total_time = total_time + str(int(math.floor(duration/60))) + ' minute'
            
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

    def download_data(self):
        """Creates a widget to download data from the Daysimeter"""
        self.download = DownloadMake()
        self.connect(self.download, QtCore.SIGNAL('savename'), self.read_data)
        
    def read_data(self, file_name):
        """Reads the data from a txt or cdf and graphs it
        
        file_name - a string of the file name
        
        """
        # Gets the file extension of the file
        ext = os.path.splitext(file_name)[-1].lower()
        # Reads the data based on the file type
        if ext == '.txt':
            self.update_header(file_name)
            timestamps, daysim_data, filetype = self.read_txt_data(file_name)
        elif ext == '.cdf':
            timestamps, daysim_data, filetype = self.read_cdf_data(file_name)
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
        file_name = str(QtGui.QFileDialog.getOpenFileName(self,
                                                       directory=def_dir,
                                                       filter="Data File (*.cdf *.txt)"))
        if not file_name:
            return
            
        self.read_data(file_name)
    
    def read_txt_data(self, file_name):
        """Reads the data from a daysimeter txt file
        
        file_name - the string filename of the file
        
        returns an array of timestamps, a recarray of daysim_data, and txt (
        the filetype)
        
        """
        # Parses the data from the file into an recarray
        daysim_data = genfromtxt(file_name, 
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
        
    def read_cdf_data(self, file_name):
        """Reads the data from a daysimeter cdf file
        
        file_name - the string filename of the file
        
        returns an array of timestamps, a dict of daysim_data, and txt (
        the filetype)
        
        """
        # Opens and parses the cdf file 
        with pycdf.CDF(file_name) as daysim_data:
            daysim_data = daysim_data.copy()
            timestamps = daysim_data['time']
            # Removes any data in the cdf related to time
            daysim_data = self.slicedict(daysim_data, 'time')
        return timestamps, daysim_data, 'cdf'
        
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
        
    def update_header(self, file_name):
        """Updates the header of the older daysimeter txt data files
        
        file_name - the string filename of the file
        
        """
        # Opens the file and parses it
        with open(file_name, 'r') as txt_file:
            lines = txt_file.readlines()
            # If Date is at the beginning of the first line, it is replaced 
            # with date and time so it can be read by read_txt
            lines[0] = sub('^Date', '#Date Time', lines[0])
            # If the line was changed,then write the file
            if lines[0]:
                open(file_name, 'w').write(''.join(lines))
        
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
        self.enabler = EnableButtons(self)
        self.enabler.connected.connect(self.enable_selection)
        self.enabler.not_connected.connect(self.disable_selection)
        self.enabler.start()
        
    def enable_selection(self):
        self.make_download.setEnabled(True)
        self.stop_logging.setEnabled(True)
        self.resume_logging.setEnabled(True)
        self.start_logging.setEnabled(True)
        self.reset_batt.setEnabled(True)
        if self.disconnected:
            self.time_connected = datetime.now()
            self.disconnected = False
    
    def disable_selection(self):
        self.make_download.setEnabled(False)
        self.stop_logging.setEnabled(False)
        self.resume_logging.setEnabled(False)
        self.start_logging.setEnabled(False)
        self.reset_batt.setEnabled(False)
        self.statusBar().showMessage('No Daysimeter plugged into computer.',\
                                     500)
        self.disconnected = True
                                     
    def run(self):
        """Runs the main window"""
        self.show()
        sys.exit(QT_APP.exec_())

        
class EnableButtons(QtCore.QThread):
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

APP = LayoutExample()
APP.run()