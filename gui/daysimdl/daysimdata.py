# -*- coding: utf-8 -*-
"""
Created on Mon Jun 17 10:43:13 2013

@author: pentla
"""

from matplotlib.backends.backend_qt4agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
import lowpassfilter as lpf

class DaysimeterData:
    def __init__(self): 
        """Creates the daysim"""
        self.fig = Figure(figsize=(400, 400), dpi=72, facecolor=(1, 1, 1), 
                          edgecolor = (0, 0, 0))    
        self.ax = self.fig.add_subplot(111)
        self.values_set = False
        self.ax_dict = {}
        self.canvas = FigureCanvas(self.fig)
        
    def show_plots(self, button_group):
        if self.values_set:
            for button in button_group.buttons():
                button_name = str(button.text())
                if button.isChecked():
                    print "Show" + button_name
                    self.ax_dict[button_name].set_visible(True)
                else:
                    print "Hide" + button_name
                    self.ax_dict[button_name].set_visible(False)
                    
    def get_plot(self):
        """Return the canvas for drawing"""
        return self.canvas
        
    def set_values(self, times, data):  
        """Set the daysimeter values from a file
        
        Sets the timestamps and data of the object(lux, CS, etc.) then smooths
        them out.
        
        """
        self.timestamps = times
        self.data = data
        self.names = list(self.data.dtype.names)
        self.smooth()
        self.make_plots()
        self.values_set = True
        
    def make_plots(self):
        """Create the plots on the canvas."""
        
        is_first = True
        colors = ('r', 'g', 'b', 'c', 'm', 'y', 'k')
        # Iterates through the sets of values (lux, CS, CLA, etc.) and creates 
        # axes for them and stores the axes in a dictionary mapped with their 
        # name e.g. ax_dict['Lux'] returns the lux axis
        for name, color in zip(self.names, colors):
            # Makes the first set of values the 'main' axis and adds to figure
            if is_first:
                self.ax_dict[name] = self.ax = self.fig.add_subplot(111)
                self.ax_dict[name].set_yscale('log')
                self.ax_dict[name].plot(self.timestamps, self.data[name], 
                                        color=color, alpha=0.8)
                is_first = False
            # Makes the rest of the values 'children' of the the main, using
            # the x axis of 'main, while creating thei own y axes
            else:
                self.ax_dict[name] = self.ax.twinx()
                self.ax_dict[name].set_yscale('log')
                self.ax_dict[name].plot(self.timestamps, self.data[name], 
                                        color=color, alpha=0.8)
                # Finds the min of the data, then sets that as the the lower y
                # bound of the plot to better align the graphs vertically                
                minimum = self.data[name].min()
                self.ax_dict[name].set_ybound(lower=minimum)
                self.ax_dict[name].tick_params(axis='y', colors=color)
        self.canvas = FigureCanvas(self.fig)
        self.fig.autofmt_xdate()
        
    def smooth(self):
        """Applies a lowpass filter to smooth out the data"""
        for name in self.names:
            if name != 'Activity':
                self.data[name] = lpf.lowpassFilter(self.data[name], 90)