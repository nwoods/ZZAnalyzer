'''

ZZ->4l cut flows/controls. Takes and FSA Ntuple as input, makes 
a root file with histograms of variables the analysis cuts on
(controls) and selected variables plotted between cuts (cut
flows). 

Author: Nate Woods, U. Wisconsin

'''

from ZZAnalyzer import ZZAnalyzer
import os
from rootpy import ROOT
from rootpy.io import root_open
from rootpy.plotting import Hist
from ZZHelpers import * # evVar, objVar, nObjVar


# Environment must be set up
assert os.environ["zza"], "Run setup.sh before running cut flows"



class ZZCutFlow(ZZAnalyzer):
    def __init__(self, channels, cutSet, infile, outfile='./results/output_cutflow.root', 
                 resultType="ZZCutFlowHists", maxEvents=float("inf"), intLumi=10000, cleanRows=True):

        # Has to happen before super is instantiated
#        self.setupTemplates()

        super(ZZCutFlow, self).__init__(channels, cutSet, infile, outfile, resultType, maxEvents, intLumi, cleanRows)


    def passCut(self, row, channel, cut):
        '''
        Overrides ZZAnalyzer.passCut, to fill cut flow histograms
        '''
        self.cutsPassed[channel][cut] += 1
        for flow in self.results.getFlowList():
            self.results.saveVar(row, channel, flow, cut)
            
    
    def preCut(self, row, channel, cut):
        '''
        Overrides ZZAnalyzer.preCut, to fill cut flow histograms
        Control functions that return iterables are presumed to want all of them
        added to the histogram (i.e. isolation for all 4 leptons). 
        '''
        if cut in self.results.getControls():
            for var in self.results.getControls()[cut]:
                self.results.saveVar(row, channel, 'control', var)






################################################################
####    To do a small test, jut run python ZZCutFlow.py    ####
################################################################

if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description='Running ZZCutFlow directly just does a little test.')
    parser.add_argument("channel", nargs='?', default='zz', type=str, help='Channel(s) to test.')
    parser.add_argument("cutset", nargs='?', default='FullSpectrumFSR', type=str, help='Cut set to test.')
    parser.add_argument("infile", nargs='?', 
                        default='%s/../ntuples/ZZTo4L_Tune4C_13TeV-powheg-pythia8_PHYS14DR_PU20bx25.root'%os.environ["zza"],
                        type=str, help='Single file to test on. No wildcards.')
    parser.add_argument("outfile", nargs='?', default='ZZTest.root', type=str, help='Test output file name.')
    parser.add_argument("resultType", nargs='?', default='ZZCutFlowHists', type=str, help='Output module.')
    parser.add_argument("nEvents", nargs='?', type=int, default=100, help="Number of test events.")
    parser.add_argument("--cleanRows", action="store_true", help="Remove redundant rows for each event.")
    args = parser.parse_args()

    a = ZZCutFlow(args.channel, args.cutset, args.infile, args.outfile, args.resultType, args.nEvents, 1000, args.cleanRows)
    print "TESTING ZZCutFlow"
    a.analyze()
    print "TEST COMPLETE"




    

            
