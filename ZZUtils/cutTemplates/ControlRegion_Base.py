
'''

Base Cutter for control regions in the 2015 HZZ4l analysis. Defines some loose
ID cuts and other things useful for CRs.

Author: Nate Woods, U. Wisconsin

'''

from SMPZZ_FullFSR_Sync import SMPZZ_FullFSR_Sync


class ControlRegion_Base(SMPZZ_FullFSR_Sync):
    def __init__(self, cutset="ControlRegion_Base"):
        super(ControlRegion_Base, self).__init__(cutset)


    def getCutTemplate(self, *args):
        '''
        Define a few useful cuts for CRs
        '''
        temp = super(ControlRegion_Base, self).getCutTemplate(self, *args)

        temp['leptonLooseID'] = {
            'cuts' : {
                'id' : 'TYPELooseID',
            },
            'objects' : 1,
        }

        temp['MediocreLeptons'] = {
            'cuts' : {
                'id' : 'leptonLooseID',
            },
            'logic' : 'objand',
        }

        # Fail either tight ID or isolation
        temp['FailTightOrIso'] = {
            'cuts' : {
                'failID' : '!leptonTightID',
                'failIso' : '!LeptonIso',
            },
            'objects' : 1,
            'logic' : 'or',
        }

        return temp


    def needReorder(self, *args):
        '''
        In the control regions, we always need to check to see if things ought
        to be reordered (the real Z is always first).
        '''
        return True



