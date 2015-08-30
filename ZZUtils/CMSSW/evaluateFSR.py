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
from rootpy import log as rlog; rlog = rlog["/evaluateFSR"]
# don't show most silly ROOT messages
logging.basicConfig(level=logging.WARNING)
rlog["/ROOT.TCanvas.Print"].setLevel(rlog.WARNING)
rlog["/ROOT.TUnixSystem.SetDisplay"].setLevel(rlog.ERROR)

# Do this import after turning off TUnixSystem.SetDisplay warnings
from rootpy.plotting import Hist, Hist2D, Canvas, Graph, Legend
from rootpy.plotting.utils import draw

from ZZPlotStyle import ZZPlotStyle

Z_MASS = 91.1876

# load FWLite C++ libraries
ROOT.gSystem.Load("libFWCoreFWLite.so");
ROOT.gSystem.Load("libDataFormatsFWLite.so");
ROOT.AutoLibraryLoader.enable()

#cms python data types
import FWCore.ParameterSet.Config as cms

# load FWlite python libraries
from DataFormats.FWLite import Handle, Events

isolated = True


def deltaPhi(phi1, phi2):
    dPhi = abs(phi2 - phi1)
    while dPhi > pi:
        dPhi -= 2*pi    
    return dPhi


def deltaR(eta1, phi1, eta2, phi2):
    dPhi = deltaPhi(phi1, phi2)
    return sqrt(dPhi**2 + (eta2 - eta1)**2)


def fillGenHistos(lep, pho, wasFound, dREt, improvesZ):
    '''
    Fill histograms for gen-level FSR. If found is True, fills numerator and
    denominator histograms. Otherwise, just denominators.
    '''
    dR = deltaR(pho.eta(), pho.phi(), lep.eta(), lep.phi())
    dPhi = deltaPhi(pho.phi(), lep.phi())
    h['genFSRPt'].fill(pho.pt())
    h['genFSRDR'].fill(dR)
    h['genFSRDEta'].fill(abs(pho.eta() - lep.eta()))
    h['genFSRDPhi'].fill(dPhi)

    for fsrType, found in wasFound.iteritems():
        for dM in [False, True]:
            if dM:
                found = (found and improvesZ[fsrType])
                maybeDM = "DM"
            else:
                maybeDM = ""

            if found:
                if "DREt" == fsrType[:4]:
                    h['foundGen%s%sFSRPt'%(fsrType, maybeDM)].fill(dREt[fsrType], pho.pt())
                    h['foundGen%s%sFSRDR'%(fsrType, maybeDM)].fill(dREt[fsrType], dR)
                    h['foundGen%s%sFSRDEta'%(fsrType, maybeDM)].fill(dREt[fsrType], abs(pho.eta() - lep.eta()))
                    h['foundGen%s%sFSRDPhi'%(fsrType, maybeDM)].fill(dREt[fsrType], dPhi)
                    h['foundGen%s%sFSRDREt'%(fsrType, maybeDM)].fill(dREt[fsrType])
                else:
                    h['foundGen%s%sFSRPt'%(fsrType, maybeDM)].fill(pho.pt())
                    h['foundGen%s%sFSRDR'%(fsrType, maybeDM)].fill(dR)
                    h['foundGen%s%sFSRDEta'%(fsrType, maybeDM)].fill(abs(pho.eta() - lep.eta()))
                    h['foundGen%s%sFSRDPhi'%(fsrType, maybeDM)].fill(dPhi)

emptyStringList = ['']
dmStringList = ['','DM']
def fillRecoHistos(lep, matched, photons, dREt, improvesZ):
    '''
    Fill histograms for reconstructed FSR. Matched should evaluate 
    to True if the matched gen lepton had FSR. If matched is True, 
    fills numerator and denominator histograms. Otherwise, just 
    denominators.
    phoLeg is a list of legacy algorithm reco photons (empty if 
    there were none).
    phoEt4DR03 and phoEt4DR01 are photons found by the square cut algorithms, 
    and should be None if there isn't one for the algorithm. 
    phoDREt is a photon found by the deltaR/eT algorithm (or None)
    '''
    for fsrType, pho in photons.iteritems():
        if pho:
            if improvesZ[fsrType]:
                dmList = dmStringList
            else:
                dmList = emptyStringList
            for maybeDM in dmList:
                if 'DREt' in fsrType:
                    dR = deltaR(pho.eta(), pho.phi(), lep.eta(), lep.phi())
                    dPhi = deltaPhi(pho.phi(), lep.phi())
                    h['all%s%sFSRPt'%(fsrType, maybeDM)].fill(dREt[fsrType], pho.pt())
                    h['all%s%sFSRDR'%(fsrType, maybeDM)].fill(dREt[fsrType], dR)
                    h['all%s%sFSRDEta'%(fsrType, maybeDM)].fill(dREt[fsrType], abs(pho.eta() - lep.eta()))
                    h['all%s%sFSRDPhi'%(fsrType, maybeDM)].fill(dREt[fsrType], dPhi)
                    h['all%s%sFSRDREt'%(fsrType, maybeDM)].fill(dREt[fsrType])
                    
                    if matched:
                        h['real%s%sFSRPt'%(fsrType, maybeDM)].fill(dREt[fsrType], pho.pt())
                        h['real%s%sFSRDR'%(fsrType, maybeDM)].fill(dREt[fsrType], dR)
                        h['real%s%sFSRDEta'%(fsrType, maybeDM)].fill(dREt[fsrType], abs(pho.eta() - lep.eta()))
                        h['real%s%sFSRDPhi'%(fsrType, maybeDM)].fill(dREt[fsrType], dPhi)
                        h['real%s%sFSRDREt'%(fsrType, maybeDM)].fill(dREt[fsrType])
        
                else:
                    dR = deltaR(pho.eta(), pho.phi(), lep.eta(), lep.phi())
                    dPhi = deltaPhi(pho.phi(), lep.phi())
                    h['all%s%sFSRPt'%(fsrType, maybeDM)].fill(pho.pt())
                    h['all%s%sFSRDR'%(fsrType, maybeDM)].fill(dR)
                    h['all%s%sFSRDEta'%(fsrType, maybeDM)].fill(abs(pho.eta() - lep.eta()))
                    h['all%s%sFSRDPhi'%(fsrType, maybeDM)].fill(dPhi)
        
                    if matched:
                        h['real%s%sFSRPt'%(fsrType, maybeDM)].fill(pho.pt())
                        h['real%s%sFSRDR'%(fsrType, maybeDM)].fill(dR)
                        h['real%s%sFSRDEta'%(fsrType, maybeDM)].fill(abs(pho.eta() - lep.eta()))
                        h['real%s%sFSRDPhi'%(fsrType, maybeDM)].fill(dPhi)


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
        if pho.pt() < 4:
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


def passZMassCut(m):
    return (m > 12. and m < 120.)


def muonsMakeZ(m1, m2):
    if m1.pdgId() != -1 * m2.pdgId():
        return False
    return passZMassCut((m1.p4()+m2.p4()).M())


def photonImprovesZ(lep1, lep2, pho):
    '''
    Returns if the invariant mass of lep1, lep2 and pho is closer to nominal Z
    mass than lep1 and lep2 alone.
    '''
    return abs((lep1.p4() + lep2.p4()).M() - Z_MASS) > abs((lep1.p4() + lep2.p4() + pho.p4()).M() - Z_MASS)


def getLegacyFSR(i, collection, label):
    '''
    For lepton i in collection, return a list of FSR photons that are
    accepted by the legacy algorithm when it is paired with any other 
    object in collection. 
    '''
    out = []
    lep = collection[i]

    for iFSR in xrange(lep.userInt("n%s"%label)):
        pho = lep.userCand("%s%d"%(label, iFSR))
        for j, lep2 in enumerate(collection):
            # don't pair with self
            if i == j:
                continue
    
            # lepton must have partner that makes an OSSF pair that looks like a (possibly off-shell) Z
            if lep.pdgId() != -1 * lep2.pdgId():
                continue
            mNoFSR = (lep.p4() + lep2.p4()).M()
            if not passZMassCut(mNoFSR):
                continue
    
            # photon must take Z closer to on-shell
            if not photonImprovesZ(lep, lep2, pho):
                continue
    
            # only use photons for m_(llgamma) < 100
            if (lep.p4() + lep2.p4() + pho.p4()).M() > 100.:
                continue
    
            # if partner has better FSR, we can ignore this FSR
            for iFSR2 in xrange(lep2.userInt("n%s"%label)):
                pho2 = lep2.userCand("%s%d"%(label, iFSR2))
                if photonImprovesZ(lep, lep2, pho2):
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


style = ZZPlotStyle()

fsrLabels = {}
fsrLabels["Leg"] = 'FSRCand'
fsrLabels["Et4DR03"] = 'et4DR03FSRCand'
fsrLabels["Et4DR01"] = 'et4DR01FSRCand'
fsrLabels["DREt"] = 'dretFSRCand'
fsrLabels["DREt15"] = 'dret15FSRCand'
fsrLabels["DREt2"] = 'dret2FSRCand'
fsrLabels["Et4DR03Iso"] = 'et4DR03IsoFSRCand'
fsrLabels["Et4DR01Iso"] = 'et4DR01IsoFSRCand'
fsrLabels["DREtIso"] = 'dretIsoFSRCand'
fsrLabels["DREt15Iso"] = 'dret15IsoFSRCand'
fsrLabels["DREt2Iso"] = 'dret2IsoFSRCand'

genFSRMatched = {"%s%s"%(fsrType,maybeDM) : 0 for fsrType in fsrLabels for maybeDM in ['','DM']}
genFSRTot = 0
recoFSRMatched = {"%s%s"%(fsrType,maybeDM) : 0 for fsrType in fsrLabels for maybeDM in ['','DM']}
recoFSRTot = {"%s%s"%(fsrType,maybeDM) : 0 for fsrType in fsrLabels for maybeDM in ['','DM']}

ptBins = [4.*i for i in range(5)]+[20.+8.*i for i in range(3)]+[60.]
dRBins = (10, 0., 0.5)

dREtBins = {}
dREtBins['DREt'] = [100, 0., 0.04]
dREtBins['DREt15'] = [100, 0., 0.02]
dREtBins['DREt2'] = [100, 0., 0.005]
dREtBins['DREtIso'] = [100, 0., 0.04]
dREtBins['DREt15Iso'] = [100, 0., 0.04]
dREtBins['DREt2Iso'] = [100, 0., 0.02]

h = {}

h['genFSRPt'] = Hist(ptBins)
h['genFSRDR'] = Hist(*dRBins)
h['genFSRDEta'] = Hist(*dRBins)
h['genFSRDPhi'] = Hist(*dRBins)

for fsrType, label in fsrLabels.iteritems():
    for maybeDM in ['', 'DM']:
        if fsrType == "Leg" and maybeDM != '': # legacy algorithm always requires mass improvement
            continue

        if 'DREt' in fsrType:
            h['all%s%sFSRDREt'%(fsrType, maybeDM)] = Hist(*dREtBins[fsrType])
            h['real%s%sFSRDREt'%(fsrType, maybeDM)] = Hist(*dREtBins[fsrType])
            h['all%s%sFSRPt'%(fsrType, maybeDM)] = Hist2D(dREtBins[fsrType][0], dREtBins[fsrType][1], dREtBins[fsrType][2], ptBins)
            h['real%s%sFSRPt'%(fsrType, maybeDM)] = Hist2D(dREtBins[fsrType][0], dREtBins[fsrType][1], dREtBins[fsrType][2], ptBins)
            h['all%s%sFSRDR'%(fsrType, maybeDM)] = Hist2D(dREtBins[fsrType][0], dREtBins[fsrType][1], dREtBins[fsrType][2], *dRBins)
            h['real%s%sFSRDR'%(fsrType, maybeDM)] = Hist2D(dREtBins[fsrType][0], dREtBins[fsrType][1], dREtBins[fsrType][2], *dRBins)
            h['all%s%sFSRDEta'%(fsrType, maybeDM)] = Hist2D(dREtBins[fsrType][0], dREtBins[fsrType][1], dREtBins[fsrType][2], *dRBins)
            h['real%s%sFSRDEta'%(fsrType, maybeDM)] = Hist2D(dREtBins[fsrType][0], dREtBins[fsrType][1], dREtBins[fsrType][2], *dRBins)
            h['all%s%sFSRDPhi'%(fsrType, maybeDM)] = Hist2D(dREtBins[fsrType][0], dREtBins[fsrType][1], dREtBins[fsrType][2], *dRBins)
            h['real%s%sFSRDPhi'%(fsrType, maybeDM)] = Hist2D(dREtBins[fsrType][0], dREtBins[fsrType][1], dREtBins[fsrType][2], *dRBins)
            h['foundGen%s%sFSRPt'%(fsrType, maybeDM)] = Hist2D(dREtBins[fsrType][0], dREtBins[fsrType][1], dREtBins[fsrType][2], ptBins)
            h['foundGen%s%sFSRDR'%(fsrType, maybeDM)] = Hist2D(dREtBins[fsrType][0], dREtBins[fsrType][1], dREtBins[fsrType][2], *dRBins)
            h['foundGen%s%sFSRDREt'%(fsrType, maybeDM)] = Hist(*dREtBins[fsrType])
            h['foundGen%s%sFSRDEta'%(fsrType, maybeDM)] = Hist2D(dREtBins[fsrType][0], dREtBins[fsrType][1], dREtBins[fsrType][2], *dRBins)
            h['foundGen%s%sFSRDPhi'%(fsrType, maybeDM)] = Hist2D(dREtBins[fsrType][0], dREtBins[fsrType][1], dREtBins[fsrType][2], *dRBins)
        else:
            h['all%s%sFSRPt'%(fsrType, maybeDM)] = Hist(ptBins)
            h['real%s%sFSRPt'%(fsrType, maybeDM)] = Hist(ptBins)
            h['all%s%sFSRDR'%(fsrType, maybeDM)] = Hist(*dRBins)
            h['real%s%sFSRDR'%(fsrType, maybeDM)] = Hist(*dRBins)
            h['all%s%sFSRDEta'%(fsrType, maybeDM)] = Hist(*dRBins)
            h['real%s%sFSRDEta'%(fsrType, maybeDM)] = Hist(*dRBins)
            h['all%s%sFSRDPhi'%(fsrType, maybeDM)] = Hist(*dRBins)
            h['real%s%sFSRDPhi'%(fsrType, maybeDM)] = Hist(*dRBins)
            h['foundGen%s%sFSRPt'%(fsrType, maybeDM)] = Hist(ptBins)
            h['foundGen%s%sFSRDR'%(fsrType, maybeDM)] = Hist(*dRBins)
            h['foundGen%s%sFSRDEta'%(fsrType, maybeDM)] = Hist(*dRBins)
            h['foundGen%s%sFSRDPhi'%(fsrType, maybeDM)] = Hist(*dRBins)
            


files  = glob.glob("/data/nawoods/DRET_ZMASS_KEEPPAT_1/GluGluHToZZTo4L_M125_13TeV_powheg_JHUgen_pythia8/submit/make_ntuples_cfg-*/*.root")
#"/hdfs/store/user/nwoods/FSR_HOMEWORK_KEEPPAT_2/GluGluToHToZZTo4L_M-125_13TeV-powheg-pythia6/*.root")
#"/hdfs/store/user/nwoods/KEEPPAT_TEST_3/GluGluToHToZZTo4L_M-125_13TeV-powheg-pythia6/*.root")
for fi, fn in enumerate(files):
    files[fi] = "file:"+fn

events = Events(files) #"file:withPAT.root")

gen, genLabel = Handle("std::vector<reco::GenParticle>"), "prunedGenParticles"
packedGen, packedGenLabel = Handle("std::vector<pat::PackedGenParticle>"), "packedGenParticles"
fsMuons, fsMuonsLabel = Handle("std::vector<pat::Muon>"), "muonsRank"


for iev, ev in enumerate(events):
    if iev % 1000 == 0:
        print "Processing event %d"%iev

    # if iev == 1000:
    #     break
        
    ev.getByLabel(genLabel, gen)
    ev.getByLabel(packedGenLabel, packedGen)
    ev.getByLabel(fsMuonsLabel, fsMuons)

    # get a list of good (tight ID+SIP) muons
    singleTightMu = [m for m in fsMuons.product() if m.userFloat("HZZ4lIDPassTight")]
    tightMu = [m for m in singleTightMu if any(muonsMakeZ(m,m2) for m2 in singleTightMu)]

    # get a list of gen muons in the fiducial volume
    genMu = [m for m in gen.product() if bool(m) and isMuonFiducial(m)]

    # Get collection of photons from packedGenParticles
    packedGenPho = [p for p in packedGen.product() if p.pdgId() == 22]

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
        fsrRec = {}
        matched = {}
        improvesZ = {}
        dREt = {}

        for fsrType, label in fsrLabels.iteritems():
            if fsrType == "Leg":
                improvesZ["Leg"] = False
                fsrLeg = [ph for ph in getLegacyFSR(tightMu.index(muR), tightMu, label) if ph.pt() > 4.]
                matched[fsrType] = (len(fsrGen) != 0 and len(fsrLeg) != 0)

                fsrRec[fsrType] = None
                if len(fsrLeg) != 0:
                    fsrRec[fsrType] = fsrLeg[0]
                    if len(fsrLeg) > 1:
                        for rfsr in fsrLeg[1:]:
                            if rfsr.pt() > fsrRec[fsrType].pt():
                                fsrRec[fsrType] = rfsr

                continue

            if muR.hasUserCand(label):
                fsrRec[fsrType] = muR.userCand(label)
            else:
                fsrRec[fsrType] = None
    
            if fsrRec[fsrType]:
                improvesZ[fsrType] = any((muR.pdgId() == -1 * otherMu.pdgId() and \
                                              passZMassCut((muR.p4() + otherMu.p4()).M()) and \
                                              photonImprovesZ(muR, otherMu, fsrRec[fsrType])) \
                                             for otherMu in tightMu)
            else:
                improvesZ[fsrType] = False
    
            matched[fsrType] = (len(fsrGen) != 0 and bool(fsrRec[fsrType]))

            if "DREt" in fsrType and fsrRec[fsrType] is not None:
                dREt[fsrType] = muR.userFloat("%sDREt"%label)


        if len(fsrGen) != 0:
            bestGen = fsrGen[0]
            if len(fsrGen) > 1:
                for gfsr in fsrGen[1:]:
                    if gfsr.pt() > bestGen.pt():
                        bestGen = gfsr

            fillGenHistos(muG, bestGen, matched, dREt, improvesZ)


        fillRecoHistos(muR, len(fsrGen)!=0, fsrRec, dREt, improvesZ)

genFSRMatched = {"%s%s"%(fsrType,maybeDM) : h['foundGen%s%sFSRPt'%(fsrType, maybeDM)].GetEntries() \
                     for fsrType in fsrLabels \
                     for maybeDM in ['','DM'] \
                     if not (fsrType == "Leg" and maybeDM == "DM")}
genFSRTot = h['genFSRPt'].GetEntries()
recoFSRMatched = {"%s%s"%(fsrType,maybeDM) : h['real%s%sFSRPt'%(fsrType, maybeDM)].GetEntries() \
                      for fsrType in fsrLabels \
                      for maybeDM in ['','DM'] \
                      if not (fsrType == "Leg" and maybeDM == "DM")}
recoFSRTot = {"%s%s"%(fsrType,maybeDM) : h['all%s%sFSRPt'%(fsrType, maybeDM)].GetEntries() \
                  for fsrType in fsrLabels \
                  for maybeDM in ['','DM'] \
                  if not (fsrType == "Leg" and maybeDM == "DM")}

print "Done!"
print ""

try:
    print "Legacy algorithm:"
    print "    Found   %d of %d gen FSR   (efficiency: %.3f %%)"%(genFSRMatched['Leg'], genFSRTot, (100. * genFSRMatched['Leg']) / genFSRTot)
    print "    Matched %d of %d found FSR (purity:     %.3f %%)"%(recoFSRMatched['Leg'], recoFSRTot['Leg'], (100. * recoFSRMatched['Leg']) / recoFSRTot['Leg'])
except ZeroDivisionError:
    print "Nothing found for Legacy algorithm"

try:
    print "Square Cut algorithm (eT>4, dR<0.3):"
    print "    Found   %d of %d gen FSR   (efficiency: %.3f %%)"%(genFSRMatched['Et4DR03'], genFSRTot, (100. * genFSRMatched['Et4DR03']) / genFSRTot)
    print "    Matched %d of %d found FSR (purity:     %.3f %%)"%(recoFSRMatched['Et4DR03'], recoFSRTot['Et4DR03'], (100. * recoFSRMatched['Et4DR03']) / recoFSRTot['Et4DR03'])
except ZeroDivisionError:
    print "Nothing found for Square Cut algorithm (eT>4, dR<0.3)"

try:
    print "Isolated Square Cut algorithm (eT>4, dR<0.3):"
    print "    Found   %d of %d gen FSR   (efficiency: %.3f %%)"%(genFSRMatched['Et4DR03Iso'], genFSRTot, (100. * genFSRMatched['Et4DR03Iso']) / genFSRTot)
    print "    Matched %d of %d found FSR (purity:     %.3f %%)"%(recoFSRMatched['Et4DR03Iso'], recoFSRTot['Et4DR03Iso'], (100. * recoFSRMatched['Et4DR03Iso']) / recoFSRTot['Et4DR03Iso'])
except ZeroDivisionError:
    print "Nothing found for isolated Square Cut algorithm (eT>4, dR<0.3)"

try:
    print "Square Cut algorithm (eT>4, dR<0.1):"
    print "    Found   %d of %d gen FSR   (efficiency: %.3f %%)"%(genFSRMatched['Et4DR01'], genFSRTot, (100. * genFSRMatched['Et4DR01']) / genFSRTot)
    print "    Matched %d of %d found FSR (purity:     %.3f %%)"%(recoFSRMatched['Et4DR01'], recoFSRTot['Et4DR01'], 
                                                                  (100. * recoFSRMatched['Et4DR01']) / recoFSRTot['Et4DR01'])
    print "deltaR/eT algorithm still needs a working point, check the plots"
except ZeroDivisionError:
    print "Nothing found for Square Cut algorithm (eT>4, dR<0.1)"

try:
    print "Isolated Square Cut algorithm (eT>4, dR<0.1):"
    print "    Found   %d of %d gen FSR   (efficiency: %.3f %%)"%(genFSRMatched['Et4DR01Iso'], genFSRTot, (100. * genFSRMatched['Et4DR01Iso']) / genFSRTot)
    print "    Matched %d of %d found FSR (purity:     %.3f %%)"%(recoFSRMatched['Et4DR01Iso'], recoFSRTot['Et4DR01Iso'], 
                                                                  (100. * recoFSRMatched['Et4DR01Iso']) / recoFSRTot['Et4DR01Iso'])
except ZeroDivisionError:
    print "Nothing found for isolated Square Cut algorithm (eT>4, dR<0.1)"

try:
    print "Square Cut algorithm (eT>4, dR<0.3) (DM):"
    print "    Found   %d of %d gen FSR   (efficiency: %.3f %%)"%(genFSRMatched['Et4DR03DM'], genFSRTot, (100. * genFSRMatched['Et4DR03DM']) / genFSRTot)
    print "    Matched %d of %d found FSR (purity:     %.3f %%)"%(recoFSRMatched['Et4DR03DM'], recoFSRTot['Et4DR03DM'], (100. * recoFSRMatched['Et4DR03DM']) / recoFSRTot['Et4DR03DM'])
except ZeroDivisionError:
    print "Nothing found for Square Cut algorithm (eT>4, dR<0.3) (DM)"

try:
    print "Isolated Square Cut algorithm (eT>4, dR<0.3) (DM):"
    print "    Found   %d of %d gen FSR   (efficiency: %.3f %%)"%(genFSRMatched['Et4DR03IsoDM'], genFSRTot, (100. * genFSRMatched['Et4DR03IsoDM']) / genFSRTot)
    print "    Matched %d of %d found FSR (purity:     %.3f %%)"%(recoFSRMatched['Et4DR03IsoDM'], recoFSRTot['Et4DR03IsoDM'], (100. * recoFSRMatched['Et4DR03IsoDM']) / recoFSRTot['Et4DR03IsoDM'])
except ZeroDivisionError:
    print "Nothing found for isolated Square Cut algorithm (eT>4, dR<0.3) (DM)"

try:
    print "Square Cut algorithm (eT>4, dR<0.1) (DM):"
    print "    Found   %d of %d gen FSR   (efficiency: %.3f %%)"%(genFSRMatched['Et4DR01DM'], genFSRTot, (100. * genFSRMatched['Et4DR01DM']) / genFSRTot)
    print "    Matched %d of %d found FSR (purity:     %.3f %%)"%(recoFSRMatched['Et4DR01DM'], recoFSRTot['Et4DR01DM'], 
                                                                  (100. * recoFSRMatched['Et4DR01DM']) / recoFSRTot['Et4DR01DM'])
    print "deltaR/eT algorithm still needs a working point, check the plots"
except ZeroDivisionError:
    print "Nothing found for Square Cut algorithm (eT>4, dR<0.1) (DM)"

try:
    print "Isolated Square Cut algorithm (eT>4, dR<0.1) (DM):"
    print "    Found   %d of %d gen FSR   (efficiency: %.3f %%)"%(genFSRMatched['Et4DR01IsoDM'], genFSRTot, (100. * genFSRMatched['Et4DR01IsoDM']) / genFSRTot)
    print "    Matched %d of %d found FSR (purity:     %.3f %%)"%(recoFSRMatched['Et4DR01IsoDM'], recoFSRTot['Et4DR01IsoDM'], 
                                                                  (100. * recoFSRMatched['Et4DR01IsoDM']) / recoFSRTot['Et4DR01IsoDM'])
except ZeroDivisionError:
    print "Nothing found for isolated Square Cut algorithm (eT>4, dR<0.1) (DM)"

print "deltaR/eT algorithm still needs a working point, check the plots"


plotDir = '~/www/dREtFSRPlotsWithIso'

# make plots look halfway decent
ROOT.gStyle.SetOptStat(0)
ROOT.gStyle.SetPadTickX(1)
ROOT.gStyle.SetPadTickY(1)
ROOT.gStyle.SetPalette(1)
ROOT.gStyle.SetLegendFillColor(0)
ROOT.gStyle.SetLegendBorderSize(0)
ROOT.gROOT.ForceStyle()

colors = {
    'Leg' : ROOT.kBlack,
    'Et4DR03' : ROOT.kRed,
    'Et4DR01' : ROOT.kBlue,
    'DREt' : ROOT.kGreen+3,
    'DREt15' : ROOT.kMagenta,
    'DREt2' : ROOT.kViolet+7,
    'Et4DR03Iso' : ROOT.kOrange-3,
    'Et4DR01Iso' : ROOT.kAzure+5,
    'DREtIso' : ROOT.kSpring,
    'DREt15Iso' : ROOT.kPink-4,
    'DREt2Iso' : ROOT.kViolet-5,
    }
colors.update({"%sDM"%k:v for k,v in colors.iteritems()})

markers = {
    'Leg' : 20,
    'Et4DR03' : 21,
    'Et4DR01' : 21,
    'DREt' : 22,
    'DREt15' : 22,
    'DREt2' : 22,
    'Et4DR03DM' : 25,
    'Et4DR01DM' : 25,
    'DREtDM' : 26,
    'DREt15DM' : 26,
    'DREt2DM' : 26,
    'Et4DR03Iso' : 21,
    'Et4DR01Iso' : 21,
    'DREtIso' : 22,
    'DREt15Iso' : 22,
    'DREt2Iso' : 22,
    'Et4DR03IsoDM' : 25,
    'Et4DR01IsoDM' : 25,
    'DREtIsoDM' : 26,
    'DREt15IsoDM' : 26,
    'DREt2IsoDM' : 26,
}

dREtCut = {
    'DREt' : 0.0159999999,
    'DREtDM' : 0.0159999999,
    'DREt15' : 0.0059999999,
    'DREt15DM' : 0.0059999999,
    'DREt2' : 0.002199999,
    'DREt2DM' : 0.002199999,
    'DREtIso' : 0.0199999999,
    'DREtIsoDM' : 0.019999999,
    'DREt15Iso' : 0.0159999999,
    'DREt15IsoDM' : 0.01599999999,
    'DREt2Iso' : 0.009999999,
    'DREt2IsoDM' : 0.0099999999,
}

dREtCutBin = {k : h["all%sFSRDREt"%k].GetXaxis().FindBin(v) for k,v in dREtCut.iteritems()}

legText = {
    'Leg' : "Legacy",
    'Et4DR03' : "E_{T_{\\gamma}} > 4, \\Delta R < 0.3",
    'Et4DR01' : "E_{T_{\\gamma}} > 4, \\Delta R < 0.1",
    'DREt' : "\\frac{\\Delta R}{E_{T_{\\gamma}}} < %0.3f"%dREtCut['DREt'],
    'DREt15' : "\\frac{\\Delta R}{E_{T_{\\gamma}}^{1.5}} < %0.4f"%dREtCut['DREt15'],
    'DREt2' : "\\frac{\\Delta R}{E_{T_{\\gamma}}^{2}} < %0.4f"%dREtCut['DREt2'],
    'Et4DR03DM' : "E_{T_{\\gamma}} > 4, \\Delta R < 0.3 (\\Delta m_{Z} \\text{ req.})",
    'Et4DR01DM' : "E_{T_{\\gamma}} > 4, \\Delta R < 0.1 (\\Delta m_{Z} \\text{ req.})",
    'DREtDM' : "\\frac{\\Delta R}{E_{T_{\\gamma}}} < %0.3f (\\Delta m_{Z} \\text{ req.})"%dREtCut['DREtDM'],
    'DREt15DM' : "\\frac{\\Delta R}{E_{T_{\\gamma}}^{1.5}} < %0.4f (\\Delta m_{Z} \\text{ req.})"%dREtCut['DREt15DM'],
    'DREt2DM' : "\\frac{\\Delta R}{E_{T_{\\gamma}}^{2}} < %0.4f (\\Delta m_{Z} \\text{ req.})"%dREtCut['DREt2DM'],
    'Et4DR03Iso' : "E_{T_{\\gamma}} > 4, \\Delta R < 0.3 \\text{ (Iso.)}",
    'Et4DR01Iso' : "E_{T_{\\gamma}} > 4, \\Delta R < 0.1 \\text{ (Iso.)}",
    'DREtIso' : "\\frac{\\Delta R}{E_{T_{\\gamma}}} < %0.3f \\text{ (Iso.)}"%dREtCut['DREt'],
    'DREt15Iso' : "\\frac{\\Delta R}{E_{T_{\\gamma}}^{1.5}} < %0.4f \\text{ (Iso.)}"%dREtCut['DREt15'],
    'DREt2Iso' : "\\frac{\\Delta R}{E_{T_{\\gamma}}^{2}} < %0.4f \\text{ (Iso.)}"%dREtCut['DREt2'],
    'Et4DR03IsoDM' : "E_{T_{\\gamma}} > 4, \\Delta R < 0.3 (\\text{Iso., } \\Delta m_{Z} \\text{ req.})",
    'Et4DR01IsoDM' : "E_{T_{\\gamma}} > 4, \\Delta R < 0.1 (\\text{Iso., } \\Delta m_{Z} \\text{ req.})",
    'DREtIsoDM' : "\\frac{\\Delta R}{E_{T_{\\gamma}}} < %0.3f (\\text{Iso., } \\Delta m_{Z} \\text{ req.})"%dREtCut['DREtDM'],
    'DREt15IsoDM' : "\\frac{\\Delta R}{E_{T_{\\gamma}}^{1.5}} < %0.4f (\\text{Iso., } \\Delta m_{Z} \\text{ req.})"%dREtCut['DREt15DM'],
    'DREt2IsoDM' : "\\frac{\\Delta R}{E_{T_{\\gamma}}^{2}} < %0.4f (\\text{Iso., } \\Delta m_{Z} \\text{ req.})"%dREtCut['DREt2DM'],
    }

legTextROC = {
    'Leg' : "Legacy",
    'Et4DR03' : "E_{T_{\\gamma}} > 4, \\Delta R < 0.3",
    'Et4DR01' : "E_{T_{\\gamma}} > 4, \\Delta R < 0.1",
    'DREt' : "\\frac{\\Delta R}{E_{T_{\\gamma}}}",
    'DREt15' : "\\frac{\\Delta R}{E_{T_{\\gamma}}^{1.5}}",
    'DREt2' : "\\frac{\\Delta R}{E_{T_{\\gamma}}^{2}}",
    'Et4DR03DM' : "E_{T_{\\gamma}} > 4, \\Delta R < 0.3 (\\Delta m_{Z} \\text{ req.})",
    'Et4DR01DM' : "E_{T_{\\gamma}} > 4, \\Delta R < 0.1 (\\Delta m_{Z} \\text{ req.})",
    'DREtDM' : "\\frac{\\Delta R}{E_{T_{\\gamma}}} (\\Delta m_{Z} \\text{ req.})",
    'DREt15DM' : "\\frac{\\Delta R}{E_{T_{\\gamma}}^{1.5}} (\\Delta m_{Z} \\text{ req.})",
    'DREt2DM' : "\\frac{\\Delta R}{E_{T_{\\gamma}}^{2}} (\\Delta m_{Z} \\text{ req.})",
    'Et4DR03Iso' : "E_{T_{\\gamma}} > 4, \\Delta R < 0.3 \\text{ (Iso.)}",
    'Et4DR01Iso' : "E_{T_{\\gamma}} > 4, \\Delta R < 0.1 \\text{ (Iso.)}",
    'DREtIso' : "\\frac{\\Delta R}{E_{T_{\\gamma}}} \\text{ (Iso.)}",
    'DREt15Iso' : "\\frac{\\Delta R}{E_{T_{\\gamma}}^{1.5}} \\text{ (Iso.)}",
    'DREt2Iso' : "\\frac{\\Delta R}{E_{T_{\\gamma}}^{2}} \\text{ (Iso.)}",
    'Et4DR03IsoDM' : "E_{T_{\\gamma}} > 4, \\Delta R < 0.3 (\\text{Iso., } \\Delta m_{Z} \\text{ req.})",
    'Et4DR01IsoDM' : "E_{T_{\\gamma}} > 4, \\Delta R < 0.1 (\\text{Iso., } \\Delta m_{Z} \\text{ req.})",
    'DREtIsoDM' : "\\frac{\\Delta R}{E_{T_{\\gamma}}} (\\text{Iso., } \\Delta m_{Z} \\text{ req.})",
    'DREt15IsoDM' : "\\frac{\\Delta R}{E_{T_{\\gamma}}^{1.5}} (\\text{Iso., } \\Delta m_{Z} \\text{ req.})",
    'DREt2IsoDM' : "\\frac{\\Delta R}{E_{T_{\\gamma}}^{2}} (\\text{Iso., } \\Delta m_{Z} \\text{ req.})",
    }

dRLegDims = [0.3, 0.77, 0.96, 0.94]
legdims = {}
legdims['eff'] = {}
legdims['eff']['DEta'] = dRLegDims
legdims['eff']['DPhi'] = dRLegDims
legdims['eff']['DR'] = dRLegDims
legdims['eff']['Pt'] = [0.12, 0.72, 0.75, 0.94]
legdims['eff']['DREt'] = [0.6, 0.75, 0.9, 0.9]
legdims['pur'] = {}
legdims['pur']['DEta'] = dRLegDims
legdims['pur']['DPhi'] = dRLegDims
legdims['pur']['DR'] = dRLegDims
legdims['pur']['Pt'] = [0.2, 0.10, 0.8, 0.35]
legdims['pur']['DREt'] = [0.6, 0.75, 0.9, 0.9]

legTextSize = 0.015
legEntryHeight = 0.005
legEntrySep = 0.003
dRLegParams = {
    'entryheight' : legEntryHeight,
    'entrysep' : legEntrySep,
    'textsize' : legTextSize,
    'leftmargin' : 0.25,
    'rightmargin' : 0.07,
    'topmargin' : 0.02,
    }

legParams = {'eff' : {}, 'pur' : {}}
legParams['eff']['DEta'] = dRLegParams
legParams['eff']['DPhi'] = dRLegParams
legParams['eff']['DR'] = dRLegParams
legParams['eff']['Pt'] = {
    'entryheight' : legEntryHeight,
    'entrysep' : legEntrySep,
    'textsize' : legTextSize,
    'leftmargin' : 0.005,
    'rightmargin' : 0.28,
    'topmargin' : 0.02,
    }
legParams['pur']['DEta'] = dRLegParams
legParams['pur']['DPhi'] = dRLegParams
legParams['pur']['DR'] = dRLegParams
legParams['pur']['Pt'] = {
    'entryheight' : legEntryHeight,
    'entrysep' : legEntrySep,
    'textsize' : legTextSize,
    'leftmargin' : 0.01,
    'rightmargin' : 0.28,
    'topmargin' : 0.68,
    }


for var in ["Pt", "DR", "DEta", "DPhi"]:
    prettyVar = var.replace("D", "\\Delta ").replace("Eta", "\\eta").replace("Phi", "\\phi").replace("Pt", "p_{T\\gamma}")

    cgen = Canvas(1000, 800)
    h['genFSR%s'%var].SetLineColor(ROOT.kBlue)
    h['genFSR%s'%var].SetLineWidth(2)
    h['genFSR%s'%var].GetXaxis().SetTitle("\\text{Gen FSR }%s"%prettyVar)
    h['genFSR%s'%var].Draw("hist")
    style.setCMSStyle(cgen, "", True, "Preliminary Simulation", 13, -1.)
    cgen.Print("%s/genFSR%s.png"%(plotDir, var))
    
    ceff = Canvas(1000, 800)
    # legEff = ROOT.TLegend(*legdims['eff'][var])
    # legEff.SetNColumns(4)
    # legEff.SetEntrySeparation(0.002*legEff.GetEntrySeparation())
    # legEff.SetTextSize(10.*legEff.GetTextSize())
    effFrame = h['genFSR%s'%var].empty_clone()
    effFrame.SetMaximum(1.1)
    effFrame.SetMinimum(0.)
    effFrame.GetXaxis().SetTitle(prettyVar)
    effFrame.GetYaxis().SetTitle("Efficiency")
    effFrame.Draw("E")

    cpur = Canvas(1000, 800)
    # legPur = ROOT.TLegend(*legdims['pur'][var])
    # legPur.SetNColumns(4)
    # legPur.SetEntrySeparation(0.002*legPur.GetEntrySeparation())
    # legPur.SetTextSize(10.*legPur.GetTextSize())
    purFrame = h['genFSR%s'%var].empty_clone()
    purFrame.SetMaximum(1.1)
    purFrame.SetMinimum(0.)
    purFrame.GetXaxis().SetTitle(prettyVar)
    purFrame.GetYaxis().SetTitle("Purity")
    purFrame.Draw()

    eff = {}
    pur = {}

    denomEff = h['genFSR%s'%var] # same for all

    for fsrType in fsrLabels:
        for maybeDM in ['', 'DM']:
            if maybeDM != '' and fsrType == 'Leg':
                continue

            key = "%s%s"%(fsrType, maybeDM)
            
            if "DREt" in fsrType:
                numEff = h['foundGen%sFSR%s'%(key,var)].ProjectionY("es%s%s"%(key,var), 1, dREtCutBin[key])
                numPur = h['real%sFSR%s'%(key,var)].ProjectionY("ps%s%s"%(key,var), 1, dREtCutBin[key])
                denomPur = h['all%sFSR%s'%(key,var)].ProjectionY("pd%s%s"%(key,var), 1, dREtCutBin[key])
            else:
                numEff = h['foundGen%sFSR%s'%(key,var)]
                numPur = h['real%sFSR%s'%(key,var)]
                denomPur = h['all%sFSR%s'%(key,var)]
                           
            eff[key] = ROOT.TGraphAsymmErrors(numEff, denomEff)
            eff[key].SetTitle(legText[key])
            eff[key].legendstyle = "LPE"
            eff[key].SetMarkerStyle(markers[key])
            eff[key].SetMarkerColor(colors[key])
            eff[key].SetLineColor(colors[key])
            eff[key].SetLineWidth(2)
            ceff.cd()
            eff[key].Draw("PSAME")
            #legEff.AddEntry(eff[key], legText[key], "LPE")

            pur[key] = ROOT.TGraphAsymmErrors(numPur, denomPur)
            pur[key].SetTitle(legText[key])
            pur[key].legendstyle = "LPE"
            pur[key].SetMarkerStyle(markers[key])
            pur[key].SetMarkerColor(colors[key])
            pur[key].SetLineColor(colors[key])
            pur[key].SetLineWidth(2)
            cpur.cd()
            pur[key].Draw("PSAME")
            #legPur.AddEntry(pur[key], legText[key], "LPE")

    ceff.cd()
    legEff = Legend(eff.values(), ceff, **legParams['eff'][var])
    legEff.SetNColumns(3)
    legEff.Draw("SAME")
    style.setCMSStyle(ceff, "", True, "Preliminary Simulation", 13, -1.)
    ceff.Print("%s/eff%s.png"%(plotDir, var))

    cpur.cd()
    legPur = Legend(pur.values(), cpur, **legParams['pur'][var])
    legPur.SetNColumns(3)
    legPur.Draw("SAME")
    style.setCMSStyle(cpur, "", True, "Preliminary Simulation", 13, -1.)
    cpur.Print("%s/purity%s.png"%(plotDir,var))        


roc = {}
efcy = {}
prty = {}

for fsrType in fsrLabels:
    if 'DREt' not in fsrType:
        continue

    cdret = Canvas(1000, 800)
    
    superscript = "^{1.5}" if "15" in fsrType else ""
    superscript = "^{2}" if "2" in fsrType else ""
    frame = h["all%sFSRDREt"%fsrType].empty_clone()
    frame.GetXaxis().SetTitle("\\frac{\\Delta R}{E_{T\\gamma}%s} \\text{ threshold}"%superscript)
    frame.GetXaxis().SetTitleOffset(1.1)
    frame.SetMinimum(0.)
    frame.SetMaximum(1.1)
    frame.Draw()

    dREtEff = {}
    dREtPur = {}

    leg = ROOT.TLegend(0.65, 0.7, 0.85, 0.88)
    
    for maybeDM in ['', 'DM']:

        key = "%s%s"%(fsrType, maybeDM)

        numEff = frame.empty_clone()
        denomEff = frame.empty_clone()
        for b in denomEff:
            b.value = genFSRTot
            b.error = sqrt(genFSRTot)
        numPur = frame.empty_clone()
        denomPur = frame.empty_clone()

        nNumEff = 0
        nNumPur = 0
        nDenomPur = 0

        for i in range(1, frame.GetNbinsX()+1):
            nNumEff += h['foundGen%sFSRDREt'%key].GetBinContent(i)
            numEff.SetBinContent(i, nNumEff)
            numEff.SetBinError(i, sqrt(nNumEff))

            nNumPur += h['real%sFSRDREt'%key].GetBinContent(i)
            nDenomPur += h['all%sFSRDREt'%key].GetBinContent(i)
            numPur.SetBinContent(i, nNumPur)
            denomPur.SetBinContent(i, nDenomPur)
            numPur.SetBinError(i, sqrt(nNumPur))
            denomPur.SetBinError(i, sqrt(nDenomPur))

        numEff.Sumw2()
        denomEff.Sumw2()
        numPur.Sumw2()
        denomPur.Sumw2()

        dREtEff[key] = ROOT.TGraphAsymmErrors(numEff, denomEff)
        dREtPur[key] = ROOT.TGraphAsymmErrors(numPur, denomPur)

        effColor = ROOT.kBlue if maybeDM == "" else ROOT.kCyan+1
        purColor = ROOT.kRed if maybeDM == "" else ROOT.kMagenta+1

        dREtEff[key].SetMarkerStyle(33)
        dREtEff[key].SetMarkerSize(2)
        dREtEff[key].SetMarkerColor(effColor)
        dREtEff[key].SetLineColor(effColor)
        dREtEff[key].SetLineWidth(2)
        dREtEff[key].Draw("PSAME")
        dREtPur[key].SetMarkerStyle(33)
        dREtPur[key].SetMarkerSize(2)
        dREtPur[key].SetMarkerColor(purColor)
        dREtPur[key].SetLineColor(purColor)
        dREtPur[key].SetLineWidth(2)
        dREtPur[key].Draw("PSAME")

        suffix = "" if maybeDM == "" else " (\\Delta m_{Z} \\text{ req.})"

        leg.AddEntry(dREtEff[key], "\\text{Efficiency}%s"%suffix, "LPE")
        leg.AddEntry(dREtPur[key], "\\text{Purity}%s"%suffix, "LPE")


        # ROC for dREt threshold
        roc[key] = Graph(dREtPur[key].GetN(), title=legTextROC[key])
        efcy[key] = [dREtEff[key][i][1] for i in xrange(dREtEff[key].GetN())]
        prty[key] = [dREtPur[key][i][1] for i in xrange(dREtPur[key].GetN())]
        for i, (ef, pr) in enumerate(zip(efcy[key], prty[key])):
            roc[key].SetPoint(i, 1.-pr, ef)
            roc[key].SetLineColor(colors[key])
            roc[key].SetLineWidth(2)
            roc[key].legendstyle = "L"
            roc[key].drawstyle = "C"
            if maybeDM:
                roc[key].linestyle = 'dashed'
            else:
                roc[key].linestyle = 'solid'
            roc[key].xaxis.SetTitle("Fake Rate (1 - purity)")
            roc[key].yaxis.SetTitle("Efficiency")
            roc[key].yaxis.SetTitleOffset(1.3)


    leg.Draw("SAME")

    style.setCMSStyle(cdret, "", True, "Preliminary Simulation", 13, -1.)
    cdret.Print("%s/effPur_%s.png"%(plotDir,fsrType))


croc = Canvas(800, 800)

# opts = "AC"
# for k,r in roc.iteritems():
#     r.Draw(opts)
#     opts = "C"

g = {}
#tex = {}
for fsrType in fsrLabels:
    if 'DREt' in fsrType:
        continue
    for maybeDM in ['', 'DM']:
        if fsrType == "Leg" and maybeDM == "DM":
            continue

        key = "%s%s"%(fsrType, maybeDM)

        g[key] = Graph(1, title=legTextROC[key])
        try:
            g[key].SetPoint(0, 1.-(1.*recoFSRMatched[key]/recoFSRTot[key]), 1.*genFSRMatched[key]/genFSRTot)
        except ZeroDivisionError:
            g[key].SetPoint(0, 0., 1.*genFSRMatched[key]/genFSRTot)
        g[key].SetMarkerStyle(markers[key])
        g[key].SetMarkerColor(colors[key])
        g[key].drawstyle = "P"
        #g[key].Draw("P")

        # tex[key] = ROOT.TLatex(g[key][0][0], g[key][0][1], legText[key])
        # tex[key].SetTextSize(tex[key].GetTextSize()*0.3)
        # tex[key].SetTextAlign(33)
        #tex[key].Draw()

draw(roc.values()+g.values(), croc, xtitle="Fake Rate (1 - purity)", ytitle="Efficiency")
leg = Legend(roc.values()+g.values(), croc, leftmargin=0.2, topmargin=0.65, rightmargin=0.03,
             entryheight=0.009, entrysep=0.0005, textsize=0.014)
leg.SetNColumns(3)
leg.Draw("SAME")

# for k, t in tex.iteritems():
#     t.Draw()
#croc.Update()
style.setCMSStyle(croc, "", True, "Preliminary Simulation", 13, -1.)
croc.Print("%s/ROCs.png"%plotDir)

for key in efcy:
    if 'DREt' not in key:
        continue

    print "%s cut   purity    efficiency"%key
    for i, (ef, pr) in enumerate(zip(efcy[key], prty[key])):
        print "%.4f:      %.3f     %.3f"%(h["all%sFSRDREt"%key].GetXaxis().GetBinUpEdge(i+1), pr, ef)
    print ""




#gWP = Graph(3)
#gWP.SetPoint(0, 1-prty[11], efcy[11])
#gWP.SetPoint(1, 1-prty[15], efcy[15])
#gWP.SetPoint(2, 1-prty[19], efcy[19])
#gWP.SetMarkerStyle(33)
#gWP.SetMarkerSize(2)
#gWP.SetMarkerColor(colors[0])
#gWP.Draw("P")
#lWP12 = ROOT.TLatex(gWP[0][0]-0.015, gWP[0][1]-0.025, "#color[8]{#frac{#Delta #kern[-0.6]{R}}{E_{T}} < 0.012}")
#lWP12.SetTextAlign(31)
#lWP12.Draw()
#lWP16 = ROOT.TLatex(gWP[1][0]-0.01, gWP[1][1], "#color[8]{#frac{#Delta #kern[-0.6]{R}}{E_{T}} < 0.016}")
#lWP16.SetTextAlign(32)
#lWP16.Draw()
#lWP20 = ROOT.TLatex(gWP[2][0]-0.01, gWP[2][1]+0.01, "#color[8]{#frac{#Delta #kern[-0.6]{R}}{E_{T}} < 0.020}")
#lWP20.SetTextAlign(31)
#lWP20.Draw()
#g15WP22 = Graph(1)
#g15WP22.SetPoint(0, 1-prty15[11], efcy15[11])
#g15WP22.SetMarkerStyle(34)
#g15WP22.SetMarkerSize(2)
#g15WP22.SetMarkerColor(colors[1])
#g15WP22.Draw("P")
#l15WP22 = ROOT.TLatex(g15WP22[0][0]+0.01, g15WP22[0][1]-0.01, "#color[6]{#frac{#Delta #kern[-0.6]{R}}{E_{T}^{1.5}} < 0.0022}")
#l15WP22.Draw()

