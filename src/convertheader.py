"""
ConvertHeader
Author: Jed Kundl
Creation Date: 20.06.2013
"""

import sys
import os
import logging
from getlogs import get_err_log, get_daysim_log, setup_logger
from getcalibinfo import get_calib_info
from getconstants import get_constants
from finddaysimeter import find_daysimeter
import constants

def convert_header(version):
    """ Determines current header and converts it to version """
    path = find_daysimeter()
    log_filename = constants.LOG_FILENAME
    
    with open(os.path.join(path, log_filename), 'r') as fp:
        info = fp.readlines()
    info = [x.strip('\n \xff') for x in info]
    
    if len(info) == 17:
        if version == 'h0':
            return
        elif version == 'h1':
            convert_header_h1()
            return
        elif version == 'h2':
            convert_header_h2()
            return
            
    else:
        if info[1] in {'1.1', '1.2'}:
            if info[27] == 'ID number(Do Not Change)':
                current_version = 'h1'
            else:
                current_version = 'h2'
    
    if current_version == version:
        return
    elif current_version == 'h1':
        convert_header_h01()        
        if version == 'h0':
            return
        elif version == 'h2':
            convert_header_h2()
    elif current_version == 'h2':
        convert_header_h02()
        if version == 'h0':
            return
        elif version == 'h1':
            convert_header_h1()
            
def convert_header_h2():
    """
    Convert an F0 header file into an h2 header file
    An F0 header is any 0.x header (Original Daysimeter 12 standard) and
    An F1 header is and 1.x header (New Daysimeter 12 standard)
    An example F1 header is available at //root/Public/bierma2 from within
    The LRC's network as of 20.06.2013
    """
    print 'here'
    log_filename = constants.LOG_FILENAME
    battery_string = constants.BATTERY_STRING
    firm_12 = constants.FIRM12
    
    #Create error log file named error.log on the desktop
    errlog_filename = get_err_log()
    setup_logger('errlog', errlog_filename)
    errlog = logging.getLogger('errlog')
    
    daysimlog_filename = get_daysim_log()
    setup_logger('daysimlog', daysimlog_filename)
    daysimlog = logging.getLogger('daysimlog')
    
    path = find_daysimeter()
    #Open header file for reading and editing
    try:
        logfile_fp = open(path + log_filename,"r+")
    #Catch IO exception (if present), add to log and quit
    except IOError:
        errlog.error('Could not open logfile')
        sys.exit(1)
    else:
        #Read each line of the header and put it into a list
        #called info.
        info = logfile_fp.readlines()
        calib_info = get_calib_info(int(info[1]))
        del(calib_info[0])
        a_constants = get_constants()
        #Remove binary garbage and whitesapce, if applicable, and format
        #strings in array.
        info = [x.strip('\n \xff') + '\n' for x in info]
        logfile_fp.close()
        os.remove(path + log_filename)
        logfile_fp = open(path + log_filename,'w')
        logfile_fp.write(info[0])
        #firm_12 is a set of daysimeter IDs below 83 (the official change
        #over) that use the LSB of activity as a rollover flag for RGB. 
        if int(info[1]) in firm_12 or int(info[1]) >= 83:
            logfile_fp.write('1.2\ndaysimeter12\n')
        else:
            logfile_fp.write('1.1\ndaysimeter12\n')
        #Shifts information down because firmware version is now on line 1
        print info[3]
        logfile_fp.write(info[3])
        logfile_fp.write(info[4])
        logfile_fp.write(info[5])
        logfile_fp.write(info[6])
        logfile_fp.write(info[2])
        print info[1]
        logfile_fp.write(info[1])
        
        #Write calibration information to file. Woohoo for putting this
        #information in the header instead of doing crazy lookups.
        logfile_fp.write(str(calib_info[0]) + '\t' + str(calib_info[1]) + \
        '\t' + str(calib_info[2]) + '\n')
        #Writes hardware specific calibration information to the header
        for x in reversed(range(5)):
            logfile_fp.write(str(a_constants[x][0]) + '\t' + \
            str(a_constants[x][1]) + '\t' + str(a_constants[x][2]) + '\n')
        #Writes CLA information to file
        logfile_fp.write(str(a_constants[5][0]) + '\t' + \
        str(a_constants[5][1]) + '\t' + str(a_constants[5][2]) + '\t' + \
        str(a_constants[5][3]) + '\n')
        #Writes notes to file        
        for x in range(7, len(info)):
            if x == 11:
                #Writes firmware version on the appropriate line
                logfile_fp.write('Firmware Version Number (0.1 old, 1.x ' + \
                'future e.g. 1.0) 1.1 = New Header, LSB of Activity is NOT' + \
                ' a flag. 1.2 = New Header, LSB is a flag.\nDevice Model\n')
                logfile_fp.write(info[13])
                continue
            if x == 12:
                logfile_fp.write(info[14])
                logfile_fp.write(info[15])
                logfile_fp.write(battery_string)
                logfile_fp.write(info[12])
                logfile_fp.write(info[11])
                break
            logfile_fp.write(info[x])
        logfile_fp.write('Calibration Factor (R,G,B)\nPhotopic Coefficient' + \
        ' (R,G,B)\nScotopic Coefficient  (R,G,B)\nMelanopsin Coefficient ' + \
        '(R,G,B)\nVlambda/macula Coefficient (R,G,B)\nScone Coefficient ' + \
        '(R,G,B)\nCLA (a2,a3,K,A)')
    #Close the logfile
    finally:
        logfile_fp.close()
        

def convert_header_h1():
    """
    Convert an F0 header file into an F1 header file
    An F0 header is any 0.x header (Original Daysimeter 12 standard) and
    An F1 header is and 1.x header (New Daysimeter 12 standard)
    An example F1 header is available at //root/Public/bierma2 from within
    The LRC's network as of 20.06.2013
    """
    log_filename = constants.LOG_FILENAME
    battery_string = constants.BATTERY_STRING
    firm_12 = constants.FIRM12
    
    #Create error log file named error.log on the desktop
    errlog_filename = get_err_log()
    setup_logger('errlog', errlog_filename)
    errlog = logging.getLogger('errlog')
    
    daysimlog_filename = get_daysim_log()
    setup_logger('daysimlog', daysimlog_filename)
    daysimlog = logging.getLogger('daysimlog')
    
    path = find_daysimeter()
    #Open header file for reading and editing
    try:
        logfile_fp = open(path + log_filename,"r+")
    #Catch IO exception (if present), add to log and quit
    except IOError:
        errlog.error('Could not open logfile')
        sys.exit(1)
    else:
        #Read each line of the header and put it into a list
        #called info.
        info = logfile_fp.readlines()
        calib_info = get_calib_info(int(info[1]))
        del(calib_info[0])
        a_constants = get_constants()
        #Remove binary garbage and whitesapce, if applicable, and format
        #strings in array.
        info = [x.strip('\n \xff') + '\n' for x in info]
        logfile_fp.close()
        os.remove(path + log_filename)
        logfile_fp = open(path + log_filename,'w')
        logfile_fp.write(info[0])
        #firm_12 is a set of daysimeter IDs below 83 (the official change
        #over) that use the LSB of activity as a rollover flag for RGB. 
        if int(info[1]) in firm_12 or int(info[1]) >= 83:
            logfile_fp.write('1.2\ndaysimeter12\n')
        else:
            logfile_fp.write('1.1\ndaysimeter12\n')
        #Shifts information down because firmware version is now on line 1
        logfile_fp.write(info[1])
        logfile_fp.write(info[4])
        logfile_fp.write(info[5])
        logfile_fp.write(info[6])
        logfile_fp.write(info[2])
        logfile_fp.write(info[3])
        #Write calibration information to file. Woohoo for putting this
        #information in the header instead of doing crazy lookups.
        logfile_fp.write(str(calib_info[0]) + '\t' + str(calib_info[1]) + \
        '\t' + str(calib_info[2]) + '\n')
        #Writes hardware specific calibration information to the header
        for x in reversed(range(5)):
            logfile_fp.write(str(a_constants[x][0]) + '\t' + \
            str(a_constants[x][1]) + '\t' + str(a_constants[x][2]) + '\n')
        #Writes CLA information to file
        logfile_fp.write(str(a_constants[5][0]) + '\t' + \
        str(a_constants[5][1]) + '\t' + str(a_constants[5][2]) + '\t' + \
        str(a_constants[5][3]) + '\n')
        #Writes notes to file        
        for x in range(7, len(info)):
            if x == 11:
                #Writes firmware version on the appropriate line
                logfile_fp.write('Firmware Version Number (0.1 old, 1.x ' + \
                'future e.g. 1.0) 1.1 = New Header, LSB of Activity is NOT' + \
                ' a flag. 1.2 = New Header, LSB is a flag.\nDevice Model\n')
            if x == 12:
                logfile_fp.write(info[14])
                logfile_fp.write(info[15])
                logfile_fp.write(battery_string)
                logfile_fp.write(info[12])
                logfile_fp.write(info[13])
                break
            logfile_fp.write(info[x])
        logfile_fp.write('Calibration Factor (R,G,B)\nPhotopic Coefficient' + \
        ' (R,G,B)\nScotopic Coefficient  (R,G,B)\nMelanopsin Coefficient ' + \
        '(R,G,B)\nVlambda/macula Coefficient (R,G,B)\nScone Coefficient ' + \
        '(R,G,B)\nCLA (a2,a3,K,A)')
    #Close the logfile
    finally:
        logfile_fp.close()
        
def convert_header_h02():
    """
    Convert ANY h2 or beyond header to an F0 header. This assumes that headers after F1
    follow the format of appending new imformation to the end of the header, 
    and no new information was inserted. Appending in this sense means appended
    to the end of the values, and to the end of the notes.
    """
    
    log_filename = constants.LOG_FILENAME
    battery_string = constants.BATTERY_STRING
    
    #Create error log file named error.log on the desktop
    errlog_filename = get_err_log()
    errlog_filename = get_err_log()
    setup_logger('errlog', errlog_filename)
    errlog = logging.getLogger('errlog')
    
    daysimlog_filename = get_daysim_log()
    setup_logger('daysimlog', daysimlog_filename)
    daysimlog = logging.getLogger('daysimlog')
    
    path = find_daysimeter()
    #Open header file for reading
    try:
        logfile_fp = open(path + log_filename,'r')
    #Catch IO exception (if present), add to log and quit
    except IOError:
        errlog.error('Could not open logfile')
        sys.exit(1)
    else:
        #Read each line of the header and put it into a list
        #called info.
        info = logfile_fp.readlines()
        #Close the file so we can open it again
        logfile_fp.close()
        #Remove binary garbage and whitesapce, if applicable, and format
        #strings in array.
        info = [x.strip('\n \xff') + '\n' for x in info]
        if len(info) == 17:
            return
        #Reference index for data to be moved about
        ref_index = info.index(battery_string)
        #Moves notes around
        info[ref_index - 5] = info[ref_index - 3]
        info[ref_index - 4] = info[ref_index + 1]
        info[ref_index - 3] = info[ref_index + 2]
        #Moves values around
        info[1] = info[8]
        info[2] = info[7]
        #magic_num is exactly that, magic
        magic_num = info.index(battery_string)
        difference = len(info) - magic_num - 1
        #Remove everything after the battery string (in notes)
        del info[magic_num+1:]
        #Remove everything after the battery string (in values)
        del info[magic_num-difference-9:magic_num-9]
        #Open the file for writing
        #Note: This deletes the old file and writes a new one.
        logfile_fp = open(path + log_filename, 'w')
        #Populate the header
        for x in info:
            logfile_fp.write(x)
    #Close the logfile
    finally:
        logfile_fp.close()        
        

def convert_header_h01():
    """
    Convert ANY header to an F0 header. This assumes that headers after F1
    follow the format of appending new imformation to the end of the header, 
    and no new information was inserted. Appending in this sense means appended
    to the end of the values, and to the end of the notes.
    """
    
    log_filename = constants.LOG_FILENAME
    battery_string = constants.BATTERY_STRING
    
    #Create error log file named error.log on the desktop
    errlog_filename = get_err_log()
    errlog_filename = get_err_log()
    setup_logger('errlog', errlog_filename)
    errlog = logging.getLogger('errlog')
    
    daysimlog_filename = get_daysim_log()
    setup_logger('daysimlog', daysimlog_filename)
    daysimlog = logging.getLogger('daysimlog')
    
    path = find_daysimeter()
    #Open header file for reading
    try:
        logfile_fp = open(path + log_filename,'r')
    #Catch IO exception (if present), add to log and quit
    except IOError:
        errlog.error('Could not open logfile')
        sys.exit(1)
    else:
        #Read each line of the header and put it into a list
        #called info.
        info = logfile_fp.readlines()
        #Close the file so we can open it again
        logfile_fp.close()
        #Remove binary garbage and whitesapce, if applicable, and format
        #strings in array.
        info = [x.strip('\n \xff') + '\n' for x in info]
        if len(info) == 17:
            return
        #Reference index for data to be moved about
        ref_index = info.index(battery_string)
        #Moves notes around
        info[ref_index - 5] = info[ref_index - 3]
        info[ref_index - 4] = info[ref_index + 1]
        info[ref_index - 3] = info[ref_index + 2]
        #Moves values around
        info[1] = info[3]
        info[2] = info[7]
        info[3] = info[8]
        #magic_num is exactly that, magic
        magic_num = info.index(battery_string)
        difference = len(info) - magic_num - 1
        #Remove everything after the battery string (in notes)
        del info[magic_num+1:]
        #Remove everything after the battery string (in values)
        del info[magic_num-difference-9:magic_num-9]
        #Open the file for writing
        #Note: This deletes the old file and writes a new one.
        logfile_fp = open(path + log_filename, 'w')
        #Populate the header
        for x in info:
            logfile_fp.write(x)
    #Close the logfile
    finally:
        logfile_fp.close()