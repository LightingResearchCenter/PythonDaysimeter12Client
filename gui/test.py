# -*- coding: utf-8 -*-
"""
Created on Wed Jun 12 15:34:13 2013

@author: pentla
"""

import sys
from PyQt4.QtCore import *
from PyQt4.QtGui import *
import numpy as np
import datetime as dt
import daysimData as dd
import functools as ft

qt_app = QApplication(sys.argv) 
 
class LayoutExample(QMainWindow):
    def __init__(self):
        QMainWindow.__init__(self)
        self.setWindowTitle('Daysimeter Download Client')
        self.setMinimumSize(600, 400)
        self.mainWidget = QWidget(self)
        
        layout = QVBoxLayout()
        formLayout = QFormLayout()
        formLayout.addWidget(QLabel('hi', self))
        
        self.data = dd.DaysimeterData()
        self.buttonBox = QGroupBox('Graph Options')
        self.createButtons()
        
        layout.addWidget(self.data)
        layout.addWidget(self.buttonBox)
        self.mainWidget.setLayout(layout)        
        
        self.setCentralWidget(self.mainWidget)
        
        self.createActions()
        self.createMenus()
        
    def createMenus(self):
        fileMenu = self.menuBar().addMenu("&File")
        fileMenu.addAction(self.openAct)
        
    def createActions(self):
        self.openAct = QAction("&Open...", self)
        self.openAct.setStatusTip = "Open a processed daysimeter file",
        self.openAct.triggered.connect(self.openFile)
        
    def createButtons(self):
        self.buttonGroup = QButtonGroup()
        self.luxButton = QRadioButton("Lux", self.buttonBox)
        self.claButton = QRadioButton("CLA", self.buttonBox)
        self.csButton = QRadioButton("CS", self.buttonBox)
        self.activityButton = QRadioButton("Activity", self.buttonBox)
        
        self.buttonGroup.addButton(self.luxButton, 0)
        self.buttonGroup.addButton(self.claButton, 1)
        self.buttonGroup.addButton(self.csButton, 2)
        self.buttonGroup.addButton(self.activityButton, 3)
        
        vbox = QVBoxLayout()        
        for i in self.buttonGroup.buttons():
            vbox.addWidget(i)
        self.buttonBox.setLayout(vbox)
        
        #self.luxButton.toggled.connect(ft.partial(self.data.graphLux, self.luxButton))
        #self.claButton.toggled.connect(ft.partial(self.data.graphCla, self.claButton))
        #self.csButton.toggled.connect(self.data.graphCs)
        #self.activityButton.toggled.connect(self.data.graphActivity)
        self.buttonGroup.buttonClicked.connect(self.plot)
        
        
    def plot(self):
        self.data.plot(self.buttonGroup)
        self.data.draw()
        
    def openFile(self):
        #fileName = str(QFileDialog.getOpenFileName(self))
        fileName = "C:\Users\pentla\Documents\GitHub\PythonDaysimeter12Client\gui\TestFile0.txt"
        daysimValues = np.genfromtxt(fileName, dtype = ('S11', 'S8', 'f8', 'f8', 'f8', 'f8'), names = True)

        daysimValues['Date'] = np.core.defchararray.add(daysimValues['Date'], ' ')
        dateTimeStr = np.core.defchararray.add(daysimValues['Date'], daysimValues['Time'])
        
        timestamps = [dt.datetime.strptime(dateTimeStr[x], "%m/%d/%Y %H:%M:%S") for x in range(len(dateTimeStr)) ]        
        self.data.setValues(timestamps, daysimValues['Lux'], daysimValues['CLA'], daysimValues['CS'], daysimValues['Activity'])
        
    
    def run(self):
        self.show()
        sys.exit(qt_app.exec_())

app = LayoutExample()
app.run()