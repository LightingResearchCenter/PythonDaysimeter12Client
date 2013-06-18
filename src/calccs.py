#CalcCS
#Author: Jed Kundl
#Creation Date: 18.06.2013
#INPUT: CLA
#OUTPUT: CS

def calcCS(CLA):
    CS = [.7*(1 - (1/(1 + (x/355.7)**(1.1026)))) for x in CLA]
    return CS
if __name__ == '__main__':calcCS([])