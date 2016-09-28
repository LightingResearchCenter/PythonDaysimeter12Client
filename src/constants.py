"""
Constants
Author: Jed Kundl
Creation Date: 19.06.2013
INPUT: 
OUTPUT: Constants
NOTE: This file contains constants which all called from various parts of the
code. Each constant has a description explaining why it is there. Constants are
centralized to make it easier to modify code.
"""
#This file just puts the constants in one place, for ease of
#editing/adding/etc

#LOG_FILENAME is the name of the header file on any daysimeter
LOG_FILENAME = 'log_info.txt'
#DATA_FILENAME is the name of the binary data file on any daysimeter
DATA_FILENAME = 'data_log.txt'
#CALIBRATION_FILENAME is the full path to the calibration file stored
#on the LRC's server. Will be obsolete when calibration is located
#in the header files.
CALIBRATION_FILENAME = '//root/projects/DaysimeterAndDimesimeterReference' \
    + 'Files/data/Day12 RGB Values.txt'
#LOCAL_CALIB_FILENAME is the name of the calibration file to be found
#locally.
LOCAL_CALIB_FILENAME = 'C:/Daysimeter Client/Day12 RGB Values.txt'
#NEW_CALIBRATION_FILENAME is the full path to the calibration file stored
#on the LRC's server. Will be obsolete when calibration is located
#in the header files. This is the file for daysimeters 366-415
NEW_CALIBRATION_FILENAME = '//root/projects/DaysimeterAndDimesimeterReference' \
    + 'Files/data/New Day12 RGB Values.txt'
#LOCAL_CALIB_FILENAME is the name of the calibration file to be found
#locally.This is the file for daysimeters 366-415
NEW_LOCAL_CALIB_FILENAME = 'C:/Daysimeter Client/New Day12 RGB Values.txt'
#CONSTANTS_FILENAME is the name of the constants stored
#on the LRC's server. Will be obsolete when calibration is located
#in the header files.
CONSTANTS_FILENAME = '//root/projects/DaysimeterAndDimesimeterReference' \
    + 'Files/data/Day12 Cal Values.txt'
#LOCAL_CONST_FILENAME is the name of the constants file to be found
#locally.
LOCAL_CONST_FILENAME = 'C:/Daysimeter Client/Day12 Cal Values.txt'
#MINUTES relates to the lowpassfilter.py and is the window the filter
#uses when smoothing out data.
MINUTES = 5
#ADJ_ACTIVE_FLAG is a boolean value determining whether the LSB
#of activity was used to record rollover of RGB values
ADJ_ACTIVE_FLAG = False
#OLD_FLAG is a boolean value determining whether the header is
#of firmware version 0.x or 1.x
OLD_FLAG = True
#FIRM12 is a set of daysimeters whose IDs are less than 83
#but have firmware version 0.2 (old header,activity LSB used as
#rollover flag) 
FIRM12 = {54, 55, 56, 57, 58, 59, 60, 61, 62, 63, 64, 65, 66, 67, 68, 69}
#BATTERY_STRING is string in the motes section pertaining to voltage.
#It is important that all future headers match the string, because
#it is used to make convertHeaderF0 work one any properly extended header.
BATTERY_STRING = 'Battery voltage (mV)\n'
#ADJ_ACTIVE_FIRM is the set of firmware versions as floats which use
#the LSB of activity as a rollover flag.
ADJ_ACTIVE_FIRM = {1.2}
#CDF_FILENAME is the name of the CDF file created by makecdf.py
DEVICE_MODEL = 'daysimeter12'
#DEVICE_VERSION is related to DEVICE_MODEL and is basically just
#here so concatenation of deviceSN is more dynamic.
DEVICE_VERSION = '12'
#LATEST_URL is the url which redirects to the latest version of the slient on
#GitHub. It is used to determine latest client version.
LATEST_URL = 'https://github.com/LightingResearchCenter/PythonDaysimeter12Client/releases/latest'