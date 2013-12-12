"""
get_err_log
Author: Jed Kundl
Creation Date: 17.06.2013
INPUT: 
OUTPUT: Location of error log
"""

import sys
import os
import pwd
import logging

def get_err_log():
    """ PURPOSE: Returns the desktop directory to store the error log. """
    #If Windows, place in program files
    if sys.platform == 'win32':
        return 'C:\Daysimeter Client\error.log'
    #Else if Mac OSX, place on desktop
    elif sys.platform == 'darwin':
        return '/Users/' + pwd.getpwuid(os.getuid())[0] + '/Desktop/error.log'
    #Else if Linux, place on desktop
    elif sys.platform.startswith('linux'):
        return '/home/' + pwd.getpwuid(os.getuid())[0] + '/Desktop/error.log'
    #Else, well hopfully you are running Linux, Mac, or Windows
    #Because without the error log, I have no place to write an
    #error that you're using an incompatiple system.
    else:
        return ''
        
def get_daysim_log():
    """ PURPOSE: Returns the  directory to store the daysimeter log. """
    #If Windows, place in program files
    if sys.platform == 'win32':
        return 'C:\Daysimeter Client\daysimeter.log'
    #Else if Mac OSX, place on desktop
    elif sys.platform == 'darwin':
        return '/Users/' + pwd.getpwuid(os.getuid())[0] + '/Desktop/daysimeter.log'
    #Else if Linux, place on desktop
    elif sys.platform.startswith('linux'):
        return '/home/' + pwd.getpwuid(os.getuid())[0] + '/Desktop/daysimeter.log'
    #Else, well hopfully you are running Linux, Mac, or Windows
    #Because without the error log, I have no place to write an
    #error that you're using an incompatiple system.
    else:
        return ''
        
def setup_logger(logger_name, log_file, level=logging.INFO):
    
    if os.path.getsize(log_file) > 64000:
        with open(log_file, 'r') as log_fp:
            data = log_fp.readlines()
            data = data[len(data)-100:]
        with open(log_file, 'w') as log_fp:
            for line in data:
                log_fp.write(line)
        
    log = logging.getLogger(logger_name)
    formatter = logging.Formatter('%(asctime)s : %(message)s')
    fileHandler = logging.FileHandler(log_file, mode='a')
    fileHandler.setFormatter(formatter)
#    streamHandler = logging.StreamHandler()
#    streamHandler.setFormatter(formatter)

    log.setLevel(level)
    log.addHandler(fileHandler)
#    log.addHandler(streamHandler)

    return logging.getLogger(logger_name)    
