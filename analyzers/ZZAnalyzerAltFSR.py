'''

ZZ->4l analyzer. Takes an FSA Ntuple as input, makes a root file 
with a bunch of histograms of interesting quantities and a cut flow 
text file.

Author: Nate Woods

'''

import os

from ZZAnalyzer import ZZAnalyzer
from FullSpectrum_DREtFSR import altFSR_cutters


class ZZAnalyzerAltFSR(ZZAnalyzer):
    def __init__(self, *args, **kwargs):
        try:
            super(ZZAnalyzerAltFSR, self).__init__(*args, **kwargs)
        except Exception as e:
            print e 
            raise

    def getCutClass(self, cutSet):
        return altFSR_cutters[cutSet]

    def analyze(self):
        try:
            super(ZZAnalyzerAltFSR, self).analyze()
        except Exception as e:
            print e
            raise

################################################################
####    To do a small test, jut run python ZZAnalyzer.py    ####
################################################################

if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description='Running ZZAnalyzerAltFSR directly just does a little test.')
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

    a = ZZAnalyzerAltFSR(args.channel, args.cutset, args.infile, args.outfile, args.resultType, args.nEvents, 1000, args.cleanRows)
    print "TESTING ZZAnalyzer"
    a.analyze()
    print "TEST COMPLETE"




