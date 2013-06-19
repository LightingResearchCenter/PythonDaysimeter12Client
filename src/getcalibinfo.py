#GetCalibInfo
#Author: Jed Kundl
#Creation Date: 17.06.2013
#INPUT: daysimeterID
#OUTPUT: A list of calibration info called calibInfo

import logging
import sys
from Tkinter import Tk
from tkFileDialog import askopenfilename
from geterrlong import getErrLog
import constants

CALIBRATION_FILENAME = constants.CALIBRATION_FILENAME
LOCAL_CALIB_FILENAME = constants.LOCAL_CALIB_FILENAME

def getCalibInfo(daysimeterID):
    
    #Create error log file named error.log on the desktop
    ERRLOG_FILENAME = getErrLog()
    logging.basicConfig(filename=ERRLOG_FILENAME,level=logging.DEBUG)
       
    #calibData gives the source of the calibration information
    #0 = not set, 1 = server, 2 = local
    calibData = 0   
    
    #Check and see if we can find the calibration information
    #on the LRC server
    #Open calibration file and get data
    try:
        calibration_fp = open(CALIBRATION_FILENAME,"r")
    #Catch IO exception, add to log and continue
    except IOError:
        logging.error('Could not open calibration file from server')
        pass
    else:
        #Read each line of the calibration file and put it 
        #into a list called calibInfo.
        calibInfo = calibration_fp.readlines()
        calibData = 1
    #Close the calibration file
    finally:
        calibration_fp.close()
            
    #Create a list of the calibration info
    calibInfo = [float(x) for x in calibInfo[daysimeterID].split('\t') if x.strip()]
    
    #If nowhere else, calibration data should be local
    if calibData == 0:
        #Open calibration file and get data
        try:
            calibration_fp = open(LOCAL_CALIB_FILENAME,"r")
        #Catch IO exception, add to log and quit
        except IOError:
            logging.error('Could not open calibration file locally')
            #If we cannot find the file locally, we ask the user to 
            #tell the program where to find it
            Tk().withdraw()
            USER_DEF_FILENAME = askopenfilename(title='Please selected a properly formatted Calibration file.')
            try:
                calibration_fp = open(USER_DEF_FILENAME,"r")
            #Catch IO exception, add to log and quit
            except IOError:
                logging.error('Could not open user defined calibration file')
                sys.exit(1)
            else:
                #Read each line of the calibration file and put it 
                #into a list called calibInfo.
                calibInfo = calibration_fp.readlines()
                calibData = 2
            #Close the calibration file
            finally:
                calibration_fp.close()
                
            #Create a list of the calibration info
            calibInfo = [float(x) for x in calibInfo[daysimeterID].split('\t') if x.strip()]
            pass
        else:
            #Read each line of the calibrations file and put it 
            #into a list called calibInfo.
            calibInfo = calibration_fp.readlines()
            calibData = 2
        #Close the calibration file
        finally:
            calibration_fp.close()
            
        #Create a list of the calibration info
        calibInfo = [float(x) for x in calibInfo[daysimeterID].split('\t') if x.strip()]
    
    #The default values for calibration are 1, 2, and 3. Although it
    #is possible that a device actually might have those calibration
    #constants, it is assumed that there is no calibration info in such a case.
    if calibInfo[1] == 1.0 and calibInfo[2] == 2.0 and calibInfo[3] == 3.0:
        logging.warning('There is no calibration info for device')
        sys.exit(1)
    
    return calibInfo
    
if __name__ == '__main__':getCalibInfo(-1)