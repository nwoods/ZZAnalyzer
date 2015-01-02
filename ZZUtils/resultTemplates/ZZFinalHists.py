'''

Template for saving histograms of ZZ analyzer results (mass and whatnot)
Inherits from ZZHistSaver, which inherits from ZZResultSaver

Author: Nate Woods, U. Wisconsin

'''


from ZZHistSaver import ZZHistSaver
from ZZHelpers import * # evVar, objVar, nObjVar, deltaR, Z_MASS
from rootpy.vector import LorentzVector


class ZZFinalHists(ZZHistSaver):
    def __init__(self, fileName, channels, *args, **kwargs):
        super(ZZFinalHists, self).__init__(fileName, channels, *args, **kwargs)


    def setupTemplate(self):
        template = {
            'all' : {
                'vars' : {
                    '4lMass' : {
                        'f' : self.copyFunc("Mass"),
                        'params' : [48, 0., 1200], 
                        },
                    '4lPt' : {
                        'f' : self.copyFunc("Pt"),
                        'params' : [50, 0., 400.],
                        },
                    '4lEta' : {
                        'f' : self.copyFunc("Eta"),
                        'params' : [20, -5., 5.],
                        },
                    '4lPhi' : {
                        'f' : self.copyFunc("Phi"),
                        'params' : [63, -3.15, 3.15],
                        },
                    '4lMt' : {
                        'f' : self.copyFunc("Mt"),
                        'params' : [48, 0., 1200.],
                        },
                    '4lMassFSR' : {
                        'f' : self.copyFunc("MassFSR"),
                        'params' : [48, 0., 1200.],
                        },
                    '4lPtFSR' : {
                        'f' : self.copyFunc("PtFSR"),
                        'params' : [50, 0., 400.],
                        },
                    '4lEtaFSR' : {
                        'f' : self.copyFunc("EtaFSR"),
                        'params' : [20, -5., 5.],
                        },
                    '4lPhiFSR' : {
                        'f' : self.copyFunc("PhiFSR"),
                        'params' : [63, -3.15, 3.15],
                        },
                    '4lMtFSR' : {
                        'f' : self.copyFunc("MtFSR"),
                        'params' : [48, 0., 1200.],
                        },
                    },
                },
            'mmmm' : {
                'vars' : {
                    'Z1Mass' : {
                        'f' : self.copyFunc("m1_m2_Mass"),
                        'params' : [65, 0., 130.], 
                        },
                    'Z2Mass' : {
                        'f' : self.copyFunc("m3_m4_Mass"),
                        'params' : [65, 0., 130.],
                        },
                    'Z1MassFSR' : {
                        'f' : self.copyFunc("m1_m2_MassFSR"),
                        'params' : [65, 0., 130.],
                        },
                    'Z2MassFSR' : {
                        'f' : self.copyFunc("m3_m4_MassFSR"),
                        'params' : [65, 0., 130.],
                        },
                    'm1Pt' : {
                        'params' : [60, 0., 120.],
                        },
                    'm1Eta' : {
                        'params' : [20, -2.5, 2.5],
                        },
                    'm1Phi' : {
                        'params' : [63, -3.15, 3.15],
                        },
                    'm2Pt' : {
                        'params' : [60, 0., 120.],
                        },
                    'm2Eta' : {
                        'params' : [20, -2.5, 2.5],
                        },
                    'm2Phi' : {
                        'params' : [63, -3.15, 3.15],
                        },
                    'm3Pt' : {
                        'params' : [60, 0., 120.],
                        },
                    'm3Eta' : {
                        'params' : [20, -2.5, 2.5],
                        },
                    'm3Phi' : {
                        'params' : [63, -3.15, 3.15],
                        },
                    'm4Pt' : {
                        'params' : [60, 0., 120.],
                        },
                    'm4Eta' : {
                        'params' : [20, -2.5, 2.5],
                        },
                    'm4Phi' : {
                        'params' : [63, -3.15, 3.15],
                        },
                    },
                },
            'eemm' : {
                'vars' : {
                    'Z1Mass' : {
                        'f' : lambda row: self.betterZMass(row, "m1_m2_Mass", "e1_e2_Mass"),
                        'params' : [65, 0., 130.], 
                        },
                    'Z2Mass' : {
                        'f' : lambda row: self.worseZMass(row, "m1_m2_Mass", "e1_e2_Mass"),
                        'params' : [65, 0., 130.],
                        },
                    'Z1MassFSR' : {
                        'f' : lambda row: self.betterZMass(row, "m1_m2_MassFSR", "e1_e2_MassFSR"),
                        'params' : [65, 0., 130.],
                        },
                    'Z2MassFSR' : {
                        'f' : lambda row: self.worseZMass(row, "m1_m2_MassFSR", "e1_e2_MassFSR"),
                        'params' : [65, 0., 130.],
                        },
                    'm1Pt' : {
                        'params' : [60, 0., 120.],
                        },
                    'm1Eta' : {
                        'params' : [20, -2.5, 2.5],
                        },
                    'm1Phi' : {
                        'params' : [63, -3.15, 3.15],
                        },
                    'm2Pt' : {
                        'params' : [60, 0., 120.],
                        },
                    'm2Eta' : {
                        'params' : [20, -2.5, 2.5],
                        },
                    'm2Phi' : {
                        'params' : [63, -3.15, 3.15],
                        },
                    'e1Pt' : {
                        'params' : [60, 0., 120.],
                        },
                    'e1Eta' : {
                        'params' : [20, -2.5, 2.5],
                        },
                    'e1Phi' : {
                        'params' : [63, -3.15, 3.15],
                        },
                    'e2Pt' : {
                        'params' : [60, 0., 120.],
                        },
                    'e2Eta' : {
                        'params' : [20, -2.5, 2.5],
                        },
                    'e2Phi' : {
                        'params' : [63, -3.15, 3.15],
                        },
                    },
                },
            'eeee' : {
                'vars' : {
                    'Z1Mass' : {
                        'f' : self.copyFunc("e1_e2_Mass"),
                        'params' : [65, 0., 130.], 
                        },
                    'Z2Mass' : {
                        'f' : self.copyFunc("e3_e4_Mass"),
                        'params' : [65, 0., 130.],
                        },
                    'Z1MassFSR' : {
                        'f' : self.copyFunc("e1_e2_MassFSR"),
                        'params' : [65, 0., 130.],
                        },
                    'Z2MassFSR' : {
                        'f' : self.copyFunc("e3_e4_MassFSR"),
                        'params' : [65, 0., 130.],
                        },
                    'e1Pt' : {
                        'params' : [60, 0., 120.],
                        },
                    'e1Eta' : {
                        'params' : [20, -2.5, 2.5],
                        },
                    'e1Phi' : {
                        'params' : [63, -3.15, 3.15],
                        },
                    'e2Pt' : {
                        'params' : [60, 0., 120.],
                        },
                    'e2Eta' : {
                        'params' : [20, -2.5, 2.5],
                        },
                    'e2Phi' : {
                        'params' : [63, -3.15, 3.15],
                        },
                    'e3Pt' : {
                        'params' : [60, 0., 120.],
                        },
                    'e3Eta' : {
                        'params' : [20, -2.5, 2.5],
                        },
                    'e3Phi' : {
                        'params' : [63, -3.15, 3.15],
                        },
                    'e4Pt' : {
                        'params' : [60, 0., 120.],
                        },
                    'e4Eta' : {
                        'params' : [20, -2.5, 2.5],
                        },
                    'e4Phi' : {
                        'params' : [63, -3.15, 3.15],
                        },
                    },
                },
            }
        
    
        return template

    
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

