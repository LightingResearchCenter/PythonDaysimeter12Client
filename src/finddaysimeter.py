#FindDaysimeter
#Author: Jed Kundl
#Creation Date: 18.06.2013
#INPUT: 
#OUTPUT: daysimeter drive ID

def findDaysimeter():
    import sys
    import os
    from win32api import GetLogicalDriveStrings
    import constants
    
    LOG_FILENAME = constants.LOG_FILENAME
    DATA_FILENAME = constants.DATA_FILENAME
    
    #If Windows
    if sys.platform == 'win32':
        drives = GetLogicalDriveStrings()
        drives = [x for x in drives.split('\\\000') if x.strip()]
        for x in drives:
            #There is a security risk in using os.path.isfile, because the
            #file could be created after the check. However, the chance of 
            #anyone expoliting this is virtually zero.
            if os.path.isfile(x + '/' + LOG_FILENAME) and os.path.isfile(x + '/' + DATA_FILENAME):
                return x + '/'
    #Else if Macintosh
    elif sys.platform == 'darwin':
        volumes = os.listdir('/Volumes')
        for x in volumes:
            if os.path.isfile(x + '/' + LOG_FILENAME) and os.path.isfile(x + '/' + DATA_FILENAME):
                return x + '/'
    #Else if Linux
    elif sys.platform.startswith('linux'):
        devices = os.listdir('/media')
        for x in devices:
            if os.path.isfile(x + '/' + LOG_FILENAME) and os.path.isfile(x + '/' + DATA_FILENAME):
                return x + '/'
    else:
        pass
####Need to write cross-platform code here