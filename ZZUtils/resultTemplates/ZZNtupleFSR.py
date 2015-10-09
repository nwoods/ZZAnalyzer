'''

Template for saving ntuple of ZZ analyzer results (mass and whatnot)
Inherits from ZZNtupleSaver, which inherits from ZZResultSaverBase

Author: Nate Woods, U. Wisconsin

'''


from ZZNtupleSaver import ZZNtupleSaver
from ZZHelpers import * # evVar, objVar, nObjVar, deltaR, Z_MASS
from rootpy.vector import LorentzVector
from itertools import combinations
from collections import OrderedDict


class ZZNtupleFSR(ZZNtupleSaver):
    def __init__(self, fileName, channels, inputNtuples, *args, **kwargs):
        self.copyVars = [[],[],[]] # 0, 1, and 2- lepton variables
        self.calcVars = [{},{},{}] # dictionary of function-makers for 0, 1 and 2-lepton calculated variables
        self.flavoredCopyVars = {'e':[],'m':[]}
        self.flavoredCalcVars = {'e':{},'m':{}}
        self.inputs = inputNtuples
        super(ZZNtupleFSR, self).__init__(fileName, channels, *args, **kwargs)

        
    def setupTemplate(self):

        self.copyVars[0] = [
            'Mass',
            'Pt',
            'Eta',
            'Phi',
            'Mt',
            'MassFSR',
            'PtFSR',
            'EtaFSR',
            'PhiFSR',
            'MtFSR',
            'evt',
            'lumi',
            'run',
            'singleEPass',
            'doubleMuPass',
            'doubleEPass',
            'singleESingleMuPass',
            'singleMuSingleEPass',
            'doubleESingleMuPass',
            'doubleMuSingleEPass',
            'tripleEPass',
            'tripleMuPass',
            'pvZ',
            'pvndof',
            'pvRho',
            'pvIsFake',
            'vbfNJets',
            'vbfj1pt',
            'vbfj2pt',
            'jet1Pt',
            'jet2Pt',
            'jet3Pt',
            'jet4Pt',
            'jet1Eta',
            'jet2Eta',
            'jet3Eta',
            'jet4Eta',
            'nJets',
            'D_bkg',
            'D_bkg_kin',
            'D_gg',
            'D_g4',
            'Djet_VAJHU',
            'HZZCategory',
            'GenWeight',
            'eVeto',
            'eVetoIso',
            'eVetoTight',
            'eVetoTightIso',
            'muVeto',
            'muVetoIso',
            'muVetoTight',
            'muVetoTightIso',
        ]

        self.copyVars[1] = [
            '%sAbsEta',
            '%sCharge',
            '%sEta',
            '%sGenCharge',
            '%sGenEnergy',
            '%sGenPdgId',
            '%sGenPhi',
            '%sMass',
            '%sPVDXY',
            '%sPVDZ',
            '%sPhi',
            '%sPt',
            '%sSIP3D',
            '%sPFChargedIso',
            '%sPFNeutralIso',
            '%sPFPhotonIso',
            '%sRho',
            ]

        self.flavoredCopyVars['e'] = [ 
            '%sMVANonTrigID',
            '%sRelPFIsoRho',
            '%sSCEnergy',
            '%sSCEta',
            '%sSCPhi',
            '%sMissingHits',
            '%sNearestMuonDR',
            '%sRelPFIsoRhoFSR',
        ]

        self.flavoredCopyVars['m'] = [
            '%sIsGlobal',
            '%sIsTracker',
            '%sRelPFIsoDBDefault',
            '%sIsPFMuon',
            '%sMatchedStations',
            '%sPFPUChargedIso',
            '%sBestTrackType',
            '%sRelPFIsoDBFSR',
            ]

        self.copyVars[2] = [
            '%s_%s_Mass',
            '%s_%s_MassFSR',
            '%s_%s_Pt',
            '%s_%s_PtFSR',
            '%s_%s_Eta',
            '%s_%s_EtaFSR',
            '%s_%s_Phi',
            '%s_%s_PhiFSR',
            '%s_%s_Mt',
            '%s_%s_MtFSR',
            '%s_%s_FSRPt',
            '%s_%s_FSREta',
            '%s_%s_FSRPhi',
            '%s_%s_SS',
            '%s_%s_DR',
            '%s_%s_MassFSR',
        ]

        self.calcVars[0] = {
        }

        self.calcVars[1] = {
        }

        self.calcVars[2] = {
        }

        self.flavoredCalcVars['m'] = {
        }

        self.flavoredCalcVars['e'] = {
        }

        obj4M = ['m' + str(i+1) for i in range(4)]
        obj4E = ['e' + str(i+1) for i in range(4)]
        obj2E2M = ['e' + str(i+1) for i in range(2)] + ['m' + str(i+1) for i in range(2)]


        template = {
            'mmmm' : {
                'final' : {
                    'vars' : self.templateForObjects('mmmm', obj4M),
                    },
                },
            'eemm' : {
                'final' : {
                    'vars' : self.templateForObjects('eemm', obj2E2M),
                    },
                },
            'eeee' : {
                'final' : {
                    'vars' : self.templateForObjects('eeee', obj4E),
                    },
                },
            }
    
        return template


    def templateForObjects(self, channel, objects):
        '''
        Takes a channel and list of objects, returns a variable template for it.
        For variables that must be calculated, if None is found instead of a
        lambda or other calculator function, the variable is copied instead of
        calculated (or allow the functions that generate the calculators to
        decide intelligently if a variable already exists).
        '''
        temp = {'copy' : {'ntuple' : self.inputs[channel], 'only' : []}}

        for n, varList in enumerate(self.copyVars):
            for objs in combinations(objects, n):
                for var in varList:
                    temp['copy']['only'].append(var%objs)

        for obj in objects:
            if obj[0] not in self.flavoredCopyVars:
                continue
            for var in self.flavoredCopyVars[obj[0]]:
                temp['copy']['only'].append(var%obj)

        for n, funcs in enumerate(self.calcVars):
            for var, func in funcs.iteritems():
                for objs in combinations(objects, n):
                    allObj = list(objs)+objects
                    f = func(*allObj)
                    if f is None:
                        temp['copy']['only'].append(var%objs)
                    else:
                        temp[var%objs] = {'f':f}

        for obj in objects:
            if obj[0] not in self.flavoredCalcVars:
                continue
            for var, func in self.flavoredCalcVars[obj[0]].iteritems():
                f = func(obj, objects)
                if f is None:
                    temp['copy']['only'].append(var%obj)
                else:
                    temp[var%obj] = {'f':f}

        return temp


