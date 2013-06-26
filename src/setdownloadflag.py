"""
set_download_flag
Author: Jed Kundl
Creation Date: 24.06.2013
INPUT: 
OUTPUT: 
"""

import constants
from finddaysimeter import find_daysimeter

def set_download_flag():
    """ PURPOSE: Sets download flag to true (0) once download is compelte. """
    path = find_daysimeter()
    log_filename = constants.LOG_FILENAME
    
    try:
        logfile_fp = open(path + log_filename,'r+')
    #This function will only ever be called if the logfile was previously
    #opened. So I chose to not bother with error handling here because
    #it's unnecessary.
    except IOError:
        pass
    else:
        #Read each line of the header and put it into a list
        #called info.
        info = logfile_fp.readlines()
        #Change status to downloaded
        #If 0.x header (pre-firmware versions being stored in header)
        if len(info) <= 17:
            info[5] = '0\n'
        #Else if version 1.x
        #I did it like this so it can be expanded easily in the future.
        #If for example the location of download flag changed to position
        #8 in firmware version 2.x, just add another elif statement
        #e.g. elif info[1][0:2] == '2.': info[8] ... you get the idea
        elif info[1][0:2] == '1.':
            info[7] = '0\n'
        #Return to top of file
        logfile_fp.seek(0)
        #Write everything to file
        for x in info:
            logfile_fp.write(x)
    #Close the logfile
    finally:
        logfile_fp.close()