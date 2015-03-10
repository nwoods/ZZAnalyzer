'''

Redundant row cleaner using algorithm from new H->ZZ->4l analysis

Author: Nate Woods, U. Wisconsin.

'''

from ZZRowCleanerBase import ZZRowCleanerBase
from ZZHelpers import * # evVar, objVar, nObjVar, Z_MASS


class HZZ4l2015Cleaner(ZZRowCleanerBase):
    def __init__(self, channel, cutter):
        super(HZZ4l2015Cleaner, self).__init__(channel, cutter)
        self.cleanAtEnd = True # do cleaning last
        self.prevDZ = 999.
        self.prevPtSum = -999.


    def isNewBest(self, row, newEvent):
        '''
        Returns True if this row is better than previous rows from the same
        event it has just seen. The correct row is the one with Z1 closest
        to on-shell, with the highest scalar Pt sum of the remaining leptons
        used as a tiebreaker. Only Zs whose leptons pass ID are considered
        (if no rows from an event pass ID, the first is considered best). 
        '''
        # To store appropriate info, we always need to do the ID+iso check

        # make a copy in case we have to reorder
        objects = self.objectTemplate
        
        if self.needReorder:
            objects = orderLeptons(row, self.channel, self.objectTemplate)

        dZ = zCompatibility(row, objects[0], objects[1])
        ptSum = objVar(row, 'PtFSR', objects[2]) + objVar(row, 'PtFSR', objects[3])

        isBest = newEvent or (dZ < self.prevDZ or (dZ == self.prevDZ and ptSum > self.prevPtSum))

        if isBest:
            self.prevDZ = dZ
            self.prevPtSum = ptSum
        
        return isBest
       
 
def orderLeptons(row, channel, objects):
    '''
    Put best (closest to nominal mass) Z candidate first. 
    FSA does this automatically for 4e and 4mu cases.
    Assumes 4 leptons, with (l1,l2) and (l3,l4) same-flavor pairs;
    will have to be overloaded for other final states.
    '''
    if channel == 'eeee' or channel == 'mmmm':
        return objects

    dM1 = zCompatibility(row,objects[0],objects[1])
    dM2 = zCompatibility(row,objects[2],objects[3])
    
    if dM1 > dM2:
        return objects[2:] + objects[:2]
    return objects




