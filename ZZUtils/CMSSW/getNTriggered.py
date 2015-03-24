'''

Little script to get the number of events triggering any relevant path.
Uses CMSSW FWLite, so it must be run from a cmsenv.

Nate Woods, U. Wisconsin

'''

# import ROOT in batch mode
import sys
oldargv = sys.argv[:]
sys.argv = [ '-b-' ]
import ROOT
ROOT.gROOT.SetBatch(True)
sys.argv = oldargv

# FWLite C++ libs
ROOT.gSystem.Load("libFWCoreFWLite.so")
ROOT.gSystem.Load("libDataFormatsFWLite.so")
ROOT.AutoLibraryLoader.enable()

# FWLite python libs
from DataFormats.FWLite import Events, Handle

# Triggers to check for
goodTriggers = [
    'HLT_Mu17_TrkIsoVVL_Mu8_TrkIsoVVL_v1',
    'HLT_Mu17_TrkIsoVVL_TkMu8_TrkIsoVVL_v1',
    'HLT_Ele23_Ele12_CaloId_TrackId_Iso_v1',
    'HLT_Mu8_TrkIsoVVL_Ele23_Gsf_CaloId_TrackId_Iso_MediumWP_v1',
    'HLT_Mu23_TrkIsoVVL_Ele12_Gsf_CaloId_TrackId_Iso_MediumWP_v1',
    'HLT_Ele17_Ele12_Ele10_CaloId_TrackId_v1',
]
goodTriggers = set(goodTriggers) # for fast lookup

triggerBits, triggerBitLabel = Handle("edm::TriggerResults"), ("TriggerResults","","HLT")

events = Events(['root://cmsxrootd.fnal.gov//store/mc/Phys14DR/GluGluToHToZZTo4L_M-125_13TeV-powheg-pythia6/MINIAODSIM/PU20bx25_tsg_PHYS14_25_V1-v1/00000/3295EF7C-2070-E411-89C4-7845C4FC35DB.root'])

nPass = 0

for iEv, event in enumerate(events):
    if iEv % 5000 == 0:
        print "Checking event %d"%iEv
    event.getByLabel(triggerBitLabel, triggerBits)
    names = event.object().triggerNames(triggerBits.product())
    for i in xrange(triggerBits.product().size()):
        if names.triggerName(i) in goodTriggers:
            if triggerBits.product().accept(i):
                nPass += 1
                break

print "%d Events passed at least one trigger among:"%nPass
for t in goodTriggers:
    print "     %s"%t
