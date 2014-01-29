# -*- coding: utf-8 -*-
"""
Created on Tue Dec 03 09:56:26 2013

@author: kundlj
"""

from win32com.shell.shell import ShellExecuteEx
from win32com.shell import shellcon
import win32process, win32event
import win32con
from ntsecuritycon import *
####
ASADMIN = 'asadmin'

script = os.path.abspath('C:/Users/kundlj/Desktop/pyinstaller-pyinstaller-61571d6/daysimdlclient/dist/daysimdlclient/daysimdlclient.exe')
params = ' '.join([script] + [ASADMIN])
print params
try:
    ShellExecuteEx(fMask=shellcon.SEE_MASK_NOCLOSEPROCESS,
                    lpVerb="runas",
                    lpFile=sys.executable,
                    lpParameters=params,
                    nShow=win32con.SW_SHOW)
except Exception, e:
    print e
    
else:
    print 'this'
    
    subprocess.Popen([sys.executable, "longtask.py"], creationflags=DETACHED_PROCESS)