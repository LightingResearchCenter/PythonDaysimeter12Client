#GetErrLog
#Author: Jed Kundl
#Creation Date: 17.06.2013
#INPUT: 
#OUTPUT: Location of error log

import os
import pwd
import getpass

def getErrLog():
    #If windows, place on desktop
    if os.name == 'nt':
        return 'C:/Users/' + getpass.getuser() + '/Desktop/error.log'
    #Else if UNIX, place of desktop
    elif os.name == 'posix':
        return '/Users/' + pwd.getpwuid(os.getuid())[0] + '/Desktop/error.log'
    #Else, place nowhere
    else:
        return ''
        
if __name__ == '__main__':getErrLog()
