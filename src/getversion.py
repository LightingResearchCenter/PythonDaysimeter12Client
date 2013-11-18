# -*- coding: utf-8 -*-
"""
Created on Thu Nov 14 11:04:14 2013

@author: kundlj
"""

import urllib2
import constants as constants_

def get_current_version(version):
    if internet_on():
        url = constants_.LATEST_URL
        request = urllib2.Request(url)
        
        try:
            urllib2.urlopen(request)
        except urllib2.URLError:
            return version
        else:
            opener = urllib2.build_opener(urllib2.HTTPRedirectHandler)
            request = opener.open(url)
            parse = [x for x in request.url.split('/')]
            return parse[len(parse) - 1]
    else:
        return version
        
def internet_on():
    try:
        urllib2.urlopen('http://www.google.com', timeout=5)
        return True
    except urllib2.URLError: 
        pass
    return False
