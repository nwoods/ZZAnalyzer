'''

A ZZAnalyzer that takes a list of events of interest and reports which cuts they failed.
Everything else happens normally.

The list of interesting events should be in the format
run:lumi:event

leading spaces, "<" and ">" are stripped out for use on diff output

Nate Woods, U. Wisconsin

'''


from ZZAnalyzer import ZZAnalyzer
from ZZHelpers import *


class SyncAnalyzer(ZZAnalyzer):
    def __init__(self, channels, cutSet, infile, outfile='./results/output_cutflow.root', 
                 resultType="ZZCutFlowHists", maxEvents=float("inf"), eventFile='failedEvents.txt',
                 intLumi=10000, cleanRows=True):
        super(SyncAnalyzer, self).__init__(channels, cutSet, infile, outfile, resultType, maxEvents, intLumi, cleanRows)
        
        # save last attempted cut of each event of interest (or 999 if it passed), keyed to tuple(run,lumi,evt)
        self.interesting = {}
        with open(eventFile, 'r') as f:
            for line in f:
                if not line:
                    continue
                words = line.lstrip("< >").split(":")
                assert len(words) == 3, "Event file improperly formatted!"
                self.interesting[tuple(int(w) for w in words)] = -999

        # whether or not we care about this row (saved since lookup is slow)
        self.currentRowInfo = (-1,-1,-1)


    def preCut(self, row, channel, cut):
        '''
        Regular preCut function, but updates the interesting event info for relevant events.
        '''
        if cut == self.cutOrder[0]:
            self.currentRowInfo = (evVar(row, 'run'), evVar(row, 'lumi'), evVar(row, 'evt'))
            if self.currentRowInfo in self.interesting and self.interesting[self.currentRowInfo] == -999:
                self.interesting[self.currentRowInfo] = 0

        if self.currentRowInfo in self.interesting and self.interesting[self.currentRowInfo] < len(self.cutOrder) - 1:
            # We only care if this is the cut after the furthest cut yet achieved
            if self.cutOrder[self.interesting[self.currentRowInfo]+1] == cut:
                self.interesting[self.currentRowInfo] += 1

        super(SyncAnalyzer, self).preCut(row, channel, cut)


    def passCut(self, row, channel, cut):
        '''
        Regular passCut function, but if this is an interesting event and the last cut, say it passed.
        '''
        if cut == 'SelectBest':
            # Have to get ID again because best cand selection is run separately afterwards
            rowID = (evVar(row, 'run'), evVar(row, 'lumi'), evVar(row, 'evt'))
            if rowID in self.interesting:
                self.interesting[rowID] = 999
            
                
        super(SyncAnalyzer, self).passCut(row, channel, cut)


    def cutReport(self):
        '''
        Regular cutReport, but also prints (to stdout) the interesting event info.
        '''
        super(SyncAnalyzer, self).cutReport()

        print "Interesting events:"
        
        for evt in sorted(self.interesting.keys()):
            result = self.interesting[evt]
            if result == 999:
                resultStr = "PASS"
            else:
                resultStr = self.cutOrder[result]
            print "%d:%d:%d :: %s"%(evt[0], evt[1], evt[2], resultStr)



################################################################
####    To do a small test, jut run python ZZAnalyzer.py    ####
################################################################

if __name__ == "__main__":
    import argparse
    import os
    
    parser = argparse.ArgumentParser(description='Running ZZAnalyzer directly just does a little test.')
    parser.add_argument("channel", nargs='?', default='zz', type=str, help='Channel(s) to test.')
    parser.add_argument("cutset", nargs='?', default='FullSpectrumFSR', type=str, help='Cut set to test.')
    parser.add_argument("infile", nargs='?', 
                        default='%s/../ntuples/ZZTo4L_Tune4C_13TeV-powheg-pythia8_PHYS14DR_PU20bx25.root'%os.environ["zza"],
                        type=str, help='Single file to test on. No wildcards.')
    parser.add_argument("outfile", nargs='?', default='ZZTest.root', type=str, help='Test output file name.')
    parser.add_argument("resultType", nargs='?', default='ZZFinalHists', type=str, help='Format of output file')
    parser.add_argument("nEvents", nargs='?', type=int, default=100, help="Number of test events.")
    parser.add_argument("eventList", nargs='?', default='eventList.txt', type=str, help='File listing interesting events to check.')
    parser.add_argument("--cleanRows", nargs='?', type=str, default='',
                        help="Name of module to clean extra rows from each event. Without this option, no cleaning is performed.")
    args = parser.parse_args()

    a = SyncAnalyzer(args.channel, args.cutset, args.infile, args.outfile, args.resultType, args.nEvents, args.eventList, 1000, args.cleanRows)
    print "TESTING ZZAnalyzer"
    a.analyze()
    print "TEST COMPLETE"
