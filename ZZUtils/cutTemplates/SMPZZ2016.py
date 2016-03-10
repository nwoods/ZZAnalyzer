from Cutter import Cutter
from ZZHelpers import *


class SMPZZ2016(Cutter):

    def getCutTemplate(self, *args):
        '''
        Full spectrum ZZ analysis, but requiring both Z candidates to be
        on-shell (mll > 60 GeV)
        '''
        temp = super(SMPZZ2016, self).getCutTemplate()

        if 'ZMassTight' in temp:
            temp['ZMassTight']['cuts']['Mass%s#lower'%self.fsrVar] = (60., ">=")
        else:
            temp['ZMassTight'] = {
                'cuts' : { 
                    'Mass%s#lower'%self.fsrVar : (60., ">="),
                    'Mass%s#upper'%self.fsrVar : (120., "<"),
                    },
                'objects' : 2,
                }

        return temp
    

    def setupCutFlow(self):
        '''
        Only differences from full spectrum are that SMP uses smart cut
        and has 4l mass cut.
        '''
        flow = super(SMPZZ2016, self).setupCutFlow()
        
        flow['Z1Mass'] = ('ZMassTight', [1,2])
        flow['Z2Mass'] = ('ZMassTight', [3,4])


        return flow
