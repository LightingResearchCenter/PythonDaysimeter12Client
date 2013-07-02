"""
read_raw
Author: Jed Kundl
Creation Date: 13.06.2013
INPUT: log_file, data_file
OUTPUT: Data to be pased to a CDF processing script
"""

import sys
import struct
import logging
import time
import math
from datetime import datetime
from datetime import timedelta
from geterrlog import get_err_log
from adjactiveflag import adj_active_flag
from getcalibinfo import get_calib_info
from processconstants import process_constants
from calcluxcla import calc_lux_cla
from lowpassfilter import lowpass_filter
from calccs import calc_cs
from finddaysimeter import find_daysimeter
from datetimetodatenum import dt2dn
import constants as constants_

def read_raw():
    """
    PURPOSE: Reads raw binary data, processes and packages it for makecdf.py
    """
    log_filename = constants_.LOG_FILENAME
    data_filename = constants_.DATA_FILENAME
    adj_active_flag_ = constants_.ADJ_ACTIVE_FLAG
    old_flag = constants_.OLD_FLAG
    adj_active_firm = constants_.ADJ_ACTIVE_FIRM
    
    #Create error log file named error.log on the desktop
    errlog_filename = get_err_log()
    if errlog_filename == '':
        sys.exit(1)
    logging.basicConfig(filename=errlog_filename, level=logging.DEBUG)
    
    path = find_daysimeter()
    #Open header file for reading
    try:
        logfile_fp = open(path + log_filename,'r')
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
        old_flag = False
    
    #Find the daysimeter device ID
    if old_flag:
        daysimeter_id = int(info[1])
        device_model = constants_.DEVICE_MODEL
        device_sn = constants_.DEVICE_VERSION + info[1]
    else:
        daysimeter_id = int(info[3])
        device_model = info[2]
        device_sn = info[2].lstrip('abcdefghijklmnopqrstuvwxyz') + info[3]
    
    #Get calibration info
    if not old_flag:
        calib_const = [float(x) for x in info[9].strip('\n').split('\t')]
        calib_info = \
        [daysimeter_id, calib_const[0], calib_const[1], calib_const[2]]
    else:
        calib_info = get_calib_info(daysimeter_id)
        
    #Open binary data file for reading
    try:
        datafile_fp = open(path + data_filename,"rb")
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
    if not old_flag:
        struct_time = time.strptime(info[4], "%m-%d-%y %H:%M")
    else:
        struct_time = time.strptime(info[2], "%m-%d-%y %H:%M")
    epoch_time = datetime.fromtimestamp(time.mktime(struct_time))
    #log_interval is interval that the Daysimeter took measurements at.
    #Since python uses seconds since epoch, cast as int
    if not old_flag:
        log_interval = int(info[5])
    else:
        log_interval = int(info[3])
    
    #Determine the number of of logged entries. Why divded by 8?
    #I'm glad you asked! There are 4 things that are logged, and
    #each item takes up 2 bytes. So, we take the total number of
    #bytes (len(data)) and dived by 2*4. It makes so much sense!
    #I will admit, I only figure that out during debugging...
    num_entries = int(math.floor(len(data)/8))
    #Create lists for raw Red, Green, Blue, and Activity
    red = [-1] * num_entries
    green = [-1] * num_entries
    blue = [-1] * num_entries
    activity = [-1] * num_entries
    #Iteratively seperate data into raw R,G,B,A
    #struct.unpack unpacks binary data given a format.
    #>H is an unsigned short (16 bit unsigned integer) in big
    #endian notation.
    for x in range(0, num_entries):
        #If value is 65278 the daysimeter reset, skip and leave
        #the value at -1
        if struct.unpack('>H', data[x*8:x*8+2])[0] == 65278:
            continue
        #If value is 65535 there are no more entires to be
        #read. Remove 'empty' entries and break
        elif struct.unpack('>H', data[x*8:x*8+2])[0] == 65535:
            del red[x:]
            del green[x:]
            del blue[x:]
            del activity[x:]
            break
        red[x] = struct.unpack('>H', data[x*8:x*8+2])[0]
        green[x] = struct.unpack('>H', data[x*8+2:x*8+4])[0]
        blue[x] = struct.unpack('>H', data[x*8+4:x*8+6])[0]
        activity[x] = struct.unpack('>H', data[x*8+6:x*8+8])[0]
        
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
            y += 1
            continue
        resets[x] = y
        x += 1
    
    #If there were resets, R,G,B,A are now shorter than resets,
    #so we shall resize it.
    del resets[len(red):]
    
    #As of right now this uses either daysimeter_id (bad) or
    #firmware version (good). Once all daysimeters use a F1.x 
    #header or above, this code can be reduced to just the 
    #elif statement (as an if, of course )
    if old_flag:    
        if (daysimeter_id >= 54 and daysimeter_id <= 69) or daysimeter_id >= 83:
            adj_active_flag_ = True
    elif float(info[1]) in adj_active_firm:
        adj_active_flag_ = True
    
    #If we are using the firmware version where the LSB of
    #activity is actually a monitor for RGB values rolling over
    #we need to adjust the values accordingly.
    if adj_active_flag_:
        adjusted_rgb = adj_active_flag(red, green, blue, activity)
        #Unpack adjusted values
        red = adjusted_rgb[0]
        green = adjusted_rgb[1]
        blue = adjusted_rgb[2]
        
    #Create list for time called times (because time is
    #a python module)
    times = [-1] * len(red)
    mat_times = [-1] * len(red)
    #Iteratively 'generate' timestamps and place into times
    for x in range(0, len(times)):
        times[x] = epoch_time + timedelta(seconds=log_interval*x)
        mat_times[x] = dt2dn(times[x])
    
    #Activity is captured on the daysimeter as a mean squared
    #value (i.e. activity = x^2 + y^2 + z^2) and is measured in
    #counts. To get the number of g's, calculate the root mean
    #square (RMS) value and multiple by .0039 (the number of g's
    #per count) *4. The *4 comes from "four right shifts in the 
    #souce code." Basically, there is some bit shifting to maximize
    #storage space in the EEPROM, and we 'un-shift' it.
    activity = [math.sqrt(x)*.0039*4 for x in activity]
    
    #Apply calibration constants to raw data
    red = [x*calib_info[1] for x in red]
    green = [x*calib_info[2] for x in green]
    blue = [x*calib_info[3] for x in blue]
    
    #If new fireware, find constants in the header, process them, and
    #calculate lux and cla
    if not old_flag:
        constants = process_constants(info[14], info[13], info[12], \
        info[11], info[10], info[15])
        temp = calc_lux_cla(red, green, blue, constants)
    #Else, search for a constants file, process constants, and calculate
    #lux and cla
    else:
        temp = calc_lux_cla(red, green, blue)
    #Unpack lux and cla
    lux = temp[0]
    cla = temp[1]

    del(temp)
    #Apply a zero phase shift filter to cla and activity
    cla = lowpass_filter(cla, log_interval)
    activity = lowpass_filter(activity, log_interval)
    #Calculate cs
    cs = calc_cs(cla)

    #Return a tuple of lists of mixed lists. The first list in the tuple is
    #global attributes, and the second is variable data
    return ([device_model, device_sn, calib_info], \
    [times, mat_times, red, green, blue, lux, cla, cs, activity, resets])

if __name__ == '__main__':
    read_raw()