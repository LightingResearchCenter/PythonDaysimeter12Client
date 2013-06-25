"""
setdownloadflag
Author: Jed Kundl
Creation Date: 25.06.2013
INPUT: 
OUTPUT: 
"""

import sys
from PyQt4.QtGui import QPushButton, QHBoxLayout, QLineEdit, QWidget, \
                        QFormLayout, QApplication, QMainWindow, QComboBox
from accesssubjectinfo import writeSubjectInfo

class subjectInfo(QWidget):
    
    def __init__(self,parent=None):
        super(subjectInfo, self).__init__(parent)
        QMainWindow.__init__(self)
        self.setWindowTitle('Enter Subject Information')
        #self.resize(600,400)
        
        self.subjectID = QLineEdit()
        self.subjectSex = QComboBox()
        self.subjectMass = QLineEdit()
        
        self.subjectID.setMaxLength(64)
        
        self.dayDOB = QComboBox()
        self.monthDOB = QComboBox()
        self.yearDOB = QComboBox()
        
        self.subjectSex.addItems(['-','Male','Female','Other'])
        
        self.dayDOB.addItem('-')
        self.monthDOB.addItem('-')
        self.yearDOB.addItem('-')
        
        self.dayDOB.addItems([str(x) for x in range(1,32)])
        self.monthDOB.addItems(['January','February','March','April','May'] + \
        ['June','July', 'August','September','October','November','December'])
        self.yearDOB.addItems([str(x) for x in reversed(range(1900,2021))])
        
        self.layoutDOB = QHBoxLayout()
        self.layoutDOB.addWidget(self.dayDOB)
        self.layoutDOB.addWidget(self.monthDOB)
        self.layoutDOB.addWidget(self.yearDOB)
        
        self.subjectMass.setInputMask('000.000')
        self.subjectMass.setText('000.000')
        
        self.submit = QPushButton('Submit')
        self.cancel = QPushButton('Cancel')
        
        buttonLayout = QHBoxLayout()
        buttonLayout.addWidget(self.submit)
        buttonLayout.addWidget(self.cancel)
        
        layout = QFormLayout()
        layout.addRow('Subject ID Number',self.subjectID)
        layout.addRow('Sex',self.subjectSex)
        layout.addRow('Date of Birth', self.layoutDOB)
        layout.addRow('Mass (in kg)', self.subjectMass)
        layout.addRow(buttonLayout)
        
        self.submit.setEnabled(False)
        
        self.setLayout(layout)
        
        self.subjectID.textChanged.connect(self.enableSubmit)
        self.subjectSex.currentIndexChanged.connect(self.enableSubmit)
        self.dayDOB.currentIndexChanged.connect(self.enableSubmit)
        self.monthDOB.currentIndexChanged.connect(self.enableSubmit)
        self.yearDOB.currentIndexChanged.connect(self.enableSubmit)
        self.subjectMass.textChanged.connect(self.enableSubmit)
        
        self.submit.pressed.connect(self.submitInfo)
        self.cancel.pressed.connect(self.close)
        
    def submitInfo(self):
        SUB_ID = str(self.subjectID.text())
        SUB_SEX = str(self.subjectSex.currentText())
        SUB_DOB = str(self.dayDOB.currentText()) + ' ' + \
            str(self.monthDOB.currentText()) + ' ' + \
            str(self.yearDOB.currentText())
        SUB_MASS = str(self.subjectMass.text())
        writeSubjectInfo(SUB_ID, SUB_SEX, SUB_DOB, SUB_MASS)
        self.close()
        
    def enableSubmit(self):
        if  not self.subjectID.text() == '' and \
            self.subjectSex.currentIndex() > 0 and \
            self.dayDOB.currentIndex() > 0 and \
            self.monthDOB.currentIndex() > 0 and \
            self.yearDOB.currentIndex() > 0 and \
            float(self.subjectMass.text()) > 0.000:
                self.submit.setEnabled(True)
        else:
            self.submit.setEnabled(False)

def main():
    # Create the Qt Application
    app = QApplication(sys.argv)
    # Create and show the form
    session = subjectInfo()
    session.show()
    # Run the main Qt loop
    sys.exit(app.exec_())
            
if __name__ == '__main__':main()