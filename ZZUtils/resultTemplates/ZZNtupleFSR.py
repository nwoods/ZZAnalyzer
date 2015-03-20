'''

Template for saving ntuple of ZZ analyzer results (mass and whatnot)
Inherits from ZZNtupleSaver, which inherits from ZZResultSaverBase

Author: Nate Woods, U. Wisconsin

'''


from ZZNtupleSaver import ZZNtupleSaver
from ZZHelpers import * # evVar, objVar, nObjVar, deltaR, Z_MASS
from rootpy.vector import LorentzVector
from itertools import combinations


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
            'doubleMuPass',
            'doubleEPass',
            'eMuPass',
            'muEPass',
            'tripleEPass',
            'pvZ',
            'pvndof',
            'pvRho',
            'pvIsFake',
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
            ]

        self.flavoredCopyVars['e'] = [ 
            '%sMVANonTrigID',
            '%sRelPFIsoRho',
            '%sSCEnergy',
            '%sSCEta',
            '%sSCPhi',
            '%sMissingHits',
            '%sNearestMuonDR',
            ]

        self.flavoredCopyVars['m'] = [
            '%sIsGlobal',
            '%sIsTracker',
            '%sRelPFIsoDBDefault',
            '%sIsPFMuon',
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
        ]

        self.calcVars[1] = {
            '%sPtFSR' : lambda lep: self.varFunctionWithPartner("Pt", lep),
            '%sEtaFSR' : lambda lep: self.varFunctionWithPartner("Eta", lep),
            '%sPhiFSR' : lambda lep: self.varFunctionWithPartner("Phi", lep),
        }

        self.calcVars[2] = {
        }

        self.flavoredCalcVars['m'] = {
            '%sRelPFIsoDBDefaultFSR' : self.muonRelPFIsoDBFSRFunction,
        }

        self.flavoredCalcVars['e'] = {
            '%sRelPFIsoRhoFSR' : self.eleRelPFIsoRhoFSRFunction,
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
                    temp[var%objs] = {'f':func(*objs)}

        for obj in objects:
            if obj[0] not in self.flavoredCalcVars:
                continue
            for var, func in self.flavoredCalcVars[obj[0]].iteritems():
                temp[var%obj] = {'f':func(obj)}

        return temp


    def isFSRLepton(self, row, lep, partner):
        '''
        For a given row, returns True if lep is better matched (smallest dR) to
        the FSR photon it shares with partner than partner is.
        If there is no FSR photon, always return False (obviously).
        '''
        sortedLeps = sorted([lep, partner]) # avoid asking for (e.g.) "e2_e1_Pt"
        fsrEta = nObjVar(row, "FSREta", *sortedLeps)
        if fsrEta == -999: # no photon
            return False
        fsrPhi = nObjVar(row, "FSRPhi", *sortedLeps)

        dR = sqrt((objVar(row, "Eta", lep) - fsrEta)**2 + \
                  (objVar(row, "Phi", lep) - fsrPhi)**2)
        dRPartner = sqrt((objVar(row, "Eta", partner) - fsrEta)**2 + \
                         (objVar(row, "Phi", partner) - fsrPhi)**2)

        return (dR < dRPartner)


    def getVarFSR(self, row, var, lep, partner):
        '''
        For lepton lep and variable pt, eta, or phi, returns the variable 
        for the lepton if it doesn't have matched FSR, or for the combined
        (lepton+photon) if it does.
        Partner is the other lepton in the Z candidate (for figuring out which 
        FSR cand to use).
        '''
        if not self.isFSRLepton(row, lep, partner):
            return objVar(row, var, lep)

        p4 = self.getP4WithFSR(row, lep, partner)

        # works for "Pt", "Eta", "Phi" & perhaps others
        func = getattr(p4, var) # func = p4.var (the function)
        return func()
            

    def getP4WithFSR(self, row, lep, partner):
        '''
        Returns the LorentzVector of the composite candidate made by lep and 
        the FSR photon matched with lep and partner.
        Doesn't check to make sure there is a photon or that lep is the 
        lepton matched with it if there is, so don't be dumb.
        '''
        p4 = self.getLeptonP4(row, lep)
        p4FSR = self.getFSRP4(row, lep, partner)

        return p4 + p4FSR


#     def deltaRZPairFSR(self, row, lep1, lep2):
#         '''
#         Finds FSR-included delta R between lep1 and lep2 assuming they are a 
#         Z pair (so we include 1 FSR photon at most).
#         '''
#         sortedLeps = sorted([lep1, lep2]) # avoid asking for (e.g.) "e2_e1_Pt"
#         fsrEta = nObjVar(row, "FSREta", *sortedLeps)
#         if fsrEta == -999: # no FSR
#             return nObjVar(row, "DR", *sortedLeps)
#         
#         if self.isFSRLepton(row, lep1, lep2):
#             match = lep1
#             other = lep2
#         else:
#             match = lep2
#             other = lep1
# 
#         p4_1 = self.getP4WithFSR(row, match, other)
#         p4_2 = self.getLeptonP4(row, other)
# 
#         return p4_1.DeltaR(p4_2)
#             
# 
#     def deltaRBothFSR(self, row, lep1, partner1, lep2, partner2):
#         '''
#         Returns deltaR between lep1 and lep2 with FSR corrections included
#         for both. partner1 and partner2 are the other leptons in the Z 
#         candidates for lep1 and lep2, for purposes of finding FSR photons.
#         Doesn't check to see if lep1 and lep2 are partners.
#         '''
#         if self.isFSRLepton(row, lep1, partner1):
#             p4_1 = self.getP4WithFSR(row, lep1, partner1)
#         else:
#             p4_1 = self.getLeptonP4(row, lep1)
#         if self.isFSRLepton(row, lep2, partner2):
#             p4_2 = self.getP4WithFSR(row, lep2, partner2)
#         else:
#             p4_2 = self.getLeptonP4(row, lep2)
# 
#         return p4_1.DeltaR(p4_2)
            

    def getLeptonP4(self, row, lep):
        '''
        Return LorentzVector for lep.
        '''
        p4 = LorentzVector()
        p4.SetPtEtaPhiM(objVar(row, "Pt", lep),
                        objVar(row, "Eta", lep),
                        objVar(row, "Phi", lep),
                        objVar(row, "Mass", lep)
                        )
        return p4
            

    def getFSRP4(self, row, lep, partner):
        '''
        Return LorentzVector for FSR photon associated with lep and partner
        '''
        p4FSR = LorentzVector()
        # sort so we ask for (e.g.) e1_e2_FSRPt instead of e2_e1_FSRPt
        leptons = sorted([lep, partner])
        p4FSR.SetPtEtaPhiM(nObjVar(row, "FSRPt", leptons[0], leptons[1]),
                           nObjVar(row, "FSREta", leptons[0], leptons[1]),
                           nObjVar(row, "FSRPhi", leptons[0], leptons[1]),
                           0. # photon massless
                           )
        return p4FSR


    def varFunctionWithPartner(self, var, lep):
        '''
        Return a function that gets var for lep, including the FSR photon 
        found for the FSA Z candidate containing lep (if lep is the lepton
        that matches).
        '''
        partner = self.getZPartner(lep)

        return lambda row: self.getVarFSR(row, var, lep, partner)


#     def massFunction(self, lep1, lep2):
#         '''
#         Returns a function to get the invariant mass of lep1 and lep2 with 
#         the FSR photons matched to the corresponding Zs included where 
#         appropriate. 
#         '''
#         partner1 = self.getZPartner(lep1)
#         # if they are partners, this is already in the ntuple
#         if partner1 == lep2:
#             return lambda row: nObjVar(row, "MassFSR", lep1, lep2)
# 
#         # Otherwise, we have to find the FSR cands and calculate ourselves
#         partner2 = self.getZPartner(lep2)
#         
#         return lambda row: self.dileptonMassBothFSR(row, lep1, partner1, lep2, partner2)


#     def deltaRFunction(self, lep1, lep2):
#         '''
#         Returns a function to get deltaR between lep1 and lep2 with 
#         the FSR photons matched to the corresponding Zs included where 
#         appropriate. 
#         '''
#         partner1 = self.getZPartner(lep1)
#         # if they are partners, this is already in the ntuple
#         if partner1 == lep2:
#             return lambda row: self.deltaRZPairFSR(row, lep1, lep2)
# 
#         # Otherwise, we have to find the FSR cands and calculate ourselves
#         partner2 = self.getZPartner(lep2)
#         
#         return lambda row: self.deltaRBothFSR(row, lep1, partner1, lep2, partner2)


    def muonRelPFIsoDBFSRFunction(self, mu):
        '''
        Return a function that calculates delta beta- and FSR-corrected 
        Relative PF isolation for this muon. Uses the FSR photon paired with
        its FSA Z candidate (if applicable).
        '''
        partner = self.getZPartner(mu)
        
        return lambda row: self.muonRelPFIsoDBFSR(row, mu, partner)


    def muonRelPFIsoDBFSR(self, row, mu, partner):
        '''
        Return delta-beta- and FSR-corrected relative PF isolation for this 
        muon, using the FSR candidate paired with it and partner.
        '''
        if not self.isFSRLepton(row, mu, partner):
            return objVar(row, "RelPFIsoDBDefault", mu)

        # sort leptons so we don't ask for something like m2_m1_Mass
        sortedLeps = sorted([mu, partner])

        deltaRFSR = sqrt( (objVar(row, "Eta", mu) - nObjVar(row, "FSREta", *sortedLeps)) ** 2 +
                          (objVar(row, "Phi", mu) - nObjVar(row, "FSRPhi", *sortedLeps)) ** 2 
        )
        
        if deltaRFSR > 0.4:
            return objVar(row, "RelPFIsoDBDefault", mu)

        chHadIso = objVar(row, "PFChargedIso", mu)
        neutHadIso = objVar(row, "PFNeutralIso", mu)
        phoIso = objVar(row, "PFPhotonIso", mu)
        puHadIso = 0.5 * objVar(row, "PFPUChargedIso", mu)
        ptFSR = nObjVar(row, "FSRPt", *sortedLeps)
        pt = self.getP4WithFSR(row, mu, partner).Pt()

        iso = (chHadIso + 
               max(0., neutHadIso + phoIso - ptFSR - puHadIso)
               )

        return iso/pt # rel iso


    def eleRelPFIsoRhoFSRFunction(self, ele):
        '''
        Return a function that calculates rho- and FSR-corrected relative
        PF isolation for this electron. Uses the FSR photon paired with
        its FSA Z candidate (if applicable).
        '''
        partner = self.getZPartner(ele)
        
        return lambda row: self.eleRelPFIsoRhoFSR(row, ele, partner)


    def eleRelPFIsoRhoFSR(self, row, ele, partner):
        '''
        Return rho- and FSR-corrected relative PF isolation for this 
        electron, using the FSR candidate paired with it and partner.
        '''
        if not self.isFSRLepton(row, ele, partner):
            return objVar(row, "RelPFIsoRho", ele)

        # sort leptons so we don't ask for something like e2_e1_Mass
        sortedLeps = sorted([ele, partner])

        deltaRFSR = sqrt( (objVar(row, "Eta", ele) - nObjVar(row, "FSREta", *sortedLeps)) ** 2 +
                          (objVar(row, "Phi", ele) - nObjVar(row, "FSRPhi", *sortedLeps)) ** 2 
        )
        
        if deltaRFSR > 0.4:
            return objVar(row, "RelPFIsoRho", ele)

        chHadIso = objVar(row, "PFChargedIso", ele)
        neutHadIso = objVar(row, "PFNeutralIso", ele)
        phoIso = objVar(row, "PFPhotonIso", ele)
        puHadIso= objVar(row, "Rho", ele) * objVar(row, "EffectiveAreaPHYS14", ele)
        ptFSR = nObjVar(row, "FSRPt", *sortedLeps)
        pt = self.getP4WithFSR(row, ele, partner).Pt()

        iso = (chHadIso + 
               max(0., neutHadIso + phoIso - ptFSR - puHadIso)
               )

        return iso/pt # rel iso


    def getZPartner(self, lep):
        '''
        Returns the lepton that FSA pairs with lep to make a Z candidate (e.g.
        'm3' if lep is 'm4').
        '''        
        lepNum = int(lep[-1])
        partnerNum = lepNum - (-1)**(lepNum % 2) # +1 if lep is odd, -1 if even
        partner = lep[0] + str(partnerNum)

        return partner
