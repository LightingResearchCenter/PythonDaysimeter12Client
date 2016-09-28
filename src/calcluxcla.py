"""
calc_lux_cla
Author: Jed Kundl
Creation Date: 17.06.2013
INPUT: Red, Green, Blue, daysimeterID
OUTPUT: lux, cla
NOTE: calc_lux_cla either takes 3 or 4 arguments. Usage: red, green, blue, [constants]
"""

import sys
import logging
from getconstants import get_constants
from getlogs import get_err_log, get_daysim_log, setup_logger

def calc_lux_cla(*args): 
    """
    PURPOSE: Calculates CS and CLA.
    NOTE: A modified version of this exists in downloadmake.py and this version
    is no logner called.    
    """
    
    errlog_filename = get_err_log()
    setup_logger('errlog', errlog_filename)
    errlog = logging.getLogger('errlog')
    
    daysimlog_filename = get_daysim_log()
    setup_logger('daysimlog', daysimlog_filename)
    daysimlog = logging.getLogger('daysimlog')
    
    if len(args) == 4:
        red = args[0]
        green = args[1]
        blue = args[2]
        device_id = args[3]
        #Constants is a list of lists, with hardware specific constants
        constants = get_constants(device_id)
    elif len(args) == 5:
        red = args[0]
        green = args[1]
        blue = args[2]
        device_id = args[3]
        constants = args[4]
    else:
        errlog.warning('Invalid usage of calc_lux_cla')
        sys.exit(1)
      
    loop_max = num_entries = len(red)
    
    #Create lux list and allocate space
    lux = [-1] * num_entries
    #Calculate and fill lux
    for x in range(0, loop_max):
        lux[x] = constants[4][0]*red[x] + constants[4][1]*green[x] + \
        constants[4][2]*blue[x]
     
    #Create lists and allocate space for each list
    scone_macula = [-1] * num_entries
    v_lamda_macula =  [-1] * num_entries
    melanopsin =  [-1] * num_entries
    v_prime =  [-1] * num_entries
    cla = [-1] * num_entries
    
    #Following is lots of fancy math which I do not understand the
    #reasoning for. I based it off the MatLab code, with some exceptions
    #to optimize code for python
    for x in range(0, loop_max):
        scone_macula[x] = constants[0][0]*red[x] + constants[0][1]*green[x] + \
        constants[0][2]*blue[x]
        v_lamda_macula[x] = constants[1][0]*red[x] + \
        constants[1][1]*green[x] + constants[1][2]*blue[x]
        melanopsin[x] = constants[2][0]*red[x] + constants[2][1]*green[x] + \
        constants[2][2]*blue[x]
        v_prime[x] = constants[3][0]*red[x] + constants[3][1]*green[x] + \
        constants[3][2]*blue[x]
        
        if scone_macula[x] > v_lamda_macula[x] * constants[5][2]:
            #Some super fancy math. I wish I knew what was going on here...
            cla[x] = melanopsin[x] + constants[5][0] * (scone_macula[x] - \
            v_lamda_macula[x] * constants[5][2]) - \
            constants[5][1]*683*(1 - 2.71**(-(v_prime[x]/(683*6.5))))
        else:
            cla[x] = melanopsin[x]
            
        cla[x] *= constants[5][3]
    cla = [0 if x < 0 else x for x in cla]
    #Pack lux and cla into a single list & return
    return [lux, cla]