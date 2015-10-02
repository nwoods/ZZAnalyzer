
'''

Cutter for the 2012 HZZ4l analysis, inherits most methods from Cutter.py

Author: Nate Woods, U. Wisconsin

'''

import Cutter
from collections import OrderedDict
from ZZHelpers import *


class FullSpectrum_FullFSR_Sync(Cutter.Cutter):
    fsrVar = "FSR"

    def __init__(self, cutset="FullSpectrum_FullFSR_Sync"):
        super(FullSpectrum_FullFSR_Sync, self).__init__(cutset)


    def getCutTemplate(self,*args):
        '''
        Template for all cuts
        '''
        cutTemplate = {
            # Good vertex
            'Vertex' : {
                'cuts' : {
                    'pvIsFake' : (1, "<"),
                    'pvndof' : (4., ">="),
                    'pvZ#POS' : (24., "<"),
                    'pvZ#NEG' : (-24., ">"),
                    'pvRho' : (2., "<"),
                },
            },

            # Triggers
            ### We don't change out cuts by channel, but we can get the same
            ### effect by requiring: 
            ###    (has muon AND passes mu triggers) OR
            ###    (has electron AND passes e triggers) OR
            ###    (has electron and muon AND passes cross triggers)
#             'MuTriggers' : {
#                 'cuts' : {
#                     'doubleMuPass' : (1, ">="),
#                 },
#                 'objects' : 'ignore',
#                 'logic' : 'or'
#             },
#             'ETriggers' : {
#                 'cuts' : {
#                     'doubleEPass' : (1, ">="), 
#                     'tripleEPass' : (1, ">="),
#                 },
#                 'logic' : 'or',
#                 'objects' : 'ignore',
#             },
#             'CrossTriggers' : {
#                 'cuts' : {
#                     'eMuPass' : (1, ">="),
#                     'muEPass' : (1, ">="),
#                 },
#                 'logic' : 'or',
#                 'objects' : 'ignore',
#             },
#             'MuHLTPaths' : {
#                 'cuts' : {
#                     'aMuon' : 'IsMuon',
#                     'muTrg' : 'MuTriggers',
#                 },
#                 'logic' : 'objor', # we just need one muon to pull this off
#             },
#             'EHLTPaths' : {
#                 'cuts' : {
#                     'anElectron' : 'IsElectron',
#                     'eTrg' : 'ETriggers',
#                 },
#                 'logic' : 'objor', # we just need one electron to pull this off
#             },
#             'CrossHLTPaths' : {
#                 'cuts' : {
#                     'muPlusE' : 'DifferentFlavor',
#                     'xTrg' : 'CrossTriggers',
#                 },
#                 'objects' : 2, # we'll pass leptons 1 and 3 in
#             },
            'Trigger' : {
                'cuts' : {
                    'doubleEPass' : (1, ">="),
                    'tripleEPass' : (1, ">="),
                    'doubleMuPass' : (1, ">="),
                    'singleMuSingleEPass' : (1, ">="),
                    'singleESingleMuPass' : (1, ">="),
                    'tripleMuPass' : (1, ">="),
                    'singleEPass' : (1, ">="),
                    'doubleESingleMuPass' : (1, ">="),
                    'doubleMuSingleEPass' : (1, ">="),
                },
                'logic' : 'or',
            },

            # Lepton ID
            'eLooseID' : {
                'cuts' : {
                    'Pt' : (7., ">="),
                    'Eta#POS' : (2.5, "<"),
                    'Eta#NEG' : (-2.5, ">="),
                    'PVDXY#POS' : (0.5, "<"),
                    'PVDZ#POS' : (1., "<"),
                    'PVDXY#NEG' : (-0.5, ">="),
                    'PVDZ#NEG' : (-1., ">="),
                    # 'MissingHits' : (2, "<"),
                },
                'objects' : '1',
            },
            'eMVAID' : {
                'cuts' : {
                    'BDTName' : 'MVANonTrigID',
                    'ptThr' : 10,
                    'etaLow' : 0.8,
                    'etaHigh' : 1.479,
                    'lowPtLowEta' : (-0.265, False),
                    'lowPtMedEta' : (-0.556, False),
                    'lowPtHighEta' : (-0.551, False),
                    'highPtLowEta' : (-0.072, False),
                    'highPtMedEta' : (-0.286, False),
                    'highPtHighEta' : (-0.267, False),
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
            'TrackerMuon' : {
                'cuts' : {
                    'IsTracker' : (1, ">="),
                    'MatchedStations' : (1, ">="), # Equivalent to tkmu arbitration
                },
                'objects' : 1,
            },
            'mTrkOrGlob' : { 
                'cuts' : { 
                    'IsGlobal' : (1, ">="),
                    'tkMu' : 'TrackerMuon',
                },
                'logic' : 'or',
                'objects' : 1,
            },
            'BestTrackType' : { # just can't be type 2 (standalone)
                'cuts' : {
                    'BestTrackType#ONE' : (2, "<"),
                    'BestTrackType#OTHER' : (3, ">="),
                },
                'objects' : 1,
                'logic' : 'or',
            },
            'mLooseID' : { 
                'cuts' : {
                    'Pt' : (5., ">="),
                    'Eta#POS' : (2.4, "<"),
                    'Eta#NEG' : (-2.4, ">="),
                    'type' : 'mTrkOrGlob',
                    'PVDXY#POS' : (0.5, "<"),
                    'PVDZ#POS' : (1., "<"),
                    'PVDXY#NEG' : (-0.5, ">="),
                    'PVDZ#NEG' : (-1., ">="),
                    'BestTrack' : 'BestTrackType',
                },
                'objects' : 1,
            },
            'mTightID' : {
                'cuts' : {
                    'looseMu' : 'mLooseID',
                    'IsPFMuon' : (1, 'greq'),
                },
                'objects' : 1,
            },
            'leptonTightID' : {
                'cuts' : {'id' : 'TYPETightID'},
                'objects' : 1,
            },
            'GoodLeptons' : {
                'cuts' : {
                    'id' : 'leptonTightID',
                },
                'logic' : 'objand',
            },

            # Cross Cleaning
            'eCrossClean' : {
                'cuts' : {
                    'NearestMuonDR' : (0.05, ">="),
                },
                'objects' : 1,
            },
            'mCrossClean' : {
                'cuts' : { 'foo' : 'true', },
                'objects' : 1,
            },
            'LeptonCrossClean' : {
                'cuts' : {
                    'clean' : 'TYPECrossClean',
                },
                'objects' : 1,
            },
            'CrossCleaning' : {
                'cuts' : {
                    'lepXClean' : 'LeptonCrossClean',
                },
                'logic' : 'objand',
            },

            # SIP
            'SIP' : {
                'cuts' : {
                    'SIP3D' : (4., "<"),
                },
                'logic' : 'objand',
            },

            # Good (OSSF) Z candidates
            'GoodZ' : {
                'cuts' : {
                    'SS' : (1, "<"),
                },
                'objects' : 2,
            },            

            # Isolation
            'mIso' : { 
                'cuts' : { 'RelPFIsoDB'+(self.fsrVar if self.fsrVar else 'Default') : (0.4, "<") },
                'objects' : 1,
            },
            'eIso' : { 
                'cuts' : { 'RelPFIsoRho'+self.fsrVar : (0.5, "<") },
                'objects' : 1,
            },
            'LeptonIso' : {
                'cuts' : {
                    'isolation' : 'TYPEIso',
                },
                'objects' : 1,
            },
            'Isolation' : {
                'cuts' : {
                    'iso' : 'LeptonIso',
                },
                'logic' : 'objand',
            },

            # Z mass round 1
            'ZMassLoose' : {
                'cuts' : { 
                    'Mass%s#lower'%self.fsrVar : (12., '>='),
                    'Mass%s#upper'%self.fsrVar : (120., '<'),
                },
                'objects' : 2,
            },

            # Overlap (ghost cleaning)
            'Overlap' : { 
                'cuts' : { 'DR' : (0.02, ">="), },
                'objects' : 'pairs',
                'logic' : 'objand',
            },

            # pt of the first and second leptons
            'Lepton1Pt' : {
                'cuts' : {
                    'Pt' : (20., '>='),
                },
                'objects' : 2, # only need to test leptons 1 and 3 in FSA ordering
                'logic' : 'objor',
            },                    
            'LeptonPairPt' : {
                'cuts' : {
                    'Pt' : (10., '>='),
                },
                'objects' : 2,
                'logic' : 'objand',
            },
            'Lepton2Pt' : { # make sure some pair of two leptons both pass the l2 pt cut
                'cuts' : {
                    'goodPair' : 'LeptonPairPt',
                },
                'logic' : 'objor',
                'objects' : 'pairs',
            },

            # QCD suppression (cut on mass of all OS pairs)
            'LeptonPairMass' : {
                'cuts' : {
                    'Mass' : (4., ">="),
                    'SS' : (1, ">="), # If same sign, we don't care about the mass (same flavor not required)
                },
                'objects' : 2,
                'logic' : 'or',
            },
            'QCDVeto' : {
                'cuts' : {
                    'invMass' : 'LeptonPairMass',
                },
                'logic' : 'objand',
                'objects' : 'pairs',
            },

            # Z1 mass
            'ZMassTight' : {
                'cuts' : { 
                    'Mass%s#lower'%self.fsrVar : (40., ">="),
                    'Mass%s#upper'%self.fsrVar : (120., "<"),
                },
                'objects' : 2,
            },

            # 4l Mass
            '4lMass' : {
                'cuts' : {
                    'Mass'+self.fsrVar : (70., ">="),
                },
            },

            # Smart Cut
            'SmartCut' : {
                'logic' : 'other',
            },
        }

        return cutTemplate


    def setupCutFlow(self):
        '''
        Dictionary with order and (one-indexed) numbers of particles to cut on
        '''
        flow = OrderedDict()
        flow['Total'] = ('true', [])
        flow['Vertex'] = ('Vertex', [])
        flow['Trigger'] = ('Trigger', [])
        flow['LeptonID'] = ('GoodLeptons', [1,2,3,4])
        flow['CrossCleaning'] = ('CrossCleaning', [1,2,3,4])
        flow['SIP'] = ('SIP', [1,2,3,4])
        flow['GoodZ1'] = ('GoodZ', [1,2])
        flow['GoodZ2'] = ('GoodZ', [3,4])
        flow['Isolation'] = ('Isolation', [1,2,3,4])
        flow['Z1MassLoose'] = ('ZMassLoose', [1,2])
        flow['Z2MassLoose'] = ('ZMassLoose', [3,4])
        flow['Overlap'] = ('Overlap', [1,2,3,4])
        flow['Lepton1Pt'] = ('Lepton1Pt', [1,3])
        flow['Lepton2Pt'] = ('Lepton2Pt', [1,2,3,4])
        flow['QCDVeto'] = ('QCDVeto', [1,2,3,4])
        flow['Z1Mass'] = ('ZMassTight', [1,2])
        flow['4lMass'] = ('4lMass', [])
        flow['SmartCut'] = ('SmartCut', [1,2,3,4])
        
        return flow


    def setupOtherCuts(self):
        '''
        Define functions that don't fit the template nicely
        '''
        temp = self.getCutTemplate()
        others = {}
        others['eMVAID'] = lambda row, obj: self.eIDTight2012(temp['eMVAID'], row, obj)
        others['SmartCut'] = lambda row, *obj: self.doSmartCut(row, *obj)

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


    def doSmartCut(self, row, *obj):
        # Doesn't apply to eemm
        if obj[0][0] != obj[2][0]:
            return True

        # Find the proper alternate Z pairing. We already checked that we have 2 OS pairs
        if nObjVar(row, 'SS', *sorted([obj[0], obj[2]])): # l1 matches l4
            altObj = [obj[0], obj[3], obj[1], obj[2]]
        else: # l1 matches l3
            altObj = [obj[0], obj[2], obj[1], obj[3]]

        altZMass = [nObjVar(row, "Mass"+self.fsrVar, *sorted(altObj[:2])), nObjVar(row, "Mass"+self.fsrVar, *sorted(altObj[2:]))]
        altZCompatibility = [zMassDist(m) for m in altZMass]
        z1Compatibility = zCompatibility(row, obj[0], obj[1], self.fsrVar)

        if altZCompatibility[0] < altZCompatibility[1]:  # Za is first
            zACompatibility = altZCompatibility[0]
            zBMass = altZMass[1]
        else:
            zACompatibility = altZCompatibility[1]
            zBMass = altZMass[0]

        return not (zACompatibility < z1Compatibility and zBMass < 12)
