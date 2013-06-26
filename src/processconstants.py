"""
process_constants
Author: Jed Kundl
Creation Date: 17.06.2013
INPUT: scone_macula, v_lamda_macula, melanopsin, v_prime, v_lamda, cla
OUTPUT: Constants to calculate cla and lux
"""

def process_constants(scone_macula, v_lamda_macula, melanopsin, \
v_prime, v_lamda, cla):
    """
    Process data by eliminating tabs, newlines, and leading/trailing
    spaces. Then, it deletes the first element of each list (the name)
    and converts the reaming elements to floats.
    """
    scone_macula = \
    [x.strip('\n') for x in scone_macula.split('\t') if x.strip()]
    v_lamda_macula = \
    [x.strip('\n') for x in v_lamda_macula.split('\t') if x.strip()]
    melanopsin = \
    [x.strip('\n') for x in melanopsin.split('\t') if x.strip()]
    v_prime = \
    [x.strip('\n') for x in v_prime.split('\t') if x.strip()]
    v_lamda = \
    [x.strip('\n') for x in v_lamda.split('\t') if x.strip()]
    cla = [x.strip('\n') for x in cla.split('\t') if x.strip()]
    
    scone_macula = [float(x) for x in scone_macula]
    v_lamda_macula = [float(x) for x in v_lamda_macula]
    melanopsin = [float(x) for x in melanopsin]
    v_prime = [float(x) for x in v_prime]
    v_lamda = [float(x) for x in v_lamda]
    cla = [float(x) for x in cla]
    
    #Pack constants into a single list & return
    return [scone_macula, v_lamda_macula, melanopsin, v_prime, v_lamda, cla]