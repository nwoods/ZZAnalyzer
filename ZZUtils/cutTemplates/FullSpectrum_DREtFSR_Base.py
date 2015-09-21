
'''

Base Cutter for 2015 HZZ4l analysis with dR/eT^n FSR.

Author: Nate Woods, U. Wisconsin

'''

from FullSpectrum_FullFSR_Sync import FullSpectrum_FullFSR_Sync


class FullSpectrum_DREtFSR_Base(FullSpectrum_FullFSR_Sync):
    fsrVar = "DREtFSR"
    dREtCut = 0.010

    def __init__(self, cutset="FullSpectrum_DREtFSR_Base"):
        super(FullSpectrum_DREtFSR_Base, self).__init__(cutset)


    def getCutTemplate(self, *args):
        '''
        Define a few useful cuts for CRs
        '''
        temp = super(FullSpectrum_DREtFSR_Base, self).getCutTemplate(self, *args)

        temp['mIso']['cuts'] = {'RelPFIsoDB'+self.fsrVar : (0.4, "<")}
        temp['eIso']['cuts'] = {'RelPFIsoRho'+self.fsrVar : (0.5, "<")}

        temp['ZMassLoose']['cuts'] = {
            'Mass%s#lower'%(self.fsrVar) : (12., '>='),
            'Mass%s#upper'%(self.fsrVar) : (120., '<'),
            }

        temp['ZMassTight']['cuts'] = {
            'Mass%s#lower'%(self.fsrVar) : (40., ">="),
            'Mass%s#upper'%(self.fsrVar) : (120., "<"),
            }
        
        temp['4lMass']['cuts'] = {
            'Mass'+self.fsrVar : (70., ">="),
            }

        return temp



