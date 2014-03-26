"""
stoplog
Author: Jed Kundl
Creation Date: 08.07.2013
"""

from finddaysimeter import find_daysimeter
import constants, logging

def stop_log():
    info_log = logging.getLogger('daysim_log')    
    
    path = find_daysimeter()
    log_filename = constants.LOG_FILENAME
    
    if not path:
        info_log.info('logfunc.py func stop_log: Daysimeter not found')
        return False
        
    with open(path + log_filename, 'r') as log_fp:
        log = log_fp.readlines()
    log[0] = '0\n'
    with open(path + log_filename, 'w') as log_fp:
        for x in log:
            log_fp.write(x)
    info_log.info('logfunc.py func stop_log: Log stopped')
    return True
            
def resume_log():
    info_log = logging.getLogger('daysim_log')    
    
    path = find_daysimeter()
    log_filename = constants.LOG_FILENAME
    
    if not path:
        info_log.info('logfunc.py func resume_log: Daysimeter not found')
        return False
        
    with open(path + log_filename, 'r') as log_fp:
        log = log_fp.readlines()
    log[0] = '4\n'
    with open(path + log_filename, 'w') as log_fp:
        for x in log:
            log_fp.write(x)
    info_log.info('logfunc.py func resume_log: Log resumed')
    return True