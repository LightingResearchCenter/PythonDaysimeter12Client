#ReadRaw
#Author: Jed Kundl
#Creation Date: 13.06.2013
#INPUT: log_file, data_file
#OUTPUT: Data to be pased to a CDF processing script
import sys
import struct
import logging
import time
import math
from Tkinter import Tk
from tkFileDialog import askopenfilename
import geterrlog

CALIBRATION_FILENAME = '//root/projects/Daysimeter and dimesimeter reference files/data/Day12 RGB Values.txt'
LOCAL_CALIB_FILENAME = 'Day12 RGB Values.txt'
LOG_FILENAME = 'log_info.txt'
DATA_FILENAME = 'data_log.txt'

def readRaw():
    #Create error log file named error.log on the desktop
    ERRLOG_FILENAME = geterrlog()
    logging.basicConfig(filename=ERRLOG_FILENAME,level=logging.DEBUG)
    
    #Open header file for reading
    try:
        logfile_fp = open(LOG_FILENAME,"r")
    #Catch IO exception (if present), add to log and quit
    except IOError:
        logging.error('Could not open logfile')
        sys.exit(1)
    else:
        #Read each line of the header and put it into a list
        #called info.
        #info[0] is status, info[1] is device ID, et cetera
        info = logfile_fp.readlines()
    #Close the logfile
    finally:
        logfile_fp.close()
        
    #Find the daysimeter device ID
    daysimeterID = int(info[1])
    
    #calibData gives the source of the calibration information
    #0 = not set, 1 = device header, 2 = server, 3 = local
    calibData = 0   
    
    #Check and see if calibration information exists on header file.
    #len(info) is 17 on devices not storing calibInfo, and 23 for
    #those that do store calibInfo
    if len(info) == 23:
        calibData = 1
        calibInfo = [daysimeterID, info[7], info[8], info[9]]
    #Else check and see if we can find the calibration information
    #on the LRC server
    else:
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
            calibData = 2
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
                calibData = 3
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
            calibData = 3
        #Close the calibration file
        finally:
            calibration_fp.close()
            
        #Create a list of the calibration info
        calibInfo = [float(x) for x in calibInfo[daysimeterID].split('\t') if x.strip()]
    
    #The default values for calibration are 1, 2, and 3. Although it
    #is possible that a device actually might have those calibration
    #constants, it is assumed that there is no calibration info.
    if calibInfo[1] == 1.0 and calibInfo[2] == 2.0 and calibInfo[3] == 3.0:
        logging.warning('There is no calibration info for device')
        sys.exit(1)
    
    #Open binary data file for reading
    try:
        datafile_fp = open(DATA_FILENAME,"rb")
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
    
#####It is assumed that time if formatted correctly, if not this
    #part of the code will not work. Time format is as follows:
    #mm-dd-yy HH:MM
    
    #Converts a time string into a float representing seconds
    #since epoch (UNIX)
    structTime = time.strptime(info[2], "%m-%d-%y %H:%M")
    epochTime = time.mktime(structTime)
    #logInterval is interval that the Daysimeter took measurements at.
    #Since python uses seconds since epoch, cast as int
    logInterval = int(info[3])
    
    #Determine the number of of logged entries
    numEntires = math.floor(len(data)/4)
    #Create lists for raw Red, Green, Blue, and Activity
    red = [-1] * numEntires
    green = [-1] * numEntires
    blue = [-1] * numEntires
    activity = [-1] * numEntires
    #Iteratively seperate data into raw R,G,B,A
    #struct.unpack unpacks binary data given a format.
    #>H is an unsigned short (16 bit unsigned integer) in big
    #endian notation.
    for x in range(0,numEntires):
        #If value is 65278 the daysimeter reset, skip and leave
        #the value at -1
        if struct.unpack('>H',data[x*8:x*8+2]) == 65278:
            continue
        #If value is 65535 there are no more entires to be
        #read. Remove 'empty' entries and break
        elif struct.unpack('>H',data[x*8:x*8+2]) == 65535:
            del red[x:]
            del green[x:]
            del blue[x:]
            del activity[x:]
            break
        red[x] = struct.unpack('>H',data[x*8:x*8+2])
        green[x] = struct.unpack('>H',data[x*8+2:x*8+4])
        blue[x] = struct.unpack('>H',data[x*8+4:x*8+6])
        activity[x] = struct.unpack('>H',data[x*8+6:x*8+8])
    
    #Remove reamining -1s (reset entires) from raw R,G,B,A
    #Note: calling len(red) 100,000 times runs this portion
    #of the code in a fraction of a second.
    x = 0
    while x < len(red):
        if red[x] == -1:
            del red[x]
            del green[x]
            del blue [x]
            del activity[x]
        x+=1
    
    #Create list for time called times (because time is
    #a python module)
    times = [-1] * len(red)
    #Iteratively 'generate' timestamps and place into times
    for x in range(0,len(times)):
        times[x] = epochTime + logInterval*x
    
    #Activity is captured on the daysimeter as a mean squared
    #value (i.e. activity = x^2 + y^2 + z^2) and is measured in
    #counts. To get the number of g's, calculate the root mean
    #square (RMS) value and multiple by .0039 (the number of g's
    #per count) *4. The *4 comes from "four right shifts in the 
    #souce code." Basically, there is some bit shifting to maximize
    #storage space in the EEPROM, and we 'un-shift' it.
    activity = [math.sqrt(x)*.0039*4 for x in activity]

    #Apply calibration constants to raw data
    red = [x*calibInfo[1] for x in red]
    green = [x*calibInfo[2] for x in green]
    blue = [x*calibInfo[3] for x in blue]
    
     
if __name__ == '__main__':readRaw()