import sys
oldargv = sys.argv[:]
sys.argv = [ '-b-' ]
from rootpy import ROOT
from rootpy.io import root_open
from rootpy.plotting import Hist, Canvas
sys.argv = oldargv
ROOT.gROOT.SetBatch(True)

from math import pi, sqrt
from itertools import combinations
import glob

import logging
# don't show most silly ROOT messages
logging.basicConfig(level=logging.WARNING)

Z_MASS = 91.1876

# load FWLite C++ libraries
ROOT.gSystem.Load("libFWCoreFWLite.so");
ROOT.gSystem.Load("libDataFormatsFWLite.so");
ROOT.AutoLibraryLoader.enable()

#cms python data types
import FWCore.ParameterSet.Config as cms

# load FWlite python libraries
from DataFormats.FWLite import Handle, Events


nPackedFSR = 0



def fillGenHistos(pho, lep, found):
    '''
    Fill histograms for gen-level FSR. If found is True, fills numerator and
    denominator histograms. Otherwise, just denominators.
    '''
    h['genFSRPt'].fill(pho.pt())
    h['genFSRDR'].fill(deltaR(pho.eta(), pho.phi(), lep.eta(), lep.phi()))
    h['genFSRDEta'].fill(abs(pho.eta() - lep.eta()))
    h['genFSRDPhi'].fill(deltaPhi(pho.phi(), lep.phi()))

    if found:
        h['foundGenFSRPt'].fill(pho.pt())
        h['foundGenFSRDR'].fill(deltaR(pho.eta(), pho.phi(), lep.eta(), lep.phi()))
        h['foundGenFSRDEta'].fill(abs(pho.eta() - lep.eta()))
        h['foundGenFSRDPhi'].fill(deltaPhi(pho.phi(), lep.phi()))


def fillRecoHistos(pho, lep, matched):
    '''
    Fill histograms for reconstructed FSR. If matched is True, fills numerator and
    denominator histograms. Otherwise, just denominators.
    '''
    h['allFSRPt'].fill(pho.pt())
    h['allFSRDR'].fill(deltaR(pho.eta(), pho.phi(), lep.eta(), lep.phi()))
    h['allFSRDEta'].fill(abs(pho.eta() - lep.eta()))
    h['allFSRDPhi'].fill(deltaPhi(pho.phi(), lep.phi()))

    if matched:
        h['realFSRPt'].fill(pho.pt())
        h['realFSRDR'].fill(deltaR(pho.eta(), pho.phi(), lep.eta(), lep.phi()))
        h['realFSRDEta'].fill(abs(pho.eta() - lep.eta()))
        h['realFSRDPhi'].fill(deltaPhi(pho.phi(), lep.phi()))


def deltaPhi(phi1, phi2):
    dPhi = abs(phi2 - phi1)
    while dPhi > pi:
        dPhi -= 2*pi    
    return dPhi


def deltaR(eta1, phi1, eta2, phi2):
    dPhi = deltaPhi(phi1, phi2)
    return sqrt(dPhi**2 + (eta2 - eta1)**2)


def firstInGenChain(p):
    '''
    Get the first gen particle in p's same-ID chain.
    '''
    ID = p.pdgId()
    while True:
        for iM in xrange(p.numberOfMothers()):
            mom = p.mother(iM)
            if not mom:
                continue

            if mom.pdgId() == ID:
                p = mom
                break
        else:
            return p


def getMotherSmart(lep, interesting=[22, 23, 24, 25]):
    '''
    If this gen lepton comes from an interesting particle 
    (by default defined as photon, Z, W, or Higgs), return 
    the last interesting mother. If it doesn't come from
    any of those, return None.
    '''
    ancestor = firstInGenChain(lep)
    for iM in xrange(ancestor.numberOfMothers()):
        mom = ancestor.mother(iM)
        if mom.pdgId() in interesting:
            return mom

    # no mother was interesting
    return None


def isMuonFiducial(mu):
    '''
    Is this gen particle a muon final state Z daughter within acceptance?
    '''
    if mu.status() != 1 or abs(mu.pdgId()) != 13:
        return False

    if mu.pt() < 5. or abs(mu.eta()) > 2.4:
        return False

    motherZ = getMotherSmart(mu, [23])
    return (motherZ is not None and motherZ.mass() > 12. and 
            motherZ.mass() < 120.)


def isAncestor(ancestor, particle):
    '''
    Is ancestor a direct ancestor of particle? 
    Uses only first mothers (this is all packedGenParticles have in 
    CMSSW_7_2_X).
    '''
    p = particle
    
    while bool(p.mother(0)):
        if ancestor == p:
            return True

        p = p.mother(0)

    return False


def getGenFSR(lep, packedGenPho):
    '''
    Return a list of all gen photons radiated by any gen lepton 
    in this gen lepton's same-ID chain. Requires pt(pho)>2GeV
    Goes to the top of the chain, then back down, checking for photon 
    daughters at each link in the prunedGenParticles.
    Then, loops through the packed gen particles provided and 
    includes any that also come from that chain.
    Assumes packedGenPho has already been skimmed (contains photons only).
    '''
    global nPackedFSR

    ID = lep.pdgId()
    out = []
    firstAncestor = firstInGenChain(lep)
    p = firstAncestor
    while True:
        next = None
        for iD in xrange(p.numberOfDaughters()):
            dau = p.daughter(iD)
            
            # Doesn't branch; i.e., only steps down to the 
            # first same-ID daughter
            if next is None and dau.pdgId() == ID:
                next = dau
                continue

            if dau.pdgId() == 22:
                if dau.pt() > 2.:
                    out.append(dau)

        else:
            if next is None:
                break
            p = next

    for pho in packedGenPho:
        if pho.pt() < 2:
            continue
        if isAncestor(firstAncestor, pho):
            out.append(pho)
            nPackedFSR += 1
            
    return out

            
def zPartnerIndex(i):
    '''
    Given the index of a lepton (0--3), get the index of its Z partner.
    '''
    if i%2:
        return i+1
    return i-1


def getRecoFSR(fs, i):
    '''
    Get the FSR candidate for daughter i in final state fsr, or
    None if it doesn't have one.
    '''
    cands = [fs.daughterUserCand(i, "FSRCand%d"%j) for j in xrange(fs.daughterAsMuon(i).userInt("nFSRCand"))]

    indices = sorted([i, zPartnerIndex(i)])

    fsr = fs.bestFSROfZ(indices[0], indices[1], "FSRCand")

    if fsr and fsr in cands:
        return FSR

    return None


def hasRecoFSR(fs, i):
    '''
    Is there an FSR photon matched to lepton i in final state fs?
    '''
    return getRecoFSR(fs, i) is not None


def getOrphanFSR(i, collection):
    '''
    For lepton i in collection, return a list of FSR photons that are
    accepted when it is paired with any other object in collection. 
    '''
    out = []
    lep = collection[i]

    for iFSR in xrange(lep.userInt("nFSRCand")):
        pho = lep.userCand("FSRCand%d"%iFSR)
        for j, lep2 in enumerate(collection):
            # don't pair with self
            if i == j:
                continue
    
            # lepton must have partner that makes an OSSF pair that looks like a (possibly off-shell) Z
            if lep.pdgId() != -1 * lep2.pdgId():
                continue
            if (lep.p4() + lep2.p4()).M() < 12. or (lep.p4() + lep2.p4()).M() > 120.:
                continue
    
            # photon must take Z closer to on-shell
            if abs((lep.p4() + lep2.p4()).M() - Z_MASS) < abs((lep.p4() + lep2.p4() + pho.p4()).M() - Z_MASS):
                continue
    
            # if partner has better FSR, we can ignore this FSR
            for iFSR2 in xrange(lep2.userInt("nFSRCand")):
                pho2 = lep2.userCand("FSRCand%d"%iFSR2)
                if abs((lep.p4() + lep2.p4()).M() - Z_MASS) > abs((lep.p4() + lep2.p4() + pho2.p4()).M() - Z_MASS):
                    if pho2.pt() > 4.:
                        if pho2.pt() > pho.pt():
                            break
                    elif pho.pt() < 4.:
                        if deltaR(lep.eta(), lep.phi(), pho.eta(), pho.phi()) > \
                                deltaR(lep2.eta(), lep2.phi(), pho2.eta(), pho2.phi()):
                            break
            else:
                # If we never found a better photon with the other lepton, this one is good
                out.append(pho)
                # don't need to check any other partners
                break
    
    return out
    

genFSRMatched = 0
genFSRTot = 0
recoFSRMatched = 0
recoFSRTot = 0

h = {}
h['allFSRPt'] = Hist(28, 0., 56.)
h['realFSRPt'] = Hist(28, 0., 56.)
h['allFSRDR'] = Hist(20, 0., 0.5)
h['realFSRDR'] = Hist(20, 0., 0.5)
h['allFSRDEta'] = Hist(20, 0., 0.5)
h['realFSRDEta'] = Hist(20, 0., 0.5)
h['allFSRDPhi'] = Hist(20, 0., 0.5)
h['realFSRDPhi'] = Hist(20, 0., 0.5)
h['genFSRPt'] = Hist(28, 0., 56.)
h['foundGenFSRPt'] = Hist(28, 0., 56.)
h['genFSRDR'] = Hist(20, 0., 0.5)
h['foundGenFSRDR'] = Hist(20, 0., 0.5)
h['genFSRDEta'] = Hist(20, 0., 0.5)
h['foundGenFSRDEta'] = Hist(20, 0., 0.5)
h['genFSRDPhi'] = Hist(20, 0., 0.5)
h['foundGenFSRDPhi'] = Hist(20, 0., 0.5)

files  = glob.glob("/hdfs/store/user/nwoods/KEEPPAT_TEST_1/GluGluToHToZZTo4L_M-125_13TeV-powheg-pythia6/*.root")
for fi, fn in enumerate(files):
    files[fi] = "file:"+fn

events = Events("file:packedTest.root")#files) 

fs4Mu, fs4MuLabel = Handle("edm::OwnVector<PATFinalState,edm::ClonePolicy<PATFinalState> >"), "cleanedFinalStateMuMuMuMu"
gen, genLabel = Handle("std::vector<reco::GenParticle>"), "prunedGenParticles"
packedGen, packedGenLabel = Handle("std::vector<pat::PackedGenParticle>"), "packedGenParticles"
fsMuons, fsMuonsLabel = Handle("std::vector<pat::Muon>"), "muonsRank"


for iev, ev in enumerate(events):
    if iev % 1000 == 0:
        print "Processing event %d"%iev

    ev.getByLabel(fs4MuLabel, fs4Mu)
    ev.getByLabel(genLabel, gen)
    ev.getByLabel(packedGenLabel, packedGen)
    ev.getByLabel(fsMuonsLabel, fsMuons)

    # get a list of good (tight ID+SIP) muons
    tightMu = []
    for mu in fsMuons.product():
        if mu.userFloat("HZZ4lIDPassTight"):
            tightMu.append(mu)

    # get a list of gen muons in the fiducial volume
    genMu = []
    for mu in gen.product():
        if bool(mu) and isMuonFiducial(mu):
            genMu.append(mu)

    # Get collection of photons from packedGenParticles
    packedGenPho = []
    for packed in packedGen.product():
        if packed.pdgId() == 22:
            packedGenPho.append(packed)

    # get a dictionary of matched muons of the form genRecoPairs[gen] = reco
    genRecoPairs = {}
    for muG in genMu:
        for muR in tightMu:
            dR = deltaR(muG.eta(), muG.phi(), muR.eta(), muR.phi())
            if dR < 0.1:
                if muG not in genRecoPairs:
                    thisIsBest = True
                else:
                    thisIsBest = (dR < deltaR(genRecoPairs[muG].eta(), genRecoPairs[muG].phi(), muG.eta(), muG.phi()))

                if thisIsBest:
                    genRecoPairs[muG] = muR

    # see if anything has FSR, if so save results
    for muG, muR in genRecoPairs.iteritems():
        fsrGen = getGenFSR(muG, packedGenPho)
        fsrRec = getOrphanFSR(tightMu.index(muR), tightMu)

        matched = (len(fsrGen) != 0 and len(fsrRec) != 0)

        for gfsr in fsrGen:
            genFSRTot += 1
            fillGenHistos(gfsr, muG, matched)
            if matched:
                genFSRMatched += 1

        for rfsr in fsrRec:
            recoFSRTot += 1
            fillRecoHistos(rfsr, muR, matched)
            if matched:
                recoFSRMatched += 1






        


print "Done!"
print "Found   %d of %d gen FSR   (efficiency: %.3f %%)"%(genFSRMatched, genFSRTot, (100. * genFSRMatched) / genFSRTot)
print "Matched %d of %d found FSR (purity:     %.3f %%)"%(recoFSRMatched, recoFSRTot, (100. * recoFSRMatched) / recoFSRTot)
print "%d packed gen FSR photons were found"%nPackedFSR

# make plots look halfway decent
ROOT.gStyle.SetOptStat(0)
ROOT.gStyle.SetPadTickX(1)
ROOT.gStyle.SetPadTickY(1)
ROOT.gStyle.SetPalette(1)
ROOT.gROOT.ForceStyle()

for var in ["Pt", "DR", "DEta", "DPhi"]:
    cgen = Canvas(1000, 800)
    h['genFSR%s'%var].SetLineColor(ROOT.EColor.kBlue)
    h['genFSR%s'%var].SetLineWidth(2)
    h['genFSR%s'%var].GetXaxis().SetTitle("\\text{Gen FSR }%s"%var.replace("D", "\\Delta ").replace("Eta", "\\eta").replace("Phi", "\\phi").replace("Pt", "p_{T\\gamma}"))
    h['genFSR%s'%var].Draw("hist")
    cgen.Print("fsrPlots/genFSR%s.png"%var)

    ceff = Canvas(1000, 800)
    effFrame = h['genFSR%s'%var].empty_clone()
    effFrame.SetMarkerColor(ROOT.EColor.kBlue)
    effFrame.SetMaximum(1.1)
    effFrame.SetMinimum(0.)
    effFrame.GetXaxis().SetTitle(var.replace("D", "\\Delta ").replace("Eta", "\\eta").replace("Phi", "\\phi").replace("Pt", "p_{T\\gamma}"))
    effFrame.GetYaxis().SetTitle("Efficiency")
    effFrame.Draw("E")
    eff = ROOT.TGraphAsymmErrors(h['foundGenFSR%s'%var], h['genFSR%s'%var])
    eff.SetMarkerStyle(20)
    eff.SetMarkerColor(ROOT.EColor.kBlue)
    eff.SetLineColor(ROOT.EColor.kBlue)
    eff.SetLineWidth(2)
    eff.Draw("PSAME")
    ceff.Print("fsrPlots/eff%s.png"%var)

    cpur = Canvas(1000, 800)
    purFrame = h['allFSR%s'%var].empty_clone()
    purFrame.SetMaximum(1.1)
    purFrame.SetMinimum(0.)
    purFrame.GetXaxis().SetTitle(var.replace("D", "\\Delta ").replace("Eta", "\\eta").replace("Phi", "\\phi").replace("Pt", "p_{T\\gamma}"))
    purFrame.GetYaxis().SetTitle("Purity")
    purFrame.Draw("E")
    pur = ROOT.TGraphAsymmErrors(h['realFSR%s'%var], h['allFSR%s'%var])
    pur.SetMarkerStyle(20)
    pur.SetMarkerColor(ROOT.EColor.kBlue)
    pur.SetLineColor(ROOT.EColor.kBlue)
    pur.SetLineWidth(2)
    pur.Draw("PSAME")
    cpur.Print("fsrPlots/purity%s.png"%var)




### OLD, KEPT JUST IN CASE

#         genFSR = getGenFSR(mu)
#         if not len(genFSR):
#             continue
# 
#         foundLep = False # have we found a matching reco lepton yet?
#         foundFSR = False # have we found a matching reco photon yet?
# 
#         if len(fs4Mu.product()) >= 4: # we can just check the final state reco muons
#             for fs in fs4Mu.product():
#                 for i in xrange(4):
#                     if fs.getDaughterGenParticle(i, 13, 0) == mu and bool(fs.daughterAsMuon(i).userFloat("HZZ4lIDPassTight")):
#                         foundLep = True
#                         if foundLep:
#                             foundFSR = hasRecoFSR(i)
#                             break
#                 if foundFSR:
#                     break
# 
#         else: # have to check "orphans" by hand (ugh)
#             for iReco, reco in enumerate(tightMu):
#                 if deltaR(mu.eta(), mu.phi(), reco.eta(), reco.phi()) < 0.1: # maybe do better matching later
#                     foundLep = True
#                     if len(getOrphanFSR(iReco, tightMu)):
#                         foundFSR = True
#                         break
#                     
#         # save all the things
#         if foundLep:
#             for fsr in genFSR:
#                 genFSRTot += 1
#                 if foundFSR: # for now, count as found if we found any reco FSR. May improve later
#                     genFSRFound += 1
#                 fillGenHistos(fsr, mu, foundFSR)
# 
# 
#     # Purity of reconstructed FSR
#     checked = set()
#     
#     # if we have final states, there's no need to muck around with orphans
#     if len(fs4Mu.product()):
#         for fs in fs4Mu.product():
#             if not fs:
#                 continue
#     
#             for idx in [[0,1],[2,3]]:
#                 if not (bool(fs.daughterAsMuon(idx[0]).userFloat("HZZ4lIDPassTight")) and \
#                             bool(fs.daughterAsMuon(idx[1]).userFloat("HZZ4lIDPassTight"))):
#                     continue
#     
#                 fsr = fs.bestFSROfZ(idx[0], idx[1], "FSRCand")
#                 if (not fsr) or fsr.isNull() or fsr in checked:
#                     continue
#     
#                 checked.add(fsr)
#     
#                 if deltaR(fs.daughter(idx[0]).eta(), fs.daughter(idx[0]).phi(), fsr.eta(), fsr.phi()) < \
#                         deltaR(fs.daughter(idx[1]).eta(), fs.daughter(idx[1]).phi(), fsr.eta(), fsr.phi()):
#                     mu = fs.daughter(idx[0])
#                     genMu = fs.getDaughterGenParticle(idx[0], 13, 0)
#                 else:
#                     mu = fs.daughter(idx[1])
#                     genMu = fs.getDaughterGenParticle(idx[1], 13, 0)
#     
#                 if genMu.isNonnull():
#                     recoFSRTot += 1
#                     if len(getGenFSR(genMu)) != 0:
#                         recoFSRMatched += 1
#                         matched = True
#                     else:
#                         matched = False
#     
#                     fillRecoHistos(fsr, mu, matched)
#     else:
#         # otherwise, do orphans by hand
#         for iReco, reco in enumerate(tightMu):
#             for genMu in gen.product():
#                 if not genMu or not isMuonFiducial(genMu):
#                     continue
#                 if deltaR(genMu.eta(), genMu.phi(), reco.eta(), reco.phi()) < 0.1: # maybe do better matching later
#                     genMatch = genMu
#                     break
#             else:
#                 # no gen match, ignore this muon
#                 continue
# 
#             fsr = getOrphanFSR(iReco, tightMu)
#             # only care if we have FSR
#             if not len(fsr):
#                 continue
# 
#             matched = bool(len(getGenFSR(genMu)))
# 
#             for pho in fsr:
#                 recoFSRTot += 1
#                 if matched:
#                     recoFSRMatched += 1
#                 fillRecoHistos(pho, reco, matched)
