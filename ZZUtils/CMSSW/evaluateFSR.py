import sys
oldargv = sys.argv[:]
sys.argv = [ '-b-' ]
from rootpy import ROOT
from rootpy.io import root_open
sys.argv = oldargv
ROOT.gROOT.SetBatch(True)

from math import pi, sqrt
from itertools import combinations
import glob

import logging
from rootpy import log; log = log["/evaluateFSR"]
# don't show most silly ROOT messages
logging.basicConfig(level=logging.WARNING)
log["/ROOT.TCanvas.Print"].setLevel(log.WARNING)
log["/ROOT.TUnixSystem.SetDisplay"].setLevel(log.ERROR)

# Do this import after turning off TUnixSystem.SetDisplay warnings
from rootpy.plotting import Hist, Hist2D, Canvas

Z_MASS = 91.1876

# load FWLite C++ libraries
ROOT.gSystem.Load("libFWCoreFWLite.so");
ROOT.gSystem.Load("libDataFormatsFWLite.so");
ROOT.AutoLibraryLoader.enable()

#cms python data types
import FWCore.ParameterSet.Config as cms

# load FWlite python libraries
from DataFormats.FWLite import Handle, Events




def deltaPhi(phi1, phi2):
    dPhi = abs(phi2 - phi1)
    while dPhi > pi:
        dPhi -= 2*pi    
    return dPhi


def deltaR(eta1, phi1, eta2, phi2):
    dPhi = deltaPhi(phi1, phi2)
    return sqrt(dPhi**2 + (eta2 - eta1)**2)


def fillGenHistos(lep, pho, found, foundAKt, foundAKt15, foundDREt, recoDREt):
    '''
    Fill histograms for gen-level FSR. If found is True, fills numerator and
    denominator histograms. Otherwise, just denominators.
    '''
    dR = deltaR(pho.eta(), pho.phi(), lep.eta(), lep.phi())
    dREt = dR / pho.et()
    dPhi = deltaPhi(pho.phi(), lep.phi())
    h['genFSRPt'].fill(pho.pt())
    h['genFSRDR'].fill(dR)
    h['genFSRDEta'].fill(abs(pho.eta() - lep.eta()))
    h['genFSRDPhi'].fill(dPhi)
    h['genFSRDREt'].fill(dREt)

    if found:
        h['foundGenFSRPt'].fill(pho.pt())
        h['foundGenFSRDR'].fill(dR)
        h['foundGenFSRDEta'].fill(abs(pho.eta() - lep.eta()))
        h['foundGenFSRDPhi'].fill(dPhi)
        h['foundGenFSRDREt'].fill(dREt)

    if foundAKt:
        h['foundGenAKtFSRPt'].fill(pho.pt())
        h['foundGenAKtFSRDR'].fill(dR)
        h['foundGenAKtFSRDEta'].fill(abs(pho.eta() - lep.eta()))
        h['foundGenAKtFSRDPhi'].fill(dPhi)
        h['foundGenAKtFSRDREt'].fill(dREt)

    if foundAKt15:
        h['foundGenAKt15FSRPt'].fill(pho.pt())
        h['foundGenAKt15FSRDR'].fill(dR)
        h['foundGenAKt15FSRDEta'].fill(abs(pho.eta() - lep.eta()))
        h['foundGenAKt15FSRDPhi'].fill(dPhi)
        h['foundGenAKt15FSRDREt'].fill(dREt)

    if foundDREt:
        h['foundGenDREtFSRPt'].fill(recoDREt, pho.pt())
        h['foundGenDREtFSRDR'].fill(recoDREt, dR)
        h['foundGenDREtFSRDEta'].fill(recoDREt, abs(pho.eta() - lep.eta()))
        h['foundGenDREtFSRDPhi'].fill(recoDREt, dPhi)
        h['foundGenDREtFSRDREt'].fill(dREt)


def fillRecoHistos(lep, matched, phoLeg, phoAKt, phoAKt15, phoDREt):
    '''
    Fill histograms for reconstructed FSR. Matched should evaluate 
    to True if the matched gen lepton had FSR. If matched is True, 
    fills numerator and denominator histograms. Otherwise, just 
    denominators.
    phoLeg is a list of legacy algorithm reco photons (empty if 
    there were none).
    phoAKt and phoAKt15 are photons found by the akT algorithms, 
    and should be None if there isn't one for the algorithm. 
    phoDREt is a photon found by the deltaR/eT algorithm (or None)
    '''
    if phoLeg:
        for pho in phoLeg:
            dR = deltaR(pho.eta(), pho.phi(), lep.eta(), lep.phi())
            dREt = dR / pho.et()
            dPhi = deltaPhi(pho.phi(), lep.phi())
            h['allFSRPt'].fill(pho.pt())
            h['allFSRDR'].fill(dR)
            h['allFSRDEta'].fill(abs(pho.eta() - lep.eta()))
            h['allFSRDPhi'].fill(dPhi)
            h['allFSRDREt'].fill(dREt)

            if matched:
                h['realFSRPt'].fill(pho.pt())
                h['realFSRDR'].fill(dR)
                h['realFSRDEta'].fill(abs(pho.eta() - lep.eta()))
                h['realFSRDPhi'].fill(dPhi)
                h['realFSRDREt'].fill(dREt)

    if phoAKt:
        dR = deltaR(phoAKt.eta(), phoAKt.phi(), lep.eta(), lep.phi())
        dREt = dR / phoAKt.et()
        dPhi = deltaPhi(phoAKt.phi(), lep.phi())
        h['allAKtFSRPt'].fill(phoAKt.pt())
        h['allAKtFSRDR'].fill(dR)
        h['allAKtFSRDEta'].fill(abs(phoAKt.eta() - lep.eta()))
        h['allAKtFSRDPhi'].fill(dPhi)
        h['allAKtFSRDREt'].fill(dREt)

        if matched:
            h['realAKtFSRPt'].fill(phoAKt.pt())
            h['realAKtFSRDR'].fill(dR)
            h['realAKtFSRDEta'].fill(abs(phoAKt.eta() - lep.eta()))
            h['realAKtFSRDPhi'].fill(dPhi)
            h['realAKtFSRDREt'].fill(dREt)

    if phoAKt15:
        dR = deltaR(phoAKt15.eta(), phoAKt15.phi(), lep.eta(), lep.phi())
        dREt = dR / phoAKt15.et()
        dPhi = deltaPhi(phoAKt15.phi(), lep.phi())
        h['allAKt15FSRPt'].fill(phoAKt15.pt())
        h['allAKt15FSRDR'].fill(dR)
        h['allAKt15FSRDEta'].fill(abs(phoAKt15.eta() - lep.eta()))
        h['allAKt15FSRDPhi'].fill(dPhi)
        h['allAKt15FSRDREt'].fill(dREt)

        if matched:
            h['realAKt15FSRPt'].fill(phoAKt15.pt())
            h['realAKt15FSRDR'].fill(dR)
            h['realAKt15FSRDEta'].fill(abs(phoAKt15.eta() - lep.eta()))
            h['realAKt15FSRDPhi'].fill(dPhi)
            h['realAKt15FSRDREt'].fill(dREt)

    if phoDREt:
        dR = deltaR(phoDREt.eta(), phoDREt.phi(), lep.eta(), lep.phi())
        dREt = dR / phoDREt.et()
        dPhi = deltaPhi(phoDREt.phi(), lep.phi())
        h['allDREtFSRPt'].fill(dREt, phoDREt.pt())
        h['allDREtFSRDR'].fill(dREt, dR)
        h['allDREtFSRDEta'].fill(dREt, abs(phoDREt.eta() - lep.eta()))
        h['allDREtFSRDPhi'].fill(dREt, dPhi)
        h['allDREtFSRDREt'].fill(dREt)

        if matched:
            h['realDREtFSRPt'].fill(dREt, phoDREt.pt())
            h['realDREtFSRDR'].fill(dREt, dR)
            h['realDREtFSRDEta'].fill(dREt, abs(phoDREt.eta() - lep.eta()))
            h['realDREtFSRDPhi'].fill(dREt, dPhi)
            h['realDREtFSRDREt'].fill(dREt)


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
    Goes to the top of the chain, then checks if that lepton is
    an ancestor of anything in packedGenPho.
    Assumes packedGenPho has already been skimmed (contains photons only).
    '''
    ID = lep.pdgId()
    out = []
    firstAncestor = firstInGenChain(lep)

    for pho in packedGenPho:
        if pho.pt() < 2:
            continue
        if isAncestor(firstAncestor, pho):
            out.append(pho)
            
    return out

            
def zPartnerIndex(i):
    '''
    Given the index of a lepton (0--3), get the index of its Z partner.
    '''
    if i%2:
        return i+1
    return i-1


def getLegacyFSR(i, collection):
    '''
    For lepton i in collection, return a list of FSR photons that are
    accepted by the legacy algorithm when it is paired with any other 
    object in collection. 
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

genFSRMatchedAKt = 0
recoFSRMatchedAKt = 0
recoFSRTotAKt = 0

genFSRMatchedAKt15 = 0
recoFSRMatchedAKt15 = 0
recoFSRTotAKt15 = 0

h = {}
h['allFSRDREt'] = Hist(40, 0., 0.04)
h['realFSRDREt'] = Hist(40, 0., 0.04)
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
h['genFSRDREt'] = Hist(40, 0., 0.04)
h['foundGenFSRDREt'] = Hist(40, 0., 0.04)

h['allAKtFSRDREt'] = Hist(40, 0., 0.04)
h['realAKtFSRDREt'] = Hist(40, 0., 0.04)
h['allAKtFSRPt'] = Hist(28, 0., 56.)
h['realAKtFSRPt'] = Hist(28, 0., 56.)
h['allAKtFSRDR'] = Hist(20, 0., 0.5)
h['realAKtFSRDR'] = Hist(20, 0., 0.5)
h['allAKtFSRDREt'] = Hist(40, 0., 0.04)
h['realAKtFSRDREt'] = Hist(40, 0., 0.04)
h['allAKtFSRDEta'] = Hist(20, 0., 0.5)
h['realAKtFSRDEta'] = Hist(20, 0., 0.5)
h['allAKtFSRDPhi'] = Hist(20, 0., 0.5)
h['realAKtFSRDPhi'] = Hist(20, 0., 0.5)
h['foundGenAKtFSRPt'] = Hist(28, 0., 56.)
h['foundGenAKtFSRDR'] = Hist(20, 0., 0.5)
h['foundGenAKtFSRDREt'] = Hist(40, 0., 0.04)
h['foundGenAKtFSRDEta'] = Hist(20, 0., 0.5)
h['foundGenAKtFSRDPhi'] = Hist(20, 0., 0.5)

h['allAKt15FSRDREt'] = Hist(40, 0., 0.04)
h['realAKt15FSRDREt'] = Hist(40, 0., 0.04)
h['allAKt15FSRPt'] = Hist(28, 0., 56.)
h['realAKt15FSRPt'] = Hist(28, 0., 56.)
h['allAKt15FSRDR'] = Hist(20, 0., 0.5)
h['realAKt15FSRDR'] = Hist(20, 0., 0.5)
h['allAKt15FSRDREt'] = Hist(40, 0., 0.04)
h['realAKt15FSRDREt'] = Hist(40, 0., 0.04)
h['allAKt15FSRDEta'] = Hist(20, 0., 0.5)
h['realAKt15FSRDEta'] = Hist(20, 0., 0.5)
h['allAKt15FSRDPhi'] = Hist(20, 0., 0.5)
h['realAKt15FSRDPhi'] = Hist(20, 0., 0.5)
h['foundGenAKt15FSRPt'] = Hist(28, 0., 56.)
h['foundGenAKt15FSRDR'] = Hist(20, 0., 0.5)
h['foundGenAKt15FSRDREt'] = Hist(40, 0., 0.04)
h['foundGenAKt15FSRDEta'] = Hist(20, 0., 0.5)
h['foundGenAKt15FSRDPhi'] = Hist(20, 0., 0.5)

h['allDREtFSRDREt'] = Hist(40, 0., 0.04)
h['realDREtFSRDREt'] = Hist(40, 0., 0.04)
h['allDREtFSRPt'] = Hist2D(40, 0., 0.04, 28, 0., 56.)
h['realDREtFSRPt'] = Hist2D(40, 0., 0.04, 28, 0., 56.)
h['allDREtFSRDR'] = Hist2D(40, 0., 0.04, 20, 0., 0.5)
h['realDREtFSRDR'] = Hist2D(40, 0., 0.04, 20, 0., 0.5)
h['allDREtFSRDEta'] = Hist2D(40, 0., 0.04, 20, 0., 0.5)
h['realDREtFSRDEta'] = Hist2D(40, 0., 0.04, 20, 0., 0.5)
h['allDREtFSRDPhi'] = Hist2D(40, 0., 0.04, 20, 0., 0.5)
h['realDREtFSRDPhi'] = Hist2D(40, 0., 0.04, 20, 0., 0.5)
h['foundGenDREtFSRPt'] = Hist2D(40, 0., 0.04, 28, 0., 56.)
h['foundGenDREtFSRDR'] = Hist2D(40, 0., 0.04, 20, 0., 0.5)
h['foundGenDREtFSRDREt'] = Hist(40, 0., 0.04)
h['foundGenDREtFSRDEta'] = Hist2D(40, 0., 0.04, 20, 0., 0.5)
h['foundGenDREtFSRDPhi'] = Hist2D(40, 0., 0.04, 20, 0., 0.5)


files  = glob.glob("/hdfs/store/user/nwoods/KEEPPAT_TEST_3/GluGluToHToZZTo4L_M-125_13TeV-powheg-pythia6/*.root")
for fi, fn in enumerate(files):
    files[fi] = "file:"+fn

events = Events(files) #"file:withPAT.root")

gen, genLabel = Handle("std::vector<reco::GenParticle>"), "prunedGenParticles"
packedGen, packedGenLabel = Handle("std::vector<pat::PackedGenParticle>"), "packedGenParticles"
fsMuons, fsMuonsLabel = Handle("std::vector<pat::Muon>"), "muonsRank"


for iev, ev in enumerate(events):
    if iev % 1000 == 0:
        print "Processing event %d"%iev

    # if iev == 2000:
    #     break
        
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
            if dR < 0.2:
                if muG not in genRecoPairs:
                    thisIsBest = True
                else:
                    thisIsBest = (dR < deltaR(genRecoPairs[muG].eta(), genRecoPairs[muG].phi(), muG.eta(), muG.phi()))

                if thisIsBest:
                    genRecoPairs[muG] = muR

    # see if anything has FSR, if so save results
    for muG, muR in genRecoPairs.iteritems():
        fsrGen = getGenFSR(muG, packedGenPho)
        fsrRec = getLegacyFSR(tightMu.index(muR), tightMu)

        if muR.hasUserCand("akFSRCand"):
            fsrAKt = muR.userCand("akFSRCand")
        else:
            fsrAKt = None
        if muR.hasUserCand("akFSRCand1p5"):
            fsrAKt15 = muR.userCand("akFSRCand1p5")
        else:
            fsrAKt15 = None
        if muR.hasUserCand("dretFSRCand"):
            fsrDREt = muR.userCand("dretFSRCand")
        else:
            fsrDREt = None

        matched = (len(fsrGen) != 0 and len(fsrRec) != 0)
        matchedAKt = (len(fsrGen) != 0 and fsrAKt is not None)
        matchedAKt15 = (len(fsrGen) != 0 and fsrAKt15 is not None)
        matchedDREt = (len(fsrGen) != 0 and fsrDREt is not None)
        if fsrDREt is not None:
            dREt = muR.userFloat("dretFSRCandDREt")
        else:
            dREt = -999.

        for gfsr in fsrGen:
            genFSRTot += 1
            fillGenHistos(muG, gfsr, matched, matchedAKt, matchedAKt15, matchedDREt, dREt)
            if matched:
                genFSRMatched += 1
            if matchedAKt:
                genFSRMatchedAKt += 1
            if matchedAKt15:
                genFSRMatchedAKt15 += 1

        recoFSRTot += len(fsrRec)
        if fsrAKt is not None:
            recoFSRTotAKt += 1
        if fsrAKt15 is not None:
            recoFSRTotAKt15 += 1
        if matched:
            recoFSRMatched += len(fsrRec)
        if matchedAKt:
            recoFSRMatchedAKt += 1
        if matchedAKt15:
            recoFSRMatchedAKt15 += 1

        fillRecoHistos(muR, matched, fsrRec, fsrAKt, fsrAKt15, fsrDREt)


        


print "Done!"
print ""
print "Legacy algorithm:"
print "    Found   %d of %d gen FSR   (efficiency: %.3f %%)"%(genFSRMatched, genFSRTot, (100. * genFSRMatched) / genFSRTot)
print "    Matched %d of %d found FSR (purity:     %.3f %%)"%(recoFSRMatched, recoFSRTot, (100. * recoFSRMatched) / recoFSRTot)
print "akT algorithm (R=0.1):"
print "    Found   %d of %d gen FSR   (efficiency: %.3f %%)"%(genFSRMatchedAKt, genFSRTot, (100. * genFSRMatchedAKt) / genFSRTot)
print "    Matched %d of %d found FSR (purity:     %.3f %%)"%(recoFSRMatchedAKt, recoFSRTotAKt, (100. * recoFSRMatchedAKt) / recoFSRTotAKt)
print "akT algorithm (R=0.15):"
print "    Found   %d of %d gen FSR   (efficiency: %.3f %%)"%(genFSRMatchedAKt15, genFSRTot, (100. * genFSRMatchedAKt15) / genFSRTot)
print "    Matched %d of %d found FSR (purity:     %.3f %%)"%(recoFSRMatchedAKt15, recoFSRTotAKt15, 
                                                              (100. * recoFSRMatchedAKt15) / recoFSRTotAKt15)
print "deltaR/eT algorithm still needs a working point, check the plots"

# make plots look halfway decent
ROOT.gStyle.SetOptStat(0)
ROOT.gStyle.SetPadTickX(1)
ROOT.gStyle.SetPadTickY(1)
ROOT.gStyle.SetPalette(1)
ROOT.gStyle.SetLegendFillColor(0)
ROOT.gROOT.ForceStyle()

colors = [
    ROOT.EColor.kGreen+1,
    ROOT.EColor.kOrange+7,
    ROOT.EColor.kMagenta,
    ]
legdims = {}
legdims['eff'] = {}
legdims['eff']['DEta'] = [0.7, 0.6, 0.9, 0.9]
legdims['eff']['DPhi'] = [0.7, 0.6, 0.9, 0.9]
legdims['eff']['DR'] = [0.7, 0.6, 0.9, 0.9]
legdims['eff']['Pt'] = [0.15, 0.6, 0.35, 0.9]
legdims['eff']['DREt'] = [0.7, 0.6, 0.9, 0.9]
legdims['pur'] = {}
legdims['pur']['DEta'] = [0.7, 0.6, 0.9, 0.9]
legdims['pur']['DPhi'] = [0.7, 0.6, 0.9, 0.9]
legdims['pur']['DR'] = [0.7, 0.6, 0.9, 0.9]
legdims['pur']['Pt'] = [0.21, 0.1, 0.41, 0.4]
legdims['pur']['DREt'] = [0.7, 0.6, 0.9, 0.9]


for var in ["Pt", "DR", "DEta", "DPhi", "DREt"]:
    prettyVar = var.replace("DREt", "\\frac{\\Delta R}{E_{T\\gamma}}").replace("D", "\\Delta ").replace("Eta", "\\eta").replace("Phi", "\\phi").replace("Pt", "p_{T\\gamma}")

    cgen = Canvas(1000, 800)
    h['genFSR%s'%var].SetLineColor(ROOT.EColor.kBlue)
    h['genFSR%s'%var].SetLineWidth(2)
    h['genFSR%s'%var].GetXaxis().SetTitle("\\text{Gen FSR }%s"%prettyVar)
    h['genFSR%s'%var].Draw("hist")
    cgen.Print("fsrPlots/genFSR%s.png"%var)
    
    ceff = Canvas(1000, 800)
    legEff = ROOT.TLegend(*legdims['eff'][var])
    legEff.SetFillColor(0)
    effFrame = h['genFSR%s'%var].empty_clone()
    effFrame.SetMaximum(1.1)
    effFrame.SetMinimum(0.)
    effFrame.GetXaxis().SetTitle(prettyVar)
    effFrame.GetYaxis().SetTitle("Efficiency")
    effFrame.Draw("E")
    eff = ROOT.TGraphAsymmErrors(h['foundGenFSR%s'%var], h['genFSR%s'%var])
    eff.SetMarkerStyle(20)
    eff.SetMarkerColor(ROOT.EColor.kBlack)
    eff.SetLineColor(ROOT.EColor.kBlack)
    eff.SetLineWidth(2)
    eff.Draw("PSAME")
    legEff.AddEntry(eff, "Legacy", "LPE")
    effAKt = ROOT.TGraphAsymmErrors(h['foundGenAKtFSR%s'%var], h['genFSR%s'%var])
    effAKt.SetMarkerStyle(21)
    effAKt.SetMarkerColor(ROOT.EColor.kRed)
    effAKt.SetLineColor(ROOT.EColor.kRed)
    effAKt.SetLineWidth(2)
    effAKt.Draw("PSAME")
    legEff.AddEntry(effAKt, "ak_{T} \\: (R=0.10)", "LPE")
    effAKt15 = ROOT.TGraphAsymmErrors(h['foundGenAKt15FSR%s'%var], h['genFSR%s'%var])
    effAKt15.SetMarkerStyle(21)
    effAKt15.SetMarkerColor(ROOT.EColor.kBlue)
    effAKt15.SetLineColor(ROOT.EColor.kBlue)
    effAKt15.SetLineWidth(2)
    effAKt15.Draw("PSAME")
    legEff.AddEntry(effAKt15, "ak_{T} \\: (R=0.15)", "LPE")
    if var != "DREt":
        effDREt = {}
        for i, cutBin in enumerate(xrange(8, 20, 4)):
            num = h['foundGenDREtFSR%s'%var].ProjectionY("es%d"%i, 1, cutBin-1)
            effDREt[cutBin] = ROOT.TGraphAsymmErrors(num, h['genFSR%s'%var])
            effDREt[cutBin].SetMarkerStyle(33)
            effDREt[cutBin].SetMarkerSize(2)
            effDREt[cutBin].SetMarkerColor(colors[i])
            effDREt[cutBin].SetLineColor(colors[i])
            effDREt[cutBin].SetLineWidth(2)
            effDREt[cutBin].Draw("PSAME")
            legEff.AddEntry(effDREt[cutBin], "\\frac{\\Delta R}{E_{T}} < %0.2f"%(cutBin/1000.), "LPE")
#     else:
#         effDREt = ROOT.TGraphAsymmErrors(h['foundGenDREtFSR%s'%var], h['genFSR%s'%var])
#         effDREt.SetMarkerStyle(33)
#         effDREt.SetMarkerColor(colors[0])
#         effDREt.SetLineColor  (colors[0])
#         effDREt.SetLineWidth(2)
#         effDREt.Draw("PSAME")
#         legEff.AddEntry(effDREt, "\\frac{\\Delta R}{E_{T\\gamma}}", "LPE")
    legEff.Draw("SAME")
    ceff.Print("fsrPlots/eff%s.png"%var)
    
    cpur = Canvas(1000, 800)
    legPur = ROOT.TLegend(*legdims['pur'][var])
    legPur.SetFillColor(0)
    purFrame = h['allFSR%s'%var].empty_clone()
    purFrame.SetMaximum(1.1)
    purFrame.SetMinimum(0.)
    purFrame.GetXaxis().SetTitle(prettyVar)
    purFrame.GetYaxis().SetTitle("Purity")
    purFrame.Draw()
    pur = ROOT.TGraphAsymmErrors(h['realFSR%s'%var], h['allFSR%s'%var])
    pur.SetMarkerStyle(20)
    pur.SetMarkerColor(ROOT.EColor.kBlack)
    pur.SetLineColor(ROOT.EColor.kBlack)
    pur.SetLineWidth(2)
    pur.Draw("PSAME")
    legPur.AddEntry(pur, "Legacy", "LPE")
    purAKt = ROOT.TGraphAsymmErrors(h['realAKtFSR%s'%var], h['allAKtFSR%s'%var])
    purAKt.SetMarkerStyle(21)
    purAKt.SetMarkerColor(ROOT.EColor.kRed)
    purAKt.SetLineColor(ROOT.EColor.kRed)
    purAKt.SetLineWidth(2)
    purAKt.Draw("PSAME")
    legPur.AddEntry(purAKt, "ak_{T} \\: (R=0.10)", "LPE")
    purAKt15 = ROOT.TGraphAsymmErrors(h['realAKt15FSR%s'%var], h['allAKt15FSR%s'%var])
    purAKt15.SetMarkerStyle(21)
    purAKt15.SetMarkerColor(ROOT.EColor.kBlue)
    purAKt15.SetLineColor(ROOT.EColor.kBlue)
    purAKt15.SetLineWidth(2)
    purAKt15.Draw("PSAME")
    legPur.AddEntry(purAKt15, "ak_{T} \\: (R=0.15)", "LPE")
    if var != "DREt":
        purDREt = {}
        for i, cutBin in enumerate(xrange(8, 20, 4)):
            num = h['realDREtFSR%s'%var].ProjectionY("ps%d"%i, 1, cutBin-1)
            denom = h['allDREtFSR%s'%var].ProjectionY("pds%d"%i, 1, cutBin-1)
            purDREt[cutBin] = ROOT.TGraphAsymmErrors(num, denom)
            purDREt[cutBin].SetMarkerStyle(33)
            purDREt[cutBin].SetMarkerSize(2)
            purDREt[cutBin].SetMarkerColor(colors[i])
            purDREt[cutBin].SetLineColor(colors[i])
            purDREt[cutBin].SetLineWidth(2)
            purDREt[cutBin].Draw("PSAME")
            legPur.AddEntry(purDREt[cutBin], "\\frac{\\Delta R}{E_{T}} < %0.2f"%(cutBin/1000.), "LPE")
#     else:
#         purDREt = ROOT.TGraphAsymmErrors(h['realDREtFSR%s'%var], h['allDREtFSR%s'%var])
#         purDREt.SetMarkerStyle(33)
#         purDREt.SetMarkerColor(colors[0])
#         purDREt.SetLineColor(colors[0])
#         purDREt.SetLineWidth(2)
#         purDREt.Draw("PSAME")
#         legPur.AddEntry(purDREt, "\\frac{\\Delta R}{E_{T}}", "LPE")
    legPur.Draw("SAME")
    cpur.Print("fsrPlots/purity%s.png"%var)


    cdreteff = Canvas(1000, 800)
    dREtEffNum = h['foundGenDREtFSRDREt'].empty_clone()
    dREtEffDenom = h['foundGenDREtFSRDREt'].empty_clone()
    dREtEffFrame = dREtEffNum.Clone()
    dREtEffFrame.GetXaxis().SetTitle("\\frac{\\Delta R}{E_{T\\gamma}} \\text{ threshold}")
    dREtEffFrame.GetXaxis().SetTitleOffset(1.1)
    dREtEffFrame.GetYaxis().SetTitle("Efficiency")
    dREtEffFrame.SetMinimum(0.)
    dREtEffFrame.SetMaximum(1.1)
    dREtEffFrame.Draw()
    nNum = 0
    for i in range(1, h['foundGenDREtFSRDREt'].GetNbinsX()+1):
        nNum += h['foundGenDREtFSRDREt'].GetBinContent(i)
        dREtEffNum.SetBinContent(i, nNum)
        dREtEffDenom.SetBinContent(i, genFSRTot)
        dREtEffNum.SetBinError(i, sqrt(nNum))
        dREtEffDenom.SetBinError(i, sqrt(genFSRTot))
    dREtEffNum.Sumw2()
    dREtEffDenom.Sumw2()
    dREtEff= ROOT.TGraphAsymmErrors(dREtEffNum, dREtEffDenom)
    dREtEff.SetMarkerStyle(33)
    dREtEff.SetMarkerSize(2)
    dREtEff.SetMarkerColor(colors[0])
    dREtEff.SetLineColor(colors[0])
    dREtEff.SetLineWidth(2)
    dREtEff.Draw("PSAME")
    cdreteff.Print("fsrPlots/dREtEff.png")


    cdretpur = Canvas(1000, 800)
    dREtPurNum = h['realDREtFSRDREt'].empty_clone()
    dREtPurDenom = h['allDREtFSRDREt'].empty_clone()
    dREtPurFrame = dREtPurNum.Clone()
    dREtPurFrame.GetXaxis().SetTitle("\\frac{\\Delta R}{E_{T\\gamma}} \\text{ threshold}")
    dREtPurFrame.GetXaxis().SetTitleOffset(1.1)
    dREtPurFrame.GetYaxis().SetTitle("Purity")
    dREtPurFrame.SetMinimum(0.)
    dREtPurFrame.SetMaximum(1.1)
    dREtPurFrame.Draw()
    nNum = 0
    nDen = 0
    for i in range(1, h['realDREtFSRDREt'].GetNbinsX()+1):
        nNum += h['realDREtFSRDREt'].GetBinContent(i)
        nDen += h['allDREtFSRDREt'].GetBinContent(i)
        dREtPurNum.SetBinContent(i, nNum)
        dREtPurDenom.SetBinContent(i, nDen)
        dREtPurNum.SetBinError(i, sqrt(nNum))
        dREtPurDenom.SetBinError(i, sqrt(nDen))
    dREtPurNum.Sumw2()
    dREtPurDenom.Sumw2()
    dREtPur= ROOT.TGraphAsymmErrors(dREtPurNum, dREtPurDenom)
    dREtPur.SetMarkerStyle(33)
    dREtPur.SetMarkerSize(2)
    dREtPur.SetMarkerColor(colors[0])
    dREtPur.SetLineColor(colors[0])
    dREtPur.SetLineWidth(2)
    dREtPur.Draw("PSAME")
    cdretpur.Print("fsrPlots/dREtPurity.png")



