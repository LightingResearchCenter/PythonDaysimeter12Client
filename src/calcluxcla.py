#CalcLuxCLA
#Author: Jed Kundl
#Creation Date: 17.06.2013
#INPUT: Red, Green, Blue, daysimeterID
#OUTPUT: lux, CLA

import sys
import logging
from getconstants import getConstants
from geterrlog import getErrLog

#calcLuxCLA either takes 3 or 4 arguments. Usage: red, green, blue, [constants]
def calcLuxCLA(*args):
    ERRLOG_FILENAME = getErrLog()
    logging.basicConfig(filename=ERRLOG_FILENAME,level=logging.DEBUG)
    
    if len(args) == 3:
        red = args[0]
        green = args[1]
        blue = args[2]
        #Constants is a list of lists, with hardware specific constants
        constants = getConstants()
    elif len(args) == 4:
        red = args[0]
        green = args[1]
        blue = args[2]
        constants = args[3]
    else:
        logging.warning('Invalid usage of calcLuxCLA')
        sys.exit(1)
        
    loopMax = numEntries = len(constants[0])
    
    #Create lux list and allocate space
    lux = [-1] * numEntries
    #Calculate and fill lux
    for x in range(0,loopMax):
        lux[x] = constants[4][0]*red[x] + constants[4][1]*green[x] + constants[4][2]*blue[x]
        
    #Create lists and allocate space for each list
    sconeMacula = [-1] * numEntries
    vLamdaMacula =  [-1] * numEntries
    melanopsin =  [-1] * numEntries
    vPrime =  [-1] * numEntries
    CLA = [-1] * numEntries
    
    #Following is lots of fancy math which I do not understand the
    #reasoning for. I based it off the MatLab code, with some exceptions
    #to optimize code for python
    for x in range(0,loopMax):
        sconeMacula[x] = constants[0][0]*red[x] + constants[0][1]*green[x] + constants[0][2]*blue[x]
        vLamdaMacula[x] = constants[1][0]*red[x] + constants[1][1]*green[x] + constants[1][2]*blue[x]
        melanopsin[x] = constants[2][0]*red[x] + constants[2][1]*green[x] + constants[2][2]*blue[x]
        vPrime[x] = constants[3][0]*red[x] + constants[3][1]*green[x] + constants[3][2]*blue[x]
        
        if sconeMacula[x] > vLamdaMacula[x] * constants[5][2]:
            #Some super fancy math. I wish I knew what was going on here...
            CLA[x] = melanopsin[x] + constants[5][0] * (sconeMacula[x] - vLamdaMacula[x] * constants[5][2]) - constants[5][1]*683*(1 - 2.71^(-(vPrime[x]/(683*6.5))));
        else:
            CLA[x] = melanopsin[x]
            
        CLA[x] *= constants[5][3]
        CLA = [0 if x < 0 else x for x in CLA]
    #Pack lux and CLA into a single list & return
    return [lux, CLA]
    
if __name__ == '__main__':calcLuxCLA([],[],[])