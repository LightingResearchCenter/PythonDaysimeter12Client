# -*- coding: utf-8 -*-
"""
Created on Mon Jun 17 10:43:13 2013

@author: pentla
"""
from matplotlib.backends.backend_qt4agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
import lowpassfilter as lpf

class DaysimeterData:
    """Takes in  Daysimeter data and creates plots for that data"""
    def __init__(self): 
        """Initializes the DaysimeterData instance for plotting
        
        Initializes a figure, creates a placeholder subplot, then adds the
        figure to a canvas
        
        """
        self.fig = Figure(figsize=(400, 400), dpi=72, facecolor=(1, 1, 1), 
                          edgecolor = (0, 0, 0))    
        self.fig.add_subplot(111)
        self.values_set = False
        self.ax_dict = {}
        self.timestamps = None
        self.data = None
        self.canvas = FigureCanvas(self.fig)
        
    def show_plots(self, button_names):
        """Show the created plots
        
        Keyword arguments:
        button_group  -- Group of buttons with buttons names matching the names
                         of the data values (e.g. Lux, CS, etc.)
                            
        """
        print button_names
        # Only tries to show plots once the data and timestamps have been set
        if self.values_set:
            # Iterates through the buttons and gets their names
            # If its name is matches an axis name, show the axis, otherwise 
            # hide it
            for name in self.ax_dict:
                if name in button_names:
                    self.ax_dict[name].set_visible(True)
                else:
                    self.ax_dict[name].set_visible(False)
                    
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
        self.smooth()
        self.values_set = True
        
    def make_plots(self):
        """Create the plots on the canvas."""
        
        is_first = True
        colors = ('r', 'g', 'b', 'c', 'm', 'y', 'k')
        main_ax = None
        names = list(self.data.dtype.names)
        # Iterates through the sets of values (lux, CS, CLA, etc.) and creates 
        # axes for them and stores the axes in a dictionary mapped with their 
        # name e.g. ax_dict['Lux'] returns the lux axis
        for name, color in zip(names, colors):
            # Makes the first set of values the 'main' axis and adds to figure
            if is_first:
                self.ax_dict[name] = main_ax = self.fig.add_subplot(111)
                self.ax_dict[name].set_yscale('log')
                self.ax_dict[name].plot(self.timestamps, self.data[name], 
                                        color=color, alpha=0.8)
                is_first = False
            # Makes the rest of the values 'children' of the the main, using
            # the x axis of 'main, while creating thei own y axes
            else:
                self.ax_dict[name] = main_ax.twinx()
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
        names = list(self.data.dtype.names)
        for name in names:
            if name != 'Activity':
                
                self.data[name] = lpf.lowpassFilter(self.data[name], 90)
                
    def get_data_names(self):
        """Returns a list of the data names"""
        return list(self.data.dtype.names)