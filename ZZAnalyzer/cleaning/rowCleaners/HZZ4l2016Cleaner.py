'''

Redundant row cleaner using algorithm from new H->ZZ->4l analysis.

Among ZZ candidates with different leptons, choose the one with the highest 
D_bkg^kin. In the case of a further tie, or for candidates with the same 
leptons, select the candidate with Z1 closest to nominal mZ.

Author: Nate Woods, U. Wisconsin.

'''

from ZZAnalyzer.cleaning import RowCleanerBase
from ZZAnalyzer.utils.helpers import evVar, objVar, zCompatibility


class HZZ4l2016Cleaner(RowCleanerBase):
    def __init__(self, cutter, initChannel='eeee'): # super(self.__class__, ... safe if nothing inherits from this
        super(self.__class__, self).__init__(cutter, initChannel)
        self.cleanAtEnd = True # do cleaning last


    def betterRow(self, a, b):
        '''
        Strategy described above
        '''
        if a.m4l == b.m4l:
            if a.dZ < b.dZ:
                return a
            return b

        if a.dbk > b.dbk:
            return a

        return b

    
    class RowInfo(RowCleanerBase.RowInfo):
        def __init__(self, row, channel, idx, objects, cuts):
            super(self.__class__, self).__init__(row, channel, idx, objects, cuts)

        def storeVars(self, row, objects, cuts):
            '''
            Need d_bkg^kin and Z1 distance from nominal mass.
            '''
            self.dbk = row.D_bkg_kin #row.D_sel_kin
            self.dZ = zCompatibility(row, objects[0], objects[1], cuts.fsrVar)
            self.m4l = evVar(row, 'Mass'+cuts.fsrVar)

