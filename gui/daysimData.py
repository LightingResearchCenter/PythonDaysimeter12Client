# -*- coding: utf-8 -*-
"""
Created on Mon Jun 17 10:43:13 2013

@author: pentla
"""

#import sys
#from PyQt4.QtCore import *
#from PyQt4.QtGui import *
#import matplotlib
 
from matplotlib.backends.backend_qt4agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure

class DaysimeterData:
    def __init__(self): 
        self.fig = Figure(figsize = (400, 400), dpi = 72, facecolor = (1, 1, 1), edgecolor = (0, 0, 0))    
        self.ax = self.fig.add_subplot(111)
        self.valuesSet = False
        self.ax_dict = {}
        self.canvas = FigureCanvas(self.fig)
        
    def make_plot(self, button_group):
        if self.valuesSet:
            for b in button_group.buttons():
                button_name = str(b.text())
                if b.isChecked():
                    self.ax_dict[button_name] = self.fig.add_subplot(111)
                    print self.ax_dict
                    axis = self.ax_dict[button_name]    
                    axis.set_yscale('log')
                    print self.data[button_name]
                    axis.plot(self.timestamps, self.data[button_name])
                    self.canvas = FigureCanvas(self.fig)
                elif button_name in self.ax_dict:
                    self.ax_dict[button_name].clear()
                    
    def get_plot(self):
        return self.canvas
        
    def setValues(self, times, data):     
        self.timestamps = times
        self.data = data
        self.valuesSet = True