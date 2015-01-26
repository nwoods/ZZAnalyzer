
'''

No cuts, everything passes.

Author: Nate Woods, U. Wisconsin

'''

import Cutter
from collections import OrderedDict
from ZZHelpers import *


class AllPass(Cutter.Cutter):
    def __init__(self):
        super(AllPass, self).__init__("FullSpectrumFSR")


    def getCutTemplate(self,*args):
        '''
        Template for all cuts
        '''
        cutTemplate = {}

        return cutTemplate


    def setupCutFlow(self):
        '''
        Dictionary with order and (one-indexed) numbers of particles to cut on
        '''
        flow = OrderedDict()
        flow['Total'] = ('true', [])
        
        return flow


    def setupOtherCuts(self):
        '''
        Define functions that don't fit the template nicely
        '''
        temp = self.getCutTemplate()
        others = {}

        return others



    


