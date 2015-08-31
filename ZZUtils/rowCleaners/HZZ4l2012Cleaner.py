'''

Redundant row cleaner using algorithm from legacy H->ZZ->4l analysis

Author: Nate Woods, U. Wisconsin.

'''

from ZZRowCleanerBase import ZZRowCleanerBase
from ZZHelpers import * # evVar, objVar, nObjVar, Z_MASS


class HZZ4l2012Cleaner(ZZRowCleanerBase):
    def __init__(self, cutter, initChannel='eeee'):
        super(HZZ4l2012Cleaner, self).__init__(cutter, initChannel)
        self.cleanAtEnd = False # do cleaning first


    def betterRow(self, a, b):
        '''
        Returns the better row. 
        The better row is the one with Z1 closer to nominal Z mass, with
        the scalar sum of the Z2 leptons' pTs used as a tiebreaker.
        When in doubt, takes b.
        '''
        if a.dZ < b.dZ or (a.dZ == b.dZ and a.ptSum > b.ptSum):
            return a
        return b


    class RowInfo(ZZRowCleanerBase.RowInfo):
        def __init__(self, row, channel, idx, objects, cuts):
            super(self.__class__, self).__init__(row, channel, idx, objects, cuts)
            
        def storeVars(self, row, objects, cuts):
            '''
            Need Z1 distance from nominal mass and scalar sum of pt of Z2 
            leptons. We only care about this row if the leptons all pass ID
            and isolation, so the variables are set to ridiculous values if 
            the event does not pass.
            '''
            allGood = True
            for lepts in [[objects[0],objects[1]],[objects[2],objects[3]]]:
                if not cuts.doCut(row, "GoodZ", *lepts):
                    allGood = False
                    break
                if not cuts.doCut(row, "ZIso", *lepts):
                    allGood = False
                    break

            if allGood:
                self.dZ = zCompatibility(row, objects[0], objects[1], cuts.fsrVar)
                self.ptSum = objVar(row, 'Pt', objects[2]) + objVar(row, 'Pt', objects[3])
            else:
                self.dZ = 999
                self.ptSum = -999

