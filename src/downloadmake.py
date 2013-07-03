"""
downloadmake
Author: Jed Kundl
Creation Date: 28.06.2013
"""

import os
import sys
import struct
import logging
import time
import math
from ConfigParser import SafeConfigParser
from datetime import datetime
from datetime import timedelta
from geterrlog import get_err_log
from adjactiveflag import adj_active_flag
from getcalibinfo import get_calib_info
from processconstants import process_constants
from lowpassfilter import lowpass_filter
from calccs import calc_cs
from finddaysimeter import find_daysimeter
from datetimetodatenum import dt2dn
from getconstants import get_constants
import constants as constants_
from spacepy import pycdf
from getlocaloffset import get_local_offset_s
from setdownloadflag import set_download_flag
from accesssubjectinfo import read_subject_info
from updateheader import update_header
from convertheader import convert_header_f1
from PyQt4 import QtGui, QtCore
    
class DownloadMake(QtGui.QWidget):
    """
    PURPOSE: Widget that manages downloading daysimeter data and making CDF 
    or CSV files. 
    """
    def __init__(self, parent=None):
        super(DownloadMake, self).__init__(parent)
        self.initUI()
        
    def initUI(self):
        """ PURPOSE: Initialize the GUI """
        self.setFixedSize(500, 100)
        self.pbar = QtGui.QProgressBar(self)
        
        self.start = QtGui.QPushButton('Start Download')
        self.done = QtGui.QPushButton('Done')
        self.start.pressed.connect(self.start_download)
        self.done.pressed.connect(self.close)

        self.status_bar = QtGui.QStatusBar()      
        
        layout = QtGui.QVBoxLayout()
        layout.addWidget(self.pbar)
        layout.addWidget(self.start)
        layout.addWidget(self.done)
        layout.addWidget(self.status_bar)
        self.setLayout(layout)
        
        self.setWindowTitle('Datsimeter Downloader')
        self.step = 0.0
        self.pbar.setValue(self.step)
        self.pbar.hide()
        self.done.hide()        
        self.show()
        
        self.parser = SafeConfigParser()
        if not self.parser.read('daysimeter.ini') == []:
            self.savedir = self.parser.get('Application Settings', 'savepath')
        else:
            self.savedir = os.getcwd()
        self.emit(QtCore.SIGNAL('savename'), self.savedir)
        
    def start_download(self):
        """ PURPOSE: Starts and manages download of data """
        if not find_daysimeter():
            self.status_bar.showMessage('No Daysimeter plugged into this' + \
            ' computer.')
        else:
            self.status_bar.showMessage('')
            self.filename = str(QtGui.QFileDialog.getSaveFileName(self, \
            ('Save File'), self.savedir, ('CDF Files (*.cdf);; CSV Files (*.csv)')))
            if not str(self.filename) == '':
                self.pbar.show()
                self.start.setText('Downloading...')
                self.status_bar.showMessage('Processing Data...')
                self.start.setEnabled(False)
                self.downloader = DownloadDaysimeter(self)
                self.connect(self.downloader, QtCore.SIGNAL('update'), \
                self.update_progress)
                self.connect(self.downloader, QtCore.SIGNAL('make'), \
                self.make)
                self.downloader.start()
        
    def make(self, data):
        """
        PURPOSE: Determines filetype to be written, creates maker thread
        that actually writes data to file.
        """
        if self.filename[len(self.filename)-4:] == '.cdf':
            self.subjectinfo = SubjectInfo()
            self.connect(self.subjectinfo, QtCore.SIGNAL('sendinfo'), \
            self.make_cdf)
            self.connect(self.subjectinfo, QtCore.SIGNAL('cancelled'), \
            self.cancelled)
            self.data = data
        else:
            self.status_bar.showMessage('Writing CSV File...')
            self.maker = MakeCSV(self, data, self.filename)
            self.connect(self.maker, QtCore.SIGNAL('update'), \
            self.update_progress)
            self.maker.start()
            
    def make_cdf(self, info):
        """ PURPOSE: Makes a CDF file. """
        self.status_bar.showMessage('Writing CDF File...')
        self.maker = MakeCDF(self, self.data, self.filename, info)
        self.connect(self.maker, QtCore.SIGNAL('update'), self.update_progress)
        self.maker.start()
        
    def cancelled(self):
        """
        PURPOSE: Determines whether the download has been cancelled, this
        usually occurs when no subject info was given.
        """
        #As a side note, the ceiling started leaking again...
        self.pbar.hide()
        self.done.setText('Download Cancelled')
        self.start.hide()
        self.done.show()
        self.status_bar.showMessage('No Subject information was entered. ' + \
        'Download cancelled.')
        
    def update_progress(self):
        """ PURPOSE: Updates progress bar when given signal to do so. """
        #it kind fakes it until it makes it
        self.step += 1
        self.pbar.setValue(self.step)
        if self.step == 100:
            if update_header():
                reply = QtGui.QMessageBox.question(self, 'Message',
            'Your daysimeter\'s header is out of date.\n' + \
            'Would you like to update it now?', QtGui.QMessageBox.Yes, \
            QtGui.QMessageBox.No)

                if reply == QtGui.QMessageBox.Yes:
                    convert_header_f1()
                else:
                    self.download_done()
            else:
                self.download_done()
        
    def download_done(self):
        """ PURPOSE: Displays done message when download is complete """
        self.status_bar.showMessage('Download Complete. It is now safe ' + \
        'to eject your daysimeter.')
        self.start.hide()
        self.done.show()
        
class SubjectInfo(QtGui.QWidget):
    """ PURPOSE: Creates a widget for a user to enter subject information """
    send_info_sig = QtCore.pyqtSignal(list)
    def __init__(self, parent=None):
        super(SubjectInfo, self).__init__(parent)
        self.setWindowTitle('Enter Subject Information')
        self.setFixedSize(300, 160)
        self.subject_id = QtGui.QLineEdit()
        self.subject_sex = QtGui.QComboBox()
        self.subject_mass = QtGui.QLineEdit()
        
        self.subject_id.setMaxLength(64)
        
        self.day_dob = QtGui.QComboBox()
        self.month_dob = QtGui.QComboBox()
        self.year_dob = QtGui.QComboBox()
        
        self.subject_sex.addItems(['-', 'Male', 'Female', 'Other'])
        
        self.day_dob.addItem('-')
        self.month_dob.addItem('-')
        self.year_dob.addItem('-')
        
        self.day_dob.addItems([str(x) for x in range(1, 32)])
        self.month_dob.addItems(['January', 'February', 'March', 'April'] + \
        ['May', 'June', 'July', 'August', 'September', 'October'] + \
        ['November', 'December'])
        self.year_dob.addItems([str(x) for x in reversed(range(1900, 2021))])
        
        self.layout_dob = QtGui.QHBoxLayout()
        self.layout_dob.addWidget(self.day_dob)
        self.layout_dob.addWidget(self.month_dob)
        self.layout_dob.addWidget(self.year_dob)
        
        self.subject_mass.setInputMask('000.000')
        self.subject_mass.setText('000.000')
        
        self.submit = QtGui.QPushButton('Submit')
        self.cancel = QtGui.QPushButton('Cancel')
        
        button_layout = QtGui.QHBoxLayout()
        button_layout.addWidget(self.submit)
        button_layout.addWidget(self.cancel)
        
        layout = QtGui.QFormLayout()
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
        self.cancel.pressed.connect(self.closeself)
        self.success = False
        
        self.show()
    
    def closeEvent(self, event):
        """ PURPOSE: Catches the close event, check to see if it is a 
        successful close, or an aborted close and takes appropriate action.
        """
        if self.success:
            event.accept()
        else:
            self.emit(QtCore.SIGNAL('cancelled'))
            event.accept()
            
    def closeself(self):
        """ PURPOSE: Signals that there was an unsuccessful close event. """
        self.emit(QtCore.SIGNAL('cancelled'))
        self.close()
        
    def submit_info(self):
        """
        PURPOSE: Take user given infomation and pass it back to the main widget
        to be sent to a file maker thread.
        """
        sub_id = str(self.subject_id.text())
        sub_sex = str(self.subject_sex.currentText())
        sub_dob = str(self.day_dob.currentText()) + ' ' + \
            str(self.month_dob.currentText()) + ' ' + \
            str(self.year_dob.currentText())
        sub_mass = str(self.subject_mass.text())
        self.success = True
        self.emit(QtCore.SIGNAL('sendinfo'), [sub_id, sub_sex, sub_dob, \
        sub_mass])
        self.close()
    
   
    def enable_submit(self):
        """
        PURPOSE: Enables submit button once all fields are filled with
        valid info.
        """
        if  not self.subject_id.text() == '' and \
            self.subject_sex.currentIndex() > 0 and \
            self.day_dob.currentIndex() > 0 and \
            self.month_dob.currentIndex() > 0 and \
            self.year_dob.currentIndex() > 0 and \
            float(self.subject_mass.text()) > 0.000:
            self.submit.setEnabled(True)
        else:
            self.submit.setEnabled(False)

        
class DownloadDaysimeter(QtCore.QThread):
    
    def __init__(self, parent):
        QtCore.QThread.__init__(self, parent)
        
    def run(self):
        """
        PURPOSE: Reads raw binary data, processed and packages it.
        """

        log_filename = constants_.LOG_FILENAME
        data_filename = constants_.DATA_FILENAME
        adj_active_flag_ = constants_.ADJ_ACTIVE_FLAG
        old_flag = constants_.OLD_FLAG
        adj_active_firm = constants_.ADJ_ACTIVE_FIRM
        #Create error log file named error.log on the desktop
        errlog_filename = get_err_log()
        if errlog_filename == '':
            sys.exit(1)
        logging.basicConfig(filename=errlog_filename, level=logging.DEBUG)
        
        path = find_daysimeter()
        #Open header file for reading
        try:
            logfile_fp = open(path + log_filename,'r')
        #Catch IO exception (if present), add to log and quit
        except IOError:
            logging.error('Could not open logfile')
            sys.exit(1)
        else:
            #Read each line of the header and put it into a list
            #called info.
            #info[0] is status, info[1] is device ID, et cetera
            info = [x.strip('\n') for x in logfile_fp.readlines()]        
        #Close the logfile
        finally:
            logfile_fp.close()
        
        #If we are using an old format, set flag to True
        if len(info) > 17:
            old_flag = False
        
        #Find the daysimeter device ID
        if old_flag:
            daysimeter_id = int(info[1])
            device_model = constants_.DEVICE_MODEL
            device_sn = constants_.DEVICE_VERSION + info[1]
        else:
            daysimeter_id = int(info[3])
            device_model = info[2]
            device_sn = info[2].lstrip('abcdefghijklmnopqrstuvwxyz') + info[3]
        
        #Get calibration info
        if not old_flag:
            calib_const = [float(x) for x in info[9].strip('\n').split('\t')]
            calib_info = \
            [daysimeter_id, calib_const[0], calib_const[1], calib_const[2]]
        else:
            calib_info = get_calib_info(daysimeter_id)
            
        #Open binary data file for reading
        try:
            datafile_fp = open(path + data_filename,'rb')
        #Catch IO exception (if present), add to log and quit
        except IOError:
            logging.error('Could not open datafile')
            sys.exit(1)
        else:
            #Read entire file into a string called data
            data = datafile_fp.read()
        #Close the datafile
        finally:
            datafile_fp.close()
    
    #####It is assumed that time is formatted correctly, if not this
        #part of the code will not work. Time format is as follows:
        #mm-dd-yy HH:MM
    
        #Converts a time string into a float representing seconds
        #since epoch (UNIX)
        if not old_flag:
            struct_time = time.strptime(info[4], "%m-%d-%y %H:%M")
        else:
            struct_time = time.strptime(info[2], "%m-%d-%y %H:%M")
        epoch_time = datetime.fromtimestamp(time.mktime(struct_time))
        #log_interval is interval that the Daysimeter took measurements at.
        #Since python uses seconds since epoch, cast as int
        if not old_flag:
            log_interval = int(info[5])
        else:
            log_interval = int(info[3])
        
        #Determine the number of of logged entries. Why divded by 8?
        #I'm glad you asked! There are 4 things that are logged, and
        #each item takes up 2 bytes. So, we take the total number of
        #bytes (len(data)) and dived by 2*4. It makes so much sense!
        #I will admit, I only figure that out during debugging...
        num_entries = int(math.floor(len(data)/8))
        #Create lists for raw Red, Green, Blue, and Activity
        red = [-1] * num_entries
        green = [-1] * num_entries
        blue = [-1] * num_entries
        activity = [-1] * num_entries
        #Iteratively seperate data into raw R,G,B,A
        #struct.unpack unpacks binary data given a format.
        #>H is an unsigned short (16 bit unsigned integer) in big
        #endian notation.
        for x in range(0, num_entries):
            #If value is 65278 the daysimeter reset, skip and leave
            #the value at -1
            if struct.unpack('>H', data[x*8:x*8+2])[0] == 65278:
                continue
            #If value is 65535 there are no more entires to be
            #read. Remove 'empty' entries and break
            elif struct.unpack('>H', data[x*8:x*8+2])[0] == 65535:
                del red[x:]
                del green[x:]
                del blue[x:]
                del activity[x:]
                break
            red[x] = struct.unpack('>H', data[x*8:x*8+2])[0]
            green[x] = struct.unpack('>H', data[x*8+2:x*8+4])[0]
            blue[x] = struct.unpack('>H', data[x*8+4:x*8+6])[0]
            activity[x] = struct.unpack('>H', data[x*8+6:x*8+8])[0]
            
        #Create array to keep track of resets; resets[x] = y means
        #there have been y resets before point x.
        resets = [-1] * len(red)
        
        #Remove reamining -1s (reset entires) from raw R,G,B,A
        #Note: calling len(red) 100,000 times runs this portion
        #of the code in a fraction of a second.
        x = y = 0
        while x < len(red):
            if red[x] == -1:
                del red[x]
                del green[x]
                del blue [x]
                del activity[x]
                y += 1
                continue
            resets[x] = y
            x += 1
        
        #If there were resets, R,G,B,A are now shorter than resets,
        #so we shall resize it.
        del resets[len(red):]
        
        #As of right now this uses either daysimeter_id (bad) or
        #firmware version (good). Once all daysimeters use a F1.x 
        #header or above, this code can be reduced to just the 
        #elif statement (as an if, of course )
        if old_flag:    
            if (daysimeter_id >= 54 and daysimeter_id <= 69) or \
            daysimeter_id >= 83:
                adj_active_flag_ = True
        elif float(info[1]) in adj_active_firm:
            adj_active_flag_ = True
        
        #If we are using the firmware version where the LSB of
        #activity is actually a monitor for RGB values rolling over
        #we need to adjust the values accordingly.
        if adj_active_flag_:
            adjusted_rgb = adj_active_flag(red, green, blue, activity)
            #Unpack adjusted values
            red = adjusted_rgb[0]
            green = adjusted_rgb[1]
            blue = adjusted_rgb[2]
            
        #Create list for time called times (because time is
        #a python module)
        times = [-1] * len(red)
        mat_times = [-1] * len(red)
        #Iteratively 'generate' timestamps and place into times
        for x in range(0, len(times)):
            times[x] = epoch_time + timedelta(seconds=log_interval*x)
            mat_times[x] = dt2dn(times[x])
            
        #Activity is captured on the daysimeter as a mean squared
        #value (i.e. activity = x^2 + y^2 + z^2) and is measured in
        #counts. To get the number of g's, calculate the root mean
        #square (RMS) value and multiple by .0039 (the number of g's
        #per count) *4. The *4 comes from "four right shifts in the 
        #souce code." Basically, there is some bit shifting to maximize
        #storage space in the EEPROM, and we 'un-shift' it.
        activity = [math.sqrt(x)*.0039*4 for x in activity]
        
        #Apply calibration constants to raw data
        red = [x*calib_info[1] for x in red]
        green = [x*calib_info[2] for x in green]
        blue = [x*calib_info[3] for x in blue]
        #If new fireware, find constants in the header, process them, and
        #calculate lux and cla
        if not old_flag:
            constants = process_constants(info[14], info[13], info[12], \
            info[11], info[10], info[15])
            temp = self.calc_lux_cla(red, green, blue, constants)
        #Else, search for a constants file, process constants, and calculate
        #lux and cla
        else:
            temp = self.calc_lux_cla(red, green, blue)
        #Unpack lux and cla
        lux = temp[0]
        cla = temp[1]
    
        del(temp)
        #Apply a zero phase shift filter to cla and activity
        cla = lowpass_filter(cla, log_interval)
        activity = lowpass_filter(activity, log_interval)
        #Calculate cs
        cs = calc_cs(cla)
        
        self.emit(QtCore.SIGNAL('make'),([device_model, device_sn, \
        calib_info], [times, mat_times, red, green, blue, lux, cla, cs, \
        activity, resets]))
        
    def calc_lux_cla(self, *args):
        """ PURPOSE: Calculates CS and CLA. """
        error_log_filename = get_err_log()
        logging.basicConfig(filename=error_log_filename, level=logging.DEBUG)
        
        if len(args) == 3:
            red = args[0]
            green = args[1]
            blue = args[2]
            #Constants is a list of lists, with hardware specific constants
            constants = get_constants()
        elif len(args) == 4:
            red = args[0]
            green = args[1]
            blue = args[2]
            constants = args[3]
        else:
            logging.warning('Invalid usage of calc_lux_cla')
            sys.exit(1)
            
        loop_max = num_entries = len(red)
        
        #Create lux list and allocate space
        lux = [-1] * num_entries
        #Calculate and fill lux
        for x in range(0, loop_max):
            lux[x] = constants[4][0]*red[x] + constants[4][1]*green[x] + \
            constants[4][2]*blue[x]
            
        #Create lists and allocate space for each list
        scone_macula = [-1] * num_entries
        v_lamda_macula =  [-1] * num_entries
        melanopsin =  [-1] * num_entries
        v_prime =  [-1] * num_entries
        cla = [-1] * num_entries
        
        emit_sig = 0
        
        #Following is lots of fancy math which I do not understand the
        #reasoning for. I based it off the MatLab code, with some exceptions
        #to optimize code for python
        for x in range(0, loop_max):
            scone_macula[x] = constants[0][0]*red[x] + \
            constants[0][1]*green[x] + constants[0][2]*blue[x]
            v_lamda_macula[x] = constants[1][0]*red[x] + \
            constants[1][1]*green[x] + constants[1][2]*blue[x]
            melanopsin[x] = constants[2][0]*red[x] + \
            constants[2][1]*green[x] + constants[2][2]*blue[x]
            v_prime[x] = constants[3][0]*red[x] + constants[3][1]*green[x] + \
            constants[3][2]*blue[x]
            
            if scone_macula[x] > v_lamda_macula[x] * constants[5][2]:
                #Some super fancy math. I wish I knew what was going on here...
                cla[x] = melanopsin[x] + constants[5][0] * (scone_macula[x] - \
                v_lamda_macula[x] * constants[5][2]) - \
                constants[5][1]*683*(1 - 2.71**(-(v_prime[x]/(683*6.5))))
            else:
                cla[x] = melanopsin[x]
            

            if math.ceil((20*x)/loop_max) > emit_sig:
                emit_sig += 1
                self.emit(QtCore.SIGNAL('update'))
            cla[x] *= constants[5][3]
        cla = [0 if x < 0 else x for x in cla]
            
        return [lux, cla]
        
class MakeCDF(QtCore.QThread):
    
    def __init__(self, parent, data, filename, info):
        QtCore.QThread.__init__(self, parent)
        self.data = data
        self.filename = filename
        self.info = info
        
    def run(self):
        """ PURPOSE: Makes a CDF file from data. """
        sub_info = self.info
        struct_time = time.strptime(sub_info[2], '%d %B %Y')
        sub_info[2] = datetime.fromtimestamp(time.mktime(struct_time))

        filename = self.filename

        if os.path.isfile(filename):
            os.remove(filename)
        data = self.data
        with pycdf.CDF(filename,'') as cdf_fp:
            #Set global attributes
            cdf_fp.attrs['creationDate'] = datetime.now()
            cdf_fp.attrs['deviceModel'] = data[0][0]
            cdf_fp.attrs['deviceSN'] = data[0][1]
            cdf_fp.attrs['redCalibration'] = data[0][2][0]
            cdf_fp.attrs['greenCalibration'] = data[0][2][1]
            cdf_fp.attrs['blueCalibration'] = data[0][2][2]
    #########The following global attributes either do not exist yet, or
    #########have no available source to pull the information from
    #        cdf_fp.attrs['uvCalibration'] = 
    #        cdf_fp.attrs['illuminanceCalibration'] =
            cdf_fp.attrs['subjectID'] = sub_info[0]
            cdf_fp.attrs['subjectSex'] = sub_info[1]
            cdf_fp.attrs['subjectDateOfBirth'] = sub_info[2]
            cdf_fp.attrs['subjectMass'] = sub_info[3]
            
            #Set variables
            cdf_fp['time'] = data[1][0]
            cdf_fp.new('matTime', type=pycdf.const.CDF_REAL8)
            cdf_fp['matTime'] = data[1][1]
            cdf_fp.new('timeOffset', get_local_offset_s(), \
            pycdf.const.CDF_INT4, False)
            cdf_fp['red'] = data[1][2]
            cdf_fp['green'] = data[1][3]
            cdf_fp['blue'] = data[1][4]
            cdf_fp['illuminance'] = data[1][5]
            cdf_fp['CLA'] = data[1][6]
            cdf_fp['CS'] = data[1][7]
            cdf_fp['activity'] = data[1][8]
            
    #        cdf_fp['xAcceleration'] =
    #        cdf_fp['yAcceleration'] =
    #        cdf_fp['zAcceleration'] =
    #        cdf_fp['uvIndex'] =
    #        cdf_fp['temperature'] =
    #        cdf_fp['longitude'] =
    #        cdf_fp['latitude'] =
    #        cdf_fp['event'] =
            
            #Set variable attributes for time
            cdf_fp['time'].attrs['description'] = 'UTC in CDF Epoch format,' + \
            ' milliseconds since 1-Jan-0000'
            cdf_fp['time'].attrs['unitPrefix'] = 'm'
            cdf_fp['time'].attrs['baseUnit'] = 's'
            cdf_fp['time'].attrs['unitType'] = 'baseSI'
            cdf_fp['time'].attrs['otherAttributes'] = ''
            
            #Set variable attributes for matTime
            cdf_fp['matTime'].attrs['description'] = 'UTC in MATLAB serial' + \
            ' date format, days since 1-Jan-0000'
            cdf_fp['matTime'].attrs['unitPrefix'] = ''
            cdf_fp['matTime'].attrs['baseUnit'] = 'days'
            cdf_fp['matTime'].attrs['unitType'] = 'nonSI'
            cdf_fp['matTime'].attrs['otherAttributes'] = ''
            
            #Set variable attributes for timeOffset
            cdf_fp['timeOffset'].attrs['description'] = 'Localized offset ' + \
            'from UTC'
            cdf_fp['timeOffset'].attrs['unitPrefix'] = ''
            cdf_fp['timeOffset'].attrs['baseUnit'] = 's'
            cdf_fp['timeOffset'].attrs['unitType'] = 'baseSI'
            cdf_fp['timeOffset'].attrs['otherAttributes'] = ''
            
            #Set variable attributes for red
            cdf_fp['red'].attrs['description'] = ''
            cdf_fp['red'].attrs['unitPrefix'] = ''
            cdf_fp['red'].attrs['baseUnit'] = 'lx'
            cdf_fp['red'].attrs['unitType'] = 'namedSI'
            cdf_fp['red'].attrs['otherAttributes'] = ''
            
            #Set variable attributes for green
            cdf_fp['green'].attrs['description'] = ''        
            cdf_fp['green'].attrs['unitPrefix'] = ''
            cdf_fp['green'].attrs['baseUnit'] = 'lx'
            cdf_fp['green'].attrs['unitType'] = 'namedSI'
            cdf_fp['green'].attrs['otherAttributes'] = ''
            
            #Set variable attributes for blue
            cdf_fp['blue'].attrs['description'] = ''
            cdf_fp['blue'].attrs['unitPrefix'] = ''
            cdf_fp['blue'].attrs['baseUnit'] = 'lx'
            cdf_fp['blue'].attrs['unitType'] = 'namedSI'
            cdf_fp['blue'].attrs['otherAttributes'] = ''
            
            #Set variable attributes for illuminance
            cdf_fp['illuminance'].attrs['description'] = ''
            cdf_fp['illuminance'].attrs['unitPrefix'] = ''
            cdf_fp['illuminance'].attrs['baseUnit'] = 'lx'
            cdf_fp['illuminance'].attrs['unitType'] = 'namedSI'
            cdf_fp['illuminance'].attrs['otherAttributes'] = ''
            
            #Set variable attributes for CLA
            cdf_fp['CLA'].attrs['description'] = 'Circadian Light'
            cdf_fp['CLA'].attrs['unitPrefix'] = ''
            cdf_fp['CLA'].attrs['baseUnit'] = 'CLA'
            cdf_fp['CLA'].attrs['unitType'] = 'nonSI'
            cdf_fp['CLA'].attrs['otherAttributes'] = 'model'
            
            #Set variable attributes for CS
            cdf_fp['CS'].attrs['description'] = 'Circadian Stimulus'
            cdf_fp['CS'].attrs['unitPrefix'] = ''
            cdf_fp['CS'].attrs['baseUnit'] = 'CS'
            cdf_fp['CS'].attrs['unitType'] = 'nonSI'
            cdf_fp['CS'].attrs['otherAttributes'] = 'model'
            
            #Set variable attributes for activity
            cdf_fp['activity'].attrs['description'] = 'Activity index in g' + \
            '-force (acceleration in m/2^2 over standard gravity 9.80665 m/s^2)'
            cdf_fp['activity'].attrs['unitPrefix'] = ''
            cdf_fp['activity'].attrs['baseUnit'] = 'g_n'
            cdf_fp['activity'].attrs['unitType'] = 'nonSI'
            cdf_fp['activity'].attrs['otherAttributes'] = 'method'
            
            #Set variable attributes for xAcceleration
    #        cdf_fp['xAcceleration'].attrs['description'] = 'Acceleration ' + \
    #        'in the x-axis relative to the accelerometer'
    #        cdf_fp['xAcceleration'].attrs['unitPrefix'] = ''
    #        cdf_fp['xAcceleration'].attrs['baseUnit'] = 'm/s^2'
    #        cdf_fp['xAcceleration'].attrs['unitType'] = 'derivedSI'
    #        cdf_fp['xAcceleration'].attrs['otherAttributes'] = ''
            
            #Set variable attributes for yAcceleration
    #        cdf_fp['yAcceleration'].attrs['description'] = 'Acceleration ' + \ 
    #        'in the y-axis relative to the accelerometer'
    #        cdf_fp['yAcceleration'].attrs['unitPrefix'] = ''
    #        cdf_fp['yAcceleration'].attrs['baseUnit'] = 'm/s^2'
    #        cdf_fp['yAcceleration'].attrs['unitType'] = 'derivedSI'
    #        cdf_fp['yAcceleration'].attrs['otherAttributes'] = ''
            
            #Set variable attributes for zAcceleration
    #        cdf_fp['zAcceleration'].attrs['description'] = 'Acceleration ' + \
    #        'in the z-axis relative to the accelerometer'
    #        cdf_fp['zAcceleration'].attrs['unitPrefix'] = ''
    #        cdf_fp['zAcceleration'].attrs['baseUnit'] = 'm/s^2'
    #        cdf_fp['zAcceleration'].attrs['unitType'] = 'derivedSI'
    #        cdf_fp['zAcceleration'].attrs['otherAttributes'] = ''
            
            #Set variable attributes for uvIndex
    #        cdf_fp['uvIndex'].attrs['description'] = 'Ultraviolet index'
    #        cdf_fp['uvIndex'].attrs['unitPrefix'] = ''
    #        cdf_fp['uvIndex'].attrs['baseUnit'] = 'uvIndex'
    #        cdf_fp['uvIndex'].attrs['unitType'] = 'nonSI'
    #        cdf_fp['uvIndex'].attrs['otherAttributes'] = ''
            
            #Set variable attributes for temperature
    #        cdf_fp['temperature'].attrs['description'] = 'Ambient air ' + \
    #        'temperature in degrees Kelvin'
    #        cdf_fp['temperature'].attrs['unitPrefix'] = ''
    #        cdf_fp['temperature'].attrs['baseUnit'] = 'K'
    #        cdf_fp['temperature'].attrs['unitType'] = 'baseSI'
    #        cdf_fp['temperature'].attrs['otherAttributes'] = ''
            
            #Set variable attributes for longitude
    #        cdf_fp['longitude'].attrs['description'] = 'Longitude in ' + \
    #        'decimal degrees'
    #        cdf_fp['longitude'].attrs['unitPrefix'] = ''
    #        cdf_fp['longitude'].attrs['baseUnit'] = 'deg'
    #        cdf_fp['longitude'].attrs['unitType'] = 'nonSI'
    #        cdf_fp['longitude'].attrs['otherAttributes'] = ''
            
            #Set variable attributes for latitude
    #        cdf_fp['latitude'].attrs['description'] = 'Latitude in ' + \
    #        'decimal degrees'
    #        cdf_fp['latitude'].attrs['unitPrefix'] = ''
    #        cdf_fp['latitude'].attrs['baseUnit'] = 'deg'
    #        cdf_fp['latitude'].attrs['unitType'] = 'nonSI'
    #        cdf_fp['latitude'].attrs['otherAttributes'] = ''
            
            #Set variable attributes for event
    #        cdf_fp['event'].attrs['description'] = 'Event marker'
    #        cdf_fp['event'].attrs['unitPrefix'] = ''
    #        cdf_fp['event'].attrs['baseUnit'] = ''
    #        cdf_fp['event'].attrs['unitType'] = ''
    #        cdf_fp['event'].attrs['otherAttributes'] = 'event code definition'
            
        #Set download flag to true (0)
        set_download_flag()
        self.emit(QtCore.SIGNAL('update'))

class MakeCSV(QtCore.QThread):
    
    def __init__(self, parent, data, filename):
        QtCore.QThread.__init__(self, parent)
        self.data = data
        self.filename = filename
        
    def run(self):
        """ PURPOSE: Makes a CSV file from data. """
        if not os.path.exists(os.getcwd() + '/usr/data/subject info.txt'):
            return False
        sub_info = read_subject_info()
        struct_time = time.strptime(sub_info[2], '%d %B %Y')
        sub_info[2] = datetime.fromtimestamp(time.mktime(struct_time))

        filename = self.filename

        with open(filename,'w') as csv_fp:
            csv_fp.write('time,red,green,blue,lux,CLA,activity\n')
            for x in range(len(self.data[1][0])):
                csv_fp.write(str(self.data[1][0][x]) + ',' + \
                str(self.data[1][2][x]) + ',' + str(self.data[1][3][x]) + ',' \
                + str(self.data[1][4][x]) + ',' +  str(self.data[1][5][x]) + \
                 ',' +  str(self.data[1][6][x]) + ',' + \
                 str(self.data[1][8][x]) + '\n')
        set_download_flag()
        self.emit(QtCore.SIGNAL('update'))

def main():
    """ PURPOSE: Creates app and runs widget """
    # Create the Qt Application
    app = QtGui.QApplication(sys.argv)
    # Create and show the form
    session = DownloadMake()
    # Run the main Qt loop
    sys.exit(app.exec_())
            
if __name__ == '__main__':
    main()          