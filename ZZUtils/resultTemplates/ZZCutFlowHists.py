'''

Template for saving histograms of ZZ cut flow and control quantities
Inherits from ZZHistSaver, which inherits from ZZResultSaver

Author: Nate Woods, U. Wisconsin

'''


from ZZHistSaver import ZZHistSaver
from ZZHelpers import * # evVar, objVar, nObjVar, deltaR, Z_MASS
from rootpy.vector import LorentzVector


class ZZCutFlowHists(ZZHistSaver):
    def __init__(self, fileName, channels, *args, **kwargs):
        # At every cut, plot these variables
        self.flowList = [
            "4lMass",
            "Z1Mass",
            "Z2Mass"
            ]
        # Make control plots of listed variables at this cut
        self.controls = {
            'Z1Iso' : ["l1Iso", "l2Iso"],
            'Z2Iso' : ["l3Iso", "l4Iso"],
            'Z1Mass' : ["Z1Mass"],
            'Z2Mass' : ["Z2Mass"],
            'Lepton1Pt' : ["lepton1Pt"],
            'Lepton2Pt' : ["lepton2Pt"],
            }

        super(ZZCutFlowHists, self).__init__(fileName, channels, *args, **kwargs)

        
    def getFlowList(self):
        '''
        Get the variables to plot at every cut
        '''
        return self.flowList


    def getControls(self):
        '''
        At this cut, plot this list of variables.
        (This function gives you the dictionary specifying that)
        '''
        return self.controls


    def saveRow(self, row, channel, nested=False):
        '''
        Not needed for cut flows
        '''
        pass


    def setupTemplate(self):
        cutList = [
            'TotalRows',
            'Total',
            'Trigger',
            'Overlap',
            'GoodZ1',
            'Z1Iso',
            'Z1Mass',
            'GoodZ2',
            'Z2Iso',
            'Z2Mass',
            'Lepton1Pt',
            'Lepton2Pt',
            'LeptonPairMass',
            '4lMass',
            ]
            
        MassVarDict = {
            'f' : self.copyFunc("MassFSR"),
            'params' : [600, 0., 1200.],
            }

        Z1MassVarDictM = {
            'f' : self.copyFunc("m1_m2_MassFSR"),
            'params' : [50, 0., 150.],
            }
        Z2MassVarDictM = {
            'f' : self.copyFunc("m3_m4_MassFSR"),
            'params' : [50, 0., 150.],
            }
        Z1MassVarDictE = {
            'f' : self.copyFunc("e1_e2_MassFSR"),
            'params' : [50, 0., 150.],
            }
        Z2MassVarDictE = {
            'f' : self.copyFunc("e3_e4_MassFSR"),
            'params' : [50, 0., 150.],
            }
        Z1MassVarDictEM = {
            'f' : lambda row: self.betterZMass(row, "e1_e2_MassFSR", "m1_m2_MassFSR"),
            'params' : [50, 0., 150.],
            }
        Z2MassVarDictEM = {
            'f' : lambda row: self.worseZMass(row, "e1_e2_MassFSR", "m1_m2_MassFSR"),
            'params' : [50, 0., 150.],
            }

        massFlow = {c : MassVarDict for c in cutList}
        Z1MassFlowE = {c : Z1MassVarDictE for c in cutList}
        Z2MassFlowE = {c : Z1MassVarDictE for c in cutList}
        Z1MassFlowM = {c : Z1MassVarDictM for c in cutList}
        Z2MassFlowM = {c : Z1MassVarDictM for c in cutList}
        Z1MassFlowEM = {c : Z1MassVarDictEM for c in cutList}
        Z2MassFlowEM = {c : Z1MassVarDictEM for c in cutList}

        makeEIsoVarDict = lambda n: {'f' : self.copyFunc("e%dRelPFIsoRho"%n), 'params' : [50, 0., 10.]}
        makeMIsoVarDict = lambda n: {'f' : self.copyFunc("m%dRelPFIsoDBDefault"%n), 'params' : [50, 0., 10.]}
        makeEMIsoVarDict1 = lambda n: {'f' : lambda row: (evVar(row, "m%dRelPFIsoDBDefault"%n) if self.betterZType(row, "MassFSR")=='m' else evVar(row, "e%dRelPFIsoRho"%n)), 'params' : [50, 0., 10.]}
        makeEMIsoVarDict2 = lambda n: {'f' : lambda row: (evVar(row, "m%dRelPFIsoDBDefault"%n) if self.worseZType(row, "MassFSR")=='m' else evVar(row, "e%dRelPFIsoRho"%n)), 'params' : [50, 0., 10.]}

        lPtParams = [50, 0., 150.]

        control4E = {"l%dIso"%(n+1) : makeEIsoVarDict(n+1) for n in range(4)}
        control4E["lepton1Pt"] = {'f' : lambda row: self.highestLeptonPt(row, "e1", "e3"), 'params' : lPtParams}
        control4E["lepton2Pt"] = {'f' : lambda row: self.secondLeptonPt(row, "e1", "e2", "e3", "e4"), 'params' : lPtParams}
        control4E["Z1Mass"] = Z1MassVarDictE
        control4E["Z2Mass"] = Z2MassVarDictE
        control4M = {"l%dIso"%(n+1) : makeMIsoVarDict(n+1) for n in range(4)}
        control4M["lepton1Pt"] = {'f' : lambda row: self.highestLeptonPt(row, "m1", "m3"), 'params' : lPtParams}
        control4M["lepton2Pt"] = {'f' : lambda row: self.secondLeptonPt(row, "m1", "m2", "m3", "m4"), 'params' : lPtParams}
        control4M["Z1Mass"] = Z1MassVarDictM
        control4M["Z2Mass"] = Z2MassVarDictM
        control2E2M = {
            'l1Iso' : makeEMIsoVarDict1(1),
            'l2Iso' : makeEMIsoVarDict1(2),
            'l3Iso' : makeEMIsoVarDict2(1),
            'l4Iso' : makeEMIsoVarDict2(2),
        }
        control2E2M["lepton1Pt"] = {'f' : lambda row: self.highestLeptonPt(row, "e1", "m1"), 'params' : lPtParams}
        control2E2M["lepton2Pt"] = {'f' : lambda row: self.secondLeptonPt(row, "e1", "e2", "m1", "m2"), 'params' : lPtParams}
        control2E2M["Z1Mass"] = Z1MassVarDictEM
        control2E2M["Z2Mass"] = Z2MassVarDictEM

        template = {
            'all' : {
                '4lMass' : {
                    'vars' : massFlow,
                },
            },
            'mmmm' : {
                'Z1Mass' : {
                    'vars' : Z1MassFlowM
                    },
                'Z2Mass' : {
                    'vars' : Z2MassFlowM
                    },
                'control' : {
                    'vars' : control4M
                    },
                },
            'eeee' : {
                'Z1Mass' : {
                    'vars' : Z1MassFlowE
                    },
                'Z2Mass' : {
                    'vars' : Z2MassFlowE
                    },
                'control' : {
                    'vars' : control4E
                    },
                },
            'eemm' : {
                'Z1Mass' : {
                    'vars' : Z1MassFlowEM
                    },
                'Z2Mass' : {
                    'vars' : Z2MassFlowEM
                    },
                'control' : {
                    'vars' : control2E2M
                    },
                },
            }
        
        return template


    def highestLeptonPt(self, row, *objects):
        '''
        Return pt of object in objects with the highest pt
        '''
        return max([objVar(row, "Pt", obj) for obj in objects])


    def secondLeptonPt(self, row, *objects):
        '''
        Return pt of second highest pt object in objects
        '''
        return sorted([objVar(row,"Pt",obj) for obj in objects])[-2]
    

    


    def betterZType(self, row, massVar):
        '''
        returns 'e' if e1_e2_massVar is the mass of Z1, 'm' if m1_m2_massVar is
        '''
        mZe = objVar(row, massVar, "e1_e2_")
        mZm = objVar(row, massVar, "m1_m2_")
        dMe = abs(mZe - Z_MASS)
        dMm = abs(mZm - Z_MASS)

        if dMe < dMm:
            return "e"
        return "m"


    def worseZType(self, row, massVar):
        '''
        returns 'e' if e1_e2_massVar is the mass of Z1, 'm' if m1_m2_massVar is
        '''
        mZe = objVar(row, massVar, "e1_e2_")
        mZm = objVar(row, massVar, "m1_m2_")
        dMe = abs(mZe - Z_MASS)
        dMm = abs(mZm - Z_MASS)

        if dMe > dMm:
            return "e"
        return "m"


    def betterZMass(self, row, var1, var2):
        '''
        Given two variable names that represent masses, returns the value of
        the one closer to the nominal Z mass.
        '''
        mZ1 = evVar(row, var1)
        mZ2 = evVar(row, var2)
        dM1 = abs(mZ1 - Z_MASS)
        dM2 = abs(mZ2 - Z_MASS)

        if dM1 < dM2:
            return mZ1
        return mZ2


    def worseZMass(self, row, var1, var2):
        '''
        Given two variable names that represent masses, returns the value of
        the one closer to the nominal Z mass.
        '''
        mZ1 = evVar(row, var1)
        mZ2 = evVar(row, var2)
        dM1 = abs(mZ1 - Z_MASS)
        dM2 = abs(mZ2 - Z_MASS)

        if dM1 > dM2:
            return mZ1
        return mZ2


#     def lepHasFSR(self, row, lep):
#         '''
#         Is this lepton the one with FSR?
#         '''
#         if int(lep[-1]) % 0:
#             lep2 = lep
#             lep1 = "%s%d"%(lep[0],int(lep[-1])-1)
#         else:
#             lep1 = lep
#             lep2 = "%s%d"%(lep[0],int(lep[-1])+1)
# 
#         fsrEta = nObjVar(row, "FSREta", lep1, lep2)
#         if fsrEta < -100: # default no-FSR value is -999
#             return False
#         fsrPhi = nObjVar(row, "FSRPhi", lep1, lep2)
# 
#         eta = objVar(row, "Eta", lep)
#         phi = objVar(row, "Phi", lep)
# 
#         return deltaR(eta, phi, fsrEta, fsrPhi) < 0.5
# 

