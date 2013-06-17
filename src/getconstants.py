#GetConstants
#Author: Jed Kundl
#Creation Date: 17.06.2013
#INPUT:
#OUTPUT: Constants to calculate CLA and lux

CONSTANTS_FILENAME = '//root/projects/Daysimeter and dimesimeter reference files/data/Day12 Cal Values.txt'
LOCAL_CONST_FILENAME = 'Day12 Cal Values.txt'

import sys
import logging
import getErrLog

def getConstants ():
    #Create error log file named error.log on the desktop
    ERRLOG_FILENAME = getErrLog()
    logging.basicConfig(filename=ERRLOG_FILENAME,level=logging.DEBUG)
    
    if True:
        #Open constants file and get data
        try:
            constants_fp = open(CONSTANTS_FILENAME,"r")
        #Catch IO exception, add to log and continue
        except IOError:
            logging.error('Could not open constants file from server')
            pass
        #Read data into lists
        else:
            #Trash handles header and/or empty lines in the file.
            #This unfortunately means that the file structure
            #cannot be changed.
            trash = constants_fp.readline()
            sconeMacula = constants_fp.readline()
            vLamdaMacula = constants_fp.readline()
            melanopsin = constants_fp.readline()
            vPrime = constants_fp.readline()
            vLamda = constants_fp.readline()
            trash = constants_fp.readline()
            trash = constants_fp.readline()
            CLA = constants_fp.readline()
            del(trash)
        #Close the file
        finally:
            constants_fp.close()
    
    else:
        #Open constants file and get data
        try:
            constants_fp = open(LOCAL_CONST_FILENAME,"r")
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
            sconeMacula = constants_fp.readline()
            vLamdaMacula = constants_fp.readline()
            melanopsin = constants_fp.readline()
            vPrime = constants_fp.readline()
            vLamda = constants_fp.readline()
            trash = constants_fp.readline()
            trash = constants_fp.readline()
            CLA = constants_fp.readline()
            del(trash)
        #Close the file
        finally:
            constants_fp.close()
    
    #Process data by eliminating tabs, newlines, and leading/trailing
    #spaces. Then, it deletes the first element of each list (the name)
    #and converts the reaming elements to floats.
    sconeMacula = [x.strip('\n') for x in sconeMacula.split('\t') if x.strip()]
    vLamdaMacula = [x.strip('\n') for x in vLamdaMacula.split('\t') if x.strip()]
    melanopsin = [x.strip('\n') for x in melanopsin.split('\t') if x.strip()]
    vPrime = [x.strip('\n') for x in vPrime.split('\t') if x.strip()]
    vLamda = [x.strip('\n') for x in vLamda.split('\t') if x.strip()]
    CLA = [x.strip('\n') for x in CLA.split('\t') if x.strip()]
    
    del(sconeMacula[0])
    del(vLamdaMacula[0])
    del(melanopsin[0])
    del(vPrime[0])
    del(vLamda[0])
    del(CLA[0])
    
    sconeMacula = [float(x) for x in sconeMacula]
    vLamdaMacula = [float(x) for x in vLamdaMacula]
    melanopsin = [float(x) for x in melanopsin]
    vPrime = [float(x) for x in vPrime]
    vLamda = [float(x) for x in vLamda]
    CLA = [float(x) for x in CLA]
    
    #Pack constants into a single list & return
    return [sconeMacula, vLamdaMacula, melanopsin, vPrime, vLamda, CLA]
    
if __name__ == '__main__':getConstants()