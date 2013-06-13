# -*- coding: utf-8 -*-
"""
Created on Wed Jun 12 15:34:13 2013

@author: pentla
"""

import sys
from PySide.QtCore import *
from PySide.QtGui import *
from numpy import loadtxt

qt_app = QApplication(sys.argv)
 
class LayoutExample(QMainWindow):
    def __init__(self):
        QMainWindow.__init__(self)
        self.setWindowTitle('Daysimeter Download Client')
        self.setMinimumSize(600, 400)
        mainWidget = QWidget()
        self.setCentralWidget(mainWidget)
        
        self.createActions()
        self.createMenus()
        
    def createMenus(self):
        fileMenu = self.menuBar().addMenu("&File")
        fileMenu.addAction(self.openAct)
        
    def createActions(self):
        self.openAct = QAction("&Open...", self)
        self.openAct.setStatusTip = "Open a processed daysimeter file",
        self.openAct.triggered.connect(self.openFile)
        
    def openFile(self):
        fileName = QFileDialog.getOpenFileName(self)
        self.values = loadtxt(filename, skiprows = 1)
    
    def run(self):
        self.show()
        qt_app.exec_()

app = LayoutExample()
app.run()