'''

Redundant row cleaner using algorithm from new H->ZZ->4l analysis
and non-isolated AKFSR

Author: Nate Woods, U. Wisconsin.

'''

from ZZRowCleanerBase import ZZRowCleanerBase
from ZZHelpers import * # evVar, objVar, nObjVar, Z_MASS


class HZZ4lAKFSRNIsoCleaner(ZZRowCleanerBase):
    def __init__(self, channel, cutter):
        super(HZZ4lAKFSRNIsoCleaner, self).__init__(channel, cutter)
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
        # make a copy in case we have to reorder
        objects = self.objectTemplate
        
        if self.needReorder:
            objects = self.cuts.orderLeptons(row, self.channel, self.objectTemplate)

        dZ = zCompatibility(row, objects[0], objects[1], fsrType='AKFSRNIso')
        ptSum = objVar(row, 'Pt', objects[2]) + objVar(row, 'Pt', objects[3])

        isBest = newEvent or (dZ < self.prevDZ or (dZ == self.prevDZ and ptSum > self.prevPtSum))

        if isBest:
            self.prevDZ = dZ
            self.prevPtSum = ptSum
        
        return isBest





