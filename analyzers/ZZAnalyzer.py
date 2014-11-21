'''

ZZ->4l analyzer. Takes an FSA Ntuple as input, makes a root file 
with a bunch of histograms of interesting quantities and a cut flow 
text file.

Author: Nate Woods

'''

import ROOT
import imp
import os
from itertools import combinations
import math
from ZZMetadata import sampleInfo
from ZZHelpers import *


Z_MASS = 91.1876

assert os.environ["zza"], "Run setup.sh before running analysis"

class ZZAnalyzer(object):
    def __init__(self, channels, cutSet, infile, outfile='./results/output.root', maxEvents=float("inf"), intLumi=10000):
        '''
        Channels:    list of strings or single string in the format (e.g.) eemm for 
                         a 2e2mu final state. '4l', 'zz' and 'ZZ' turn into ['eeee' 'eemm' 'mmmm']
        cutSet:      string with the name of the cut template to use
        infile:      string of an input file name, with path
        outfile:     string of an output file name, with path
        maxEvents:   stop after this many events processed
        intLumi:     in output text file, report how many events we would expect for this integrated luminosity
        '''
        # cheat, for now
        self.zPtVar = 'PtFsr'
        self.zEtaVar = 'EtaFsr'
        self.zPhiVar = 'PhiFsr'
        self.zMassVar = 'MassFsr'
        
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
        cutpath = os.environ["zza"]+"/ZZUtils/templates"
        cutf, cutfName, cutdesc = imp.find_module(cutSet, [cutpath])
        assert cutf, 'Set of cuts %s does not exist in %s'%(cutSet,cutpath)
        cutmod = imp.load_module(cutSet, cutf, cutfName, cutdesc)
        cutclass = getattr(cutmod, cutSet)

        self.cuts = cutclass()

        self.cutOrder = self.cuts.getCutList()

        self.inFile = infile

        self.sample = self.inFile.split('/')[-1].replace('.root','')
        
        self.outFile = outfile

        self.maxEvents = maxEvents
        # if we don't use all the events, we need to know how many we would have done in the whole thing
        if self.maxEvents < float('inf'):
            self.ntupleSize = {}

        self.prepareCutSummary()

        self.getHistoDict(self.channels)

        self.intLumi = intLumi


    def prepareCutSummary(self):
        '''
        Prepare dictionary with number of events passing each cut for each channel.
        Adds first item for number of rows before the combinatorics cut.
        '''
        self.cutsPassed = {}
        for channel in self.channels:
            self.cutsPassed[channel] = {}
            for cut in ['TotalRows']+self.cutOrder:
                self.cutsPassed[channel][cut] = 0


    def analyze(self):
        '''
        For a given file, do the whole analysis and output the results to 
        self.outFile
        '''

        inFile = ROOT.TFile.Open(self.inFile)
        assert bool(inFile), 'No file %s'%self.inFile

        for channel in self.channels:
            ntuple = inFile.Get(channel+'/final/Ntuple')

            if self.maxEvents < float('inf'):
                self.ntupleSize[channel] = ntuple.GetEntries()

            objectTemplate = self.mapObjects(channel)
            objects = objectTemplate
            needReorder = channel[0][0] != channel[-1][0]

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
                
                # Always pass "TotalRows" because it's always a new row
                self.passCut(row, channel, "TotalRows")

                # Ignore wrong version of event
                if self.cutsPassed[channel]['TotalRows'] in wrongRows:
                    continue

                if needReorder:
                    objects = self.orderLeptons(row, channel, objectTemplate)

                evPass = True
                for cut in self.cutOrder:
                    self.preCut(row, channel, cut)
                    if self.cuts.analysisCut(row, cut, *objects):
                        self.passCut(row, channel, cut)
                    else:
                        evPass = False
                        break

                if evPass:
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
        nEvent = 0
        redundantRows = set()

        prevRun = -1
        prevLumi = -1
        prevEvt = -1
        prevDZ = 999.
        prevPtSum = -999.
        prevRow = -1
        
        objectTemplate = self.mapObjects(channel)
        objects = objectTemplate
        needReorder = channel[0][0] != channel[-1][0]

        for row in ntuple:
            if nEvent == self.maxEvents:
                print "%s: Found redundant rows for %d %s events, ending"%(self.sample, self.maxEvents, channel)
                break

            nRow += 1
            if nRow % 5000 == 0:
                print "%s: Finding redundant rows %s row %d"%(self.sample, channel, self.cutsPassed[channel]["Total"])

            if needReorder:
                objects = self.orderLeptons(row, channel, objectTemplate)

            # Keep track of events within this function by run, lumi block, and event number
            run =  evVar(row, 'run')
            lumi = evVar(row, 'lumi')
            evt =  evVar(row,'evt')
            sameEvent = (evt == prevEvt and lumi == prevLumi and run == prevRun)

            if not sameEvent:
                nEvent += 1

            # The best row for the event is actually the best one *that passes ID cuts*
            # so we have to treat a row that fails them as automatically bad. But, we can
            # only do this when the row is actually a duplicate, to keep our cut stats accurate.
            allGood = True
            for lepts in [[objects[0],objects[1]],[objects[2],objects[3]]]:
                if not self.cuts.doCut(row, "GoodZ", *lepts):
                    allGood = False
                    break
                if not self.cuts.doCut(row, "ZIso", *lepts):
                    allGood = False
                    break

            if not allGood:
                if sameEvent:
                    redundantRows.add(nRow)
                else:
                    prevRun = run
                    prevLumi = lumi
                    prevEvt = evt
                    prevDZ = 999.
                    prevPtSum = -999.
                    prevRow = nRow
                continue
            
            dZ = self.zCompatibility(row, objects[0], objects[1])
            ptSum = objVar(row, 'Pt', objects[2]) + objVar(row, 'Pt', objects[3])

            # if this doesn't seem to be a duplicate event, we don't need to do anything but store
            # its info in case it's the first of several
            if not sameEvent:
                prevRun = run
                prevLumi = lumi
                prevEvt = evt
                prevDZ = dZ
                prevPtSum = ptSum
                prevRow = nRow
                continue
            else:
                if dZ < prevDZ:
                    redundantRows.add(prevRow)
                    prevRun = run
                    prevLumi = lumi
                    prevEvt = evt
                    prevDZ = dZ
                    prevPtSum = ptSum
                    prevRow = nRow
                elif dZ == prevDZ:
                    if ptSum > prevPtSum:
                        redundantRows.add(prevRow)
                        prevRun = run
                        prevLumi = lumi
                        prevEvt = evt
                        prevDZ = dZ
                        prevPtSum = ptSum
                        prevRow = nRow
                    else:
                        redundantRows.add(nRow)
                else:
                    redundantRows.add(nRow)
                    
        return redundantRows
       
 
    def orderLeptons(self, row, channel, objects):
        '''
        Put best (closest to nominal mass) Z candidate first. 
        FSA does this automatically for 4e and 4mu cases.
        Assumes 4 leptons, with (l1,l2) and (l3,l4) same-flavor pairs;
        will have to be overloaded for other final states.
        '''
        if channel == 'eeee' or channel == 'mmmm':
            return objects

        dM1 = self.zCompatibility(row,objects[0],objects[1])
        dM2 = self.zCompatibility(row,objects[2],objects[3])
        
        if dM1 > dM2:
            return objects[2:] + objects[:2]
        return objects


    def zCompatibility(self, row, ob1, ob2):
        '''
        Absolute distance from Z mass. 1000 if same sign.
        '''
        if nObjVar(row, 'SS', ob1, ob2):
            return 1000
        return abs(nObjVar(row, self.zMassVar, ob1, ob2) - Z_MASS)


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
        if objects[0][0] == objects[1][0] and not nObjVar(row, 'SS', objects[0], objects[1]):
            ossfs.extend(objects[:2])
        if objects[2][0] == objects[3][0] and not nObjVar(row, 'SS', objects[2], objects[3]):
            ossfs.extend(objects[2:])
            
        # If there's 0 or 1 Z candidate, we don't need to worry about order
        if len(ossfs) < 4:
            return ossfs

        # if this is 2e2mu, we might need to flip if the 2mu Z was better
        if channel == 'eemm':
            mass1 = nObjVar(row, self.zMassVar, ossfs[0], ossfs[1])
            mass2 = nObjVar(row, self.zMassVar, ossfs[2], ossfs[3])
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
        # Single objects
        for obj in objects:
            self.histos[channel][obj+'Pt'].Fill(objVar(row, 'Pt', obj))
            self.histos[channel][obj+'Eta'].Fill(objVar(row, 'Eta', obj))
            self.histos[channel][obj+'Phi'].Fill(objVar(row, 'Phi', obj))
            
        # Composite objects
        Z1Mom = ROOT.TLorentzVector()
        Z2Mom = ROOT.TLorentzVector()
        Z1Mom.SetPtEtaPhiM(nObjVar(row, self.zPtVar, objects[0], objects[1]),
                           nObjVar(row, self.zEtaVar, objects[0], objects[1]),
                           nObjVar(row, self.zPhiVar, objects[0], objects[1]),
                           nObjVar(row, self.zMassVar, objects[0], objects[1])
        )
        Z2Mom.SetPtEtaPhiM(nObjVar(row, self.zPtVar, objects[2], objects[3]),
                           nObjVar(row, self.zEtaVar, objects[2], objects[3]),
                           nObjVar(row, self.zPhiVar, objects[2], objects[3]),
                           nObjVar(row, self.zMassVar, objects[2], objects[3])
        )
        totalMom = Z1Mom + Z2Mom
                   
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


    def cutReport(self):
        '''
        Save a text file with cut information. 
        Same name as outfile but .txt instead of .root.
        '''
        totals = {}
        expectedTotals = {}
        # factor to translate n events in MC to m events in data
        for cut in ['TotalRows']+self.cutOrder:
            totals[cut] = 0
            expectedTotals[cut] = 0.

        with open(self.outFile.replace('.root','.txt'), 'w') as f:
            for channel in self.channels:
                if self.cutsPassed[channel]['Total'] != self.maxEvents:
                    expectedFactor = sampleInfo[self.sample]['xsec'] * self.intLumi / sampleInfo[self.sample]['n']
                else:
                    # estimate fraction that would have passed to be nPassedTot/nEvents ~ nPassed * nRowsTot / (nRows * nEvents)
                    # must make this approximation because we don't know what fraction of the sample was cut out
                    #     by the ntuplizer
                    expectedFactor = sampleInfo[self.sample]['xsec'] * self.intLumi * \
                                     self.ntupleSize[channel] / \
                                     (self.cutsPassed[channel]['TotalRows'] * sampleInfo[self.sample]['n'])

                f.write("\n%-32s in %0.0f pb^-1\n"%(channel+':',self.intLumi))
                for cut in ['TotalRows']+self.cutOrder:
                    expected = self.cutsPassed[channel][cut] * expectedFactor
                    f.write("%16s : %-9d :      %0.2f\n"%(cut, self.cutsPassed[channel][cut], expected))
                    totals[cut] += self.cutsPassed[channel][cut]
                    expectedTotals[cut] += expected
                                                     
            f.write("\n%-32s in %0.0f pb^-1\n"%('Total:',self.intLumi))
            for cut in ['TotalRows']+self.cutOrder:
                f.write("%16s : %-9d :      %0.2f\n"%(cut, totals[cut], expectedTotals[cut]))
    



################################################################
####    To do a small test, jut run python ZZAnalyzer.py    ####
################################################################

if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description='Running ZZAnalyzer directly just does a little test.')
    parser.add_argument("channel", nargs='?', default='zz', type=str, help='Channel(s) to test.')
    parser.add_argument("cutset", nargs='?', default='FullSpectrumFSR', type=str, help='Cut set to test.')
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




