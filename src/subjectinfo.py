"""
subjectinfo
Author: Jed Kundl
Creation Date: 25.06.2013
"""

import sys
from PyQt4.QtGui import QPushButton, QHBoxLayout, QLineEdit, QWidget, \
                        QFormLayout, QApplication, QMainWindow, QComboBox
from PyQt4 import QtCore


class SubjectInfo(QWidget):
    """ 
    PURPOSE: Creates a widget for a user to enter subject information. This 
    particular file is a standalone widget, but a modified version exists in
    downloadmake.py
    """
    send_info_sig = QtCore.pyqtSignal(list)
    
    def __init__(self, args, parent=None):
        super(SubjectInfo, self).__init__(parent)
        QMainWindow.__init__(self)
        self.setWindowTitle('Enter Subject Information')
        
        self.subject_id = QLineEdit()
        self.subject_sex = QComboBox()
        self.subject_mass = QLineEdit()
        
        self.subject_id.setMaxLength(64)
        
        self.day_dob = QComboBox()
        self.month_dob = QComboBox()
        self.year_dob = QComboBox()
        
        self.day_start = QComboBox()
        self.month_start = QComboBox()
        self.year_start = QComboBox()
        self.hour_start = QComboBox()
        self.minute_start = QComboBox()
        
        self.day_end = QComboBox()
        self.month_end = QComboBox()
        self.year_end = QComboBox()
        self.hour_end = QComboBox()
        self.minute_end = QComboBox()
        
        self.subject_sex.addItems(['-', 'Male', 'Female', 'Other'])
        
        self.day_dob.addItem('-')
        self.month_dob.addItem('-')
        self.year_dob.addItem('-')
        
        self.day_dob.addItems([str(x) for x in range(1, 32)])
        self.month_dob.addItems(['January', 'February', 'March', 'April'] + \
        ['May', 'June', 'July', 'August', 'September', 'October'] + \
        ['November', 'December'])
        self.year_dob.addItems([str(x) for x in reversed(range(1900, 2021))])
        
        self.day_start.addItems([str(x) for x in range(1, 32)])
        self.month_start.addItems([str(x) for x in range(1,13)])
        self.year_start.addItems([str(x) for x in reversed(range(2013, 2021))])
        self.hour_start.addItems([str(x) for x in range(24)])
        self.minute_start.addItems([str(x) for x in range(60)])
        
        self.day_end.addItems([str(x) for x in range(1, 32)])
        self.month_end.addItems([str(x) for x in range(1,13)])
        self.year_end.addItems([str(x) for x in reversed(range(2013, 2021))])
        self.hour_end.addItems([str(x) for x in range(24)])
        self.minute_end.addItems([str(x) for x in range(60)])
        
        self.layout_dob = QHBoxLayout()
        self.layout_dob.addWidget(self.day_dob)
        self.layout_dob.addWidget(self.month_dob)
        self.layout_dob.addWidget(self.year_dob)
        
        
        self.layout_start = QHBoxLayout()
        self.layout_start.addWidget(self.day_start)
        self.layout_start.addWidget(self.month_start)
        self.layout_start.addWidget(self.year_start)
        self.layout_start.addWidget(self.hour_start)
        self.layout_start.addWidget(self.minute_start)
        
        self.layout_end = QHBoxLayout()
        self.layout_end.addWidget(self.day_end)
        self.layout_end.addWidget(self.month_end)
        self.layout_end.addWidget(self.year_end)
        self.layout_end.addWidget(self.hour_end)
        self.layout_end.addWidget(self.minute_end)
        
        self.subject_mass.setInputMask('000.000')
        self.subject_mass.setText('000.000')
        
        self.submit = QPushButton('Submit')
        self.cancel = QPushButton('Cancel')
        
        button_layout = QHBoxLayout()
        button_layout.addWidget(self.submit)
        button_layout.addWidget(self.cancel)
        
        layout = QFormLayout()
        layout.addRow('Subject ID Number', self.subject_id)
        layout.addRow('Sex', self.subject_sex)
        layout.addRow('Date of Birth', self.layout_dob)
        layout.addRow('Mass (in kg)', self.subject_mass)
        layout.addRow('Start Date (DD/MM/YYYY HH:MM)', self.layout_start)
        layout.addRow('End Date (DD/MM/YYYY HH:MM)', self.layout_end)
        layout.addRow(button_layout)
        
        self.submit.setEnabled(False)
        
        self.setLayout(layout)
        
        self.subject_id.textChanged.connect(self.enable_submit)
        self.subject_sex.currentIndexChanged.connect(self.enable_submit)
        self.day_dob.currentIndexChanged.connect(self.enable_submit)
        self.month_dob.currentIndexChanged.connect(self.enable_submit)
        self.year_dob.currentIndexChanged.connect(self.enable_submit)
        self.subject_mass.textChanged.connect(self.enable_submit)
        
        self.submit.setDefault(True)
        self.submit.pressed.connect(self.submit_info)
        self.cancel.pressed.connect(self.close)
        
        self.show()


    def submit_info(self):
        """
        PURPOSE: Submit info given my user and pass to function that saves it
        """
        sub_id = str(self.subject_id.text())
        sub_sex = str(self.subject_sex.currentText())
        sub_dob = str(self.day_dob.currentText()) + ' ' + \
            str(self.month_dob.currentText()) + ' ' + \
            str(self.year_dob.currentText())
        sub_mass = str(self.subject_mass.text())
        self.send_info_sig.emit([sub_id, sub_sex, sub_dob, sub_mass])
        self.close()
    
   
    def enable_submit(self):
        """ PURPOSE: Enables submit button once all fields are filled with
        valid info """
        if  not self.subject_id.text() == '':
            self.submit.setEnabled(True)
        else:
            self.submit.setEnabled(False)
            
    def keyPressEvent(self, qKeyEvent):
        if qKeyEvent.key() == QtCore.Qt.Key_Return and self.submit.isEnabled(): 
            self.submit_info()
        else:
            pass

def main():
    """ PURPOSE: Creates app and runs widget """
    # Create the Qt Application
    app = QApplication(sys.argv)
    # Create and show the form
    session = SubjectInfo()
    # Run the main Qt loop
    sys.exit(app.exec_())
            
if __name__ == '__main__':
    main()