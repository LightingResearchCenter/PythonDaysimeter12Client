"""
AccessSubjectInfo
Author: Jed Kundl
Creation Date: 25.06.2013
INPUT: ID, sex, DOB, mass or None
OUTPUT: None or ID, sex, DOB, mass
"""

import os

def writeSubjectInfo(ID, sex, DOB, mass):
    if not os.path.isdir(os.getcwd() + '/usr/data'):
        os.makedirs(os.getcwd() + '/usr/data')
    with open('./usr/data/subject info.txt','w') as fp:
        fp.write(ID + '\n' + sex + '\n' + DOB + '\n' + mass)
        
def readSubjectInfo():
    with open('usr/data/subject info.txt','r') as fp:
        info = [x.strip('\n') for x in fp.readlines()]
        return [info[0], info[1], info[2], info[3]]
    return []