"""
CalcCS
Author: Jed Kundl
Creation Date: 18.06.2013
INPUT: CLA
OUTPUT: CS
"""

def calc_cs(cla):
    """ PURPOSE: Calulates Circadian Stimulus. """
    #Magic formula created by the LRC
    return [.7*(1 - (1/(1 + (x/355.7)**(1.1026)))) for x in cla]