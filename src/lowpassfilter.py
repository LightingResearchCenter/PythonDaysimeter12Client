#LowpassFilter
#Author: Jed Kundl
#Creation Date: 18.06.2013
#INPUT: data, sSampleRate
#OUTPUT: filtered data

#sSampleRate is the sample rate, in seconds. It should be the log
#interval of the daysimeter device

def lowpassFilter(data, sSampleRate):   
    from scipy.signal import filtfilt
    from numpy import ones
    import constants
    from math import floor
    
    MINUTES = constants.MINUTES
  
    #hSampleRate is the sample rate in hertz
    hSampleRate = 1.0/sSampleRate
    window_size = int(floor(MINUTES * 60 * hSampleRate))
    b = ones(window_size)/window_size
    return filtfilt(b, [1], data, padlen=0)