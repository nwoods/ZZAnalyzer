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
                 resultType="ZZCutFlowHists", maxEvents=float("inf"), intLumi=10000):

        # Has to happen before super is instantiated
#        self.setupTemplates()

        super(ZZCutFlow, self).__init__(channels, cutSet, infile, outfile, resultType, maxEvents, intLumi)


#     def setupTemplates(self):
#         '''
#         Template histograms for controls and flows, so we know how to bin
#         '''
#         self.controlTemplates = {
#             'Z1Iso' :     Hist(50, 0., 10., name='Z1Iso_control_TEMPLATE', title="Isolation"),
#             'Z2Iso' :     Hist(50, 0., 10., name='Z2Iso_control_TEMPLATE', title="Isolation"),
#             'Z1Mass' :    Hist(50, 0., 150., name='Z1Mass_control_TEMPLATE', title="Z1 Invariant Mass"),
#             'Z2Mass' :    Hist(50, 0., 150., name='Z2Mass_control_TEMPLATE', title="Z2 Invariant Mass"),
#             'Lepton1Pt' : Hist(50, 0., 150., name='Lepton1Pt_control_TEMPLATE', title="Lepton 1 Pt"),
#             'Lepton2Pt' : Hist(50, 0., 150., name='Lepton2Pt_control_TEMPLATE', title="Lepton 2 Pt"),
#             }
#         self.flowTemplates = {
#             '4lMass' : Hist(36, 100., 1000., name='4lMass_cutflow_TEMPLATE', title="4l Invariant Mass"),
#             'Z1Mass' : Hist(50, 0., 150., name='Z1Mass_cutflow_TEMPLATE', title="Z1 Invariant Mass"),
#             'Z2Mass' : Hist(50, 0., 150., name='Z2Mass_cutflow_TEMPLATE', title="Z2 Invariant Mass"),
#             }


#     def getHistoDict(self, channels):
#         '''
#         Overrides ZZAnalyzer.getHistoDict. Sets up dictionary structure such that
#         self.histos[channel]['control'][cut] = TH1F
#         self.histos[channel][flow][cut] = TH1F
# 
#         Same goofy ':~:' business as in ZZAnalyzer.getHistoDict, see there for explanation.
#         '''
#         self.histos = {}
# 
#         for channel in channels+["Total"]:
#             self.histos[channel] = {}
#             self.histos[channel]['control'] = {}
#             for flow in self.flows:
#                 self.histos[channel][flow] = {}
#             for control, ctemplate in self.controlTemplates.iteritems():
#                 self.histos[channel]['control'][control] = ctemplate.Clone("%s_control:~:%s"%(control,channel))
#             for cut in ['TotalRows']+self.cutOrder:
#                 for flow, ftemplate in self.flowTemplates.iteritems():
#                     self.histos[channel][flow][cut] = ftemplate.Clone("%s_cutflow_%s:~:%s"%(flow, cut,channel))
                    

#     def saveAllHistos(self):
#         '''
#         Save all histograms to self.outFile, in directories by channel/flow[ or 'control']/cut_histogram
#         '''
#         f = root_open(self.outFile, 'RECREATE')
# 
#         dirs = []
#         for channel, flowDict in self.histos.iteritems():
#             topDir = ROOT.TDirectoryFile(channel, channel+" cutflow and control")
#             for flow, cutDict in flowDict.iteritems():
#                 flowDir = topDir.mkdir(flow)
#                 for cut, hist in cutDict.iteritems():
#                 # Change name to be consistent                                                                                                  
#                     name = hist.GetName()
#                     name = name.split(":~:")[0]
#                     hist.SetName(name)
#                     flowDir.Append(hist)
# 
#             dirs.append(topDir)
# 
#         for dir in dirs:
#             dir.Write()
#         f.close()



#     def fillHistos(self, row, channel, objects):
#         '''
#         Not needed for cut flows
#         '''
#         pass


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
    args = parser.parse_args()

    a = ZZCutFlow(args.channel, args.cutset, args.infile, args.outfile, args.resultType, args.nEvents)
    print "TESTING ZZCutFlow"
    a.analyze()
    print "TEST COMPLETE"




    

            
