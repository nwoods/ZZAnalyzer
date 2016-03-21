
'''

No cuts, everything passes.

Author: Nate Woods, U. Wisconsin

'''

from ZZAnalyzer.cuts import Cutter

from collections import OrderedDict


class AllPass(Cutter):
    fsrVar = "DREtFSR"
    def __init__(self):
        super(AllPass, self).__init__("AllPass")


    def setupCutFlow(self):
        '''
        Dictionary with order and (one-indexed) numbers of particles to cut on
        '''
        flow = super(AllPass, self).setupCutFlow()
        
        return flow


    def setupOtherCuts(self):
        '''
        Define functions that don't fit the template nicely
        '''
        others = super(AllPass, self).setupOtherCuts()

        return others



    


