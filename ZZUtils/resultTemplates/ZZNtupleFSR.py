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
            '%sCBIDMedium',
            '%sCBIDLoose',
        ]

        self.flavoredCopyVars['m'] = [
            '%sIsGlobal',
            '%sIsTracker',
            '%sRelPFIsoDBDefault',
            '%sIsPFMuon',
            '%sMatchedStations',
            '%sPFPUChargedIso',
            '%sBestTrackType',
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

        self.calcVars[0] = {
        }

        self.calcVars[1] = {
        }

        self.calcVars[2] = {
            '%s_%s_MassFSR' : self.massFunction,
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

        dR = deltaR(objVar(row, "Eta", lep), objVar(row, "Phi", lep),
                    fsrEta, fsrPhi)
        dRPartner = deltaR(objVar(row, "Eta", partner), objVar(row, "Phi", partner), 
                    fsrEta, fsrPhi)

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


    def massFunction(self, *args):
        '''
        Returns a function to get the invariant mass of lep1 and lep2 with 
        the FSR photons matched to the corresponding Zs included where 
        appropriate. 
        Arguments should go like (lep1, lep2, arrayOfAllLeps)
        '''
        lep1 = args[0]
        lep2 = args[1]
        allObj = args[2:]

        partner1 = self.getZPartner(lep1)
        # if they are partners, this is already in the ntuple
        if partner1 == lep2:
            return None

        # Otherwise, we have to find the FSR cands and calculate ourselves
        partner2 = self.getZPartner(lep2)
        
        return lambda row: self.dileptonMassBothFSR(row, lep1, partner1, lep2, partner2)


    def dileptonMassBothFSR(self, row, lep1, partner1, lep2, partner2):
        '''
        Returns invariant mass of lep1 and lep2, including FSR photons for
        either. Partner1 and partner2 are the other leptons in the two
        Z candidates, for purposes of finding FSR photons.
        Doesn't check to see if lep1 and lep2 are partners.
        Photon is only included if it brings the pair closer to nominal Z mass.
        If two photons could work, it picks one via the original FSR algorithm.
        '''
        fsrP4 = {}

        for leps in [[lep1, partner1],[lep2, partner2]]:
            if self.isFSRLepton(row, *leps):
                fsrP4[leps[0]] = self.getFSRP4(row, *leps)

        if len(fsrP4) == 0:
            return nObjVar(row, "Mass", lep1, lep2)

        lepP4 = {lep1:self.getLeptonP4(row, lep1), lep2:self.getLeptonP4(row, lep2)}

        for lep in [lep1, lep2]:
            if lep not in fsrP4:
                continue
            pho = fsrP4[lep]
            mWith = (lepP4[lep1]+lepP4[lep2]+pho).M()
            mWithout = (lepP4[lep1]+lepP4[lep2]).M()
            if zMassDist(mWith) > zMassDist(mWithout):
                fsrP4.pop(lep)

        if len(fsrP4) == 0:
            return nObjVar(row, "Mass", lep1, lep2)
        if len(fsrP4) == 1:
            for l, pho in fsrP4.iteritems():
                return (lepP4[lep1]+lepP4[lep2]+pho).M()

        if fsrP4[lep1].Pt() > 4 and fsrP4[lep1].Pt() > fsrP4[lep2]:
            return (lepP4[lep1]+lepP4[lep2]+fsrP4[lep1]).M()
        if fsrP4[lep2].Pt() > 4:
            return (lepP4[lep1]+lepP4[lep2]+fsrP4[lep2]).M()
        
        dr1 = deltaR(lepP4[lep1].Eta(), lepP4[lep1].Phi(), fsrP4[lep1].Eta(), fsrP4[lep1].Phi())
        dr2 = deltaR(lepP4[lep2].Eta(), lepP4[lep2].Phi(), fsrP4[lep2].Eta(), fsrP4[lep2].Phi())

        if dr1 < dr2:
            return (lepP4[lep1]+lepP4[lep2]+fsrP4[lep1]).M()
        return (lepP4[lep1]+lepP4[lep2]+fsrP4[lep2]).M()


    def muonRelPFIsoDBFSRFunction(self, mu, allObj):
        '''
        Return a function that calculates delta beta- and FSR-corrected 
        relative PF isolation for this muon. Uses the FSR photon paired with
        either primary Z candidate (if applicable).
        Arguments should go like (mu, arrayOfAllObjects)
        '''
        partner = self.getZPartner(mu)

        otherZLeps = []
        for ob in allObj:
            if ob != mu and ob != partner:
                otherZLeps.append(ob)
        otherZLeps = sorted(otherZLeps)
        
        return lambda row: self.muonRelPFIsoDBFSR(row, mu, partner, otherZLeps)


    def muonRelPFIsoDBFSR(self, row, mu, partner, otherZLeps):
        '''
        Return delta-beta- and FSR-corrected relative PF isolation for this 
        muon, using the FSR candidate paired with it and partner.
        '''
        # sort leptons so we don't ask for something like m2_m1_Mass (otherZLeps should already be sorted)
        thisZLeps = sorted([mu, partner])

        # find distance from mu to photons (if they exist)
        ptFSR1 = nObjVar(row, "FSRPt", *thisZLeps)
        if ptFSR1 > 0:
            p4FSR1 = self.getFSRP4(row, mu, partner)
            deltaRFSR1 = deltaR(objVar(row, "Eta", mu), objVar(row, "Phi", mu), p4FSR1.Eta(), p4FSR1.Phi())
        else:
            deltaRFSR1 = 999
        ptFSR2 = nObjVar(row, "FSRPt", *otherZLeps)
        if ptFSR2 > 0:
            p4FSR2 = self.getFSRP4(row, *otherZLeps)
            deltaRFSR2 = deltaR(objVar(row, "Eta", mu), objVar(row, "Phi", mu), p4FSR2.Eta(), p4FSR2.Phi())
        else:
            deltaRFSR2 = 999
        
        if deltaRFSR1 > 0.4 and deltaRFSR2 > 0.4:
            return objVar(row, "RelPFIsoDBDefault", mu)
            
        ptFSR = 0
        if deltaRFSR1 < 0.4 and deltaRFSR1 > 0.01:
            ptFSR += p4FSR1.Pt()
        if deltaRFSR2 < 0.4 and deltaRFSR2 > 0.01:
            ptFSR += p4FSR2.Pt()

        chHadIso = objVar(row, "PFChargedIso", mu)
        neutHadIso = objVar(row, "PFNeutralIso", mu)
        phoIso = objVar(row, "PFPhotonIso", mu)
        puHadIso = 0.5 * objVar(row, "PFPUChargedIso", mu)

        iso = (chHadIso + 
               max(0., neutHadIso + phoIso - ptFSR - puHadIso)
               )

        return iso/objVar(row, "Pt", mu) # rel iso using pt of lepton only, no FSR


    def eleRelPFIsoRhoFSRFunction(self, ele, allObj):
        '''
        Return a function that calculates rho- and FSR-corrected 
        relative PF isolation for this electron. Uses the FSR photon paired with
        either primary Z candidate (if applicable).
        '''
        partner = self.getZPartner(ele)

        otherZLeps = []
        for ob in allObj:
            if ob != ele and ob != partner:
                otherZLeps.append(ob)
        otherZLeps = sorted(otherZLeps)
        
        return lambda row: self.eleRelPFIsoRhoFSR(row, ele, partner, otherZLeps)


    def eleRelPFIsoRhoFSR(self, row, ele, partner, otherZLeps):
        '''
        Return rho- and FSR-corrected relative PF isolation for this 
        electron, using the FSR candidate paired with it and partner.
        '''
        # sort leptons so we don't ask for something like m2_m1_Mass (otherZLeps should already be sorted)
        thisZLeps = sorted([ele, partner])

        # find distance from mu to photons (if they exist)
        ptFSR1 = nObjVar(row, "FSRPt", *thisZLeps)
        if ptFSR1 > 0:
            p4FSR1 = self.getFSRP4(row, ele, partner)
            deltaRFSR1 = deltaR(objVar(row, "Eta", ele), objVar(row, "Phi", ele), p4FSR1.Eta(), p4FSR1.Phi())
        else:
            deltaRFSR1 = 999
        ptFSR2 = nObjVar(row, "FSRPt", *otherZLeps)
        if ptFSR2 > 0:
            p4FSR2 = self.getFSRP4(row, *otherZLeps)
            deltaRFSR2 = deltaR(objVar(row, "Eta", ele), objVar(row, "Phi", ele), p4FSR2.Eta(), p4FSR2.Phi())
        else:
            deltaRFSR2 = 999
        
        if deltaRFSR1 > 0.4 and deltaRFSR2 > 0.4:
            return objVar(row, "RelPFIsoRho", ele)
            
        ptFSR = 0
        if deltaRFSR1 < 0.4 and (abs(objVar(row, "SCEta", ele)) < 1.479 or deltaRFSR1 > 0.08):
            ptFSR += p4FSR1.Pt()
        if deltaRFSR2 < 0.4 and (abs(objVar(row, "SCEta", ele)) < 1.479 or deltaRFSR2 > 0.08):
            ptFSR += p4FSR2.Pt()

        chHadIso = objVar(row, "PFChargedIso", ele)
        neutHadIso = objVar(row, "PFNeutralIso", ele)
        phoIso = objVar(row, "PFPhotonIso", ele)
        puHadIso = objVar(row, "Rho", ele) * objVar(row, "EffectiveAreaPHYS14", ele)

        iso = (chHadIso + 
               max(0., neutHadIso + phoIso - ptFSR - puHadIso)
               )

        return iso/objVar(row, "Pt", ele) # rel iso using pt of lepton only, no FSR


    def getZPartner(self, lep):
        '''
        Returns the lepton that FSA pairs with lep to make a Z candidate (e.g.
        'm3' if lep is 'm4').
        '''        
        lepNum = int(lep[-1])
        partnerNum = lepNum - (-1)**(lepNum % 2) # +1 if lep is odd, -1 if even
        partner = lep[0] + str(partnerNum)

        return partner

        
