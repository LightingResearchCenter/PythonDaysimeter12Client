#ConvertHeader
#Author: Jed Kundl
#Creation Date: 20.06.2013
#INPUT: 
#OUTPUT:

#Convert an F0 header file into an F1 header file
#An F0 header is any 0.x header (Original Daysimeter 12 standard) and
#An F1 header is and 1.x header (New Daysimeter 12 standard)
#An example F1 header is available at \\root\Public\bierma2 from within
#The LRC's network as of 20.06.2013
def convertHeaderF1():
    import sys
    import logging
    from geterrlog import getErrLog
    from getcalibinfo import getCalibInfo
    from getconstants import getConstants
    from finddaysimeter import findDaysimeter
    import constants

    LOG_FILENAME = constants.LOG_FILENAME
    BATTERY_STRING = constants.BATTERY_STRING
    FIRM12 = constants.FIRM12
    
    #Create error log file named error.log on the desktop
    ERRLOG_FILENAME = getErrLog()
    if ERRLOG_FILENAME == '':
        sys.exit(1)
    logging.basicConfig(filename=ERRLOG_FILENAME,level=logging.DEBUG)
    
    PATH = findDaysimeter()
    #Open header file for reading and editing
    try:
        logfile_fp = open(PATH + LOG_FILENAME,"r+")
    #Catch IO exception (if present), add to log and quit
    except IOError:
        logging.error('Could not open logfile')
        sys.exit(1)
    else:
        #Read each line of the header and put it into a list
        #called info.
        info = logfile_fp.readlines()
        calibInfo = getCalibInfo(int(info[1]))
        aConstants = getConstants()
        #Remove binary garbage and whitesapce, if applicable, and format
        #strings in array.
        info = [x.strip('\n \xff') + '\n' for x in info]
        #Seek to the second line. Because seek reads bytes, if the length
        #of first time changes at all, then this will no longer work.
        logfile_fp.seek(3)
        #FIRM12 is a set of daysimeter IDs below 83 (the official change
        #over) that use the LSB of activity as a rollover flag for RGB. 
        if int(info[1]) in FIRM12 or int(info[1]) >= 83:
            logfile_fp.write('1.2\n')
        else:
            logfile_fp.write('1.1\n')
        #Shifts information down because firmware version is now on line 1
        for x in range(2,8):
            logfile_fp.write(info[x-1])
        #Write calibration information to file. Woohoo for putting this
        #information in the header instead of doing crazy lookups.
        logfile_fp.write(str(calibInfo[0]) + '\t' + str(calibInfo[1]) + '\t' + str(calibInfo[2]) + '\n')
        #Writes hardware specific calibration information to the header
        for x in reversed(range(5)):
            logfile_fp.write(str(aConstants[x][0]) + '\t' + str(aConstants[x][1]) + '\t' + str(aConstants[x][2]) + '\n')
        #Writes CLA information to file
        logfile_fp.write(str(aConstants[5][0]) + '\t' + str(aConstants[5][1]) + '\t' + str(aConstants[5][2]) + '\t' + str(aConstants[5][3]) + '\n')
        #Writes notes to file        
        for x in range(7,len(info)):
            if x == 11:
                #Writes firmware version on the appropriate line
                logfile_fp.write('Firmware Version Number (0.1 old, 1.x future e.g. 1.0) 1.1 = New Header, LSB of Activity is NOT a flag. 1.2 = New Header, LSB is a flag.\n')
            if x == len(info) - 1:
                logfile_fp.write(BATTERY_STRING)
                continue
            logfile_fp.write(info[x])
        logfile_fp.write('Calibration Factor (R,G,B)\nPhotopic Coefficient (R,G,B)\nScotopic Coefficient  (R,G,B)\nMelanopsin Coefficient (R,G,B)\nVlambda/macula Coefficient (R,G,B)\nScone Coefficient (R,G,B)\nCLA (a2,a3,K,A)')
    #Close the logfile
    finally:
        logfile_fp.close()

#Convert ANY header to an F0 header. This assumes that headers after F1
#follow the format of appending new imformation to the end of the header, and
#no new information was inserted. Appending in this sense means appended
#to the end of the values, and to the end of the notes.
def convertHeaderF0():
    import sys
    import logging
    from geterrlog import getErrLog
    from finddaysimeter import findDaysimeter
    import constants

    LOG_FILENAME = constants.LOG_FILENAME
    BATTERY_STRING = constants.BATTERY_STRING
    
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
        info = logfile_fp.readlines()
        #Remove binary garbage and whitesapce, if applicable, and format
        #strings in array.
        info = [x.strip('\n \xff') + '\n' for x in info]
        #magicNum is exactly that, magic
        magicNum = info.index(BATTERY_STRING)
        difference = len(info) - magicNum - 1
        #Remove everything after the battery string (in notes)
        del info[magicNum+1:]
        #Remove the inserted firmware version (in notes)
        del info[magicNum-6]
        #Remove everything after the battery string (in values)
        del info[magicNum-difference-10:magicNum-10]
        #Remove the interted firmware versoin (in notes)
        del info[1]
        #Close the file so we can open it again
        logfile_fp.close()
        #Open the file for writing
        #Note: This deletes the old file and writes a new one.
        logfile_fp = open(PATH + LOG_FILENAME, 'w')
        #Populate the header
        for x in info:
            logfile_fp.write(x)
    #Close the logfile
    finally:
        logfile_fp.close()