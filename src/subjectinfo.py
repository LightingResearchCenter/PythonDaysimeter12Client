"""
subjectinfo
Author: Jed Kundl
Creation Date: 25.06.2013
"""

import sys
from PyQt4.QtGui import QPushButton, QHBoxLayout, QLineEdit, QWidget, \
                        QFormLayout, QApplication, QMainWindow, QComboBox
from accesssubjectinfo import write_subject_info


class SubjectInfo(QWidget):
    """ PURPOSE: Creates a widget for a user to enter subject information """
    def __init__(self, parent=None):
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
        
        self.subject_sex.addItems(['-', 'Male', 'Female', 'Other'])
        
        self.day_dob.addItem('-')
        self.month_dob.addItem('-')
        self.year_dob.addItem('-')
        
        self.day_dob.addItems([str(x) for x in range(1, 32)])
        self.month_dob.addItems(['January', 'February', 'March', 'April'] + \
        ['May', 'June', 'July', 'August', 'September', 'October'] + \
        ['November', 'December'])
        self.year_dob.addItems([str(x) for x in reversed(range(1900, 2021))])
        
        self.layout_dob = QHBoxLayout()
        self.layout_dob.addWidget(self.day_dob)
        self.layout_dob.addWidget(self.month_dob)
        self.layout_dob.addWidget(self.year_dob)
        
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
        layout.addRow(button_layout)
        
        self.submit.setEnabled(False)
        
        self.setLayout(layout)
        
        self.subject_id.textChanged.connect(self.enable_submit)
        self.subject_sex.currentIndexChanged.connect(self.enable_submit)
        self.day_dob.currentIndexChanged.connect(self.enable_submit)
        self.month_dob.currentIndexChanged.connect(self.enable_submit)
        self.year_dob.currentIndexChanged.connect(self.enable_submit)
        self.subject_mass.textChanged.connect(self.enable_submit)
        
        self.submit.pressed.connect(self.submit_info)
        self.cancel.pressed.connect(self.close)

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
        write_subject_info(sub_id, sub_sex, sub_dob, sub_mass)
        self.close()
    
   
    def enable_submit(self):
        """ PURPOSE: Enables submit button once all fields are filled with
        valid info """
        if  not self.subject_id.text() == '' and \
            self.subject_sex.currentIndex() > 0 and \
            self.day_dob.currentIndex() > 0 and \
            self.month_dob.currentIndex() > 0 and \
            self.year_dob.currentIndex() > 0 and \
            float(self.subject_mass.text()) > 0.000:
            self.submit.setEnabled(True)
        else:
            self.submit.setEnabled(False)

def main():
    """ PURPOSE: Creates app and runs widget """
    # Create the Qt Application
    app = QApplication(sys.argv)
    # Create and show the form
    session = SubjectInfo()
    session.show()
    # Run the main Qt loop
    sys.exit(app.exec_())
            
if __name__ == '__main__':
    main()