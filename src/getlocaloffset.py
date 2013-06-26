"""
get_local_offset
Author: Jed Kundl
Creation Date: 21.06.2013
INPUT: 
OUTPUT: Local UTC offset
"""

import dateutil.tz
import datetime

def get_local_offset_s():
    """ PURPOSE: Get local offset in seconds. """
    local_time_zone = dateutil.tz.tzlocal()
    local_offset = local_time_zone.utcoffset(datetime.datetime.now())
    return local_offset.days * 86400 + local_offset.seconds

def get_local_offset_m():
    """ Get local offset in minutes. """
    local_time_zone = dateutil.tz.tzlocal()
    local_offset = local_time_zone.utcoffset(datetime.datetime.now())
    return (local_offset.days * 86400 + local_offset.seconds)/60
    
def get_local_offset_h():
    """ Get local offset in hours. """    
    local_time_zone = dateutil.tz.tzlocal()
    local_offset = local_time_zone.utcoffset(datetime.datetime.now())
    return (local_offset.days * 86400 + local_offset.seconds)/3600
    
def get_local_offset_d():
    """ Get loval offset in days. """    
    local_time_zone = dateutil.tz.tzlocal()
    local_offset = local_time_zone.utcoffset(datetime.datetime.now())
    return local_offset.days + local_offset.seconds/86400