'''

Useful helper functions used everywhere in this analyzer.

Author: N. Woods, U. Wisconsin

'''

from math import pi, sqrt
from json import load as loadJSON

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


def parseChannels(channels):
    '''
    Take a string or list of strings and return a list of channels.
    '''
    if type(channels) == str:
        if channels in ['4l', 'zz', 'ZZ']:
            return ['eeee', 'eemm', 'mmmm']
        elif channels in ['3l', 'zl', 'Zl', 'z+l', 'Z+l']:
            return ['eee', 'eem', 'emm', 'mmm']
        else:
            chanList = channels.split(',')
            assert all(all(letter in ['e','m','t','g','j'] for letter in ch) and len(ch) <= 4 for ch in chanList),\
                'Invalid channel ' + channels
            return chanList
    else:
        assert isinstance(channels, list), 'Channels must be a list or a string'
        out = []
        for ch in channels:
            out += parseChannels(ch)
        return out


_zzhelpers_object_maps_ = {}
def mapObjects(channel):
    '''
    Return a list of objects of the form ['e1','e2','m1','m2'] or ['e1','e2','m']
    Objects are in alphabetical/numerical order order
    '''
    global _zzhelpers_object_maps_

    try:
        return _zzhelpers_object_maps_[channel]
    except KeyError:
        nObjects = {}
        objects = []
    
        for obj in channel:
            if obj not in nObjects:
                nObjects[obj] = 1
            else:
                nObjects[obj] += 1
    
        for obj, num in nObjects.iteritems():
            if num == 1:
                objects.append(obj)
            else:
                for i in range(num):
                    objects.append(obj+str(i+1))
        
        objects.sort()

        _zzhelpers_object_maps_[channel] = objects
        return objects


def dictFromJSONFile(fName):
    '''
    Take a JSON file, return a dict with the information.
    '''
    with open(fName) as f:
        return loadJSON(f)
