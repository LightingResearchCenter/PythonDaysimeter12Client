"""
adj_active_flag (Adjust Activity Flag)
Author: Jed Kundl
Creation Date: 17.06.2013
INPUT: Red, Green, Blue, Activity
OUTPUT: Processed Red, Green, Blue, Activity
"""

def adj_active_flag(red, green, blue, activity):
    """
    PURPOSE: Adjusts red, green, blue values if LSB of activity was used to
    monitor rollover.    
    """
    loop_max = len(activity)
    #The LSB of activity was used to measure rollover values for R, G, B.
    #So if activity is odd, then we need to calculate the actual values
    #for R, G, B and "eliminate" the added 1 to activity.
    for x in range(0, loop_max):
        if activity[x] % 2 == 1:
            red[x] = red[x]*10
            green[x] = green[x]*10
            blue[x] = blue[x]*10
            activity[x] -= 1
            
    #Pack adjusted values into a single list & return
    return [red, green, blue, activity]