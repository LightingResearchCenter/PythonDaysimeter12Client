#GetErrLog
#Author: Jed Kundl
#Creation Date: 17.06.2013
#INPUT: 
#OUTPUT: Location of error log

def getErrLog():
    import os
    import sys
    import pwd
    import getpass
    #If Windows, place on desktop
    if sys.platform == 'win32':
        return 'C:/Users/' + getpass.getuser() + '/Desktop/error.log'
    #Else if Mac OSX, place on desktop
    elif sys.platform == 'darwin':
        return '/Users/' + pwd.getpwuid(os.getuid())[0] + '/Desktop/error.log'
    #Else if Linux, place on desktop
    elif sys.platform.startswith('linux'):
        return '/home/' + pwd.getpwuid(os.getuid())[0] + '/Desktop/error.log'
    #Else, well hopfully you are running Linux, Mac, or Windows
    #Because without the error log, I have no place to write an
    #error that you're using an incompatiple system.
    else:
        return ''
        
if __name__ == '__main__':getErrLog()
