'''

Useful helper functions used everywhere in this analyzer.

Author: N. Woods, U. Wisconsin

'''

from math import pi, sqrt


def evVar(row, var):
    '''
    Get variable from final state
    '''
    return getattr(row,var)


def objVar(row, var, obj):
    '''
    Get variable associated with single object
    '''
    return getattr(row, obj+var)


def nObjVar(row, var, *obj):
    '''
    Get an n object composite variable
    Works for 0 or 1 object too, but the other Var functions are faster for those
    '''
    return getattr(row, '_'.join([o for o in obj]+[var]))


def deltaR(eta1, phi1, eta2, phi2):
    dPhi = abs(phi2 - phi1)
    while dPhi > pi:
        dPhi -= 2*pi
    return sqrt(dPhi**2 + (eta2 - eta1)**2)


Z_MASS = 91.1876


def zCompatibility(row, obj1, obj2, fsrVar="FSR"):
    '''
    Distance from the nominal Z mass for this pair of objects. Does not check 
    for OSSF.
    '''
    mVar = "Mass"
    if fsrVar:
        try:
            mVar += fsrVar
        except TypeError:
            pass

    m = nObjVar(row, mVar, obj1, obj2)

    return zMassDist(m)


def zMassDist(mass):
    '''
    Absolute distance of this number from the nominal Z mass.
    '''
    return abs(mass - Z_MASS)


def zCompatibility_checkSign(row, ob1, ob2, fsrVar="FSR"):
    '''
    Absolute distance from Z mass. 1000 if same sign.
    '''
    if nObjVar(row, 'SS', ob1, ob2):
        return 1000

    return zCompatibility(row, ob1, ob2, fsrVar)


def makeNumberPretty(n, maxDigits=10):
    '''
    Take a number, return a string of it with the right number of digits
    and whatnot.
    Cuts off at maxDigits places after the decimal point.
    Assumes you want all digits before the decimal point no matter what.
    '''
    if int(n) == n: # integer
        return "%d"%n

    nDecimals = 0
    m = n
    while nDecimals < maxDigits:
        nDecimals += 1
        m *= 10
        if int(m) == m:
            break
    
    preFormat = "%%.%df"%nDecimals
    return preFormat%n

