'''
Cutter for the legacy SMP ZZ analysis, inherits most methods from Cutter.py
Author: Nate Woods, U. Wisconsin
'''

import Cutter
from collections import OrderedDict
from ZZHelpers import *


class SMPZZ8TeV(Cutter.Cutter):
    def __init__(self):
        super(SMPZZ8TeV, self).__init__("SMPZZ8TeV")


    def getCutTemplate(self,*args):
        '''
        Template for all cuts
        '''
        cutTemplate = {
            # Basic cuts
            'Trigger' : {
                'cuts' : {
                    'doubleMuPass' : (1, ">="),
                    'doubleEPass' : (1, ">="), 
                    'mu8ele17Pass' : (1, ">="),
                    'mu17ele8Pass' : (1, ">="),
                    'tripleEPass' : (1,">="),
                },
                'logic' : 'or',
            },
            'Overlap' : { 
                'cuts' : { 'DR' : (0.1, ">="), },
                'objects' : 'pairs',
                'logic' : 'objand',
            },
            'mIso' : { 
                'cuts' : { 'RelPFIsoDBDefault' : (0.4, "<") },
                'objects' : '1',
            },
            'mTightIso' : { 
                'cuts' : { 'RelPFIsoDBDefault' : (0.2, "<") },
                'objects' : '1',
            },
            'eIso' : { 
                'cuts' : { 'RelPFIsoRho' : (0.4, "<") },
                'objects' : '1',
            },
            'eTightIso' : { 
                'cuts' : { 'RelPFIsoRho' : (0.2, "<") },
                'objects' : '1',
            },
            'eSelection' : {
                'cuts' : {
                    'Pt' : (7., ">="),
                    'Eta#POS' : (2.5, "<"),
                    'Eta#NEG' : (-2.5, ">="),
#                    'SIP3D' : (4., "<"),  # Do via stupid hack below
                    'PVDXY#POS' : (0.5, "<"),
                    'PVDZ#POS' : (1., "<"),
                    'PVDXY#NEG' : (-0.5, ">="),
                    'PVDZ#NEG' : (-1., ">="),
                },
                'objects' : '1',
            },
            'mSelection' : { 
                'cuts' : {
                    'Pt' : (5., ">="),
                    'Eta#POS' : (2.4, "<"),
                    'Eta#NEG' : (-2.4, ">="),
#                    'SIP3D' : (4., "<"),  # Do via stupid hack below
                    'PVDXY#POS' : (0.5, "<"),
                    'PVDZ#POS' : (1., "<"),
                    'PVDXY#NEG' : (-0.5, ">="),
                    'PVDZ#NEG' : (-1., ">="),
                },
                'objects' : '1',
            },
            'SIP3D' : {
                'cuts' : {
                    'IP3DS' : (4., "<"),
                    },
                'objects' : '1',
            },
            'mID' : { 
                'cuts' : { 
                    'IsGlobal' : (1, ">="),
                    'IsTracker' : (1, ">="),
                },
                'logic' : 'or',
                'objects' : '1',
            },
            'eID' : {
                'cuts' : {
                    'BDTName' : 'MVANonTrig',
                    'ptThr' : 10,
                    'etaLow' : 0.8,
                    'etaHigh' : 1.479,
                    'lowPtLowEta' : (0.47, ">="),
                    'lowPtMedEta' : (0.004, ">="),
                    'lowPtHighEta' : (0.295, ">="),
                    'highPtLowEta' : (-0.34, ">="),
                    'highPtMedEta' : (-0.65, ">="),
                    'highPtHighEta' : (0.6, ">="),
                },
                'objects' : '1',
                'logic' : 'other',
            },
            'OS' : {
                'cuts' : { 'SS' : (1., "<") },
                'logic' : 'and',
                'objects' : '2',
            },
            'Z1Mass' : {
                'cuts' : { 
                    'Mass#lower' : (60., ">="),
                    'Mass#upper' : (120., "<"),
                },
                'objects' : '2',
            },
            'Z2Mass' : {
                'cuts' : { 
                    'Mass#lower' : (60., ">="),
                    'Mass#upper' : (120., "<"),
                },
                'objects' : '2',
            },
            'LeptonPairMass' : {
                'cuts' : {
                    'Mass' : (4., ">="),
                    'SS' : (1, "<"), # Must be opposite sign, same flavor not required
                },
                'objects' : '2',
                'logic' : 'or',
            },
            'Lepton1Pt' : {
                'cuts' : {
                    'Pt' : (20., ">="),
                },
                'objects' : '1',
            },                    
            'Lepton2Pt' : {
                'cuts' : {
                    'Pt' : (10., ">="),
                },
                'objects' : '1',
            },
            '4lMass' : {
                'cuts' : { 'Mass' : (100., ">="), },
            },

            # Cuts that call other cuts
            'NoOverlap' : {
                'cuts' : { 'ovrlp' : 'Overlap' },
                'objects' : 'pairs',
                'logic' : 'objand',
            },
            'ZID' : {
                'cuts' : {
                    'ID' : 'TYPEID',
                    'select' : 'TYPESelection',
                    'SIP3D' : 'SIP3D',
                },
                'objects' : '2',
                'logic' : 'objand',
            },
            'GoodZ' : {
                'cuts' : {
                    'OS' : 'OS',
                    'idsel' : 'ZID',
                },
                'objects' : 'pairs',
            },            
            'ZIso' : {
                'cuts' : {
                    'iso' : 'TYPEIso'
                },
                'objects' : '2',
                'logic' : 'objand',
            },
            'L1Pt' : {
                'cuts' : {
                    'l1pt' : 'Lepton1Pt',
                },
                'logic' : 'objor',
                'objects' : '2',
            },
            'L2Pt' : {
                'cuts' : {
                    'Pt' : 'Lepton2Pt',
                },
                'logic' : 'other',
                'objects' : '4',
            },
            'QCDVeto' : {
                'cuts' : {
                    'lpm' : 'LeptonPairMass',
                },
                'logic' : 'objand',
                'objects' : 'pairs',
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
        flow['Overlap'] = ('NoOverlap', [1,2,3,4])
        flow['GoodZ1'] = ('GoodZ', [1,2])
        flow['Z1Iso'] = ('ZIso', [1,2])
        flow['Z1Mass'] = ('Z1Mass', [1,2])
        flow['GoodZ2'] = ('GoodZ', [3,4])
        flow['Z2Iso'] = ('ZIso', [3,4])
        flow['Z2Mass'] = ('Z2Mass', [3,4])
        flow['Lepton1Pt'] = ('L1Pt', [1,3])
        flow['Lepton2Pt'] = ('L2Pt', [1,2,3,4])
        flow['LeptonPairMass'] = ('QCDVeto', [1,2,3,4])
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


    def orderLeptons(self, row, channel, objects):
        '''
        Same as default but no FSR.
        '''
        dM1 = zCompatibility_checkSign(row,objects[0],objects[1], False)
        dM2 = zCompatibility_checkSign(row,objects[2],objects[3], False)
        
        if dM1 > dM2:
            return objects[2:] + objects[:2]
        return objects

