"""
lowpass_filter
Author: Jed Kundl
Creation Date: 18.06.2013
INPUT: data, s_sample_rate
OUTPUT: filtered data
"""

from scipy.signal import filtfilt
from numpy import ones
import constants
from math import floor

#s_sample_rate is the sample rate, in seconds. It should be the log
#interval of the daysimeter device

def lowpass_filter(data, s_sample_rate):   
    """
    PURPOSE: Filters data using a zero phase distortion filter to smooth data
    curves.
    """
    minutes = constants.MINUTES
    #h_sample_rate is the sample rate in hertz
    h_sample_rate = 1.0/s_sample_rate
    window_size = int(floor(minutes * 60 * h_sample_rate))
    b = ones(window_size)/window_size
    if s_sample_rate > 150:
        return data
    else:
        return filtfilt(b, [1], data, padlen=0)