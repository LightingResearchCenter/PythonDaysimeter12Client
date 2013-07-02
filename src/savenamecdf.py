"""
savename_cdf
Author: Jed Kundl
Creation Date: 24.06.2013
INPUT: None
OUTPUT: The path the CDF file should be saved as
"""

import os
from Tkinter import Tk
from tkFileDialog import asksaveasfilename
from tkMessageBox import showerror


def savename_cdf():
    """
    PURSPOE: Promt user for savename of outputted CDF.
    NOTE: Code is no longer used, but remains for furture use.
    """
    valid_name = False
    
    Tk().withdraw()
    while not valid_name:
        filename = asksaveasfilename()
        if not filename[len(filename)-4:len(filename)] == '.cdf':
            showerror(None,'Error: Invalid file extension.\nMust be ".cdf"')
        else:
            valid_name = True
    if os.path.isfile(filename):
        os.remove(filename)
    return filename