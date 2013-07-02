"""
updateheader.py
Author: Jed Kundl
Creation Date: 26.06.2013
"""
import constants
from finddaysimeter import find_daysimeter

def update_header():
    """
    PURPOSE: Function checks to see whether daysimeter's header is out of date.
    If it is, function returns True, else function returns False.
    """
    log_filename = constants.LOG_FILENAME
    path = find_daysimeter()
    
    with open(path + log_filename, 'r') as log_fp:
        info = log_fp.readlines()
        if len(info) == 17:
            return True
    return False