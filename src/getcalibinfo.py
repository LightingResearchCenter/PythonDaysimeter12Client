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
from geterrlog import get_err_log
import constants

def get_calib_info(daysimeter_id):
    """ PURPOSE: Finds the calibration info for a given daysimeter. """
    
    calibration_filename = constants.CALIBRATION_FILENAME
    local_calib_filename = constants.LOCAL_CALIB_FILENAME

    
    #Create error log file named error.log on the desktop
    errlog_filename = get_err_log()
    logging.basicConfig(filename=errlog_filename, level=logging.DEBUG)
       
    #calib_data gives the source of the calibration information
    #0 = not set, 1 = server, 2 = local
    calib_data = 0   
    
    #Check and see if we can find the calibration information
    #on the LRC server
    #Open calibration file and get data
    try:
        calibration_fp = open(calibration_filename,"r")
    #Catch IO exception, add to log and continue
    except IOError:
        logging.error('Could not open calibration file from server')
    else:
        #Read each line of the calibration file and put it 
        #into a list called calib_info.
        calib_info = calibration_fp.readlines()
        calib_data = 1
    #Close the calibration file
    finally:
        calibration_fp.close()
        
    #Create a list of the calibration info
    calib_info = \
    [float(x) for x in calib_info[daysimeter_id].split('\t') if x.strip()]
    
    #If nowhere else, calibration data should be local
    if calib_data == 0:
        #Open calibration file and get data
        try:
            calibration_fp = open(local_calib_filename,"r")
        #Catch IO exception, add to log and quit
        except IOError:
            logging.error('Could not open calibration file locally')
            #If we cannot find the file locally, we ask the user to 
            #tell the program where to find it
            Tk().withdraw()
            user_def_filename = askopenfilename(title='Please selected a \
            properly formatted Calibration file.')
            try:
                calibration_fp = open(user_def_filename,"r")
            #Catch IO exception, add to log and quit
            except IOError:
                logging.error('Could not open user defined calibration file')
                return False
            else:
                #Read each line of the calibration file and put it 
                #into a list called calib_info.
                calib_info = calibration_fp.readlines()
                calib_data = 2
            #Close the calibration file
            finally:
                calibration_fp.close()
                
            #Create a list of the calibration info
            calib_info = [float(x) for x in \
            calib_info[daysimeter_id].split('\t') if x.strip()]
        else:
            #Read each line of the calibrations file and put it 
            #into a list called calib_info.
            calib_info = calibration_fp.readlines()
            calib_data = 2
        #Close the calibration file
        finally:
            calibration_fp.close()
            
        #Create a list of the calibration info
        calib_info = \
        [float(x) for x in calib_info[daysimeter_id].split('\t') if x.strip()]
        
    #The default values for calibration are 1, 2, and 3. Although it
    #is possible that a device actually might have those calibration
    #constants, it is assumed that there is no calibration info in such a case.
    if calib_info[1] == 1.0 and calib_info[2] == 2.0 and calib_info[3] == 3.0:
        logging.warning('There is no calibration info for device')
#        sys.exit(1)
        
    return calib_info