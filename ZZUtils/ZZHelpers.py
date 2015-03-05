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
    if dPhi > pi:
        dPhi -= 2*pi
    return sqrt(dPhi**2 + (eta2 - eta1)**2)


Z_MASS = 91.1876


def zCompatibility(row, obj1, obj2, useFSR=True):
    '''
    Distance from the nominal Z mass for this pair of objects. Does not check 
    for OSSF.
    '''
    if useFSR:
        mVar = "MassFSR"
    else:
        mVar = "Mass"
    m = nObjVar(row, mVar, obj1, obj2)

    return zMassDist(m)


def zMassDist(mass):
    '''
    Absolute distance of this number from the nominal Z mass.
    '''
    return abs(mass - Z_MASS)
