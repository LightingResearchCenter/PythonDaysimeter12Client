"""
set_download_flag
Author: Jed Kundl
Creation Date: 24.06.2013
"""

import constants, logging
from finddaysimeter import find_daysimeter

def set_download_flag():
    """
    PURPOSE: Once binary data has been downloaded, processed and saved, this
    function modifies the header file and sets the download flag to downloaded (0)
    """
    path = find_daysimeter()
    log_filename = constants.LOG_FILENAME
    
    info_log = logging.getLogger('daysim_log')    
    info_log.info('setdownloadflag.py func set_download_flag: Finding Daysimeter log file')
    
    try:
        logfile_fp = open(path + log_filename,'r+')
    #This function will only ever be called if the logfile was previously
    #opened. So I chose to not bother with error handling here because
    #it's unnecessary.
    except IOError:
        info_log.info('setdownloadflag.py func set_download_flag: No log file found')
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
            info[5] = '0\n'
        #Return to top of file
        logfile_fp.seek(0)
        #Write everything to file
        for x in info:
            logfile_fp.write(x)
        info_log.info('setdownloadflag.py func set_download_flag: Log file found, download flag set')
    #Close the logfile
    finally:
        logfile_fp.close()