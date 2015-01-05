
'''

Cutter for the 2012 HZZ4l analysis with gen fiducial cuts first.
Inherits most methods from Cutter.py

Author: Nate Woods, U. Wisconsin

'''

import Cutter
from collections import OrderedDict
from rootpy.vector import LorentzVector
from math import atan, sin, exp
from ZZHelpers import *


class FullSpectrumFSR_efficiency(Cutter.Cutter):
    def __init__(self):
        super(FullSpectrumFSR_efficiency, self).__init__("FullSpectrumFSR")


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
                'cuts' : { 'RelPFIsoDBDefault' : (0.2, True) },
                'objects' : '1',
                'logic' : 'and',
                'type' : 'base',
            },
            'eIso' : { 
                'cuts' : { 'RelPFIsoRho' : (0.4, True) },
                'logic' : 'and',
                'objects' : '1',
                'type' : 'base',
            },
            'eTightIso' : { 
                'cuts' : { 'RelPFIsoRho' : (0.2, True) },
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
                    'MassFSR#lower' : (40., False),
                    'MassFSR#upper' : (120., True),
                },
                'objects' : '2',
                'type' : 'base',
                'logic' : 'and',
            },
            'Z2Mass' : {
                'cuts' : { 
                    'MassFSR#lower' : (12., False),
                    'MassFSR#upper' : (120., True),
                },
                'objects' : '2',
                'type' : 'base',
                'logic' : 'and',
            },
            'LeptonPairMass' : {
                'cuts' : {
                    'MassFSR' : (4., False),
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
            'eGenEta' : {
                'cuts' : { 
                    'GenEta#NEG' : (-2.5, False), # no match gives -999
                    'GenEta#POS' : (2.5, True),
                },
                'logic' : 'and',
                'objects' : '1',
                'type' : 'base',
            },
            'mGenEta' : {
                'cuts' : { 
                    'GenEta#NEG' : (-2.4, False), # no match gives -999
                    'GenEta#POS' : (2.4, True),
                },
                'logic' : 'and',
                'objects' : '1',
                'type' : 'base',
            },
            'eGenPt' : {
                'cuts' : { 
                    'GenPt' : 7.,
                },
                'logic' : 'other',
                'objects' : '1',
                'type' : 'base',
            },
            'mGenPt' : {
                'cuts' : { 
                    'GenPt' : 5.,
                },
                'logic' : 'other',
                'objects' : '1',
                'type' : 'base',
            },
            'Lepton1GenPt' : {
                'cuts' : { 
                    'GenPt' : 20.,
                },
                'logic' : 'other',
                'objects' : '1',
                'type' : 'base',
            },
            'Lepton2GenPt' : {
                'cuts' : { 
                    'GenPt' : 10.,
                },
                'logic' : 'other',
                'objects' : '1',
                'type' : 'base',
            },
            'Z1GenMass' : {
                'cuts' : { 
                    'lower' : 40.,
                    'upper' : 120.,
                },
                'objects' : '2',
                'type' : 'base',
                'logic' : 'other',
            },
            'Z2GenMass' : {
                'cuts' : { 
                    'lower' : 12.,
                    'upper' : 120.,
                },
                'objects' : '2',
                'type' : 'base',
                'logic' : 'other',
            },

            # Cuts that call other cuts
            'L1GenPt': {
                'cuts' : {
                    'GenPt' : 'Lepton1GenPt',
                },
                'logic' : 'or',
                'objects' : '4',
                'type' : 'caller',
            },
            'L2GenPt': {
                'cuts' : {
                    'GenPt' : 'Lepton2GenPt',
                },
                'logic' : 'other',
                'objects' : '4',
                'type' : 'caller',
            },
            'GenLeptons' : {
                'cuts' : {
                    'genEta' : 'TYPEGenEta',
                    'genPt' : 'TYPEGenPt',
                    },
                'logic' : 'and',
                'objects' : '4',
                'type' : 'caller',
            },
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
        flow['GenLeptons'] = ('GenLeptons', [1,2,3,4])
        flow['Lepton1GenPt'] = ('L1GenPt', [1,2,3,4])
        flow['Lepton2GenPt'] = ('L2GenPt', [1,2,3,4])
        flow['Z1GenMass'] = ('Z1GenMass', [1,2])
        flow['Z2GenMass'] = ('Z2GenMass', [3,4])
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
        others['eGenPt'] = lambda row, obj: self.genPtCut(temp['eGenPt'], row, obj)
        others['mGenPt'] = lambda row, obj: self.genPtCut(temp['mGenPt'], row, obj)
        others['Lepton1GenPt'] = lambda row, *obj: self.genPtCut(temp['Lepton1GenPt'], row, *obj)
        others['Lepton2GenPt'] = lambda row, *obj: self.genPtCut(temp['Lepton2GenPt'], row, *obj)
        others['L2GenPt'] = lambda row, *obj: self.genPtCutTwoObjects(temp['Lepton2GenPt'], row, *obj)
        others['Z1GenMass'] = lambda row, *obj: self.genZMassCut(temp['Z1GenMass'], row, *obj)
        others['Z2GenMass'] = lambda row, *obj: self.genZMassCut(temp['Z2GenMass'], row, *obj)

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

    
    def genPtCutTwoObjects(self, params, row, *obj):
        nPassed = 0
        for ob in obj:
            if self.genPtCut(params, row, ob):
                nPassed += 1
            if nPassed == 2:
                return True
        return False

        
    def genPtCut(self, params, row, obj):
        '''
        Returns True if pt of gen object matched to obj is above threshold
        '''
        genPt = self.getGenP4(row, obj).Pt()
        return genPt >= params['cuts']['GenPt']


    def genZMassCut(self, params, row, *obj):
        '''
        Get inv mass of two objects, cuts on it (using params['cuts']['upper'] and ...['lower']
        '''
        p41 = self.getGenP4(row, obj[0])
        p42 = self.getGenP4(row, obj[1])
        
        zP4 = p41 + p42
        mZ = zP4.M()

        return mZ < params['cuts']['upper'] and mZ >= params['cuts']['lower']

    
    def getGenP4(self, row, obj):
        '''
        Return the 4-momentum of the gen object matched to obj
        '''
        en = objVar(row, "GenEnergy", obj)
        if en == -999: # don't care since it will fail gen eta anyway
            return LorentzVector()

        m = objVar(row, "Mass", obj)
        eta = objVar(row, "GenEta", obj)
        phi = objVar(row, "GenPhi", obj)
        
        # Calculate pt ourselves since ROOT won't do it
        theta = 2*atan(exp(-eta))        
        pt = sqrt(en**2 - m**2) * sin(theta)

        p4 = LorentzVector()
        p4.SetPtEtaPhiE(pt, eta, phi, en)
        return p4
