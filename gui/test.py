# -*- coding: utf-8 -*-
"""
Created on Wed Jun 12 15:34:13 2013

@author: pentla
"""

import sys
import PyQt4.QtGui as qt
import numpy as np
import datetime as dt
import graphingwidget as gw

QT_APP = qt.QApplication(sys.argv) 
 
class LayoutExample(qt.QMainWindow):
    def __init__(self):
        qt.QMainWindow.__init__(self)
        self.setWindowTitle('Daysimeter Download Client')
        self.setMinimumSize(600, 400)
        self.main_widget = gw.GraphingWidget(self)
        self.setCentralWidget(self.main_widget)
        #self.create_actions()
        self.create_menus()
        
    def create_menus(self):
        file_menu = self.menuBar().addMenu("&File")
        file_actions = self.create_menu_actions()
        file_menu.addAction(file_actions)
        
    def create_menu_actions(self):
        open_act = qt.QAction("&Open...", self)
        open_act.setStatusTip = "Open a processed daysimeter file",
        open_act.triggered.connect(self.open_file)
        
        quit_act = qt.QAction("&Quit", self)
        
        return open_act
        
    def create_action(self, name, status_tip,  function)
        
    def open_file(self):
        file_name = str(qt.QFileDialog.getOpenFileName(self))
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