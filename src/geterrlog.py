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

def get_err_log():
    """ PURPOSE: Returns the desktop directory to store the error log. """
    #If Windows, place on desktop
    if sys.platform == 'win32':
        return 'C:\Program Files (x86)\Daysimeter Client\error.log'
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