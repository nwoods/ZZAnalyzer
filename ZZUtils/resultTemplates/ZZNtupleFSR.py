'''

Template for saving ntuple of ZZ analyzer results (mass and whatnot)
Inherits from ZZNtupleSaver, which inherits from ZZResultSaverBase

Author: Nate Woods, U. Wisconsin

'''


from ZZNtupleSaver import ZZNtupleSaver
from ZZHelpers import * # evVar, objVar, nObjVar, deltaR, Z_MASS
from rootpy.vector import LorentzVector


class ZZNtupleFSR(ZZNtupleSaver):
    def __init__(self, fileName, channels, *args, **kwargs):
        super(ZZNtupleFSR, self).__init__(fileName, channels, *args, **kwargs)


    def setupTemplate(self):
        varsInAll = {
            'Mass' : {},
            'Pt' : {},
            'Eta' : {},
            'Phi' : {},
            'Mt' : {},
            'MassFSR' : {},
            'PtFSR' : {},
            'EtaFSR' : {},
            'PhiFSR' : {},
            'MtFSR' : {},
            'evt' : {},
            'lumi' : {},
            'run' : {},
            'doubleMuPass' : {},
            'doubleEPass' : {},
            'eMuPass' : {},
            'muEPass' : {},
            'tripleEPass' : {},
            }

        twoLepCopyVars = [
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


        vars4Mu = {
            'm1AbsEta' : {},
            'm1Charge' : {},
            'm1EffectivArea2012' : {},
            'm1Pt' : {},
            'm1Eta' : {},
            'm1Phi' : {},
            'm1IsGlobal' : {},
            'm1IsTracker' : {},
            'm1Mass' : {},
            'm1SIP3D' : {},
            'm1PVDZ' : {},
            'm1PVDXY' : {},
            'm1RelPFIsoRho' : {},
            'm1RelPFIsoDBDefault' : {},
            

        template = {
            'mmmm' : {
                'final' : {
                    'vars' : {
                        'm1_m2_Mass' : {},
                        'm1_m3_Mass' : {},
                        'm1_m4_Mass' : {},
                        'm2_m3_Mass' : {},
                        'm2_m4_Mass' : {},
                        'm3_m4_Mass' : {},
                        'm1_m2_MassFSR' : {},
                        'm1_m3_MassFSR' : {},
                        'm1_m4_MassFSR' : {},
                        'm2_m3_MassFSR' : {},
                        'm2_m4_MassFSR' : {},
                        'm3_m4_MassFSR' : {},
                        },
                    },
                },
            'eemm' : {
                'final' : {
                    'vars' : {
                        'e1_e2_Mass' : {},
                        'e1_m1_Mass' : {},
                        'e1_m2_Mass' : {},
                        'e2_m1_Mass' : {},
                        'e2_m2_Mass' : {},
                        'm1_m2_Mass' : {},
                        'e1_e2_MassFSR' : {},
                        'e1_m1_MassFSR' : {},
                        'e1_m2_MassFSR' : {},
                        'e2_m1_MassFSR' : {},
                        'e2_m2_MassFSR' : {},
                        'm1_m2_MassFSR' : {},
                        },
                    },
                },
            'eeee' : {
                'final' : {
                    'vars' : {
                        'e1_e2_Mass' : {},
                        'e1_e3_Mass' : {},
                        'e1_e4_Mass' : {},
                        'e2_e3_Mass' : {},
                        'e2_e4_Mass' : {},
                        'e3_e4_Mass' : {},
                        'e1_e2_MassFSR' : {},
                        'e1_e3_MassFSR' : {},
                        'e1_e4_MassFSR' : {},
                        'e2_e3_MassFSR' : {},
                        'e2_e4_MassFSR' : {},
                        'e3_e4_MassFSR' : {},
                        },
                    },
                },
            }
        
    
        return template

    
