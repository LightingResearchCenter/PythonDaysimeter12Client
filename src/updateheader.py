"""
updateheader.py
Author: Jed Kundl
Creation Date: 26.06.2013
"""
import constants
from finddaysimeter import find_daysimeter
import logging

def update_header():
    """
    PURPOSE: Function checks to see whether daysimeter's header is out of date.
    If it is, function returns True, else function returns False.
    """
    info_log = logging.getLogger('daysim_log')
    
    info_log.info('updateheader.py func update_header: Searching for Daysimeter')
    log_filename = constants.LOG_FILENAME
    path = find_daysimeter()
    info_log.info('updateheader.py func update_header: Daysimeter found')
    
    info_log.info('updateheader.py func update_header: Opening Daysimeter header file')
    with open(path + log_filename, 'r') as log_fp:
        info_log.info('updateheader.py func update_header: Reading Daysimeter header file')
        info = log_fp.readlines()
        if len(info) == 17:
            info_log.info('updateheader.py func update_header: Header is v0, should be updated')
            return True
        elif not len(info[3]) == 3:
            info_log.info('updateheader.py func update_header: Header is v1, must be updated')
            return True
    info_log.info('updateheader.py func update_header: Header is v2, up to date')
    return False