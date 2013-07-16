# -*- coding: utf-8 -*-
"""
Created on Mon Jun 17 10:43:13 2013

@author: pentla
"""
from matplotlib.backends.backend_qt4agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
from numpy import ones
import lowpassfilter as lpf

class DaysimeterData:
    """Takes in  Daysimeter data and creates plots for that data"""
    def __init__(self): 
        """Initializes the DaysimeterData instance for plotting
        
        Initializes a figure, creates a placeholder subplot, then adds the
        figure to a canvas
        
        """
        self.fig = Figure(figsize=(600, 400), dpi=72, facecolor=(1, 1, 1), 
                          edgecolor = (0, 0, 0))    
        self.fig.add_subplot(111)
        self.values_set = False
        self.ax_dict = {}
        self.plot_tup = []
        self.timestamps = None
        self.data = None
        self.attrs = None
        self.canvas = FigureCanvas(self.fig)
        
    def show_plots(self, button_names):
        """Show the created plots
        
        button_group - Group of buttons with buttons names matching the names
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
        
    def set_values(self, timestamps, data, filetype):  
        """Set the daysimeter values from a file
        
        times - data structure of datetimes containing the timestamps of the 
                daysimeter data
        data - dict of the the different kinds of data taken in from the 
               daysimeter 
        filetype - a string that is either 'cdf' or 'txt'
        
        Sets the timestamps, the data from the daysimeter (lux, CS, etc.) then 
        smooths them out.
        
        """
        self.timestamps = timestamps
        self.data = data
        if filetype == 'cdf':
            self.attrs = data['attrs']
            del data['attrs']
        self.values_set = True
        
    def make_plots(self):
        """Create the plots from the data."""
        
        colors = ('aqua', 'black', 'fuchsia', 'gray', 'lime', 'maroon', 
                  'navy', 'olive', 'orange', 'purple', 'silver', 'teal',
                  'white', 'yellow')
        main_ax = None
        names = self.get_data_names()
        plots = []
        
        main_ax = self.fig.add_subplot(111)
        main_ax.plot(self.timestamps, 
                     ones(len(self.timestamps)), visible=False)
        main_ax.set_yticklabels([])
        # Iterates through the sets of values (lux, CS, CLA, etc.) and creates 
        # axes for them and stores the axes in a dictionary mapped with their 
        # name e.g. ax_dict['Lux'] returns the lux axis
        for name, color in zip(names, colors):
            if name in ['red', 'green', 'blue']:
                color = name
            # Makes the rest of the values 'children' of the the main, using
            # the x axis of 'main, while creating thei own y axes
            self.ax_dict[name] = main_ax.twinx()
            self.ax_dict[name].set_yscale('log')
            plots.extend(self.ax_dict[name].plot(self.timestamps,
                         self.data[name], color=color, alpha=0.8,
                         label=name))
            # Finds the min of the data, then sets that as the the lower y
            # bound of the plot to better align the graphs vertically    
            minimum = self.data[name].min()
            self.ax_dict[name].set_ybound(lower=minimum)
            self.ax_dict[name].tick_params(axis='y', colors=color)
        self.fig.legend(plots, names, loc=(.05,.03), ncol=3)
        #self.fig.autofmt_xdate(rotation=0)
        self.fig.subplots_adjust(bottom=0.2)
        self.canvas = FigureCanvas(self.fig)
        
    def smooth(self):
        """Applies a lowpass filter to smooth out the data"""
        names = self.get_data_names()
        for name in names:
            if name != 'Activity':
                self.data[name] = lpf.lowpassFilter(self.data[name], 90)
                
    def get_data_names(self):
        """Returns a list of the data names"""
        if not self.attrs:
            return list(self.data.dtype.names)
        else:
            return self.data.keys()
            
    def get_metadata(self):
        """Returns a dictionary of the cdf's attributes"""
        if self.attrs:
            return self.attrs
        else:
            return {}