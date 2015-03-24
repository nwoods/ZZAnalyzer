'''

Dump lepton information in the approved HZZ4l sync format.
Only does each lepton once regardless of number of rows. Sorts by pt.

Is most useful when sorted afterwards with a command like

$ sort -t : -k 1n -k 2n -k 3n -k5nr leptonSync.txt

Author: N. Woods, U. Wisconsin

'''

from ZZHelpers import *
from rootpy.io import root_open
import argparse


class LeptonCollection(object):
    class Lepton(object):
        def __init__(self, name, row, pt=0):
            if pt != 0:
                self.pt = pt
            else:
                self.pt = objVar(row, 'Pt', name)
            self.eta = objVar(row, 'Eta', name)
            self.phi = objVar(row, 'Phi', name)
            self.sip = objVar(row, 'SIP3D', name)
            self.chHadIso = objVar(row, 'PFChargedIso', name)
            self.neutHadIso = objVar(row, 'PFNeutralIso', name)
            self.phoIso = objVar(row, 'PFPhotonIso', name)
            self.puCorr = 0 # daughter class must define
            self.combRelIso = -1 # Daughter class must define
            self.bdt = 0 # daughter class must define (if electron)
            self.pdgId = 0 # daughter class must define
        def dumpInfo(self, run, lumi, evt):
            return ("%d:%d:%d:%d:%.2f:%.2f:%.2f:%.2f:%.2f:%.2f:%.2f:%.2f:%.3f:%.3f\n"%(run, lumi, evt, self.pdgId, self.pt, self.eta, \
                                                                               self.phi, self.sip, self.chHadIso, self.neutHadIso, \
                                                                               self.phoIso, self.puCorr, self.combRelIso, self.bdt))
    class Muon(Lepton):
        def __init__(self, name, row, pt=0):
            super(LeptonCollection.Muon, self).__init__(name, row, pt)
            self.combRelIso = objVar(row, 'RelPFIsoDBDefault', name)
            self.pdgId = -13 * objVar(row, "Charge", name)
            self.puCorr = objVar(row, "PFPUChargedIso", name)

    class Electron(Lepton):
        def __init__(self, name, row, pt=0):
            super(LeptonCollection.Electron, self).__init__(name, row, pt)
            self.combRelIso = objVar(row, 'RelPFIsoRho', name)
            self.bdt = objVar(row, 'MVANonTrigID', name)
            self.pdgId = -11 * objVar(row, "Charge", name)
            self.puCorr = objVar(row, 'Rho', name)
                                                        
                     
    def __init__(self, run, lumi, evt):
        self.leptons = {}
        self.run = run
        self.lumi = lumi
        self.evt = evt

    def addLepton(self, name, row):
        pt = objVar(row, 'Pt', name)
        if pt in self.leptons:
            # Do nothing if we've already seen this one
            return
        if name[0] == 'e':
            self.leptons[pt] = LeptonCollection.Electron(name, row, pt)
        else:
            self.leptons[pt] = LeptonCollection.Muon(name, row, pt)

    def writeAll(self, oFile):
        for pt in sorted(self.leptons.keys(), reverse=True):
            oFile.write(self.leptons[pt].dumpInfo(self.run, self.lumi, self.evt))

        
def getObjects(channel):
    nObj = {}
    for letter in channel:
        if letter not in nObj:
            nObj[letter] = 1
        else:
            nObj[letter] += 1
    out = []
    for letter in nObj:
        if nObj[letter] == 1:
            out.append(letter)
        else:
            out += [letter+str(n+1) for n in range(nObj[letter])]
    return out

parser = argparse.ArgumentParser(description='Dump information about the leptons in an ntuple to a text file, for synchronization.')
parser.add_argument('input', type=str, nargs=1, help='Input root file')
parser.add_argument('output', type=str, nargs='?', default='leptonSync.txt',
                    help='Name of the text file to output.')
parser.add_argument('channels', nargs='?', type=str, default='zz',
                    help='Comma separated (no spaces) list of channels, or keyword "zz" for eeee,mmmm,eemm')
# parser.add_argument('--nThreads', type=int,  # just left to remind myself how if needed
#                     help='Maximum number of threads for simultaneous processing. If unspecified, python figures how many your machine can deal with automatically, to a maximum of 4.')

args = parser.parse_args()

if args.channels == 'zz':
    channels = ['eeee', 'eemm', 'mmmm']
else:
    channels = args.channels.split(',')

inFile = args.input[0]

with root_open(inFile) as fin:
    with open(args.output, 'w') as fout:
        for channel in channels:
            print "\nChannel %s:"%channel
            ntuple = fin.Get(channel+'/final/Ntuple')
            objects = getObjects(channel)
            evtLeps = LeptonCollection(-1,-1,-1)
            
            for n, row in enumerate(ntuple):
                if n % 500 == 0:
                    print "Processing row %d"%n
                evt = evVar(row, 'evt')
                lumi = evVar(row, 'lumi')
                run = evVar(row, 'run')
                if evt != evtLeps.evt or lumi != evtLeps.lumi or run != evtLeps.run:
                    evtLeps.writeAll(fout)
                    evtLeps = LeptonCollection(run, lumi, evt)
                
                for lep in objects:
                    evtLeps.addLepton(lep, row)
                    
            # Make sure the last row gets written
            evtLeps.writeAll(fout)

print "Done!"







