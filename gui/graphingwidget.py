# -*- coding: utf-8 -*-
"""
Created on Tue Jun 25 16:27:54 2013

@author: pentla
"""
import PyQt4.QtGui as qt
from PyQt4 import QtGui
import daysimdata as dd
from PyQt4.QtCore import Signal
import string

class GraphingWidget(qt.QWidget):
    """A graphing widget that contains a graph and a button box with radio 
    buttons for controlling the plots shown on the graph"""
    
    def __init__(self, parent=None):
        """Creates a graphing widget with a placeholder graph and button box"""
        super(GraphingWidget, self).__init__(parent)
        self.data = dd.DaysimeterData()
        self.buttons = ButtonBox(self)
        self.plot = self.data.get_plot()
        self.metadata = DisplayMetadata(self)
        
        self.sel_all = QtGui.QPushButton('Select All')
        self.sel_none = QtGui.QPushButton('Deselect All')
        
        self.sel_all.pressed.connect(self.select_all)
        self.sel_none.pressed.connect(self.deselect_all)
        
        self.hbox = qt.QHBoxLayout()
        self.hbox.addWidget(self.buttons)
        self.hbox.addWidget(self.metadata)
        self.layout = qt.QVBoxLayout()
        self.layout.addWidget(self.plot)
        self.layout.addLayout(self.hbox)
        self.setLayout(self.layout)
        
    def select_all(self):
        for button in self.buttons._button_group.buttons():
            button.setChecked(True)
        self.buttons.get_buttons_pressed()
        
    def deselect_all(self):
        for button in self.buttons._button_group.buttons():
            button.setChecked(False)
        self.buttons.get_buttons_pressed()
        
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
        # new data, and adds it to this widgetself.buttons
        self.plot.deleteLater()
        self.plot = self.data.get_plot()
        self.layout.addWidget(self.plot)
        
        #Clear the horizontal layout for use
        self.hbox.deleteLater()
        self.hbox = qt.QHBoxLayout()
        
        # Deletes the current set of buttons, creates a new set, and adds it to
        # this widget
        self.buttons.deleteLater()
        self.buttons = ButtonBox(self).make_buttons(self.data.get_data_names())
        
        not_a_button_layout = qt.QHBoxLayout()
        not_a_button_layout.addWidget(self.sel_all)
        not_a_button_layout.addWidget(self.sel_none)
        
        radio_layout = QtGui.QVBoxLayout()
        radio_layout.addWidget(self.buttons)
        radio_layout.addLayout(not_a_button_layout)
        
        self.hbox.addLayout(radio_layout)
        
        # Deletes the current set of metadata, creates a new set, and adds it
        # to this widget
        self.metadata.deleteLater()
        metadata = self.data.get_metadata()
        self.metadata = DisplayMetadata(self).set_metadata(metadata)
        self.hbox.addWidget(self.metadata)
        
        self.layout.addLayout(self.hbox)
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
        """Creates buttons based on the names given and returns itself
        
        names - A list of strings representing the names of the buttons that
                should be made
        
        """
        ordered_names = []
        lower_names = []
        if 'red' in names:
            ordered_names.append('red')
        if 'green' in names:
            ordered_names.append('green')
        if 'blue' in names:
            ordered_names.append('blue')
        if 'Lux' in names:
            ordered_names.append('lux')
        if 'CLA' in names:
            ordered_names.append('CLA')
        if 'CS' in names:
            ordered_names.append('CS')
        if 'activity' in names:
            ordered_names.append('activity')
        names.sort()
        for name in ordered_names:
            lower_names.append(string.lower(name))
        for name in names:
            if string.lower(name) not in lower_names:
                ordered_names.append(name)

        self._button_group = qt.QButtonGroup()
        self._button_group.setExclusive(False)
        grid = qt.QGridLayout()
        # Creates a button for each name in the list given and adds that button
        # to the button group (container for the objects) and the button box 
        # (container for the buttons in the GUI)
        col = row = 0
        for name in ordered_names:
            button = qt.QRadioButton(name, self)
            self._button_group.addButton(button)
            # Only put 5 buttons per row, then make a new column
            if row >= 5:
                col += 1
                row = 0
            grid.addWidget(button, row, col)
            row += 1
        self.setLayout(grid)
        self._button_group.buttonClicked.connect(self.get_buttons_pressed)
        return self
        
        
    def get_buttons_pressed(self):
        """Emits a list of button names that are currently checked"""
        button_names = []
        for button in self._button_group.buttons():
            if button.isChecked():
                button_names.append(str(button.text()))
        self.buttonsChecked.emit(button_names)
        
class DisplayMetadata(qt.QWidget):
    """A widget that displays the different metadata"""
    
    def __init__(self, parent=None):
        """Initializes the widget with a grid layout"""
        super(DisplayMetadata, self).__init__(parent)
        self.grid = qt.QGridLayout()
        
    def set_metadata(self, metadata):
        """Sets the text contained in the widget to the given metadata
        
        metadata - a dict of the different pieces of metadata
        
        """
        # Creates a text label for each key in the given dict. After there are
        # 5 items in a row, it starts a new column
        row = col = 0
        for title in metadata.keys():
            text = '<b>' +  title + '</b>' + '- ' + str(metadata[title][0])
            q_text = qt.QLabel(text, self)
            self.grid.addWidget(q_text, row, col)
            row += 1
            if row >= 5:
                col += 1
                row = 0
        self.setLayout(self.grid)
        return self