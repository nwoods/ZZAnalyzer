'''

ZZ->4l analyzer. Takes an FSA Ntuple as input, makes a root file
with a bunch of histograms of interesting quantities and a cut flow
text file.

Author: Nate Woods

'''

# no silly ROOT messages
import logging
from rootpy import log as rlog; rlog = rlog['/Analyzer']
logging.basicConfig(level=logging.WARNING)
rlog["/ROOT.TUnixSystem.SetDisplay"].setLevel(rlog.ERROR)
rlog["/ROOT.TTree.SetBranchStatus"].setLevel(rlog.CRITICAL)

from rootpy import ROOT
from rootpy.io import root_open
from rootpy.plotting import Hist
from rootpy.io.file import DoesNotExist
from rootpy import ROOTError

import os
from itertools import combinations
import math

from ZZAnalyzer.metadata import sampleInfo
from ZZAnalyzer.utils.helpers import * # evVar, objVar, nObjVar, parseChannels, mapObjects, Z_MASS
from ZZAnalyzer.cuts import getCutClass
from ZZAnalyzer.results import NtupleCopier
from ZZAnalyzer.cleaning import getCleanerClass

assert os.environ["zza"], "Run setup.sh before running analysis"

class Analyzer(object):
    def __init__(self, channels, baseCutSet, inFile, outfile='./results/output.root',
                 maxEvents=float("inf"), intLumi=10000, rowCleaner='',
                 cutModifiers=[], ntupleDir='ntuple'):
        '''
        channels:    list of strings or single string in the format (e.g.) eemm for
                         a 2e2mu final state. '4l', 'zz' and 'ZZ' turn into ['eeee' 'eemm' 'mmmm']
        cutSet:      string with the name of the cut template to use
        infile:      string of an input file name, with path
        outfile:     string of an output file name, with path
        maxEvents:   stop after this many events processed
        intLumi:     in output text file, report how many events we would expect for this integrated luminosity
        rowCleaner:  name of a module to clean out redundant rows. If an empty
                         string (or other False boolean), no cleaning is performed.
        '''
        self.cutSet = [baseCutSet]+cutModifiers
        CutClass = getCutClass(baseCutSet, *cutModifiers)

        self.cuts = CutClass()

        self.outFile = outfile

        self.cutOrder = self.cuts.getCutList()

        self.sample = inFile.split('/')[-1].replace('.root','')
        self.inFile = root_open(inFile)
        assert bool(inFile), 'No file %s'%self.inFile

        self.maxEvents = maxEvents
        # if we don't use all the events, we need to know how many we would have done in the whole thing
        if self.maxEvents < float('inf'):
            self.ntupleSize = {}

        self.channels = parseChannels(channels)

        self.ntuples = {}
        for channel in parseChannels(channels):
            try:
                nt = self.inFile.Get('/'.join([channel,ntupleDir]))
                # if not nt.GetEntries():
                #     raise DoesNotExist('')
                self.ntuples[channel] = nt
                nt.create_buffer()
            except DoesNotExist:
                print "Ntuple for channel %s is empty or not found! Skipping."%channel
                self.channels.remove(channel)
                continue

            if self.maxEvents < float('inf'):
                self.ntupleSize[channel] = self.ntuples[channel].GetEntries()

        self.results = NtupleCopier(self.outFile, **self.ntuples)

        self.prepareCutSummary()

        self.intLumi = intLumi

        self.cleanRows = bool(rowCleaner)
        if self.cleanRows:
            self.CleanerClass = getCleanerClass(rowCleaner)



    def prepareCutSummary(self):
        '''
        Prepare dictionary with number of events passing each cut for each channel.
        If redundant row cleaning is done, an extra item will be added later (not here)
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
        if self.cleanRows:
            # For events with more than 4 leptons, FSA Ntuples just have one
            #     row for each possible combination of objects. We have to know
            #     which one is the right one. Can do this before or after other cuts
            rowCleaner = self.CleanerClass(self.cuts)
            cleanAfter = rowCleaner.cleanAfter()

            if not cleanAfter:
                for channel in self.channels:
                    self.cutsPassed[channel]["TotalRows"] = 0 # hold number of rows pre-cleaning
                    rowCleaner.setChannel(channel)
                    for iRow, row in enumerate(self.ntuples[channel]):
                        if iRow == self.maxEvents:
                            break
                        if (iRow % 5000) == 0:
                            print "%s: Finding redundant rows for %s row %d"%(self.sample, channel, iRow)
                        rowCleaner.bookRow(row, iRow)
                    rowCleaner.finalize()
        else:
            cleanAfter = False


        for channel in self.channels:

            objectTemplate = mapObjects(channel)
            objects = objectTemplate
            needReorder = self.cuts.needReorder(channel)

            if cleanAfter:
                rowCleaner.setChannel(channel)
                self.cutsPassed[channel]["SelectBest"] = 0

                self.ntuples[channel].SetBranchStatus('*', 0)
                for branch in self.ntuples[channel].iterbranchnames():
                    for pattern in self.cuts.branchesNeeded:
                        if pattern.match(branch):
                            self.ntuples[channel].SetBranchStatus(branch, 1)
                            break


            iRow = -1 # in case of empty ntuple
            # Loop through and do the cuts
            for iRow, row in enumerate(self.ntuples[channel]):
                # If we've hit maxEvents, we're done
                if iRow == self.maxEvents:
                    print "%s: Reached %d %s rows, ending"%(self.sample, self.maxEvents, channel)
                    break

                if self.cleanRows:
                    if not cleanAfter:
                        # Always pass "TotalRows" because it's always a new row
                        self.passCut(row, channel, "TotalRows")
                        # Ignore wrong version of event (if we're cleaning now)
                        if rowCleaner.isRedundant(row, channel, iRow):
                            continue

                # Report progress every 5000 rows
                if iRow % 5000 == 0:
                    print "%s: Processing %s row %d"%(self.sample, channel, iRow)

                if needReorder:
                    objects = self.cuts.orderLeptons(row, channel, objectTemplate)

                evPass = True
                for cut in self.cutOrder:
                    self.preCut(row, channel, cut)
                    if self.cuts.analysisCut(row, cut, *objects):
                        self.passCut(row, channel, cut)
                    else:
                        evPass = False
                        break

                if evPass:
                    if cleanAfter: # Don't save yet, still might get cleaned
                        rowCleaner.bookRow(row, iRow)
                    else:
                        self.results.saveRow(row, channel)
            else:
                print "%s: Done with %s (%d rows)"%(self.sample, channel, iRow+1)

            if cleanAfter:
                self.ntuples[channel].SetBranchStatus('*', 1)

        if cleanAfter:
            rowCleaner.finalize()
            for channel in self.channels:
                for iRow, row in enumerate(self.ntuples[channel]):
                    if iRow == self.maxEvents:
                        break
                    if rowCleaner.isRedundant(row, channel, iRow):
                        continue
                    else:
                        self.passCut(row, channel, "SelectBest")
                        self.results.saveRow(row, channel)



        print "%s: Done with all channels, saving results as %s"%(self.sample, self.outFile)

        self.results.save()

        self.inFile.close()

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


    def getOSSF(self, row, channel, objects=[]):
        '''
        Will return a list of same flavor, opposite sign leptons ordered by closeness
        to nominal Z mass. Will only return as many pairs as are in the row, so length<4
        means there are not two Z candidates in the event. Assumes 4 objects which are all
        leptons. If objects list is given, uses that. Otherwise figures it out from channel.

        Takes advantage of the fact that FSA ntuples place best Z candidate first in
        eeee and mmmm cases.
        '''
        if not objects:
            objects = mapObjects(channel)

        if len(objects) != 4:
            return []

        ossfs = []
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


    def cutReport(self):
        '''
        Save a text file with cut information.
        Same name as outfile but .txt instead of .root.
        '''
        totals = {}
#         expectedTotals = {}
        # factor to translate n events in MC to m events in data
        for cut in self.cutOrder:
            totals[cut] = 0
#             expectedTotals[cut] = 0.

        with open(self.outFile.replace('.root','.txt'), 'w') as f:
            for channel in self.channels:
                for cleanerCut in ["TotalRows", "SelectBest"]:
                    if cleanerCut in self.cutsPassed[channel] and cleanerCut not in totals:
                        totals[cleanerCut] = 0
#                         expectedTotals[cleanerCut] = 0
                        break
#                 if self.cutsPassed[channel]['Total'] != self.maxEvents:
#                     expectedFactor = sampleInfo[self.sample]['xsec'] * self.intLumi / sampleInfo[self.sample]['n']
#                 else:
#                     # estimate fraction that would have passed to be nPassedTot/nEvents ~ nPassed * nRowsTot / (nRows * nEvents)
#                     # must make this approximation because we don't know what fraction of the sample was cut out
#                     #     by the ntuplizer
#                     expectedFactor = sampleInfo[self.sample]['xsec'] * self.intLumi * \
#                                      self.ntupleSize[channel] / \
#                                      (self.cutsPassed[channel]['TotalRows'] * sampleInfo[self.sample]['n'])

                f.write("\n%-32s\n"%channel) # in %0.0f pb^-1\n"%(channel+':',self.intLumi))
                if "TotalRows" in self.cutsPassed[channel]:
                    listOfCuts = ['TotalRows']+self.cutOrder
                elif "SelectBest" in self.cutsPassed[channel]:
                    listOfCuts = self.cutOrder+["SelectBest"]
                else:
                    listOfCuts = self.cutOrder
                for cut in listOfCuts:
#                     expected = self.cutsPassed[channel][cut] * expectedFactor
                    f.write("%16s : %-9d\n"%(cut, self.cutsPassed[channel][cut]))
                    # :      %0.2f\n"%(cut, self.cutsPassed[channel][cut], expected))
                    totals[cut] += self.cutsPassed[channel][cut]
#                     expectedTotals[cut] += expected

            if "TotalRows" in self.cutsPassed[channel]:
                listOfCuts = ['TotalRows']+self.cutOrder
            elif "SelectBest" in self.cutsPassed[channel]:
                listOfCuts = self.cutOrder+["SelectBest"]
            else:
                listOfCuts = self.cutOrder
            f.write("Total\n")
#             f.write("\n%-32s in %0.0f pb^-1\n"%('Total:',self.intLumi))
            for cut in listOfCuts:
                f.write("%16s : %-9d\n"%(cut, totals[cut])) # :      %0.2f\n"%(cut, totals[cut], expectedTotals[cut]))




################################################################
####    To do a small test, jut run python Analyzer.py    ####
################################################################

if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description='Running Analyzer directly just does a little test.')
    parser.add_argument("channel", nargs='?', default='zz', type=str, help='Channel(s) to test.')
    parser.add_argument("cutset", nargs='?', default='BaseCuts2016', type=str, help='Base cut set to test.')
    parser.add_argument("infile", nargs='?',
                        default='/data/nawoods/ntuples/zzNtuples_mc_26jan2016_0/ZZTo4L_13TeV_powheg_pythia8.root',
                        type=str, help='Single file to test on. No wildcards.')
    parser.add_argument("outfile", nargs='?', default='ZZTest.root', type=str, help='Test output file name.')
    parser.add_argument("nEvents", nargs='?', type=int, default=100, help="Number of test events.")
    parser.add_argument("--cleanRows", nargs='?', type=str, default='',
                        help="Name of module to clean extra rows from each event. Without this option, no cleaning is performed.")
    parser.add_argument("--modifiers", nargs='*', type=str,
                        help="Other cut sets that modify the base cuts.")
    parser.add_argument("--ntupleDir", nargs="?", default='ntuple',
                        type=str,
                        help=("path to the ntuple in the root file, "
                              "relative to the channel. So the "
                              "ntuple will be channel/<this variable>"))
    args = parser.parse_args()

    if args.modifiers:
        mods = args.modifiers
    else:
        mods = []

    a = Analyzer(args.channel, args.cutset, args.infile, args.outfile,
                   args.nEvents, 1000, args.cleanRows,
                   cutModifiers=mods, ntupleDir=args.ntupleDir)

    print "TESTING Analyzer"
    a.analyze()
    print "TEST COMPLETE"




