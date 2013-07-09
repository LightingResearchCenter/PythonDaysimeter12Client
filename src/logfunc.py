"""
stoplog
Author: Jed Kundl
Creation Date: 08.07.2013
"""

from finddaysimeter import find_daysimeter
import constants

def stop_log():
    path = find_daysimeter()
    log_filename = constants.LOG_FILENAME
    
    if not path:
        return False
        
    with open(path + log_filename, 'r') as log_fp:
        log = log_fp.readlines()
    log[0] = '0\n'
    with open(path + log_filename, 'w') as log_fp:
        for x in log:
            log_fp.write(x)
            
def resume_log():
    path = find_daysimeter()
    log_filename = constants.LOG_FILENAME
    
    if not path:
        return False
        
    with open(path + log_filename, 'r') as log_fp:
        log = log_fp.readlines()
    log[0] = '4\n'
    with open(path + log_filename, 'w') as log_fp:
        for x in log:
            log_fp.write(x)        