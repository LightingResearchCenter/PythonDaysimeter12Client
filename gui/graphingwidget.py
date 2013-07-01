# -*- coding: utf-8 -*-
"""
Created on Tue Jun 25 16:27:54 2013

@author: pentla
"""
import PyQt4.QtGui as qt
import daysimdata as dd
from PyQt4.QtCore import Signal

class GraphingWidget(qt.QWidget):
    """A graphing widget that contains a graph and a button box with radio 
    buttons for controlling the plots shown on the graph"""
    
    def __init__(self, parent=None):
        """Creates a graphing widget with a placeholder graph and button box"""
        super(GraphingWidget, self).__init__(parent)
        self.data = dd.DaysimeterData()
        self.buttons = ButtonBox(self)
        self.plot = self.data.get_plot()
        
        self.layout = qt.QVBoxLayout()
        self.layout.addWidget(self.plot)
        self.layout.addWidget(self.buttons)
        self.setLayout(self.layout)
        
    def set_data(self, timestamps, data, filetype):
        """Sets the data from the daysimeter and creates the plot and buttons
        
        timestamps - An ndarray of date times
        data - A recarray of the data values (e.g. Lux, CS, etc.)
        
        """
        # Creates a new daysimeter data object, sets its data, and creates the
        # new plots
        self.data = dd.DaysimeterData()
        self.data.set_values(timestamps, data, filetype)
        self.data.make_plots()
        # Deletes the current plot in tht widget, sets it to the plot in the
        # new data, and adds it to this widget
        self.plot.deleteLater()
        self.plot = self.data.get_plot()
        self.layout.addWidget(self.plot)
        
        # Deletes the current set of buttons, creates a new set, and adds it to
        # this widget
        self.buttons.deleteLater()
        self.buttons = ButtonBox(self).make_buttons(self.data.get_data_names())
        self.layout.addWidget(self.buttons)
        # Shows the set of plots with their corresponding buttons checked
        self.buttons.buttonsChecked.connect(self.show_plots)
        
    def show_plots(self, names):
        """Only shows the subplots listed in names
        
        names - list of strings that represents the names of the graph values
                to show
                
        """
        self.data.show_plots(names)
        self.plot.draw()
        
class ButtonBox(qt.QGroupBox):
    """A button box that contains radio buttons created based on the data that
    will emit the list of buttons currently checked when any is pressed"""
    
    buttonsChecked = Signal(list)
    def __init__(self, parent=None):
        """Initializes the buttons box with the title 'Graph Options'"""
        super(ButtonBox, self).__init__(parent)
        self._button_group = qt.QButtonGroup()
        self.setTitle("Graph Options")
        
    def make_buttons(self, names=['Lux', 'CLA', 'CS', 'Activity']):
        """Creates buttons based on the names given
        
        names - A list of strings representing the names of the buttons that
                should be made
        
        """
        self._button_group = qt.QButtonGroup()
        self._button_group.setExclusive(False)
        vbox = qt.QVBoxLayout()
        # Creates a button for each name in the list given and adds that button
        # to the button group (container for the objects) and the button box 
        # (container for the buttons in the GUI)
        for name in names:
            button = qt.QRadioButton(name, self)
            self._button_group.addButton(button)
            vbox.addWidget(button)
        self.setLayout(vbox)
        self._button_group.buttonClicked.connect(self.get_buttons_pressed)
        return self
        
        
    def get_buttons_pressed(self):
        """Emits a list of button names that are currently checked"""
        button_names = []
        for button in self._button_group.buttons():
            if button.isChecked():
                button_names.append(str(button.text()))
        self.buttonsChecked.emit(button_names)