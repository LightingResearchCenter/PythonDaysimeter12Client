"""
get_calib_info
Author: Jed Kundl
Creation Date: 17.06.2013
INPUT: daysimeter_id
OUTPUT: A list of calibration info called calib_info
"""

import logging
import sys
from Tkinter import Tk
from tkFileDialog import askopenfilename
from getlogs import get_err_log, get_daysim_log, setup_logger
import constants

def get_calib_info(daysimeter_id):
    """ PURPOSE: Finds the calibration info for a given daysimeter. """
    
    calibration_filename = constants.CALIBRATION_FILENAME
    local_calib_filename = constants.LOCAL_CALIB_FILENAME

    #Create error log file named error.log on the desktop
    errlog_filename = get_err_log()
    setup_logger('errlog', errlog_filename)
    errlog = logging.getLogger('errlog')
    
    daysimlog_filename = get_daysim_log()
    setup_logger('daysimlog', daysimlog_filename)
    daysimlog = logging.getLogger('daysimlog')
       
    #calib_data gives the source of the calibration information
    #0 = not set, 1 = server, 2 = local
    calib_data = 0   
    
    #Check and see if we can find the calibration information
    #on the LRC server
    #Open calibration file and get data
    daysimlog.info('getcalibinfo.py func get_calib_info: Opening calibration file')
    try:
        calibration_fp = open(calibration_filename,"r")
    #Catch IO exception, add to log and continue
    except IOError:
        errlog.error('Could not open calibration file from server')
    else:
        #Read each line of the calibration file and put it 
        #into a list called calib_info.
        calib_info = calibration_fp.readlines()
        calib_data = 1
        #Create a list of the calibration info
        calib_info = \
        [float(x) for x in calib_info[daysimeter_id].split('\t') if x.strip()]
        daysimlog.info('getcalibinfo.py func get_calib_info: Calibration info read from server')
    
    #If nowhere else, calibration data should be local
    if calib_data == 0:
        #Open calibration file and get data
        try:
            calibration_fp = open(local_calib_filename,"r")
        #Catch IO exception, add to log and quit
        except IOError:
            errlog.error('Could not open calibration file locally')
            #If we cannot find the file locally, we ask the user to 
            #tell the program where to find it
            Tk().withdraw()
            user_def_filename = askopenfilename(title='Please selected a ' + \
            'properly formatted Calibration file.')
            try:
                calibration_fp = open(user_def_filename,"r")
            #Catch IO exception, add to log and quit
            except IOError:
                errlog.error('Could not open user defined calibration file')
                return False
            else:
                #Read each line of the calibration file and put it 
                #into a list called calib_info.
                calib_info = calibration_fp.readlines()
                calib_data = 2
                daysimlog.info('getcalibinfo.py func get_calib_info: Calibration info read from manual entry')
            #Close the calibration file
                
            #Create a list of the calibration info
            calib_info = [float(x) for x in \
            calib_info[daysimeter_id].split('\t') if x.strip()]
        else:
            #Read each line of the calibrations file and put it 
            #into a list called calib_info.
            calib_info = calibration_fp.readlines()
            calib_data = 2
            #Create a list of the calibration info
            calib_info = \
            [float(x) for x in calib_info[daysimeter_id].split('\t') if x.strip()]
            daysimlog.info('getcalibinfo.py func get_calib_info: Calibration info read from local file')

            
    

        
    #The default values for calibration are 1, 2, and 3. Although it
    #is possible that a device actually might have those calibration
    #constants, it is assumed that there is no calibration info in such a case.
    if calib_info[1] == 1.0 and calib_info[2] == 2.0 and calib_info[3] == 3.0:
        errlog.warning('There is no calibration info for device')
        daysimlog.info('getcalibinfo.py func get_calib_info: No calibration information found')
#        sys.exit(1)
    calibration_fp.close()

    return calib_info