# -*- coding: utf-8 -*-
"""
Created on Thu Nov 14 11:04:14 2013

@author: kundlj
"""

import urllib2
import constants as constants_
import logging

def get_current_version(version):
    daysim_log = logging.getLogger('daysim_log')
    err_log = logging.getLogger('err_log')
    daysim_log.info('Checking for updates.')
    if internet_on():
        url = constants_.LATEST_URL
        request = urllib2.Request(url)
        
        try:
            urllib2.urlopen(request)
        except urllib2.URLError:
            err_log.error('Daysimeter could not access latest release')
            return version
        else:
            opener = urllib2.build_opener(urllib2.HTTPRedirectHandler)
            request = opener.open(url)
            parse = [x for x in request.url.split('/')]
            current_version = parse[len(parse) - 1]
            daysim_log.info('Most recent version is ' + current_version + \
                            ', this version is ' + version + '.')
            return current_version
    else:
        return version
        
def internet_on():
    daysim_log = logging.getLogger('daysim_log')
    err_log = logging.getLogger('err_log')
    try:
        urllib2.urlopen('http://www.google.com', timeout=5)
        daysim_log.info('Daysimeter is connected to the internet.')
        return True
    except urllib2.URLError:
        err_log.warning('Daysimeter is not connected to the internet.')
        pass
    return False
