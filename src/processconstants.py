#ProcessConstants
#Author: Jed Kundl
#Creation Date: 17.06.2013
#INPUT: sconeMacula, vLamdaMacula, melanopsin, vPrime, vLamda, CLA
#OUTPUT: Constants to calculate CLA and lux

def processConstants(sconeMacula, vLamdaMacula, melanopsin, vPrime, vLamda, CLA):
    #Process data by eliminating tabs, newlines, and leading/trailing
    #spaces. Then, it deletes the first element of each list (the name)
    #and converts the reaming elements to floats.
    sconeMacula = [x.strip('\n') for x in sconeMacula.split('\t') if x.strip()]
    vLamdaMacula = [x.strip('\n') for x in vLamdaMacula.split('\t') if x.strip()]
    melanopsin = [x.strip('\n') for x in melanopsin.split('\t') if x.strip()]
    vPrime = [x.strip('\n') for x in vPrime.split('\t') if x.strip()]
    vLamda = [x.strip('\n') for x in vLamda.split('\t') if x.strip()]
    CLA = [x.strip('\n') for x in CLA.split('\t') if x.strip()]
    
    sconeMacula = [float(x) for x in sconeMacula]
    vLamdaMacula = [float(x) for x in vLamdaMacula]
    melanopsin = [float(x) for x in melanopsin]
    vPrime = [float(x) for x in vPrime]
    vLamda = [float(x) for x in vLamda]
    CLA = [float(x) for x in CLA]
    
    #Pack constants into a single list & return
    return [sconeMacula, vLamdaMacula, melanopsin, vPrime, vLamda, CLA]