'''

ZZ->4l analyzer. Takes an FSA Ntuple as input, makes a root file 
with a bunch of histograms of interesting quantities as output.
By default, runs on all root files in a folder. I'll probably add
an option to change that later. It keeps the outputs separate.

Usage: 

Author: Nate Woods

'''

import ROOT
#import sys
#sys.path.append("../ZZUtils")
from ZZUtils import Cutter
#import argparse
#import sys
import os
import glob
from itertools import combinations

Z_MASS = 91.1876

assert os.environ["zza"], "Run setup.sh before running analysis"

class ZZAnalyzer(object):
    def __init__(self, channels, cutSet, infile, outfile='./results/output.root', maxEvents=float("inf")):

        if type(channels) == str:
            if channels == '4l' or channels == 'zz' or channels == 'ZZ':
                self.channels = ['eeee', 'eemm', 'mmmm']
            else:
                assert all(letter in ['e','m','t','g','j'] for letter in channels) and len(channels) <= 4, 'Invalid channel ' + channels
                self.channels = [channels]
        else:
            assert type(channels)==list, 'Channels must be a list or a string'
            assert all ((all(letter in ['e','m','t','g','j'] for letter in channel) and len(channel) <= 4) for channel in channels), 'Invalid channel in ['+','.join(channels)+']'
            self.channels = channels

        self.cutSet = cutSet
        self.cuts = Cutter.Cutter(self.cutSet)

        self.inFile = infile

        self.sample = self.inFile.split('/')[-1].replace('.root','')
        
        self.outFile = outfile

        self.maxEvents = maxEvents

        # Too lazy to go look up Python's version of an ordered hash table, keeping the order separately
        self.cutOrder = [
            "total",
            "combinatorics",
            "trigger",
            "ID",
            "selection",
            "isolation",
            "overlap",
            "OSSF1",
            "Z1Mass",
            "OSSF2",
            "Z2Mass",
            "lepton1Pt",
            "lepton2Pt",
            "leptonPairMass",
            "4lMass"
            ]
        
        # Dictionary with number of events passing each cut for each channel
        self.cutsPassed = {}
        for channel in self.channels:
            self.cutsPassed[channel] = {}
            for cut in self.cutOrder:
                self.cutsPassed[channel][cut] = 0

        self.getHistoDict(self.channels)



    def analyze(self):
        '''
        For a given file, do the whole analysis and output the results to 
        self.outFile
        '''
        # Sample name is file name without path or '.root'
        sampleName = self.inFile.split('/')[-1].replace('.root', '')

        inFile = ROOT.TFile.Open(self.inFile)
        assert bool(inFile), 'No file %s'%self.inFile

        for channel in self.channels:
            objectTemplate = self.mapObjects(channel)
            ntuple = inFile.Get(channel+'/final/Ntuple')

            # For events with more than 4 leptons, FSA Ntuples just have one
            #     row for each possible combination of objects. We have to know
            #     which one is the right one
            wrongRows = self.getRedundantRows(ntuple, channel)

            for row in ntuple:
                # If we've hit maxEvents, we're done
                if self.cutsPassed[channel]['total'] == self.maxEvents:
                    print "%s: Reached %d %s events, ending"%(self.sample, self.maxEvents, channel)
                    break

                # Report progress every 5000 events
                if self.cutsPassed[channel]['total'] % 5000 == 0:
                    print "%s: Processing %s event %d"%(self.sample, channel, self.cutsPassed[channel]["total"])
                
                self.cutsPassed[channel]["total"] += 1

                # Ignore wrong version of event
                if self.cutsPassed[channel]['total'] in wrongRows:
                    continue
                self.cutsPassed[channel]["combinatorics"] += 1
                    
                objects = self.getOSSF(row, channel, objectTemplate)

                # Pass HLT
                if not self.cuts.doCut(row, 'trigger'):
                    continue
                self.cutsPassed[channel]["trigger"] += 1

                # Pass ID cuts
                if not self.cutOnAll(row, 'ID', objects):
                    continue
                self.cutsPassed[channel]["ID"] += 1
                
                # Pass selection cuts
                if not self.cutOnAll(row, 'Selection', objects):
                    continue
                self.cutsPassed[channel]["selection"] += 1

                # Pass isolation cuts
                if not self.cutOnAll(row, 'Iso', objects):
                    continue
                self.cutsPassed[channel]["isolation"] += 1

                # Pass overlap cuts
                if not self.checkOverlaps(row, objects):
                    continue
                self.cutsPassed[channel]["overlap"] += 1

                # Make sure we have one good Z candidate (pair of OSSF leptons)
                if len(objects) < 2:
                    continue
                self.cutsPassed[channel]["OSSF1"] += 1

                # Make sure it's a good Z
                if not self.cuts.doCut(row, 'Z1Mass', objects[0], objects[1]):
                    continue
                self.cutsPassed[channel]["Z1Mass"] += 1
                
                # Make sure there's a second good Z candidate
                if len(objects) < 4:
                    continue
                self.cutsPassed[channel]["OSSF2"] += 1

                # Make sure it's a good-ish Z
                if not self.cuts.doCut(row, 'Z2Mass', objects[2], objects[3]):
                    continue
                self.cutsPassed[channel]["Z2Mass"] += 1
                
                # Make sure at least one lepton has pt>20
                if not any(self.cuts.doCut(row, 'lepton1Pt', obj) for obj in objects):
                    continue
                self.cutsPassed[channel]["lepton1Pt"] += 1

                # Make sure another has pt>10
                if not any(self.cuts.doCut(row, 'lepton2Pt', pair[0]) and self.cuts.doCut(row, 'lepton2Pt', pair[1]) \
                           for pair in combinations(objects,2)):
                    continue
                self.cutsPassed[channel]["lepton2Pt"] += 1

                # All opposite-sign pairs of leptons must have an invariant mass > 4GeV (regardless of flavor)
                if not all(getVar(row, 'SS', pair[0], pair[1]) or self.cuts.doCut(row, 'leptonPairMass', pair[0], pair[1]) \
                           for pair in combinations(objectTemplate, 2)): # use template to maintain alphanumeric order
                    continue
                self.cutsPassed[channel]["leptonPairMass"] += 1

                # 4l inv. mass window
                if not self.cuts.doCut(row, '4lMass'):
                    continue
                self.cutsPassed[channel]["4lMass"] += 1

                self.fillHistos(row, channel, objects)
            else:
                print "%s: Done with %s (%d events)"%(self.sample, channel, self.cutsPassed[channel]['total'])
                
        print "%s: Done with all channels, saving results"%self.sample

        self.saveAllHistos()

        self.cutReport()
                

    def mapObjects(self, channel):
        '''
        Return a list of objects of the form ['e1','e2','m1','m2'] or ['e1','e2','m']
        Objects are in alphabetical/numerical order order
        '''
        nObjects = {}
        objects = []

        for obj in channel:
            if obj not in nObjects:
                nObjects[obj] = 1
            else:
                nObjects[obj] += 1

        for obj, num in nObjects.iteritems():
            if num == 1:
                objects.append(obj)
            else:
                for i in range(num):
                    objects.append(obj+str(i+1))
        
        objects.sort()

        return objects


    def getRedundantRows(self, ntuple, channel):
        '''
        Returns a list of row numbers of rows that are the incorrect combinatorial
        version of the relevant event. The correct row is the one with Z1 closest
        to on-shell, with the highest scalar Pt sum of the remaining leptons used as a 
        tiebreaker
        '''
        nRow = 0
        redundantRows = set()

        prevRun = -1
        prevLumi = -1
        prevEvt = -1
        prevZ = -999.
        prevPtSum = -999.
        prevRow = -1
        
        objectTemplate = self.mapObjects(channel)

        for row in ntuple:
            if nRow == self.maxEvents:
                break

            nRow += 1
            objects = self.getOSSF(row, channel, objectTemplate)

            # Keep track of events within this function by run, lumi block, and event number
            run = getVar(row, 'run')
            lumi = getVar(row, 'lumi')
            evt = getVar(row,'evt')
            sameEvent = (evt == prevEvt and lumi == prevLumi and run == prevRun)

            # The best row for the event is actually the best one *that passes ID cuts*
            # so we have to treat a row that fails them as automatically bad. But, we can
            # only do this when the row is actually a duplicate, to keep our cut stats accurate.
            allGood = False
            for obj in objects:
                if not self.cuts.doCut(row, obj[0]+'ID', obj):
                    break
                if not self.cuts.doCut(row, obj[0]+'Selection', obj):
                    break
                if not self.cuts.doCut(row, obj[0]+'Iso', obj):
                    break
            else:
                # If we never break, the leptons must be OK, as long as there are the right number
                allGood = len(objects) == 4
            if not allGood:
                if sameEvent:
                    redundantRows.add(nRow)
                else:
                    prevRun = run
                    prevLumi = lumi
                    prevEvt = evt
                    prevZ = -999.
                    prevPtSum = -999.
                    prevRow = nRow
                continue
            
            Zmass = getVar(row, 'Mass', objects[0], objects[1])
            ptSum = getVar(row, 'Pt', objects[2]) + getVar(row, 'Pt', objects[3])

            # if this doesn't seem to be a duplicate event, we don't need to do anything but store
            # its info in case it's the first of several
            if not sameEvent:
                prevRun = run
                prevLumi = lumi
                prevEvt = evt
                prevZ = Zmass
                prevPtSum = ptSum
                prevRow = nRow
                continue
            else:
                if abs(Zmass - Z_MASS) < abs(prevZ - Z_MASS):
                    redundantRows.add(prevRow)
                    prevRun = run
                    prevLumi = lumi
                    prevEvt = evt
                    prevZ = Zmass
                    prevPtSum = ptSum
                    prevRow = nRow
                elif abs(Zmass - Z_MASS) == abs(prevZ - Z_MASS):
                    if ptSum > prevPtSum:
                        redundantRows.add(prevRow)
                        prevRun = run
                        prevLumi = lumi
                        prevEvt = evt
                        prevZ = Zmass
                        prevPtSum = ptSum
                        prevRow = nRow
                    else:
                        redundantRows.add(nRow)
                else:
                    redundantRows.add(nRow)
                    
        return redundantRows
       
 
    def getOSSF(self, row, channel, objects):
        '''
        Will return a list of same flavor, opposite sign leptons ordered by closeness
        to nominal Z mass. Will only return as many pairs as are in the row, so length<4
        means there are not two Z candidates in the event. Assumes 4 objects which are all
        leptons. Don't use otherwise.

        Takes advantage of the fact that FSA ntuples place best Z candidate first in
        eeee and mmmm cases.
        '''
        ossfs = []
        
        # only include pairs that are OSSF
        if objects[0][0] == objects[1][0] and not getVar(row, 'SS', objects[0], objects[1]):
            ossfs.extend(objects[:2])
        if objects[2][0] == objects[3][0] and not getVar(row, 'SS', objects[2], objects[3]):
            ossfs.extend(objects[2:])
            
        # If there's 0 or 1 Z candidate, we don't need to worry about order
        if len(ossfs) < 4:
            return ossfs

        # if this is 2e2mu, we might need to flip if the 2mu Z was better
        if channel == 'eemm':
            mass1 = getVar(row, 'Mass', ossfs[0], ossfs[1])
            mass2 = getVar(row, 'Mass', ossfs[2], ossfs[3])
            if abs(mass2 - Z_MASS) < abs(mass1 - Z_MASS):
                return ossfs[2:]+ossfs[:2]
        return ossfs

        
    def getHistoDict(self, channels):
        '''
        Return a dictionary of empty TH1Fs organized as hists[channel][quantity] = hist
        '''
        self.histos = {}

        for channel in channels+['Total']:
            self.histos[channel] = {}

            if channel != 'Total':
                objects = self.mapObjects(channel)
                for obj in objects:
                    self.histos[channel][obj+'Pt'] = ROOT.TH1F(obj+'Pt', obj+'Pt', 60, 0., 120.)
                    self.histos[channel][obj+'Eta'] = ROOT.TH1F(obj+'Eta', obj+' Eta', 12, -3., 3.)
                    self.histos[channel][obj+'Phi'] = ROOT.TH1F(obj+'Phi', obj+' Phi', 32, -3.2, 3.2)
            for obj in ['Z1', 'Z2']:
                self.histos[channel][obj+'Pt'] = ROOT.TH1F(obj+'Pt', obj+' Pt', 60, 0., 120.)
                self.histos[channel][obj+'Eta'] = ROOT.TH1F(obj+'Eta', obj+' Eta', 12, -3., 3.)
                self.histos[channel][obj+'Phi'] = ROOT.TH1F(obj+'Phi', obj+' Phi', 32, -3.2, 3.2)
                self.histos[channel][obj+'Mass'] = ROOT.TH1F(obj+'Mass', obj+' Mass', 60, 5., 125.)
            self.histos[channel]['4lPt'] = ROOT.TH1F('4lPt', '4l Pt', 60, 0., 300.)
            self.histos[channel]['4lEta'] = ROOT.TH1F('4lEta', '4l Eta', 12, -3., 3.)
            self.histos[channel]['4lPhi'] = ROOT.TH1F('4lPhi', '4l Phi', 32, -3.2, 3.2)
            self.histos[channel]['4lMass'] = ROOT.TH1F('4lMass', '4l Mass', 60, 70., 2010.)
            self.histos[channel]['4lMt'] = ROOT.TH1F('4lMt', '4l Mt', 60, 30., 2000.)


    def fillHistos(self, row, channel, objects):
        '''
        Add this row's objects to the output histograms
        '''
        # Need object 4momenta to calculate some values
        momenta = []

        for obj in objects:
            mom = ROOT.TLorentzVector()
            mass = 0
            if obj[0] == 'e':
                mass = 0.000511
            if obj[0] == 'm':
                mass = 0.1057
            mom.SetPtEtaPhiM(getVar(row, 'Pt', obj), getVar(row, 'Eta', obj), getVar(row, 'Phi', obj), mass)
            momenta.append(mom)

        Z1Mom = momenta[0] + momenta[1]
        Z2Mom = momenta[2] + momenta[3]
        totalMom = Z1Mom + Z2Mom
        
        for title in [channel, 'Total']:
            # Single objects
            if title != 'Total':
                for obj in objects:
                    self.histos[title][obj+'Pt'].Fill(getVar(row, 'Pt', obj))
                    self.histos[title][obj+'Eta'].Fill(getVar(row, 'Eta', obj))
                    self.histos[title][obj+'Phi'].Fill(getVar(row, 'Phi', obj))
            
            self.histos[title]['Z1Pt'].Fill(Z1Mom.Pt())
            self.histos[title]['Z1Eta'].Fill(Z1Mom.Eta())
            self.histos[title]['Z1Phi'].Fill(Z1Mom.Phi())
            self.histos[title]['Z1Mass'].Fill(Z1Mom.M())
                   
            self.histos[title]['Z2Pt'].Fill(Z2Mom.Pt())
            self.histos[title]['Z2Eta'].Fill(Z2Mom.Eta())
            self.histos[title]['Z2Phi'].Fill(Z2Mom.Phi())
            self.histos[title]['Z2Mass'].Fill(Z2Mom.M())
                   
            self.histos[title]['4lPt'].Fill(totalMom.Pt())
            self.histos[title]['4lEta'].Fill(totalMom.Eta())
            self.histos[title]['4lPhi'].Fill(totalMom.Phi())
            self.histos[title]['4lMass'].Fill(totalMom.M())
            self.histos[title]['4lMt'].Fill(totalMom.Mt())


    def saveAllHistos(self):
        '''
        Save all histograms to self.outFile, in directories by channel (+Total)
        '''
        f = ROOT.TFile(self.outFile, 'RECREATE')

        dirs = []
        for channel, hDict in self.histos.iteritems():
            dirs.append(ROOT.TDirectoryFile(channel, channel+" histograms"))
            for name, hist in hDict.iteritems():
                dirs[-1].Append(hist)

        for dir in dirs:
            dir.Write()
        f.Close()


    def cutOnAll(self, row, var, objects):
        '''
        Loop over all objects in the final state and see if they pass a single-particle
        cut like isolation or ID or whatever
        '''
        for obj in objects:
            if not self.cuts.doCut(row, obj[0] + var, obj):
                return False
        return True
        

    def checkOverlaps(self, row, objects):
        '''
        Checks all pairs of leptons for overlap
        '''
        for pair in combinations(objects,2):
            # order correctly to make sure the variable will exist
            if pair[1] < pair[0]:
                pair = [pair[1], pair[0]]
            if not self.cuts.doCut(row, 'overlap', *pair):
                return False
        return True


    def cutReport(self):
        '''
        Save a text file with cut information. 
        Same name as outfile but .txt instead of .root.
        '''
        totals = {}
        for cut in self.cutOrder:
            totals[cut] = 0
        with open(self.outFile.replace('.root','.txt'), 'w') as f:
            for channel in self.channels:
                f.write("\n" + channel + ":\n")
                for cut in self.cutOrder:
                    f.write(cut + ": " + str(self.cutsPassed[channel][cut]) + "\n")
                    totals[cut] += self.cutsPassed[channel][cut]

            f.write("\nTotal:\n")
            for cut in self.cutOrder:
                f.write(cut + ": " + str(totals[cut]) + "\n")
    

def getVar(row, var, *objects):
    '''
    Return a variable from an ntuple row. If no objects are specified, it gets
    the "bare" variable (e.g. Mass). If one object is specified, it will return
    the variable specific to that object (e.g. e1Pt). If more objects are 
    specified, it will give the combined object for all of them (e.g. e1_e2_Mass).
    '''

    if not objects:
        return getattr(row,var)
        
    if len(objects) == 1:
        return getattr(row, objects[0]+var)

    # move from tuple to list to sort
    items = [o for o in objects].sort()
    return getattr(row, '_'.join(objects) + '_' + var)


def getInputs(indir):
    '''
    Given a directory where input files reside, gives back file names (with 
    paths).
    '''

    if indir[-1] == '/':
        fileNames = glob.glob(indir + '*.root')
    else:
        fileNames = glob.glob(indir + '/*.root')

    return fileNames







