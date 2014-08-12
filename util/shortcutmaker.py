# -*- coding: utf-8 -*-
"""
Created on Fri Jul 19 12:21:49 2013

@author: kundlj
"""

import os, winshell
from win32com.client import Dispatch

def main(): 
    desktop = winshell.desktop()
    path = os.path.join(desktop, "Daysimeter Client.lnk")
    target = r"C:/Daysimeter Client/daysimdlclient/daysimdlclient.exe"
    wDir = r"C:/Daysimeter Client/daysimdlclient"
    icon = r"C:/Daysimeter Client/daysimdlclient/daysimdlclient.exe"
     
    shell = Dispatch('WScript.Shell')
    shortcut = shell.CreateShortCut(path)
    shortcut.Targetpath = target
    shortcut.WorkingDirectory = wDir
    shortcut.IconLocation = icon
    shortcut.save()
    
    if os.path.exists(os.path.join(os.getcwd(), 'daysimdlclient.exe')):
        os.remove(os.path.join(os.getcwd(), 'daysimdlclient.exe'))
        
    if os.path.exists(os.path.join(os.getcwd(), 'cdf35_1_0-setup-32.exe')):
        os.remove(os.path.join(os.getcwd(), 'cdf35_1_0-setup-32.exe'))
        
if __name__ == '__main__':
    main()