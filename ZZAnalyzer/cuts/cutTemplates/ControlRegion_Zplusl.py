
'''

Cutter for Z+l_loose control region for the 2015 HZZ4l analysis. 
Inherits from the control region base class. 
Two leptons must make a good (tight ID, |m-mZ|<10) Z, the other must
pass loose lepton ID. A separate analyzer can run over the result of
this analyzer to get the numerator for the fake rate study (this is the
denominator).

Author: Nate Woods, U. Wisconsin

'''

from collections import OrderedDict

from ZZAnalyzer.cuts.cutTemplates.ControlRegion_Base import ControlRegion_Base
from ZZAnalyzer.utils.helpers import Z_MASS

from rootpy.vector import LorentzVector


class ControlRegion_Zplusl(ControlRegion_Base):
    def __init__(self, cutset="ControlRegion_Zplusl"):
        super(ControlRegion_Zplusl, self).__init__(cutset)


    def getCutTemplate(self, *args):
        '''
        Add a few cuts we need for the SS CR
        '''
        temp = super(ControlRegion_Zplusl, self).getCutTemplate(self, *args)

        # ee and mumu triggers only here
        temp['Trigger'] = {
            'cuts' : {
                'doubleEPass' : (1, ">="),
                'doubleMuPass' : (1, ">="),
                },
            'logic' : 'or',
            }

        # # trigger object matching
        # temp['eTriggerMatch'] = {
        #     'cuts' : {
        #         'MatchesDoubleE' : (1., ">="),
        #         },
        #     'objects' : 1,
        #     }
        # temp['mTriggerMatch'] = {
        #     'cuts' : {
        #         'MatchesDoubleMu' : (1., ">="),
        #         },
        #     'objects' : 1,
        #     }
        # temp['leptonTriggerMatch'] = {
        #     'cuts' : {
        #         'trgMtch' : 'TYPETriggerMatch',
        #         },
        #     'objects' : 1,
        #     }
        # temp['ZTriggerMatch'] = {
        #     'cuts' : {
        #         'trgMtch' : 'leptonTriggerMatch',
        #         },
        #     'logic' : 'objand',
        #     }

        # Event is not in another category
        temp['4lVeto'] = {
            'cuts' : {
                '3e'   : '4lVeto3e',
                '2e1m' : '4lVeto2e1m',
                '1e2m' : '4lVeto1e2m',
                '3m'   : '4lVeto3m',
            },
            'logic' : 'or',
        }
        temp['4lVeto3e'] = {
            'cuts' : {
                'nZZLooseElec#up' : (3.1, '<'),
                'nZZLooseElec#down' : (2.9, '>='),
                'nZZLooseMu' : (0.1, '<'),
                },
            }
        temp['4lVeto2e1m'] = {
            'cuts' : {
                'nZZLooseElec#up' : (2.1, '<'),
                'nZZLooseElec#down' : (1.9, '>='),
                'nZZLooseMu#up' : (1.1, '<'),
                'nZZLooseMu#down' : (0.9, '>='),
                },
            }
        temp['4lVeto1e2m'] = {
            'cuts' : {
                'nZZLooseElec#up' : (1.1, '<'),
                'nZZLooseElec#down' : (0.9, '>='),
                'nZZLooseMu#up' : (2.1, '<'),
                'nZZLooseMu#down' : (1.9, '>='),
                },
            }
        temp['4lVeto3m'] = {
            'cuts' : {
                'nZZLooseElec' : (0.1, '<'),
                'nZZLooseMu#up' : (3.1, '<'),
                'nZZLooseMu#down' : (2.9, '>='),
                },
            }

        temp['ZMassTight']['cuts']['Mass%s#lower'%self.fsrVar] = (Z_MASS-10., ">=")
        temp['ZMassTight']['cuts']['Mass%s#upper'%self.fsrVar] = (Z_MASS+10., "<")

        temp['METVeto'] = {
            'cuts' : {
                'type1_pfMETEt' : (25., "<"),
                },
            }

        temp['MtVeto'] = {
            'cuts' : {
                'MtToMET' : (30., "<"),
            },
            'objects' : 1,
        }

        return temp


    def setupCutFlow(self):
        '''
        As the full spectum cutter, except as above
        No call to super(), as this is really the only 3l cutter
        '''
        flow = OrderedDict()
        
        flow['Trigger'] = ('Trigger', [])
        flow['METVeto'] = ('METVeto', [])
        flow['ExtraLepVeto'] = ('4lVeto', [])
        flow['ZLeptonID'] = ('GoodLeptons', [1,2])
        flow['ZLeptonIso'] = ('Isolation', [1,2])
        # flow['ZLeptonTriggerMatch'] = ('ZTriggerMatch', [1,2])
        flow['Lepton3ID'] = ('leptonLooseID', [3])
        flow['MtVeto'] = ('MtVeto', [3])
        flow['SIP'] = ('SIP', [1,2,3])
        flow['GoodZ'] = ('GoodZ', [1,2])
        flow['ZMass'] = ('ZMassTight', [1,2])
        flow['Overlap'] = ('Overlap', [1,2,3])
        flow['Lepton1Pt'] = ('Lepton1Pt', [1,3])
        flow['Lepton2Pt'] = ('Lepton2Pt', [1,2,3])
        flow['QCDVeto'] = ('QCDVeto', [1,2,3])
        flow['Vertex'] = ('Vertex', [])
        
        return flow


    def needReorder(self, channel):
        '''
        3e, 3mu, and eemu are already in the right order. emumu is always in 
        the wrong order (should always be m1, m2, e)
        '''
        return channel == 'emm'


    def orderLeptons(self, row, channel, objects):
        '''
        Should only get called for emumu channel, where we always need 
        to swap the order.
        '''
        return objects[1:]+[objects[0]]
