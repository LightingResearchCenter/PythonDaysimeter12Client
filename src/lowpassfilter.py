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
    
    MINUTES = constants.MINUTES

    #hSampleRate is the sample rate in hertz
    hSampleRate = 1/sSampleRate
    magicNum = MINUTES * 60 * hSampleRate
    b = [1] * magicNum
    b = [x/magicNum for x in b]
    temp = filtfilt(b,1,data)
    return [float(x) for x in temp]
    
if __name__ == '__main__':lowpassFilter([],-1)

