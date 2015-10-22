
'''

SMP ZZ analysis but with WZ muon ID.

Author: Nate Woods, U. Wisconsin

'''

from SMPZZ_FullFSR_Sync import SMPZZ_FullFSR_Sync


class SMPZZ_WZMuons(SMPZZ_FullFSR_Sync):
    def __init__(self, cutset="SMPZZ_WZMuons"):
        super(SMPZZ_WZMuons, self).__init__(cutset)


    def getCutTemplate(self, *args):
        '''
        Define a few useful cuts for CRs
        '''
        temp = super(SMPZZ_WZMuons, self).getCutTemplate(self, *args)

        temp['mLooseID'] = {
            'cuts' : {
                'Pt' : (10., ">="),
                'Eta#POS' : (2.4, "<"),
                'Eta#NEG' : (-2.4, ">="),
                'PVDXY#POS' : (0.5, "<"),
                'PVDZ#POS' : (1., "<"),
                'PVDXY#NEG' : (-0.5, ">="),
                'PVDZ#NEG' : (-1., ">="),
                'BestTrack' : 'BestTrackType',
                'PFIDLoose' : (1., ">="),
            },
            'objects' : 1,
        }

        temp['mTightID'] = {
            'cuts' : {
                'looseMu' : 'mLooseID',
                'PFIDTight' : (1., ">="),
            },
            'objects' : 1,
        }

        return temp

