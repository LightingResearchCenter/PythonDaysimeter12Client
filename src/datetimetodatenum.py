"""
DateTimeToDateNum
Author: Jed Kundl
Creation Date: 19.06.2013
INPUT: Python datetime
OUTPUT: MatLab date_num
"""

from datetime import timedelta
from datetime import datetime

def dt2dn(date_time):
    """ PURPOSE: Convert date_time into a matlab date_num. """
    #Adds 366 days to date_time because date_time() measures from year 1
    #and not year 0. Also, year 0 had 366 days in it.
    date_num = date_time + timedelta(days = 366)
    fraction = (date_time-datetime(date_time.year, date_time.month, \
    date_time.day,0, 0, 0)).seconds / (24.0 * 60.0 * 60.0)
    return date_num.toordinal() + fraction