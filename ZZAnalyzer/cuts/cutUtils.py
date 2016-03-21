#############################################################################
#                                                                           #
#    cutUtils.py                                                            #
#                                                                           #
#    Rearranges cut templates to produce Cutters with desired properties,   #
#    e.g., add blinding to any Cutter or make control regions from any      #
#    base Cutter.                                                           #
#                                                                           #
#    Author: Nate Woods, U. Wisconsin                                       #
#                                                                           #
#############################################################################


import os, imp

assert os.environ["zza"], "Run setup.sh before running analysis"

from ZZAnalyzer.utils.helpers import importClass


def combineCuts(BaseCutter, *Modifiers):
    '''
    Combine a number of cutters into a single class. 
    The only difference between BaseCutter and the modifiers is that BaseCutter
    is always placed last in the list of parent classes for the new class, so
    it ends up last in the MRO.
    '''
    CutterList = list(Modifiers)
    CutterList.append(BaseCutter)

    newClassName = "_".join(c.__name__ for c in CutterList)

    NewCutter = type(newClassName, tuple(CutterList), {})

    return NewCutter


def getCutClass(baseCutterName, *otherCutterNames):
    '''
    Given names of several cutters, make a new class that combines them.
    The first one is guaranteed to follow the others in the MRO, so the 
    others may overwrite some of what it does.
    '''
    BaseCutter = importClass(baseCutterName, 'cut')
    OtherCutters = [importClass(n, 'cut') for n in otherCutterNames]

    return combineCuts(BaseCutter, *OtherCutters)

