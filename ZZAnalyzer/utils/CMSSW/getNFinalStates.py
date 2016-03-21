'''

Little script to get the number of events in each final state for a Higgs MC file.
Uses CMSSW FWLite, so it must be run from a cmsenv.

Nate Woods, U. Wisconsin

'''

import ROOT
import sys
from DataFormats.FWLite import Events, Handle


def getFSLeptons(p):
    '''
    Returns a 3-digit int where the digits are the number of electrons, muons and taus.
    E.g., if the final state is 2e2t, 202 is returned.
    Recursive.
    '''
    # If this is a lepton, we're all set
    pid = abs(p.pdgId())
    if pid == 11 or pid == 13 or pid == 15:
        return 10**((15-pid)/2) # 100 for electron, 10 for muon, 1 for tau
    
    # Otherwise, see what it decayed into
    lepts = 0
    for i in xrange(p.numberOfDaughters()):
        lepts += getFSLeptons(p.daughter(i))

    return lepts


events = Events(['root://cmsxrootd.fnal.gov//store/mc/Phys14DR/GluGluToHToZZTo4L_M-125_13TeV-powheg-pythia6/MINIAODSIM/PU20bx25_tsg_PHYS14_25_V1-v1/00000/3295EF7C-2070-E411-89C4-7845C4FC35DB.root'])

pHandle = Handle("std::vector<reco::GenParticle>")
pLabel = ("prunedGenParticles")

n = {} # number of events in each channel

for e in range(5):
    for m in range(5):
        for t in range(5):
            n[e*100+m*10+t]=0

count = 0
for event in events:
    if count % 1000 == 0:
        print "Processing event %i"%count
    count += 1

    event.getByLabel(pLabel, pHandle)
    particles = pHandle.product()

    for p in particles:
        # If this is a Higgs, figure out its final state and move on to the next event
        if p.pdgId() == 25:
            n[getFSLeptons(p)] += 1
            break

        # Otherwise, we don't care
        continue

print ""
total = 0
for chan, tot in n.iteritems():
    channel = ''
    while chan >= 100:
        channel += 'e'
        chan -= 100
    while chan >= 10:
        channel += 'm'
        chan -= 10
    while chan != 0:
        channel += 't'
        chan -= 1

    if tot != 0:
        total += tot
        print "%s, %i"%(channel, tot)
        
print "Total: %i"%total
