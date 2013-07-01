# -*- coding: utf-8 -*-
"""
Created on Wed Jun 12 15:34:13 2013

@author: pentla
"""

import sys, os
import PyQt4.QtGui as qt
import numpy as np
import datetime as dt
import graphingwidget as gw
from ConfigParser import ConfigParser
from subjectinfo import SubjectInfo
from functools import partial
from spacepy import pycdf
from re import sub, search

QT_APP = qt.QApplication(sys.argv) 
 
class LayoutExample(qt.QMainWindow):
    def __init__(self):
        qt.QMainWindow.__init__(self)
        self.setWindowTitle('Daysimeter Download Client')
        self.setMinimumSize(600, 400)
        self.main_widget = gw.GraphingWidget(self)
        self.setCentralWidget(self.main_widget)
        self.init = None
        self.create_menus()
        self.load_config()
        
    def load_config(self, update=None):
        dir_path = os.getcwd()
        file_path = os.path.join(dir_path, 'daysimeter.ini')
        w_init_file = open(file_path, mode='r+')
        r_init_file = open(file_path, mode='r')
        self.init = ConfigParser()
        self.init.readfp(r_init_file)
        if not self.init.sections():
            print(self.init.sections())
            self.init.add_section("Application Settings")
            self.set_sub_info()
            self.set_save_path()
        elif update == 'Application Settings':
            self.set_save_path() 
        self.init.write(w_init_file)
        w_init_file.close()
        r_init_file.close()

    def set_save_path(self):
        dir_name = str(qt.QFileDialog.getExistingDirectory(self))
        self.init.set("Application Settings", 'savepath', dir_name)
        gw.ButtonBox().make_buttons(self.main_widget.get_)
        
    def set_sub_info(self):
        info = SubjectInfo(self)
        if info.exec_():
            self.init = info.get_info(self.init)            
        
    def create_menus(self):
        self.create_file_menu()
        self.create_daysimeter_menu()
        
    def create_file_menu(self):
        file_menu = self.menuBar().addMenu('&File')
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
        actions.extend([open_act, quit_act])
        for action in actions:
            file_menu.addAction(action)
            
    def create_daysimeter_menu(self):
        daysim_menu = self.menuBar().addMenu('&Daysim')
        actions = []
        set_sub_info = qt.QAction("&Set subject info", 
                                  self,
                                  triggered=partial(self.load_config, 
                                                    update='Subject Info'))
        set_savepath = qt.QAction("&Set save path", 
                                  self,
                                  statusTip="Set the save path for the \
                                  processed Daysimeter data file",
                                  triggered=partial(self.load_config, 
                                                    update='savepath'))
        actions.extend([set_sub_info, set_savepath])
        for action in actions:
            daysim_menu.addAction(action)
        
    def open_file(self):
        file_name = str(qt.QFileDialog.getOpenFileName(self, 
                                                       filter="Data File (*.cdf *.txt)"))
        if not file_name:
            return
        
        ext = os.path.splitext(file_name)[-1].lower()
        if ext == '.txt':
            self.update_header(file_name)
            timestamps, daysim_values, filetype = self.read_txt_data(file_name)
        else:
            timestamps, daysim_values, filetype = self.read_cdf_data(file_name)
        self.main_widget.set_data(timestamps, daysim_values, filetype)
    
    def read_txt_data(self, file_name):
        daysim_values = np.genfromtxt(file_name, 
                                     dtype=['S11', 'S8', 'f8', 'f8', 'f8', 'f8'],
                                     names=True)

        daysim_values['Date'] = np.core.defchararray.add(daysim_values['Date'], 
                                                         ' ')
        datetime_str = np.core.defchararray.add(daysim_values['Date'],
                                                daysim_values['Time'])
        timestamps = [dt.datetime.strptime(datetime_str[x], "%m/%d/%Y %H:%M:%S")
                      for x in range(len(datetime_str))]
        daysim_values = self.remove_datetime_fields(daysim_values)
        return timestamps, daysim_values, 'txt'
        
    def read_cdf_data(self, file_name):
        with pycdf.CDF(file_name) as data_cdf:
            data_cdf = data_cdf.copy()
            time = data_cdf['time']
            data_cdf = self.slicedict(data_cdf, 'time')
        return time, data_cdf, 'cdf'
        #graphing_options = gw.ButtonBox().make_buttons()
       # self.init.set("Application Settings", 'graphvars', dir_name)
        
    def slicedict(self, d, s):
        return {k:v for k,v in d.iteritems() if s not in k.lower()}
        
    def update_header(self, file_name):
        with open(file_name, 'r') as f:
            lines = f.readlines()
            lines[0] = sub('^Date', '#Date Time', lines[0])
            if lines[0]:
                print "New header" + lines[0]
                open(file_name, 'w').write(''.join(lines))
        
    def remove_datetime_fields(self, data_array):
        names = list(data_array.dtype.names)
        new_names = names[2:]
        return data_array[new_names]
    
    def run(self):
        self.show()
        sys.exit(QT_APP.exec_())

APP = LayoutExample()
APP.run()