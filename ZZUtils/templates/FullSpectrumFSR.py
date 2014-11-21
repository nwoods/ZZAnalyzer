
'''

Cutter for the 2012 HZZ4l analysis, inherits most methods from Cutter.py

Author: Nate Woods, U. Wisconsin

'''

import Cutter
from collections import OrderedDict
from ZZHelpers import *


class FullSpectrumFSR(Cutter.Cutter):
    def __init__(self):
        super(FullSpectrumFSR, self).__init__("FullSpectrumFSR")


    def getCutTemplate(self,*args):
        '''
        Template for all cuts
        '''
        cutTemplate = {
            # Basic cuts
            'Trigger' : {
                'cuts' : {
                    'doubleMuPass' : (1, False),
                    'doubleMuTrkPass' : (1, False),
                    'doubleEPass' : (1, False), 
                    'mu17ele8Pass' : (1, False),
                    'mu8ele17Pass' : (1, False),
                },
                'logic' : 'or',
                'type' : 'base',
            },
            'Overlap' : { 
                'cuts' : { 'DR' : (0.1, False), },
                'objects' : '2',
                'type' : 'base',
                'logic' : 'and',
            },
            'mIso' : { 
                'cuts' : { 'RelPFIsoDBDefault' : (0.4, True) },
                'logic' : 'and',
                'objects' : '1',
                'type' : 'base',
            },
            'mTightIso' : { 
                'cuts' : { 'RelPFIsoDB' : (0.2, True) },
                'objects' : '1',
                'logic' : 'and',
                'type' : 'base',
            },
            'eIso' : { 
                'cuts' : { 'RelPFIsoRhoFSR' : (0.4, True) },
                'logic' : 'and',
                'objects' : '1',
                'type' : 'base',
            },
            'eTightIso' : { 
                'cuts' : { 'RelPFIsoRhoFSR' : (0.2, True) },
                'logic' : 'and',
                'objects' : '1',
                'type' : 'base',
            },
            'eSelection' : {
                'cuts' : {
                    'Pt' : (7., False),
                    'AbsEta' : (2.5, True),
                    'SIP3D' : (4., True),
                    'PVDXY#POS' : (0.5, True),
                    'PVDZ#POS' : (1., True),
                    'PVDXY#NEG' : (-0.5, False),
                    'PVDZ#NEG' : (-1., False),
                },
                'logic' : 'and',
                'objects' : '1',
                'type' : 'base'
            },
            'mSelection' : { 
                'cuts' : {
                    'Pt' : (5., False),
                    'AbsEta' : (2.4, True),
                    'SIP3D' : (4., True),
                    'PVDXY#POS' : (0.5, True),
                    'PVDZ#POS' : (1., True),
                    'PVDXY#NEG' : (-0.5, False),
                    'PVDZ#NEG' : (-1., False),
                },
                'logic' : 'and',
                'objects' : '1',
                'type' : 'base',
            },
            'mID' : { 
                'cuts' : { 
                    'IsGlobal' : (1, False),
                    'IsTracker' : (1, False),
                },
                'logic' : 'or',
                'objects' : '1',
                'type' : 'base',
            },
            'eID' : {
                'cuts' : {
                    'BDTName' : 'MVANonTrigCSA14',
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
                'type' : 'base',
                'logic' : 'other',
            },
            'OS' : {
                'cuts' : { 'SS' : (1., True) },
                'logic' : 'and',
                'objects' : '2',
                'type' : 'base',
            },
            'Z1Mass' : {
                'cuts' : { 
                    'MassFsr#lower' : (40., False),
                    'MassFsr#upper' : (120., True),
                },
                'objects' : '2',
                'type' : 'base',
                'logic' : 'and',
            },
            'Z2Mass' : {
                'cuts' : { 
                    'MassFsr#lower' : (12., False),
                    'MassFsr#upper' : (120., True),
                },
                'objects' : '2',
                'type' : 'base',
                'logic' : 'and',
            },
            'LeptonPairMass' : {
                'cuts' : {
                    'Mass' : (4., False),
                    'SS' : (1, True), # Must be opposite sign, same flavor not required
                },
                'objects' : '2',
                'type' : 'base',
                'logic' : 'or',
            },
            'Lepton1Pt' : {
                'cuts' : {
                    'Pt' : (20., False),
                },
                'logic' : 'and',
                'objects' : '1',
                'type' : 'base',
            },                    
            'Lepton2Pt' : {
                'cuts' : {
                    'Pt' : (10., False),
                },
                'logic' : 'and',
                'objects' : '1',
                'type' : 'base',
            },
            '4lMass' : {
                'cuts' : { 'MassFSR' : (0., False), },
                'logic' : 'and',
                'type' : 'base',
            },

            # Cuts that call other cuts
            'NoOverlap' : {
                'cuts' : { 'ovrlp' : 'Overlap' },
                'objects' : 'pairs',
                'logic' : 'and',
                'type' : 'caller',
                },
            'ZID' : {
                'cuts' : {
                    'ID' : 'TYPEID',
                    'select' : 'TYPESelection',
                },
                'objects' : '2',
                'logic' : 'and',
                'type' : 'caller',
            },
            'GoodZ' : {
                'cuts' : {
                    'OS' : 'OS',
                    'idsel' : 'ZID',
                },
                'logic' : 'and',
                'objects' : 'pairs',
                'type' : 'caller',
            },            
            'ZIso' : {
                'cuts' : {
                    'iso' : 'TYPEIso'
                },
                'logic' : 'and',
                'objects' : '2',
                'type' : 'caller',
            },
            'L1Pt' : {
                'cuts' : {
                    'l1pt' : 'Lepton1Pt',
                },
                'logic' : 'or',
                'objects' : '2',
                'type' : 'caller',
            },
            'L2Pt' : {
                'cuts' : {
                    'Pt' : 'Lepton2Pt',
                },
                'logic' : 'other',
                'objects' : '4',
                'type' : 'caller',
            },
            'MesonVeto' : {
                'cuts' : {
                    'lpm' : 'LeptonPairMass',
                },
                'logic' : 'and',
                'objects' : 'pairs',
                'type' : 'caller',
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
        flow['Overlap'] = ('NoOverlap', [])
        flow['GoodZ1'] = ('GoodZ', [1,2])
        flow['Z1Iso'] = ('ZIso', [1,2])
        flow['Z1Mass'] = ('Z1Mass', [1,2])
        flow['GoodZ2'] = ('GoodZ', [3,4])
        flow['Z2Iso'] = ('ZIso', [3,4])
        flow['Z2Mass'] = ('Z2Mass', [3,4])
        flow['Lepton1Pt'] = ('L1Pt', [1,3])
        flow['Lepton2Pt'] = ('L2Pt', [1,2,3,4])
        flow['LeptonPairMass'] = ('MesonVeto', [1,2,3,4])
        flow['4lMass'] = ('4lMass', [])
        
        return flow


    def setupOtherCuts(self):
        '''
        Define functions that don't fit the template nicely
        '''
        temp = self.getCutTemplate()
        others = {}
        others['eID'] = lambda row, obj: self.eIDTight2012(temp['eID'], row, obj)
        others['L2Pt'] = lambda row, *obj: self.ptCutTwoObjects(temp['L2Pt'], row, *obj)

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

    


