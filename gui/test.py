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
import ConfigParser

QT_APP = qt.QApplication(sys.argv) 
 
class LayoutExample(qt.QMainWindow):
    def __init__(self):
        qt.QMainWindow.__init__(self)
        self.setWindowTitle('Daysimeter Download Client')
        self.setMinimumSize(600, 400)
        self.main_widget = gw.GraphingWidget(self)
        self.setCentralWidget(self.main_widget)
        
        self.create_menus()
        
    def load_config(self):
        dir_path = os.getcwd()
        file_path = os.path.join(dir_path, 'daysim.ini')
        
        
    def create_menus(self):
        self.create_file_menu()
        self.create_daysimeter_menu()
        
    def create_file_menu(self):
        file_menu = self.menuBar().addMenu('&File')
        actions = []
        open_act = self.create_action("&Open...", 
                                      self.open_file,
                                      statustip="Open a processed daysimeter file",
                                      shortcut=qt.QKeySequence.Open)
        
        quit_act = self.create_action("&Quit",
                                      sys.exit,
                                      shortcut=qt.QKeySequence.Quit)
        actions.extend([open_act, quit_act])
        for action in actions:
            file_menu.addAction(action)
            
    def create_daysimeter_menu(self):
        daysim_menu = self.menuBar().addMenu('&Daysim')
        actions = []
        #actions = self.create_action("&Set save path")
        
    def create_action(self, name, function, statustip=None,
                      shortcut=None):
        """Convenience function for creating new actions"""
        action = qt.QAction(name, self)
        if statustip:
            action.setStatusTip(statustip)
        if shortcut:
            action.setShortcut(shortcut)
        action.triggered.connect(function)
        return action
        
        
    def open_file(self):
        file_name = str(qt.QFileDialog.getOpenFileName(self))
        if not file_name:
            return
        #file_name = "C:\Users\pentla\Documents\GitHub\PythonDaysimeter12Client\gui\TestFile0.txt"
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
        self.main_widget.set_data(timestamps, daysim_values)
        
    def remove_datetime_fields(self, data_array):
        names = list(data_array.dtype.names)
        new_names = names[2:]
        return data_array[new_names]
    
    def run(self):
        self.show()
        sys.exit(QT_APP.exec_())

APP = LayoutExample()
APP.run()