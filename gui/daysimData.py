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

class DaysimeterData(FigureCanvas):
    def __init__(self): 
        self.fig = Figure(figsize = (400, 400), dpi = 72, facecolor = (1, 1, 1), edgecolor = (0, 0, 0))    
        self.ax = self.fig.add_subplot(111)
        self.valuesSet = False
        self.ax_dict = dict()
        
        FigureCanvas.__init__(self, self.fig)
        
    def plot(self, button_group):
        if self.valuesSet:
            for b in button_group.buttons():
                button_name = b.text()
                if b.isChecked():
                    self.ax_dict[button_name] = self.fig.add_subplot(111)
                    print self.ax_dict
                    axis = self.ax_dict[button_name]    
                    axis.set_yscale('log')
                    axis.plot(self.dateTimes, self.lux)
                    self = FigureCanvas(self.fig)
                print self.ax_dict
                if button_name in self.ax_dict:
                    #self.ax_dict[button_name].clear()
                    print('Else')
        
        
    def graphLux(self, button):
        if (self.valuesSet):
            if (button.isChecked()):
                self.axLux = self.fig.add_subplot(111)
                self.axLux.set_yscale('log')
                self.axLux.plot(self.dateTimes, self.lux)
                self = FigureCanvas(self.fig)
            
            else:
                self.axLux.clear()
            
    def graphCla(self, button):
        if (self.valuesSet):
            if (button.isChecked()):
                self.axCla = self.fig.add_subplot(111)
                self.axCla.set_yscale('log')
                self.axCla.plot(self.dateTimes, self.cla)
                self = FigureCanvas(self.fig)
            
            else:
                self.axCla.clear()
            
    def graphCs(self, button):
        if (self.valuesSet):
            if (button.isChecked()):
                self.axCs = self.fig.add_subplot(111)
                self.axCs.set_yscale('log')
                self.axCs.plot(self.dateTimes, self.cla)
                self = FigureCanvas(self.fig)
            
            else:
                self.axCs.clear()
                
    def graphActivity(self, button):
        if (self.valuesSet):
            if (button.isChecked()):
                self.axCla = self.fig.add_subplot(111)
                self.axCla.set_yscale('log')
                self.axCla.plot(self.dateTimes, self.cla)
                self = FigureCanvas(self.fig)
            
            else:
                self.axCla.clear()
        
    def setValues(self, times, lux, cla, cs, activity):     
        self.dateTimes = times
        self.lux = lux
        self.cla = cla
        self.cs = cs
        self.activity = activity
        self.valuesSet = True