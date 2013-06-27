"""
downloadmake
Author: Jed Kundl
Creation Date: 26.06.2013
"""
import sys
import os
from PyQt4.QtGui import QMessageBox, QMainWindow, QApplication, QFileDialog
from updateheader import update_header
from convertheader import convert_header_f1
from makecdf import make_cdf
from finddaysimeter import find_daysimeter

class DownloadMake(QMainWindow):
    """ PURPOSE: Wrapper that calls download, process, and write functions. """
    def __init__(self):
        super(DownloadMake, self).__init__()
        QMainWindow.__init__(self)
        
        if not find_daysimeter():
            NoDaysimeter(self).exec_()
            self.close()
            
        else:
            if update_header():
                if UpdateHeader(self).exec_() == QMessageBox.YesRole:
                    convert_header_f1()
            
            filename = str(QFileDialog.getSaveFileName(self, \
            ("Save CDF"), "./", ("CDF Files (*.cdf)")))
            if os.path.isfile(filename):
                os.remove(filename)
            
            if make_cdf(filename):
                DownloadComplete(self).exec_()
            else:
                DownloadError(self).exec_()

class UpdateHeader(QMessageBox):
    """ PURPOSE: Ask if user wants to update out of date header. """
    def __init__(self, parent):
        super(UpdateHeader, self).__init__(parent)
        self.setWindowTitle('Update Header')
        
        self.setText('Your Daysimeter\'s header is out of date.')
        self.setInformativeText('Would you like to update it now?')
        
        self.addButton('No', QMessageBox.NoRole)
        self.addButton('Yes', QMessageBox.YesRole)
        
class DownloadComplete(QMessageBox):
    """ PURPOSE: Success message if everything goes okay. """
    def __init__(self, parent):
        super(DownloadComplete, self).__init__(parent)
        self.setWindowTitle('Success!')
        self.setText('Download Complete.')
        
class DownloadError(QMessageBox):
    """ PURPOSE: Failure message if things don't work. """
    def __init__(self, parent):
        super(DownloadError, self).__init__(parent)
        self.setWindowTitle('Error')
        self.setText('Download Failed.')
        
class NoDaysimeter(QMessageBox):
    """ PURPOSE: Failure message if things don't work. """
    def __init__(self, parent):
        super(NoDaysimeter, self).__init__(parent)
        self.setWindowTitle('Error')
        self.setText('There is no Daysimeter plugged into this computer.')
        
        
def main():
    """ PURPOSE: Creates app and runs widget """
    # Create the Qt Application
    app = QApplication(sys.argv)
    app.setApplicationName('Daysimeter Downloader')
    # Create and show the form
    DownloadMake()
    # Run the main Qt loop
    sys.exit(app.exec_())
            
if __name__ == '__main__':
    main()