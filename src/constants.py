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
import datetime
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
#UTC_OFFSETS is a dictionary of UTC Offsets stored as datetime.timedelta objects
UTC_OFFSETS = {0: datetime.timedelta(-1, 43200), 1 : datetime.timedelta(-1, 46800), \
               2 : datetime.timedelta(-1, 50400), 3 : datetime.timedelta(-1, 52200), \
               4 : datetime.timedelta(-1, 54000), 5 : datetime.timedelta(-1, 57600), \
               6 : datetime.timedelta(-1, 61200), 7 : datetime.timedelta(-1, 64800), \
               8 : datetime.timedelta(-1, 68400), 9 : datetime.timedelta(-1, 70200), \
               10 : datetime.timedelta(-1, 72000), 11 : datetime.timedelta(-1, 73800), \
               12 : datetime.timedelta(-1, 75600), 13 : datetime.timedelta(-1, 79200), \
               14 : datetime.timedelta(-1, 82800), 15 : datetime.timedelta(0), \
               16 : datetime.timedelta(0, 3600), 17 : datetime.timedelta(0, 7200), \
               18 : datetime.timedelta(0, 10800), 19 : datetime.timedelta(0, 12600), \
               20 : datetime.timedelta(0, 14400), 21 : datetime.timedelta(0, 16200), \
               22 : datetime.timedelta(0, 18000), 23 : datetime.timedelta(0, 19800), \
               24 : datetime.timedelta(0, 20700), 25 : datetime.timedelta(0, 21600), \
               26 : datetime.timedelta(0, 23400), 27 : datetime.timedelta(0, 25200), \
               28 : datetime.timedelta(0, 28800), 29 : datetime.timedelta(0, 31500), \
               30 : datetime.timedelta(0, 32400), 31 : datetime.timedelta(0, 34200), \
               32 : datetime.timedelta(0, 36000), 33 : datetime.timedelta(0, 37800), \
               34 : datetime.timedelta(0, 39600), 35 : datetime.timedelta(0, 41400), \
               36 : datetime.timedelta(0, 43200), 37 : datetime.timedelta(0, 45900), \
               38 : datetime.timedelta(0, 46800), 39 : datetime.timedelta(0, 50400)}