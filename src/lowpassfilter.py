#LowpassFilter
#Author: Jed Kundl
#Creation Date: 18.06.2013
#INPUT: data, sSampleRate
#OUTPUT: filtered data

from scipy.signal import filtfilt
import constants

MINUTES = constants.MINUTES

#sSampleRate is the sample rate, in seconds. It should be the log
#interval of the daysimeter device
def lowpassFilter(data, sSampleRate):
    #hSampleRate is the sample rate in hertz
    hSampleRate = 1/sSampleRate
    magicNum = MINUTES * 60 * hSampleRate
    b = [1] * magicNum
    b = [x/magicNum for x in b]
    
    return filtfilt(b,1,data)
    
if __name__ == '__main__':lowpassFilter([],-1)

