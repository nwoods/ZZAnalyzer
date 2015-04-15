'''

Redundant row cleaner using algorithm from legacy H->ZZ->4l analysis

Author: Nate Woods, U. Wisconsin.

'''

from ZZRowCleanerBase import ZZRowCleanerBase
from ZZHelpers import * # evVar, objVar, nObjVar, Z_MASS


class HZZ4l2012Cleaner(ZZRowCleanerBase):
    def __init__(self, channel, cutter):
        super(HZZ4l2012Cleaner, self).__init__(channel, cutter)
        self.cleanAtEnd = False # do cleaning first
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
            objects = self.cuts.orderLeptons(row, self.channel, self.objectTemplate)

        allGood = True
        for lepts in [[objects[0],objects[1]],[objects[2],objects[3]]]:
            if not self.cuts.doCut(row, "GoodZ", *lepts):
                allGood = False
                break
            if not self.cuts.doCut(row, "ZIso", *lepts):
                allGood = False
                break

        if allGood:
            dZ = zCompatibility(row, objects[0], objects[1])
            ptSum = objVar(row, 'Pt', objects[2]) + objVar(row, 'Pt', objects[3])
        else:
            dZ = 999
            ptSum = -999

        isBest = newEvent or (dZ < self.prevDZ or (dZ == self.prevDZ and ptSum > self.prevPtSum))

        if isBest:
            self.prevDZ = dZ
            self.prevPtSum = ptSum
        
        return isBest
       
 



