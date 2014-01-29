# -*- coding: utf-8 -*-
"""
Created on Tue Dec 03 11:01:15 2013

@author: kundlj
"""

import os
import shutil

def main(): 
    desktop = 'C:/Users/kundlj/Desktop'
    
    if not os.getcwd() == desktop:
        if os.path.exists('C:/Program Files (x86)/Daysimeter Client/runclient.exe'):
            shutil.copy(os.path.join(os.getcwd(), 'runclient.exe'), desktop)
            os.rename(os.path.join(desktop, 'runclient.exe'), \
                      os.path.join(desktop, 'Daysimeter Client.exe'))
    elif os.path.exists('C:/Program Files (x86)/Daysimeter Client/runclient.exe'):
        os.remove('C:/Program Files (x86)/Daysimeter Client/runclient.exe')
    else:
        os.startfile('C:/Program Files (x86)/Daysimeter Client/daysimdlclient/daysimdlclient.exe')
        
if __name__ == '__main__':
    main()