
'''

Cutter for the 2012 HZZ4l analysis, inherits most methods from Cutter.py

Author: Nate Woods, U. Wisconsin

'''

import Cutter
from collections import OrderedDict
from ZZHelpers import *


class FullSpectrum_FullFSR(Cutter.Cutter):
    def __init__(self):
        super(FullSpectrum_FullFSR, self).__init__("FullSpectrum_FullFSR")


    def getCutTemplate(self,*args):
        '''
        Template for all cuts
        '''
        cutTemplate = {
            # Basic cuts
            'Trigger' : {
                'cuts' : {
                    'doubleMuPass' : (1, False),
                    'doubleEPass' : (1, False), 
                    'eMuPass' : (1, False),
                    'muEPass' : (1, False),
                    'tripleEPass' : (1,False),
                },
                'logic' : 'or',
            },
            'Overlap' : { 
                'cuts' : { 'DR' : (0.1, False), },
                'objects' : 'pairs',
                'logic' : 'objand',
            },
            'eLooseID' : {
                'cuts' : {
                    'Pt' : (7., False),
                    'Eta#POS' : (2.5, True),
                    'Eta#NEG' : (-2.5, False),
#                    'SIP3D' : (4., True),
                    'PVDXY#POS' : (0.5, True),
                    'PVDZ#POS' : (1., True),
                    'PVDXY#NEG' : (-0.5, False),
                    'PVDZ#NEG' : (-1., False),
                },
                'objects' : '1',
            },
            'eMVAID' : {
                'cuts' : {
                    'BDTName' : 'MVANonTrigID',
                    'ptThr' : 10,
                    'etaLow' : 0.8,
                    'etaHigh' : 1.479,
                    'lowPtLowEta' : (0.47, False),
                    'lowPtMedEta' : (0.004, False),
                    'lowPtHighEta' : (0.295, False),
                    'highPtLowEta' : (-0.34, False),
                    'highPtMedEta' : (-0.65, False),
                    'highPtHighEta' : (0.6, False),
                },
                'objects' : '1',
                'logic' : 'other',
            },
            'eTightID' : {
                'cuts' : {
                    'MVA' : 'eMVAID',
                    'looseEle' : 'eLooseID',
                },
                'objects' : 1,
            },
            'mTrkOrGlob' : { 
                'cuts' : { 
                    'IsGlobal' : (1, False),
                    'IsTracker' : (1, False),
                },
                'logic' : 'or',
                'objects' : '1',
            },
            'mLooseID' : { 
                'cuts' : {
                    'Pt' : (5., False),
                    'Eta#POS' : (2.4, True),
                    'Eta#NEG' : (-2.4, False),
                    'type' : 'mTrkOrGlob',
                    'PVDXY#POS' : (0.5, True),
                    'PVDZ#POS' : (1., True),
                    'PVDXY#NEG' : (-0.5, False),
                    'PVDZ#NEG' : (-1., False),
                },
                'objects' : '1',
            },
            'mTightID' : {
                'cuts' : {
                    'looseMu' : 'mLooseID',
                    'IsGlobal' : (1, 'greq'),
                },
                'objects' : 1,
            },
            'leptonTightID' : {
                'cuts' : {'id' : 'TYPETightID'},
                'objects' : 1,
            },
            'ZID' : {
                'cuts' : {
                    'ID' : 'leptonTightID',
                },
                'objects' : 2,
                'logic' : 'objand',
            },
            'GoodZ' : {
                'cuts' : {
                    'SS' : (1, "<"),
                    'idsel' : 'ZID',
                },
                'objects' : 2,
            },            
            'mIso' : { 
                'cuts' : { 'RelPFIsoDBDefaultFSR' : (0.4, True) },
                'objects' : '1',
            },
            'eIso' : { 
                'cuts' : { 'RelPFIsoRhoFSR' : (0.4, True) },
                'objects' : '1',
            },
            'ZIso' : {
                'cuts' : {
                    'isolation' : 'TYPEIso',
                },
                'objects' : 2,
                'logic' : 'objand',
            },
            'Z1Mass' : {
                'cuts' : { 
                    'MassFSR#lower' : (40., False),
                    'MassFSR#upper' : (120., True),
                },
                'objects' : '2',
            },
            'Z2Mass' : {
                'cuts' : { 
                    'MassFSR#lower' : (12., 'greaterthan'),
                    'MassFSR#upper' : (120., 'less'),
                },
                'objects' : 2,
            },
            'Lepton1Pt' : {
                'cuts' : {
                    'PtFSR' : (20., 'greq'),
                },
                'objects' : '2',
                'logic' : 'objor',
            },                    
            'LeptonPairPt' : {
                'cuts' : {
                    'PtFSR' : (10., '>='),
                },
                'objects' : '2',
                'logic' : 'objand',
            },
            'Lepton2Pt' : { # make sure some pair of two leptons both pass the l2 pt cut
                'cuts' : {
                    'goodPair' : 'LeptonPairPt',
                },
                'logic' : 'objor',
                'objects' : 'pairs',
            },
            'LeptonPairMass' : {
                'cuts' : {
                    'Mass' : (4., False),
                    'SS' : (1, True), # Must be opposite sign, same flavor not required
                },
                'objects' : '2',
                'logic' : 'or',
            },
            'QCDVeto' : {
                'cuts' : {
                    'invMass' : 'LeptonPairMass',
                },
                'logic' : 'objand',
                'objects' : 'pairs',
            },
            '4lMass' : {
                'cuts' : { 'MassFSR' : (0., False), },
            },
        }

        return cutTemplate


    def setupCutFlow(self):
        '''
        Dictionary with order and (one-indexed) numbers of particles to cut on
        '''
        flow = OrderedDict()
        flow['Total'] = ('true', [])
        flow['Trigger'] = ('Trigger', [])
        flow['Overlap'] = ('Overlap', [])
        flow['GoodZ1'] = ('GoodZ', [1,2])
        flow['Z1Iso'] = ('ZIso', [1,2])
        flow['Z1Mass'] = ('Z1Mass', [1,2])
        flow['GoodZ2'] = ('GoodZ', [3,4])
        flow['Z2Iso'] = ('ZIso', [3,4])
        flow['Z2Mass'] = ('Z2Mass', [3,4])
        flow['Lepton1Pt'] = ('Lepton1Pt', [1,3])
        flow['Lepton2Pt'] = ('Lepton2Pt', [1,2,3,4])
        flow['LeptonPairMass'] = ('QCDVeto', [1,2,3,4])
        flow['4lMass'] = ('4lMass', [])
        
        return flow


    def setupOtherCuts(self):
        '''
        Define functions that don't fit the template nicely
        '''
        temp = self.getCutTemplate()
        others = {}
        others['eMVAID'] = lambda row, obj: self.eIDTight2012(temp['eMVAID'], row, obj)

        return others


    def eIDTight2012(self, params, row, obj):
        BDTName = params['cuts']['BDTName']
        pt = objVar(row, 'Pt', obj)
        eta = objVar(row, 'SCEta', obj)
        bdt = objVar(row, BDTName, obj)
        if pt < params['cuts']['ptThr']:
            ptStr = 'lowPt'
        else:
            ptStr = 'highPt'

        if abs(eta) < params['cuts']['etaLow']:
            etaStr = 'LowEta'
        elif abs(eta) > params['cuts']['etaHigh']:
            etaStr = 'HighEta'
        else:
            etaStr = 'MedEta'

        return self.cutObjVar(row, BDTName, params['cuts'][ptStr+etaStr][0], params['cuts'][ptStr+etaStr][1], obj)


    def ptCutTwoObjects(self, params, row, *obj):
        nPassed = 0
        for ob in obj:
            if self.doCut(row, params['cuts']['Pt'], ob):
                nPassed += 1
            if nPassed == 2:
                return True
        return False

    


