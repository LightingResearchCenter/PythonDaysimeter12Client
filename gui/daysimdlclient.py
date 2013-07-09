# -*- coding: utf-8 -*-
"""
Created on Wed Jun 12 15:34:13 2013

@author: pentla
"""

import sys, os
sys.path.insert(0, os.pardir)
import PyQt4.QtGui as qt
from PyQt4.QtCore import SIGNAL
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
from src.startnewlog import StartNewLog

QT_APP = qt.QApplication(sys.argv) 
 
class LayoutExample(qt.QMainWindow):
    """The main window for the daysimeter download client. It opens daysimeter
    data files and displays a central widget"""
    def __init__(self):
        """Initialize the daysimeter client with a placeholder widget
        
        Creates the main window, creates the menus, and loads info from the
        ini file        
        """
        qt.QMainWindow.__init__(self)
        self.setWindowTitle('Daysimeter Download Client')
        self.setMinimumSize(600, 400)
        self.main_widget = gw.GraphingWidget(self)
        self.setCentralWidget(self.main_widget)
        self.init = None
        self.create_menus()
        self.load_config()
        
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
            init_file = open(file_path, mode='r+')
            self.init.readfp(init_file)
            init_file.seek(0)
        else:
            init_file = open(file_path, mode='w+')
            self.init.add_section("Application Settings")
            self.set_save_path()
        # Update the Application settings
        if update == 'savepath':
            self.set_save_path()
        self.init.write(init_file)
        init_file.close()

    def set_save_path(self):
        """Create a dialog to set the savepath and set it in the ini file"""
        dir_name = str(qt.QFileDialog.getExistingDirectory(self),
                       directory=self.init.get('Application Settings', 'savepath'))
        if dir_name:
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
        open_act = qt.QAction("&Open...", 
                              self,
                              statusTip="Open a processed daysimeter file",
                              shortcut=qt.QKeySequence.Open,
                              triggered=self.open_file)
        quit_act = qt.QAction("&Quit", 
                              self,
                              shortcut=qt.QKeySequence.Quit,
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
        set_savepath = qt.QAction("&Set Save Path", 
                                  self,
                                  statusTip="Set the save path for the \
                                  processed Daysimeter data file",
                                  triggered=partial(self.load_config, 
                                                    update='savepath'))
        make_download = qt.QAction("&Download Data", 
                                  self,
                                  statusTip="Set the save path for the \
                                  processed Daysimeter data file",
                                  triggered=self.download_data)
                                  
        stop_logging = qt.QAction('&Stop Current Log', self, statusTip='Stop ' + \
                                  'current log', triggered=self.stop_log)
                                  
        resume_logging = qt.QAction('&Resume Current Log', self, statusTip='Resumes ' + \
                                  'current log', triggered=self.resume_log)
                                  
        start_logging = qt.QAction('&Start New Log', self, statusTip='Starts'+\
                                   ' a new data log.', triggered=self.start_log)
        # Adds the options to the menu
        log_menu = qt.QMenu(daysim_menu)
        log_menu.setTitle('Log')
        log_list = [start_logging, stop_logging, resume_logging]
        for item in log_list:
            log_menu.addAction(item)
        actions.extend([make_download, set_savepath])
        for action in actions:
            daysim_menu.addAction(action)
        daysim_menu.addMenu(log_menu)
    
    def start_log(self):
        self.new_log = StartNewLog()
    
    def stop_log(self):
        stop_log()
        
    def resume_log(self):
        resume_log()
    
    def download_data(self):
        """Creates a widget to download data from the Daysimeter"""
        self.download = DownloadMake()
        self.connect(self.download, SIGNAL('savename'), self.read_data)
        
    def read_data(self, file_name):
        """Reads the data from a txt of cdf and graphs it
        
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
            
        # Sets the data in the graphing widget
        self.main_widget.set_data(timestamps, daysim_data, filetype)
        
    def open_file(self):
        """Opens and read a cdf or txt file and pass its data"""
        file_name = str(qt.QFileDialog.getOpenFileName(self,
                                                       directory=self.init.get('Application Settings', 'savepath'),
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
    
    def run(self):
        """Runs the main window"""
        self.show()
        sys.exit(QT_APP.exec_())

APP = LayoutExample()
APP.run()