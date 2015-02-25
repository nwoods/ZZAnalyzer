
'''

Cutter for the 2012 HZZ4l analysis, inherits most methods from Cutter.py

Author: Nate Woods, U. Wisconsin

'''

import Cutter
from collections import OrderedDict
from ZZHelpers import *


class SMPZZ_FullFSR_IDSplit(Cutter.Cutter):
    def __init__(self):
        super(SMPZZ_FullFSR_IDSplit, self).__init__("SMPZZ_FullFSR_IDSplit")


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
                'type' : 'base',
            },
            'Overlap' : { 
                'cuts' : { 'DRFSR' : (0.1, False), },
                'objects' : '2',
                'type' : 'base',
                'logic' : 'and',
            },
            'mIso' : { 
                'cuts' : { 'RelPFIsoDBDefaultFSR' : (0.4, True) },
                'logic' : 'and',
                'objects' : '1',
                'type' : 'base',
            },
            'mTightIso' : { 
                'cuts' : { 'RelPFIsoDBDefaultFSR' : (0.2, True) },
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
                    'Eta#POS' : (2.5, True),
                    'Eta#NEG' : (-2.5, False),
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
            'eKinematics' : {
                'cuts' : {
                    'Pt' : (7., False),
                    'Eta#POS' : (2.5, True),
                    'Eta#NEG' : (-2.5, False),
                },
                'logic' : 'and',
                'objects' : '1',
                'type' : 'base'
            },
            'SIP' : {
                'cuts' : {
                    'SIP3D' : (4., True),
                },
                'logic' : 'and',
                'objects' : '1',
                'type' : 'base'
            },
            'PV' : {
                'cuts' : {
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
                    'Eta#POS' : (2.4, True),
                    'Eta#NEG' : (-2.4, False),
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
            'mKinematics' : { 
                'cuts' : {
                    'Pt' : (5., False),
                    'Eta#POS' : (2.4, True),
                    'Eta#NEG' : (-2.4, False),
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
                    'MassFSR#lower' : (60., False),
                    'MassFSR#upper' : (120., True),
                },
                'objects' : '2',
                'type' : 'base',
                'logic' : 'and',
            },
            'Z2Mass' : {
                'cuts' : { 
                    'MassFSR#lower' : (60., False),
                    'MassFSR#upper' : (120., True),
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
                    'PtFSR' : (20., False),
                },
                'logic' : 'and',
                'objects' : '1',
                'type' : 'base',
            },                    
            'Lepton2Pt' : {
                'cuts' : {
                    'PtFSR' : (10., False),
                },
                'logic' : 'and',
                'objects' : '1',
                'type' : 'base',
            },
            '4lMass' : {
                'cuts' : { 'MassFSR' : (100., False), },
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
                },
                'objects' : '2',
                'logic' : 'and',
                'type' : 'caller',
            },
            'ZSelection' : {
                'cuts' : {
                    'select' : 'TYPESelection',
                },
                'objects' : '2',
                'logic' : 'and',
                'type' : 'caller',
            },
            'ZKinematics' : {
                'cuts' : {
                    'select' : 'TYPEKinematics',
                },
                'objects' : '2',
                'logic' : 'and',
                'type' : 'caller',
            },
            'ZSIP' : {
                'cuts' : {
                    'select' : 'SIP',
                },
                'objects' : '2',
                'logic' : 'and',
                'type' : 'caller',
            },
            'ZPV' : {
                'cuts' : {
                    'select' : 'PV',
                },
                'objects' : '2',
                'logic' : 'and',
                'type' : 'caller',
            },
            'GoodZID' : {
                'cuts' : {
                    'OS' : 'OS',
                    'idsel' : 'ZID',
                },
                'logic' : 'and',
                'objects' : 'pairs',
                'type' : 'caller',
            },            
            'GoodZSelection' : {
                'cuts' : {
                    'idsel' : 'ZSelection',
                },
                'logic' : 'and',
                'objects' : 'pairs',
                'type' : 'caller',
            },            
            'GoodZ' : {
                'cuts' : {
                    'OS' : 'OS',
                    'id' : 'ZID',
                    'sel' : 'ZSelection',
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
            'QCDVeto' : {
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
        flow['Z1ID'] = ('GoodZID', [1,2])
        flow['Z1Kinematics'] = ('ZKinematics', [1,2])
        flow['Z1SIP'] = ('ZSIP', [1,2])
        flow['Z1PV'] = ('ZPV', [1,2])
        flow['Z1Iso'] = ('ZIso', [1,2])
        flow['Z1Mass'] = ('Z1Mass', [1,2])
        flow['Z2ID'] = ('GoodZID', [3,4])
        flow['Z2Kinematics'] = ('ZKinematics', [3,4])
        flow['Z2SIP'] = ('ZSIP', [3,4])
        flow['Z2PV'] = ('ZPV', [3,4])
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

    


