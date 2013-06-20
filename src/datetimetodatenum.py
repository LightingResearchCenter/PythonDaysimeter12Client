#DateTimeToDateNum
#Author: Jed Kundl
#Creation Date: 19.06.2013
#INPUT: Python datetime
#OUTPUT: MatLab datenum

def dt2dn(dateTime):
    from datetime import timedelta
    from datetime import datetime

    #Adds 366 days to dateTime because datetime() measures from year 1
    #and not year 0. Also, year 0 had 366 days in it.
    dateNum = dateTime + timedelta(days = 366)
    fraction = (dateTime-datetime(dateTime.year,dateTime.month,dateTime.day,0,0,0)).seconds / (24.0 * 60.0 * 60.0)
    return dateNum.toordinal() + fraction