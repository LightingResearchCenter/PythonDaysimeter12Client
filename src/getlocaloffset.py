#GetLocalOffset
#Author: Jed Kundl
#Creation Date: 21.06.2013
#INPUT: 
#OUTPUT: Local UTC offset

#Local offset in seconds
def getLocalOffsetS():
    import dateutil.tz
    import datetime
    
    localTimeZone = dateutil.tz.tzlocal()
    localOffset = localTimeZone.utcoffset(datetime.datetime.now())
    return localOffset.days * 86400 + localOffset.seconds

#Local offset in minutes  
def getLocalOffsetM():
    import dateutil.tz
    import datetime
    
    localTimeZone = dateutil.tz.tzlocal()
    localOffset = localTimeZone.utcoffset(datetime.datetime.now())
    return (localOffset.days * 86400 + localOffset.seconds)/60

#Local offset in hours    
def getLocalOffsetH():
    import dateutil.tz
    import datetime
    
    localTimeZone = dateutil.tz.tzlocal()
    localOffset = localTimeZone.utcoffset(datetime.datetime.now())
    return (localOffset.days * 86400 + localOffset.seconds)/3600

#Loval offset in days    
def getLocalOffsetD():
    import dateutil.tz
    import datetime
    
    localTimeZone = dateutil.tz.tzlocal()
    localOffset = localTimeZone.utcoffset(datetime.datetime.now())
    return localOffset.days + localOffset.seconds/86400