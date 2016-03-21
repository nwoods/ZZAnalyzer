'''

Redundant row cleaner that keeps the row with the best Z1 candidate

Author: Nate Woods, U. Wisconsin.

'''

from ZZAnalyzer.cleaning import RowCleanerBase
from ZZAnalyzer.utils.helpers import zCompatibility


class SingleZCleaner(RowCleanerBase):
    def __init__(self, cutter, initChannel='eeee'): 
        # super(self.__class__, ... safe if nothing inherits from this
        super(self.__class__, self).__init__(cutter, initChannel)
        self.cleanAtEnd = True # do cleaning last


    def betterRow(self, a, b):
        '''
        The correct row is the one with Z closest to on-shell. 
        If they're the same, keep the first because we don't care.
        '''
        if a.dZ <= b.dZ:
            return a
        return b

    
    class RowInfo(RowCleanerBase.RowInfo):
        def __init__(self, row, channel, idx, objects, cuts):
            super(self.__class__, self).__init__(row, channel, idx, objects, cuts)

        def storeVars(self, row, objects, cuts):
            '''
            Need Z1 distance from nominal mass.
            '''
            self.dZ = zCompatibility(row, objects[0], objects[1], cuts.fsrVar)


