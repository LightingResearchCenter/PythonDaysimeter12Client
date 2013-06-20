#Constants
#Author: Jed Kundl
#Creation Date: 19.06.2013
#INPUT: 
#OUTPUT: Constants

#This file just puts the constants in one place, for ease of
#editing/adding/etc

#LOG_FILENAME is the name of the header file on any daysimeter
LOG_FILENAME = 'log_info.txt'
#DATA_FILENAME is the name of the binary data file on any daysimeter
DATA_FILENAME = 'data_log.txt'
#CALIBRATION_FILENAME is the full path to the calibration file stored
#on the LRC's server. Will be obsolete when calibration is located
#in the header files.
CALIBRATION_FILENAME = '//root/projects/Daysimeter and dimesimeter reference files/data/Day12 RGB Values.txt'
#LOCAL_CALIB_FILENAME is the name of the calibration file to be found
#locally. Ideally, this should never work because that would mean
#there was a random file sitting on the daysimeter.
LOCAL_CALIB_FILENAME = 'Day12 RGB Values.txt'
#CONSTANTS_FILENAME is the name of the constants stored
#on the LRC's server. Will be obsolete when calibration is located
#in the header files.
CONSTANTS_FILENAME = '//root/projects/Daysimeter and dimesimeter reference files/data/Day12 Cal Values.txt'
#LOCAL_CONST_FILENAME is the name of the constants file to be found
#locally. Ideally, this should never work because that would mean
#there was a random file sitting on the daysimeter.
LOCAL_CONST_FILENAME = 'Day12 Cal Values.txt'
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
FIRM12 = {54,55,56,57,58,59,60,61,62,63,64,65,66,67,68,69}
BATTERY_STRING = 'Battery voltage (mV/10)\n'