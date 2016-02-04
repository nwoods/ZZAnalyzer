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

        temp['4lMass']['cuts'] = {'Mass%s'%self.fsrVar : (70., ">=")}
        
        return temp
    

    def setupCutFlow(self):
        '''
        Only differences from full spectrum are that SMP uses smart cut
        and has 4l mass cut.
        '''
        flow = super(SMPZZ2016, self).setupCutFlow()
        flow['4lMass'] = ('4lMass', [])
        flow['SmartCut'] = ('SmartCut', [1,2,3,4])

        return flow
