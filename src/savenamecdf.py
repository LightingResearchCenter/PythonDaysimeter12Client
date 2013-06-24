#savenameCDF
#Author: Jed Kundl
#Creation Date: 24.06.2013
#INPUT: 
#OUTPUT: The path the CDF file should be saved as

def savenameCDF():
    import os
    from Tkinter import Tk
    from tkFileDialog import asksaveasfilename
    from tkMessageBox import showerror
    
    VALID_NAME = False
    
    Tk().withdraw()
    while not VALID_NAME:
        filename = asksaveasfilename()
        if not filename[len(filename)-4:len(filename)] == '.cdf':
            showerror(None,'Error: Invalid file extension.\nMust be ".cdf"')
        else:
            VALID_NAME = True
    if os.path.isfile(filename):
        os.remove(filename)
    return filename