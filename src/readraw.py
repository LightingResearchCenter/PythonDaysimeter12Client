#ReadRaw
#Author: Jed Kundl
#Creation Date: 13.06.2013
#INPUT: log_file, data_file
#OUTPUT: Data to be pased to a CDF processing script

def readRaw():
    import sys
    import struct
    import logging
    import time
    import math
    from Tkinter import Tk
    from tkMessageBox import askyesno
    from datetime import datetime
    from datetime import timedelta
    from geterrlog import getErrLog
    from adjactiveflag import adjActiveFlag
    from getcalibinfo import getCalibInfo
    from processconstants import processConstants
    from calcluxcla import calcLuxCLA
    from lowpassfilter import lowpassFilter
    from calccs import calcCS
    from finddaysimeter import findDaysimeter
    from datetimetodatenum import dt2dn
    from convertheader import convertHeaderF1
    import constants
    
    LOG_FILENAME = constants.LOG_FILENAME
    DATA_FILENAME = constants.DATA_FILENAME
    ADJ_ACTIVE_FLAG = constants.ADJ_ACTIVE_FLAG
    OLD_FLAG = constants.OLD_FLAG
    ADJ_ACTIVE_FIRM = constants.ADJ_ACTIVE_FIRM
    
    #Create error log file named error.log on the desktop
    ERRLOG_FILENAME = getErrLog()
    if ERRLOG_FILENAME == '':
        sys.exit(1)
    logging.basicConfig(filename=ERRLOG_FILENAME,level=logging.DEBUG)
    
    PATH = findDaysimeter()
    #Open header file for reading
    try:
        logfile_fp = open(PATH + LOG_FILENAME,'r')
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
        OLD_FLAG = False
    
    #Find the daysimeter device ID
    if OLD_FLAG:
        daysimeterID = int(info[1])
        deviceModel = constants.DEVICE_MODEL
        deviceSN = constants.DEVICE_VERSION + info[1]
    else:
        daysimeterID = int(info[3])
        deviceModel = info[2]
        deviceSN = info[2].lstrip('abcdefghijklmnopqrstuvwxyz') + info[3]
    
    #Get calibration info
    if not OLD_FLAG:
        calibConst = [float(x) for x in info[9].strip('\n').split('\t')]
        calibInfo = [daysimeterID, calibConst[0], calibConst[1], calibConst[2]]
    else:
        calibInfo = getCalibInfo(daysimeterID)
        
    #Open binary data file for reading
    try:
        datafile_fp = open(PATH + DATA_FILENAME,"rb")
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
    if not OLD_FLAG:
        structTime = time.strptime(info[4], "%m-%d-%y %H:%M")
    else:
        structTime = time.strptime(info[2], "%m-%d-%y %H:%M")
    epochTime = datetime.fromtimestamp(time.mktime(structTime))
    #logInterval is interval that the Daysimeter took measurements at.
    #Since python uses seconds since epoch, cast as int
    if not OLD_FLAG:
        logInterval = int(info[5])
    else:
        logInterval = int(info[3])
    
    #Determine the number of of logged entries. Why divded by 8?
    #I'm glad you asked! There are 4 things that are logged, and
    #each item takes up 2 bytes. So, we take the total number of
    #bytes (len(data)) and dived by 2*4. It makes so much sense!
    #I will admit, I only figure that out during debugging...
    numEntries = int(math.floor(len(data)/8))
    #Create lists for raw Red, Green, Blue, and Activity
    red = [-1] * numEntries
    green = [-1] * numEntries
    blue = [-1] * numEntries
    activity = [-1] * numEntries
    #Iteratively seperate data into raw R,G,B,A
    #struct.unpack unpacks binary data given a format.
    #>H is an unsigned short (16 bit unsigned integer) in big
    #endian notation.
    for x in range(0,numEntries):
        #If value is 65278 the daysimeter reset, skip and leave
        #the value at -1
        if struct.unpack('>H',data[x*8:x*8+2])[0] == 65278:
            continue
        #If value is 65535 there are no more entires to be
        #read. Remove 'empty' entries and break
        elif struct.unpack('>H',data[x*8:x*8+2])[0] == 65535:
            del red[x:]
            del green[x:]
            del blue[x:]
            del activity[x:]
            break
        red[x] = struct.unpack('>H',data[x*8:x*8+2])[0]
        green[x] = struct.unpack('>H',data[x*8+2:x*8+4])[0]
        blue[x] = struct.unpack('>H',data[x*8+4:x*8+6])[0]
        activity[x] = struct.unpack('>H',data[x*8+6:x*8+8])[0]
        
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
            y+=1
            continue
        resets[x] = y
        x+=1
    
    #If there were resets, R,G,B,A are now shorter than resets,
    #so we shall resize it.
    del resets[len(red):]
    
    #As of right now this uses either daysimeterID (bad) or
    #firmware version (good). Once all daysimeters use a F1.x 
    #header or above, this code can be reduced to just the 
    #elif statement (as an if, of course )
    if OLD_FLAG:    
        if (daysimeterID >= 54 and daysimeterID <= 69) or daysimeterID >= 83:
            ADJ_ACTIVE_FLAG = True
    elif float(info[1]) in ADJ_ACTIVE_FIRM:
        ADJ_ACTIVE_FLAG = True
    
    #If we are using the firmware version where the LSB of
    #activity is actually a monitor for RGB values rolling over
    #we need to adjust the values accordingly.
    if ADJ_ACTIVE_FLAG:
        adjustedRGB = adjActiveFlag(red,green,blue,activity)
        #Unpack adjusted values
        red = adjustedRGB[0]
        green = adjustedRGB[1]
        blue = adjustedRGB[2]
        
    #Create list for time called times (because time is
    #a python module)
    times = [-1] * len(red)
    matTimes = [-1] * len(red)
    #Iteratively 'generate' timestamps and place into times
    for x in range(0,len(times)):
        times[x] = epochTime + timedelta(seconds=logInterval*x)
        matTimes[x] = dt2dn(times[x])
    
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
    
    #If new fireware, find constants in the header, process them, and
    #calculate lux and CLA
    if not OLD_FLAG:
        constants = processConstants(info[14],info[13],info[12],info[11],info[10],info[15])
        temp = calcLuxCLA(red,green,blue,constants)
    #Else, search for a constants file, process constants, and calculate
    #lux and CLA
    else:
        temp = calcLuxCLA(red,green,blue)
    #Unpack lux and CLA
    lux = temp[0]
    CLA = temp[1]

    del(temp)
    #Apply a zero phase shift filter to CLA and activity
#    CLA = lowpassFilter(CLA,logInterval)
#    activity = lowpassFilter(activity,logInterval)
    #Calculate CS
    CS = calcCS(CLA)
    
    if OLD_FLAG:
        Tk().withdraw()
        if askyesno(None,'Your ' + deviceModel + '\'s header file is out of date.\nWould you like to update it now?'):
            convertHeaderF1()
    
    #Return a tuple of lists of mixed lists. The first list in the tuple is
    #global attributes, and the second is variable data
    return ([deviceModel, deviceSN, calibInfo],[times, matTimes, red, green, blue, lux, CLA, CS, activity, resets])

if __name__ == '__main__':readRaw()