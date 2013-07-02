"""
get_constants
Author: Jed Kundl
Creation Date: 17.06.2013
INPUT:
OUTPUT: Constants to calculate cla and lux
"""

import sys
import logging
from geterrlog import get_err_log
import constants

def get_constants ():  
    """ PURPOSE: Get constants for calculations. """
    constants_filename = constants.CONSTANTS_FILENAME
    local_const_filename = constants.LOCAL_CONST_FILENAME

    #Create error log file named error.log on the desktop
    errlog_filename = get_err_log()
    logging.basicConfig(filename=errlog_filename, level=logging.DEBUG)
    
    if True:
        #Open constants file and get data
        try:
            constants_fp = open(constants_filename,"r")
        #Catch IO exception, add to log and continue
        except IOError:
            logging.error('Could not open constants file from server')
        #Read data into lists
        else:
            #Trash handles header and/or empty lines in the file.
            #This unfortunately means that the file structure
            #cannot be changed.
            trash = constants_fp.readline()
            scone_macula = constants_fp.readline()
            v_lamda_macula = constants_fp.readline()
            melanopsin = constants_fp.readline()
            v_prime = constants_fp.readline()
            v_lamda = constants_fp.readline()
            trash = constants_fp.readline()
            trash = constants_fp.readline()
            cla = constants_fp.readline()
            del(trash)
        #Close the file
        finally:
            constants_fp.close()
            
    else:
        #Open constants file and get data
        try:
            constants_fp = open(local_const_filename,"r")
        #Catch IO exception, add to log and quit
        except IOError:
            logging.error('Could not open constants file locally')
            sys.exit(1)
        #Read data into lists
        else:
            #Trash handles header and/or empty lines in the file.
            #This unfortunately means that the file structure
            #cannot be changed.
            trash = constants_fp.readline()
            scone_macula = constants_fp.readline()
            v_lamda_macula = constants_fp.readline()
            melanopsin = constants_fp.readline()
            v_prime = constants_fp.readline()
            v_lamda = constants_fp.readline()
            trash = constants_fp.readline()
            trash = constants_fp.readline()
            cla = constants_fp.readline()
            del(trash)
        #Close the file
        finally:
            constants_fp.close()
            
    #Process data by eliminating tabs, newlines, and leading/trailing
    #spaces. Then, it deletes the first element of each list (the name)
    #and converts the reaming elements to floats.
    scone_macula = \
    [x.strip('\n') for x in scone_macula.split('\t') if x.strip()]
    v_lamda_macula = \
    [x.strip('\n') for x in v_lamda_macula.split('\t') if x.strip()]
    melanopsin = [x.strip('\n') for x in melanopsin.split('\t') if x.strip()]
    v_prime = [x.strip('\n') for x in v_prime.split('\t') if x.strip()]
    v_lamda = [x.strip('\n') for x in v_lamda.split('\t') if x.strip()]
    cla = [x.strip('\n') for x in cla.split('\t') if x.strip()]
    
    del(scone_macula[0])
    del(v_lamda_macula[0])
    del(melanopsin[0])
    del(v_prime[0])
    del(v_lamda[0])
    del(cla[0])
    
    scone_macula = [float(x) for x in scone_macula]
    v_lamda_macula = [float(x) for x in v_lamda_macula]
    melanopsin = [float(x) for x in melanopsin]
    v_prime = [float(x) for x in v_prime]
    v_lamda = [float(x) for x in v_lamda]
    cla = [float(x) for x in cla]
    
    #Pack constants into a single list & return
    return [scone_macula, v_lamda_macula, melanopsin, v_prime, v_lamda, cla]