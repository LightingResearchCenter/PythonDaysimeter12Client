# -*- coding: utf-8 -*-
"""
Created on Wed Jun 12 15:34:13 2013

@author: pentla
"""

import sys
import PyQt4.QtGui as qt
import numpy as np
import datetime as dt
import daysimdata as dd

QT_APP = qt.QApplication(sys.argv) 
 
class LayoutExample(qt.QMainWindow):
    def __init__(self):
        qt.QMainWindow.__init__(self)
        self.setWindowTitle('Daysimeter Download Client')
        self.setMinimumSize(600, 400)
        self.main_widget = qt.QWidget(self)
        
        layout = qt.QVBoxLayout()
        form_layout = qt.QFormLayout()
        form_layout.addWidget(qt.QLabel('hi', self))
        
        self.data = dd.DaysimeterData()
        self.plot = self.data.get_plot()
        self.button_box = qt.QGroupBox('Graph Options')
        
        layout.addWidget(self.plot)
        layout.addWidget(self.button_box)
        self.main_widget.setLayout(layout)        
        
        self.setCentralWidget(self.main_widget)
        
        self.create_actions()
        self.create_menus()
        
    def create_menus(self):
        file_menu = self.menuBar().addMenu("&File")
        file_menu.addAction(self.open_act)
        
    def create_actions(self):
        self.open_act = qt.QAction("&Open...", self)
        self.open_act.setStatusTip = "Open a processed daysimeter file",
        self.open_act.triggered.connect(self.open_file)
        
    def make_buttons(self, names):
        self.button_group = qt.QButtonGroup()
        self.button_group.setExclusive(False)
        vbox = qt.QVBoxLayout()
        button_dict = {}
        for name in names:
            button_dict[name] = qt.QRadioButton(name, self.button_box)
            self.button_group.addButton(button_dict[name])
            vbox.addWidget(button_dict[name])
        self.button_box.setLayout(vbox)
        self.button_group.buttonClicked.connect(self.make_plot)
        
    def make_plot(self):
        self.data.show_plots(self.button_group)
        self.plot.draw()
        
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
        self.data.set_values(timestamps, daysim_values)
        self.make_buttons(self.data.get_data_names())
        
    def remove_datetime_fields(self, data_array):
        names = list(data_array.dtype.names)
        new_names = names[2:]
        return data_array[new_names]
    
    def run(self):
        self.show()
        sys.exit(QT_APP.exec_())

APP = LayoutExample()
APP.run()