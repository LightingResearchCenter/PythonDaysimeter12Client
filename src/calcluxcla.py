#CalcLuxCLA
#Author: Jed Kundl
#Creation Date: 17.06.2013
#INPUT: Red, Green, Blue, daysimeterID
#OUTPUT: lux, CLA

import getConstants

def calcLuxCLA(red, green, blue):
    #Constants is a list of lists, with hardware specific constants
    constants = getConstants()    
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
        
    #Pack lux and CLA into a single list & return
    return [lux, CLA]
    
if __name__ == '__main__':calcLuxCLA([],[],[])