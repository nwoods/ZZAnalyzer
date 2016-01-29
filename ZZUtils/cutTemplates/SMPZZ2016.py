from Cutter import Cutter
from ZZHelpers import *


class SMPZZ2016(Cutter):

    def getCutTemplate(self, *args):
        '''
        Full spectrum ZZ analysis, but requiring both Z candidates to be
        on-shell (mll > 60 GeV)
        '''
        temp = super(SMPZZ2016, self).getCutTemplate()

        temp['ZMassTight']['cuts']['Mass%s#lower'%self.fsrVar] = (60., ">=")
        temp['ZMassLoose']['cuts']['Mass%s#lower'%self.fsrVar] = (60., ">=")
        
        return temp
    

    def setupCutFlow(self):
        '''
        Only difference from full spectrum is that SMP uses smart cut.
        '''
        flow = super(SMPZZ2016, self).setupCutFlow()
        flow['SmartCut'] = ('SmartCut', [1,2,3,4])

        return flow
