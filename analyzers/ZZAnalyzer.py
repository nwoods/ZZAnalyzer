'''

ZZ->4l analyzer. Takes an FSA Ntuple as input, makes a root file 
with a bunch of histograms of interesting quantities as output.
By default, runs on all root files in a folder. I'll probably add
an option to change that later. It keeps the outputs separate.

Author: Nate Woods

'''

import ROOT
import Cutter
import os
from itertools import combinations
import math



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
            "Total",
            "Combinatorics",
            "Trigger",
            "Overlap",
            "Z1ID",
            "Z1Iso",
            "Z1Mass",
            "Z2ID",
            "Z2Iso",
            "Z2Mass",
            "Lepton1Pt",
            "Lepton2Pt",
            "LeptonPairMass",
            "4lMass"
            ]
        
        self.prepareCutSummary()

        self.getHistoDict(self.channels)



    def prepareCutSummary(self):
        '''
        Prepare dictionary with number of events passing each cut for each channel
        '''
        self.cutsPassed = {}
        for channel in self.channels:
            self.cutsPassed[channel] = {}
            for cut in self.cutOrder:
                self.cutsPassed[channel][cut] = 0


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
                if self.cutsPassed[channel]['Total'] == self.maxEvents:
                    print "%s: Reached %d %s events, ending"%(self.sample, self.maxEvents, channel)
                    break

                # Report progress every 5000 events
                if self.cutsPassed[channel]['Total'] % 5000 == 0:
                    print "%s: Processing %s event %d"%(self.sample, channel, self.cutsPassed[channel]["Total"])
                
                # Always pass "Total"
                self.passCut(row, channel, "Total")

                # Ignore wrong version of event
                if self.cutsPassed[channel]['Total'] in wrongRows:
                    continue
                self.passCut(row, channel, "Combinatorics")
                    
                objects = self.getOSSF(row, channel, objectTemplate)

                # Pass HLT
                if not self.cuts.doCut(row, 'Trigger'):
                    self.preCut(row, channel, 'Trigger')
                    continue
                self.passCut(row, channel, "Trigger")

                # Pass overlap cuts
                self.preCut(row, channel, 'Overlap')
                if not self.checkOverlaps(row, objects):
                    continue
                self.passCut(row, channel, "Overlap")

                ### Make sure there's one good Z candidate
                # Make sure we have one potential Z candidate (pair of OSSF lepton candidates)
                self.preCut(row, channel, 'Z1ID')
                if len(objects) < 2:
                    continue

                # Z1 ID cuts
                if not self.cutOnAll(row, 'ID', objects[:2]):
                    continue
                
                # Z1 selection cuts
                if not self.cutOnAll(row, 'Selection', objects[:2]):
                    continue
                self.passCut(row, channel, "Z1ID")

                # Z1 isolation cuts
                self.preCut(row,channel, "Z1Iso")
                if not self.cutOnAll(row, 'Iso', objects[:2]):
                    continue
                self.passCut(row, channel, "Z1Iso")

                # Make sure it's a good Z
                self.preCut(row, channel, 'Z1Mass')
                if not self.cuts.doCut(row, 'Z1Mass', objects[0], objects[1]):
                    continue
                self.passCut(row, channel, "Z1Mass")
                
                ### Make sure we have an additional good Z candidate
                # second pair of OSSF lepton candidates
                self.preCut(row, channel, 'Z2ID')
                if len(objects) < 4:
                    continue

                # Z2 ID cuts
                if not self.cutOnAll(row, 'ID', objects[2:]):
                    continue
                
                # Z2 selection cuts
                if not self.cutOnAll(row, 'Selection', objects[2:]):
                    continue
                self.passCut(row, channel, "Z2ID")

                # Z2 isolation cuts
                self.preCut(row, channel, "Z2Iso")
                if not self.cutOnAll(row, 'Iso', objects[2:]):
                    continue
                self.passCut(row, channel, "Z2Iso")

                # Make sure it's a good-ish Z
                self.preCut(row, channel, 'Z2Mass')
                if not self.cuts.doCut(row, 'Z2Mass', objects[2], objects[3]):
                    continue
                self.passCut(row, channel, "Z2Mass")
                
                # Make sure at least one lepton has pt>20
                self.preCut(row, channel, 'Lepton1Pt')
                if not any(self.cuts.doCut(row, 'Lepton1Pt', obj) for obj in objects):
                    continue
                self.passCut(row, channel, "Lepton1Pt")

                # Make sure another has pt>10
                self.preCut(row, channel, 'Lepton2Pt')
                if not any(self.cuts.doCut(row, 'Lepton2Pt', pair[0]) and self.cuts.doCut(row, 'Lepton2Pt', pair[1]) \
                           for pair in combinations(objects,2)):
                    continue
                self.passCut(row, channel, "Lepton2Pt")

                # All opposite-sign pairs of leptons must have an invariant mass > 4GeV (regardless of flavor)
                self.preCut(row, channel, 'LeptonPairMass')
                if not all(getVar(row, 'SS', pair[0], pair[1]) or self.cuts.doCut(row, 'LeptonPairMass', pair[0], pair[1]) \
                           for pair in combinations(objectTemplate, 2)): # use template to maintain alphanumeric order
                    continue
                self.passCut(row, channel, "LeptonPairMass")

                # 4l inv. mass window
                self.preCut(row, channel, '4lMass')
                if not self.cuts.doCut(row, '4lMass'):
                    continue
                self.passCut(row, channel, "4lMass")

                self.fillHistos(row, channel, objects)
            else:
                print "%s: Done with %s (%d events)"%(self.sample, channel, self.cutsPassed[channel]['Total'])
                
        print "%s: Done with all channels, saving results"%self.sample

        self.saveAllHistos()

        self.cutReport()
                

    def passCut(self, row, channel, cut):
        '''
        Function to run after cut is passed. Here, just updates the cut summary. In
        derived classes, may be overwritten to do other things like fill cut flow
        histograms.
        '''
        self.cutsPassed[channel][cut] += 1
        
        
    def preCut(self, row, channel, cut):
        '''
        Here, does nothing. In derived classes, may be used to do things like make 
        control plots.
        '''
        pass


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
       
 
    def getOSSF(self, row, channel, objects=[]):
        '''
        Will return a list of same flavor, opposite sign leptons ordered by closeness
        to nominal Z mass. Will only return as many pairs as are in the row, so length<4
        means there are not two Z candidates in the event. Assumes 4 objects which are all
        leptons. If objects list is given, uses that. Otherwise figures it out from channel.

        Takes advantage of the fact that FSA ntuples place best Z candidate first in
        eeee and mmmm cases.
        '''
        ossfs = []
        if not objects:
            objects = self.MapObjects(channel)
        
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
        
        The (ROOT internal) name of the histo will the the sensible obvious thing, with ":~:"+channel
        appended to the end so that ROOT doesn't get mad (ROOT TSMASH!). The weird ":~:" is so that we
        can easily remove the channel before we put it into a file.
        '''
        self.histos = {}

        for channel in channels+['Total']:
            self.histos[channel] = {}

            if channel != 'Total':
                objects = self.mapObjects(channel)
                for obj in objects:
                    self.histos[channel][obj+'Pt'] = ROOT.TH1F(obj+'Pt'+":~:"+channel, obj+'Pt', 240, 0., 120.)
                    self.histos[channel][obj+'Eta'] = ROOT.TH1F(obj+'Eta'+":~:"+channel, obj+' Eta', 100, -5., 5.)
                    self.histos[channel][obj+'Phi'] = ROOT.TH1F(obj+'Phi'+":~:"+channel, obj+' Phi', 64, -math.pi, math.pi)
            for obj in ['Z1', 'Z2']:
                self.histos[channel][obj+'Pt'] = ROOT.TH1F(obj+'Pt'+":~:"+channel, obj+' Pt', 240, 0., 120.)
                self.histos[channel][obj+'Eta'] = ROOT.TH1F(obj+'Eta'+":~:"+channel, obj+' Eta', 100, -5., 5.)
                self.histos[channel][obj+'Phi'] = ROOT.TH1F(obj+'Phi'+":~:"+channel, obj+' Phi', 64, -math.pi, math.pi)
                self.histos[channel][obj+'Mass'] = ROOT.TH1F(obj+'Mass'+":~:"+channel, obj+' Mass', 260, 0., 130.)
            self.histos[channel]['4lPt'] = ROOT.TH1F('4lPt'+":~:"+channel, '4l Pt', 200, 0., 400.)
            self.histos[channel]['4lEta'] = ROOT.TH1F('4lEta'+":~:"+channel, '4l Eta', 100, -5., 5.)
            self.histos[channel]['4lPhi'] = ROOT.TH1F('4lPhi'+":~:"+channel, '4l Phi', 64, -math.pi, math.pi)
            self.histos[channel]['4lMass'] = ROOT.TH1F('4lMass'+":~:"+channel, '4l Mass', 600, 0., 1200.)
            self.histos[channel]['4lMt'] = ROOT.TH1F('4lMt'+":~:"+channel, '4l Mt', 600, 0., 1200.)


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
        
        # Single objects
        for obj in objects:
            self.histos[channel][obj+'Pt'].Fill(getVar(row, 'Pt', obj))
            self.histos[channel][obj+'Eta'].Fill(getVar(row, 'Eta', obj))
            self.histos[channel][obj+'Phi'].Fill(getVar(row, 'Phi', obj))

        for title in [channel, 'Total']:
            
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
            for foo, hist in hDict.iteritems():
                # Change name to be consistent
                name = hist.GetName()
                name = name.split(":~:")[0]
                hist.SetName(name)
                dirs[-1].Append(hist)

        for dir in dirs:
            dir.Write()
        f.Close()


    def cutOnAll(self, row, var, objects):
        '''
        Loop over all objects and see if they pass a single-particle
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
            if not self.cuts.doCut(row, 'Overlap', *pair):
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



################################################################
####    To do a small test, jut run python ZZAnalyzer.py    ####
################################################################

if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description='Running ZZAnalyzer directly just does a little test.')
    parser.add_argument("channel", nargs='?', default='zz', type=str, help='Channel(s) to test.')
    parser.add_argument("cutset", nargs='?', default='FullSpectrum2012', type=str, help='Cut set to test.')
    parser.add_argument("infile", nargs='?', 
                        default='%s/../ntuples/ZZTo4L_Tune4C_13TeV-powheg-pythia8_Spring14miniaod_PU20bx25.root'%os.environ["zza"],
                        type=str, help='Single file to test on. No wildcards.')
    parser.add_argument("outfile", nargs='?', default='ZZTest.root', type=str, help='Test output file name.')
    parser.add_argument("nEvents", nargs='?', type=int, default=100, help="Number of test events.")
    args = parser.parse_args()

    a = ZZAnalyzer(args.channel, args.cutset, args.infile, args.outfile, args.nEvents)
    print "TESTING ZZAnalyzer"
    a.analyze()
    print "TEST COMPLETE"




