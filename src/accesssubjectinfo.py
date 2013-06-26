"""
AccessSubjectInfo
Author: Jed Kundl
Creation Date: 25.06.2013
INPUT: id_, sex, date_of_birth, mass or None
OUTPUT: None or id_, sex, date_of_birth, mass
"""

import os

def write_subject_info(id_, sex, date_of_birth, mass):
    """ PURPOSE: Writes subject info to .txt file. """
    if not os.path.isdir(os.getcwd() + '/usr/data'):
        os.makedirs(os.getcwd() + '/usr/data')
    with open('./usr/data/subject info.txt','w') as sub_fp:
        sub_fp.write(id_ + '\n' + sex + '\n' + date_of_birth + '\n' + mass)
        
def read_subject_info():
    """ PURPOSE: Reads subject info from .txt file. """
    with open('usr/data/subject info.txt','r') as sub_fp:
        info = [x.strip('\n') for x in sub_fp.readlines()]
        return [info[0], info[1], info[2], info[3]]
    return []