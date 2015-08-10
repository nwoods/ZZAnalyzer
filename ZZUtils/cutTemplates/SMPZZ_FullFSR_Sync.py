
'''

Cutter for the 2015 standard model (i.e. on-shell) ZZ analysis.
Inherits from the full spectrum cutter.

Author: Nate Woods, U. Wisconsin

'''


from collections import OrderedDict
from FullSpectrum_FullFSR_Sync import FullSpectrum_FullFSR_Sync


class SMPZZ_FullFSR_Sync(FullSpectrum_FullFSR_Sync):
    def __init__(self, cutset="SMPZZ_FullFSR_Sync"):
        super(SMPZZ_FullFSR_Sync, self).__init__(cutset)


    def getCutTemplate(self, *args):
        '''
        Full spectrum ZZ analysis, but requiring both Z candidates to be
        on-shell (m4l > 60 GeV), and requiring the candidate m4l
        to be greater than 100 GeV.
        '''
        temp = super(SMPZZ_FullFSR_Sync, self).getCutTemplate()

        temp['ZMassTight']['cuts']['MassFSR#lower'] = (60, ">=")
        temp['4lMass']['cuts']['MassFSR'] = (100, ">=")
        del temp['eMVAID']
        temp['eTightID'] = {
            'cuts' : {
                'CBIDMedium' : (1, ">="),
                'looseEle' : 'eLooseID',
            },
            'objects' : 1,
        }
        temp['mLooseID']['cuts']['Pt'] = (10, ">=")
        temp['eLooseID']['cuts']['Pt'] = (10, ">=")
#        temp['eLooseID']['cuts']['CBIDLoose'] = (1, ">=")
        
        return temp
    

    def setupOtherCuts(self):
        others = super(SMPZZ_FullFSR_Sync, self).setupOtherCuts()
        del others['eMVAID']

        return others


    def setupCutFlow(self):
        '''
        Starting with the full spectrum cut flow, require all Z candidates
        to pass "tight" mass cuts.
        '''
        flow = OrderedDict()
        for name, cut in super(SMPZZ_FullFSR_Sync, self).setupCutFlow().iteritems():
            if name == "Z1Mass":
                continue
            
            if name[0] == "Z" and "MassLoose" in name:
                if name[1] == "1":
                    newName = "Z1Mass"
                    objects = [1,2]
                elif name[1] == "2":
                    newName = "Z2Mass"
                    objects = [3,4]

                flow[newName] = ("ZMassTight", objects)
                continue

            flow[name] = cut

        return flow
            

