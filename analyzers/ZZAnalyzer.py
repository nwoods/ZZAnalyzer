'''

ZZ->4l analyzer. Takes an FSA Ntuple as input, makes a root file 
with a bunch of histograms of interesting quantities and a cut flow 
text file.

Author: Nate Woods

'''

# no silly ROOT messages
import logging
from rootpy import log as rlog; rlog = rlog['/ZZAnalyzer']
logging.basicConfig(level=logging.WARNING)
rlog["/ROOT.TUnixSystem.SetDisplay"].setLevel(rlog.ERROR)

from rootpy import ROOT
from rootpy.io import root_open
from rootpy.plotting import Hist
import imp
import os
from itertools import combinations
import math
from ZZMetadata import sampleInfo
from ZZHelpers import * # evVar, objVar, nObjVar


Z_MASS = 91.1876

assert os.environ["zza"], "Run setup.sh before running analysis"

class ZZAnalyzer(object):
    def __init__(self, channels, cutSet, inFile, outfile='./results/output.root', 
                 resultType = "ZZFinalHists", maxEvents=float("inf"), intLumi=10000, rowCleaner=''):
        '''
        Channels:    list of strings or single string in the format (e.g.) eemm for 
                         a 2e2mu final state. '4l', 'zz' and 'ZZ' turn into ['eeee' 'eemm' 'mmmm']
        cutSet:      string with the name of the cut template to use
        infile:      string of an input file name, with path
        outfile:     string of an output file name, with path
        maxEvents:   stop after this many events processed
        intLumi:     in output text file, report how many events we would expect for this integrated luminosity
        rowCleaner:  name of a module to clean out redundant rows. If an empty 
                         string (or other False boolean), no cleaning is performed.
        '''
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
        cutpath = os.environ["zza"]+"/ZZUtils/cutTemplates"
        cutf, cutfName, cutdesc = imp.find_module(cutSet, [cutpath])
        assert cutf, 'Set of cuts %s does not exist in %s'%(cutSet,cutpath)
        cutmod = imp.load_module(cutSet, cutf, cutfName, cutdesc)
        cutclass = getattr(cutmod, cutSet)

        self.cuts = cutclass()

        self.outFile = outfile

        self.cutOrder = self.cuts.getCutList()

        self.sample = inFile.split('/')[-1].replace('.root','')        
        self.inFile = root_open(inFile)
        assert bool(inFile), 'No file %s'%self.inFile

        self.maxEvents = maxEvents
        # if we don't use all the events, we need to know how many we would have done in the whole thing
        if self.maxEvents < float('inf'):
            self.ntupleSize = {}

        self.ntuples = {}
        for channel in self.channels:
            self.ntuples[channel] = self.inFile.Get(channel+'/final/Ntuple')

            if self.maxEvents < float('inf'):
                self.ntupleSize[channel] = self.ntuples[channel].GetEntries()

        self.resultType = resultType
        resultpath = os.environ["zza"]+"/ZZUtils/resultTemplates"
        resf, resfName, resdesc = imp.find_module(resultType, [resultpath])
        assert resf, 'Result template %s does not exist in %s'%(resultType,resultpath)
        resmod = imp.load_module(resultType, resf, resfName, resdesc)
        resultclass = getattr(resmod, resultType)

        self.results = resultclass(self.outFile, self.channels, self.ntuples)

        self.prepareCutSummary()

        self.intLumi = intLumi

        self.cleanRows = bool(rowCleaner)
        if self.cleanRows:
            cleanerpath = os.environ["zza"]+"/ZZUtils/rowCleaners"
            cleanerf, cleanerfName, cleanerdesc = imp.find_module(rowCleaner, [cleanerpath])
            assert cleanerf, 'Row cleaner %s does not exist in %s'%(rowCleaner, cleanerpath)
            cleanermod = imp.load_module(rowCleaner, cleanerf, cleanerfName, cleanerdesc)
            self.CleanerClass = getattr(cleanermod, rowCleaner)



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
        
            objectTemplate = self.mapObjects(channel)
            objects = objectTemplate
            needReorder = self.cuts.needReorder(channel)

            if cleanAfter:
                rowCleaner.setChannel(channel)
                self.cutsPassed[channel]["SelectBest"] = 0

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
                        self.results.saveRow(row, channel, nested=True)
            else:
                print "%s: Done with %s (%d rows)"%(self.sample, channel, iRow+1)

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
                        self.results.saveRow(row, channel, nested=True)
                        
                    
                
        print "%s: Done with all channels, saving results as %s"%(self.sample, self.outFile)

        self.inFile.close()

        self.results.save()

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
####    To do a small test, jut run python ZZAnalyzer.py    ####
################################################################

if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description='Running ZZAnalyzer directly just does a little test.')
    parser.add_argument("channel", nargs='?', default='zz', type=str, help='Channel(s) to test.')
    parser.add_argument("cutset", nargs='?', default='FullSpectrumFSR', type=str, help='Cut set to test.')
    parser.add_argument("infile", nargs='?', 
                        default='%s/../ntuples/ZZTo4L_Tune4C_13TeV-powheg-pythia8_PHYS14DR_PU20bx25.root'%os.environ["zza"],
                        type=str, help='Single file to test on. No wildcards.')
    parser.add_argument("outfile", nargs='?', default='ZZTest.root', type=str, help='Test output file name.')
    parser.add_argument("resultType", nargs='?', default='ZZFinalHists', type=str, help='Format of output file')
    parser.add_argument("nEvents", nargs='?', type=int, default=100, help="Number of test events.")
    parser.add_argument("--cleanRows", nargs='?', type=str, default='',
                        help="Name of module to clean extra rows from each event. Without this option, no cleaning is performed.")
    args = parser.parse_args()

    a = ZZAnalyzer(args.channel, args.cutset, args.infile, args.outfile, args.resultType, args.nEvents, 1000, args.cleanRows)
    print "TESTING ZZAnalyzer"
    a.analyze()
    print "TEST COMPLETE"




