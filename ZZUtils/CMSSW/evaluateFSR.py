import sys
oldargv = sys.argv[:]
sys.argv = [ '-b-' ]
from rootpy import ROOT
from rootpy.io import root_open
from rootpy.plotting import Hist, Hist2D, Canvas
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




def deltaPhi(phi1, phi2):
    dPhi = abs(phi2 - phi1)
    while dPhi > pi:
        dPhi -= 2*pi    
    return dPhi


def deltaR(eta1, phi1, eta2, phi2):
    dPhi = deltaPhi(phi1, phi2)
    return sqrt(dPhi**2 + (eta2 - eta1)**2)


def fillGenHistos(lep, pho, found, foundAKt, foundDREt, recoDREt):
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

    if foundDREt:
        h['foundGenDREtFSRPt'].fill(recoDREt, pho.pt())
        h['foundGenDREtFSRDR'].fill(recoDREt, dR)
        h['foundGenDREtFSRDEta'].fill(recoDREt, abs(pho.eta() - lep.eta()))
        h['foundGenDREtFSRDPhi'].fill(recoDREt, dPhi)
        h['foundGenDREtFSRDREt'].fill(dREt)


def fillRecoHistos(lep, matched, phoLeg, phoAKt, phoDREt):
    '''
    Fill histograms for reconstructed FSR. Matched should evaluate 
    to True if the matched gen lepton had FSR. If matched is True, 
    fills numerator and denominator histograms. Otherwise, just 
    denominators.
    phoLeg is a list of legacy algorithm reco photons (empty if 
    there were none).
    phoAKt is a photon found by the akT algorithm, and should be None
    if there isn't one. 
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

#     p = firstAncestor
#     while True:
#         next = None
#         for iD in xrange(p.numberOfDaughters()):
#             dau = p.daughter(iD)
#             
#             # Doesn't branch; i.e., only steps down to the 
#             # first same-ID daughter
#             if next is None and dau.pdgId() == ID:
#                 next = dau
#                 continue
# 
#             if dau.pdgId() == 22:
#                 if dau.pt() > 2.:
#                     out.append(dau)
# 
#         else:
#             if next is None:
#                 break
#             p = next

            
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

h = {}
h['allFSRDREt'] = Hist(40, 0., 0.4)
h['realFSRDREt'] = Hist(40, 0., 0.4)
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
h['genFSRDREt'] = Hist(40, 0., 0.4)
h['foundGenFSRDREt'] = Hist(40, 0., 0.4)

h['allAKtFSRDREt'] = Hist(40, 0., 0.4)
h['realAKtFSRDREt'] = Hist(40, 0., 0.4)
h['allAKtFSRPt'] = Hist(28, 0., 56.)
h['realAKtFSRPt'] = Hist(28, 0., 56.)
h['allAKtFSRDR'] = Hist(20, 0., 0.5)
h['realAKtFSRDR'] = Hist(20, 0., 0.5)
h['allAKtFSRDREt'] = Hist(40, 0., 0.4)
h['realAKtFSRDREt'] = Hist(40, 0., 0.4)
h['allAKtFSRDEta'] = Hist(20, 0., 0.5)
h['realAKtFSRDEta'] = Hist(20, 0., 0.5)
h['allAKtFSRDPhi'] = Hist(20, 0., 0.5)
h['realAKtFSRDPhi'] = Hist(20, 0., 0.5)
h['foundGenAKtFSRPt'] = Hist(28, 0., 56.)
h['foundGenAKtFSRDR'] = Hist(20, 0., 0.5)
h['foundGenAKtFSRDREt'] = Hist(40, 0., 0.4)
h['foundGenAKtFSRDEta'] = Hist(20, 0., 0.5)
h['foundGenAKtFSRDPhi'] = Hist(20, 0., 0.5)

h['allDREtFSRDREt'] = Hist(40, 0., 0.4)
h['realDREtFSRDREt'] = Hist(40, 0., 0.4)
h['allDREtFSRPt'] = Hist2D(40, 0., 0.4, 28, 0., 56.)
h['realDREtFSRPt'] = Hist2D(40, 0., 0.4, 28, 0., 56.)
h['allDREtFSRDR'] = Hist2D(40, 0., 0.4, 20, 0., 0.5)
h['realDREtFSRDR'] = Hist2D(40, 0., 0.4, 20, 0., 0.5)
h['allDREtFSRDEta'] = Hist2D(40, 0., 0.4, 20, 0., 0.5)
h['realDREtFSRDEta'] = Hist2D(40, 0., 0.4, 20, 0., 0.5)
h['allDREtFSRDPhi'] = Hist2D(40, 0., 0.4, 20, 0., 0.5)
h['realDREtFSRDPhi'] = Hist2D(40, 0., 0.4, 20, 0., 0.5)
h['foundGenDREtFSRPt'] = Hist2D(40, 0., 0.4, 28, 0., 56.)
h['foundGenDREtFSRDR'] = Hist2D(40, 0., 0.4, 20, 0., 0.5)
h['foundGenDREtFSRDREt'] = Hist(40, 0., 0.4)
h['foundGenDREtFSRDEta'] = Hist2D(40, 0., 0.4, 20, 0., 0.5)
h['foundGenDREtFSRDPhi'] = Hist2D(40, 0., 0.4, 20, 0., 0.5)


files  = glob.glob("/hdfs/store/user/nwoods/KEEPPAT_TEST_2/GluGluToHToZZTo4L_M-125_13TeV-powheg-pythia6/*.root")
for fi, fn in enumerate(files):
    files[fi] = "file:"+fn

events = Events("file:withPAT.root") #files) 

gen, genLabel = Handle("std::vector<reco::GenParticle>"), "prunedGenParticles"
packedGen, packedGenLabel = Handle("std::vector<pat::PackedGenParticle>"), "packedGenParticles"
fsMuons, fsMuonsLabel = Handle("std::vector<pat::Muon>"), "muonsRank"


for iev, ev in enumerate(events):
    if iev % 1000 == 0:
        print "Processing event %d"%iev

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
        fsrRec = getLegacyFSR(tightMu.index(muR), tightMu)

        if iev < 10:
            for n in muR.userCandNames():
                print n
            print "Done! \n"

        for n in muR.userCandNames():
            if "ak" in n or "AK" in n:
                print n

        if muR.hasUserCand("akFSRCand"):
            fsrAKt = muR.userCand("akFSRCand")
            print "found one with pt %f"%fsrAKt.pt()
        else:
            fsrAKt = None
        if muR.hasUserCand("dretFSRCand"):
            fsrDREt = muR.userCand("dretFSRCand")
        else:
            fsrDREt = None

        matched = (len(fsrGen) != 0 and len(fsrRec) != 0)
        matchedAKt = (len(fsrGen) != 0 and fsrAKt is not None)
        matchedDREt = (len(fsrGen) != 0 and fsrDREt is not None)
        if fsrDREt is not None:
            dREt = muR.userFloat("dretFSRCandDREt")
        else:
            dREt = -999.

        for gfsr in fsrGen:
            genFSRTot += 1
            fillGenHistos(muG, gfsr, matched, matchedAKt, matchedDREt, dREt)
            if matched:
                genFSRMatched += 1
            if matchedAKt:
                genFSRMatchedAKt += 1

        recoFSRTot += len(fsrRec)
        if fsrAKt is not None:
            recoFSRTotAKt += 1
        if matched:
            recoFSRMatched += len(fsrRec)
        if matchedAKt:
            recoFSRMatchedAKt += 1

        fillRecoHistos(muR, matched, fsrRec, fsrAKt, fsrDREt)


        


print "Done!"
print ""
print "Legacy algorithm:"
print "    Found   %d of %d gen FSR   (efficiency: %.3f %%)"%(genFSRMatched, genFSRTot, (100. * genFSRMatched) / genFSRTot)
print "    Matched %d of %d found FSR (purity:     %.3f %%)"%(recoFSRMatched, recoFSRTot, (100. * recoFSRMatched) / recoFSRTot)
print "akT algorithm:"
print "    Found   %d of %d gen FSR   (efficiency: %.3f %%)"%(genFSRMatchedAKt, genFSRTot, (100. * genFSRMatchedAKt) / genFSRTot)
print "    Matched %d of %d found FSR (purity:     %.3f %%)"%(recoFSRMatchedAKt, recoFSRTotAKt, (100. * recoFSRMatchedAKt) / recoFSRTotAKt)
print "    No FSR found at all :("
print "deltaR/eT algorithm still needs a working point, check the plots"


# make plots look halfway decent
ROOT.gStyle.SetOptStat(0)
ROOT.gStyle.SetPadTickX(1)
ROOT.gStyle.SetPadTickY(1)
ROOT.gStyle.SetPalette(1)
ROOT.gROOT.ForceStyle()

colors = [
    ROOT.EColor.kCyan-7,
    ROOT.EColor.kRed,
    ROOT.EColor.kOrange+7,
    ROOT.EColor.kViolet+7,
    ROOT.EColor.kMagenta,
    ]

for var in ["Pt", "DR", "DEta", "DPhi", "DREt"]:
    prettyVar = var.replace("DREt", "\\frac{\\Delta R}{E_{T\\gamma}}").replace("D", "\\Delta ").replace("Eta", "\\eta").replace("Phi", "\\phi").replace("Pt", "p_{T\\gamma}")

    cgen = Canvas(1000, 800)
    h['genFSR%s'%var].SetLineColor(ROOT.EColor.kBlue)
    h['genFSR%s'%var].SetLineWidth(2)
    h['genFSR%s'%var].GetXaxis().SetTitle("\\text{Gen FSR }%s"%prettyVar)
    h['genFSR%s'%var].Draw("hist")
    cgen.Print("fsrPlots/genFSR%s.png"%var)
    
    ceff = Canvas(1000, 800)
    legEff = ROOT.TLegend(0.4, 0.2, 0.6, 0.5)
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
    legEff.AddEntry(effAKt, "ak_{T}", "LPE")
    if var != "DREt":
        effDREt = {}
        for i, cutBin in enumerate(xrange(4, 24, 4)):
            num = h['foundGenDREtFSR%s'%var].ProjectionY("es%d"%i, 1, cutBin-1)
            effDREt[cutBin] = ROOT.TGraphAsymmErrors(num, h['genFSR%s'%var])
            effDREt[cutBin].SetMarkerStyle(33)
            effDREt[cutBin].SetMarkerColor(colors[i])
            effDREt[cutBin].SetLineColor(colors[i])
            effDREt[cutBin].SetLineWidth(2)
            effDREt[cutBin].Draw("PSAME")
            legEff.AddEntry(effDREt[cutBin], "\\frac{\\Delta R}{E_{T}} < %0.2f"%(cutBin/10.), "LPE")
    else:
        effDREt = ROOT.TGraphAsymmErrors(h['foundGenDREtFSR%s'%var], h['genFSR%s'%var])
        effDREt.SetMarkerStyle(33)
        effDREt.SetMarkerColor(ROOT.EColor.kRed)
        effDREt.SetLineColor(ROOT.EColor.kRed)
        effDREt.SetLineWidth(2)
        effDREt.Draw("PSAME")
        legEff.AddEntry(effDREt, "\\frac{\\Delta R}{E_{T}}", "LPE")
    legEff.Draw("SAME")
    ceff.Print("fsrPlots/eff%s.png"%var)
    
    cpur = Canvas(1000, 800)
    legPur = ROOT.TLegend(0.4, 0.2, 0.6, 0.5)
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
    legPur.AddEntry(purAKt, "ak_{T}", "LPE")
    if var != "DREt":
        purDREt = {}
        for i, cutBin in enumerate(xrange(4, 24, 4)):
            num = h['realDREtFSR%s'%var].ProjectionY("ps%d"%i, 1, cutBin-1)
            denom = h['allDREtFSR%s'%var].ProjectionY("pds%d"%i, 1, cutBin-1)
            purDREt[cutBin] = ROOT.TGraphAsymmErrors(num, denom)
            purDREt[cutBin].SetMarkerStyle(33)
            purDREt[cutBin].SetMarkerColor(colors[i])
            purDREt[cutBin].SetLineColor(colors[i])
            purDREt[cutBin].SetLineWidth(2)
            purDREt[cutBin].Draw("PSAME")
            legPur.AddEntry(purDREt[cutBin], "\\frac{\\Delta R}{E_{T}} < %0.2f"%(cutBin/10.), "LPE")
    else:
        purDREt = ROOT.TGraphAsymmErrors(h['foundGenDREtFSR%s'%var], h['genFSR%s'%var])
        purDREt.SetMarkerStyle(33)
        purDREt.SetMarkerColor(ROOT.EColor.kRed)
        purDREt.SetLineColor(ROOT.EColor.kRed)
        purDREt.SetLineWidth(2)
        purDREt.Draw("PSAME")
        legPur.AddEntry(purDREt, "\\frac{\\Delta R}{E_{T}}", "LPE")
    legPur.Draw("SAME")
    cpur.Print("fsrPlots/purity%s.png"%var)


#     cpur = Canvas(1000, 800)
#     purFrame = h['allFSR%s'%var].empty_clone()
#     purFrame.SetMaximum(1.1)
#     purFrame.SetMinimum(0.)
#     purFrame.GetXaxis().SetTitle(prettyVar)
#     purFrame.GetYaxis().SetTitle("Purity")
#     purFrame.Draw("E")
#     pur = ROOT.TGraphAsymmErrors(h['realFSR%s'%var], h['allFSR%s'%var])
#     pur.SetMarkerStyle(20)
#     pur.SetMarkerColor(ROOT.EColor.kBlue)
#     pur.SetLineColor(ROOT.EColor.kBlue)
#     pur.SetLineWidth(2)
#     pur.Draw("PSAME")
#     cpur.Print("fsrPlots/purity%s.png"%var)




