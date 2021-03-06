'''

Redundant row cleaner using algorithm from new H->ZZ->4l analysis

Author: Nate Woods, U. Wisconsin.

'''

from ZZAnalyzer.cleaning import RowCleanerBase
from ZZAnalyzer.utils.helpers import objVar, zCompatibility


class HZZ4l2015Cleaner(RowCleanerBase):
    def __init__(self, cutter, initChannel='eeee'): # super(self.__class__, ... safe if nothing inherits from this
        super(self.__class__, self).__init__(cutter, initChannel)
        self.cleanAtEnd = True # do cleaning last


    def branchesToEnable(self):
        out = super(HZZ4l2015Cleaner, self).branchesToEnable()
        return out + ['[em][1-3]?_[em][1-4]?_Mass'+self.cuts.fsrVar,
                      '[em][1-4]?Pt']


    def betterRow(self, a, b):
        '''
        The correct row is the one with Z1 closest
        to on-shell, with the highest scalar Pt sum of the remaining leptons
        used as a tiebreaker. 
        '''
        if a.dZ < b.dZ or (a.dZ == b.dZ and a.ptSum > b.ptSum):
            return a
        return b

    
    class RowInfo(RowCleanerBase.RowInfo):
        def __init__(self, row, channel, idx, objects, cuts):
            super(self.__class__, self).__init__(row, channel, idx, objects, cuts)

        def storeVars(self, row, objects, cuts):
            '''
            Need Z1 distance from nominal mass and scalar sum of pt of Z2 
            leptons.
            '''
            self.dZ = zCompatibility(row, objects[0], objects[1], cuts.fsrVar)
            self.ptSum = objVar(row, 'Pt', objects[2]) + objVar(row, 'Pt', objects[3])

