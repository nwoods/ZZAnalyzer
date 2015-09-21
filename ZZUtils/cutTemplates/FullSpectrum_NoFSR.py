
'''

Base Cutter for 2015 HZZ4l analysis with dR/eT^n FSR.

Author: Nate Woods, U. Wisconsin

'''

from FullSpectrum_FullFSR_Sync import FullSpectrum_FullFSR_Sync


class FullSpectrum_NoFSR(FullSpectrum_FullFSR_Sync):
    fsrVar = ""

    def __init__(self, cutset="FullSpectrum_NoFSR"):
        super(FullSpectrum_NoFSR, self).__init__(cutset)


    def getCutTemplate(self, *args):
        '''
        Define a few useful cuts for CRs
        '''
        temp = super(FullSpectrum_NoFSR, self).getCutTemplate(self, *args)

        temp['mIso']['cuts'] = {'RelPFIsoDBDefault' : (0.4, "<")}
        temp['eIso']['cuts'] = {'RelPFIsoRho' : (0.5, "<")}

        temp['ZMassLoose']['cuts'] = {
            'Mass#lower' : (12., '>='),
            'Mass#upper' : (120., '<'),
            }

        temp['ZMassTight']['cuts'] = {
            'Mass#lower' : (40., ">="),
            'Mass#upper' : (120., "<"),
            }
        
        temp['4lMass']['cuts'] = {
            'Mass' : (70., ">="),
            }

        return temp



