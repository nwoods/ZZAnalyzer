from Cutter import Cutter
from ZZHelpers import *


class HZZ2016(Cutter):
    def getCutTemplate(self,*args):
        '''
        Template for all cuts
        '''
        temp = super(HZZ2016, self).getCutTemplate(*args)

        temp['ZMassLoose']['cuts']['Mass%s#lower'%self.fsrVar] = (12., '>=')

        return temp


    def setupCutFlow(self):
        '''
        Only flow difference from full spectrum is that HZZ uses smart cut.
        '''
        flow = super(HZZ2016, self).setupCutFlow()
        flow['SmartCut'] = ('SmartCut', [1,2,3,4])

        return flow
