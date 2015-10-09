
'''

Cutter for skimming on lepton ID for the 2015 HZZ4l analysis.
Inherits from the SMP ZZ->4l Cutter.

Author: Nate Woods, U. Wisconsin

'''

from SMPZZ_FullFSR_Sync import SMPZZ_FullFSR_Sync


class LeptonIDSkim(SMPZZ_FullFSR_Sync):
    def __init__(self, cutset="LeptonIDSkim"):
        super(LeptonIDSkim, self).__init__(cutset)


    def setupCutFlow(self):
        '''
        As the full spectum cutter, but don't do anything afterlepton ID
        '''
        flow = super(LeptonIDSkim, self).setupCutFlow()
        # Remove everything after LeptonID
        foundIt = False
        for cut in flow:
            if cut == 'LeptonID':
                foundIt = True
            elif foundIt:
                flow.pop(cut)
        
        return flow


