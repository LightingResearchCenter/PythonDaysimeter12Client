#DateTimeToDateNum
#Author: Jed Kundl
#Creation Date: 19.06.2013
#INPUT: Python datetime
#OUTPUT: MatLab datenum

from datetime import timedelta
from datetime import datetime

def dt2dn(dateTime):
    dateNum = dateTime + timedelta(days = 366)
    fraction = (dateTime-datetime(dateTime.year,dateTime.month,dateTime.day,0,0,0)).seconds / (24.0 * 60.0 * 60.0)
    return dateNum.toordinal() + fraction