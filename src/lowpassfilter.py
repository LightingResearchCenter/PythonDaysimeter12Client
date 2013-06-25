#LowpassFilter
#Author: Jed Kundl
#Creation Date: 18.06.2013
#INPUT: data, sSampleRate
#OUTPUT: filtered data

#sSampleRate is the sample rate, in seconds. It should be the log
#interval of the daysimeter device

def lowpassFilter(data, sSampleRate):   
    from scipy.signal import filtfilt
    import constants
    import math
    
    MINUTES = constants.MINUTES
#####THIS FUNCTION IS NOT WORKING PROPERLY YET
#####I'VE BEEN TRYING TO FIGURE IT OUT BUT THE CODE I'M BASING IT OFF
#####WAS VERY POORLY COMMENTED
    
    #hSampleRate is the sample rate in hertz
    hSampleRate = 1/sSampleRate
    magicNum = int(math.floor(MINUTES * 60 * hSampleRate))
    b = [1] * magicNum
    b = [x/magicNum for x in b]
    temp = filtfilt(b,[1],data,padlen=0)
    return [float(x) for x in temp]