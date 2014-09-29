'''

ZZ->4l cut flows/controls. Takes and FSA Ntuple as input, makes 
a root file with histograms of variables the analysis cuts on
(controls) and selected variables plotted between cuts (cut
flows). 

Author: Nate Woods, U. Wisconsin

'''

from ZZAnalyzer import ZZAnalyzer, getVar
import os
import ROOT

# Environment must be set up
assert os.environ["zza"], "Run setup.sh before running cut flows"



class ZZCutFlow(ZZAnalyzer):
    def __init__(self, channels, cutSet, infile, outfile='./results/output_cutflow.root', maxEvents=float("inf")):

        # Has to happen before super is instantiated
        self.setupTemplates()

        # Dictionary of functions to calculate value for flow plots, to be filled between cuts
        self.flows = {
            '4lMass' : self.getMass,
            'Z1Mass' : self.getZ1Mass,
            'Z2Mass' : self.getZ2Mass,
            }

        # Dictionary of fuctions to calculate values for control plots (variables cut on)
        self.controls = {
            'Isolation' : self.getIso,
            'Z1Mass' : self.getZ1Mass,
            'Z2Mass' : self.getZ2Mass,
            'Lepton1Pt' : self.getLepton1Pt,
            'Lepton2Pt' : self.getLepton2Pt,
            }

        super(ZZCutFlow, self).__init__(channels, cutSet, infile, outfile, maxEvents)




    def setupTemplates(self):
        '''
        Template histograms for controls and flows, so we know how to bin
        '''
        self.controlTemplates = {
            'Isolation' : ROOT.TH1F('Isolation_control_TEMPLATE', "Isolation", 50, 0., 10.),
            'Z1Mass' : ROOT.TH1F('Z1Mass_control_TEMPLATE', "Z1 Invariant Mass", 30, 0., 150.),
            'Z2Mass' : ROOT.TH1F('Z2Mass_control_TEMPLATE', "Z2 Invariant Mass", 30, 0., 150.),
            'Lepton1Pt' : ROOT.TH1F('Lepton1Pt_control_TEMPLATE', "Lepton 1 Pt", 50, 0., 150.),
            'Lepton2Pt' : ROOT.TH1F('Lepton2Pt_control_TEMPLATE', "Lepton 2 Pt", 50, 0., 150.),
            }
        self.flowTemplates = {
            '4lMass' : ROOT.TH1F('3lMass_cutflow_TEMPLATE', "4l Invariant Mass", 36, 100., 1000.),
            'Z1Mass' : ROOT.TH1F('Z1Mass_cutflow_TEMPLATE', "Z1 Invariant Mass", 50, 0., 150.),
            'Z2Mass' : ROOT.TH1F('Z2Mass_cutflow_TEMPLATE', "Z2 Invariant Mass", 50, 0., 150.),
            }


    def getHistoDict(self, channels):
        '''
        Overrides ZZAnalyzer.getHistoDict. Sets up dictionary structure such that
        self.histos[channel]['control'][cut] = TH1F
        self.histos[channel][flow][cut] = TH1F

        Same goofy ':~:' business as in ZZAnalyzer.getHistoDict, see there for explanation.
        '''
        self.histos = {}

        for channel in channels+["Total"]:
            self.histos[channel] = {}
            self.histos[channel]['control'] = {}
            for flow in self.flows:
                self.histos[channel][flow] = {}
            for control, ctemplate in self.controlTemplates.iteritems():
                self.histos[channel]['control'][control] = ctemplate.Clone("%s_control:~:%s"%(control,channel))
            for cut in self.cutOrder:
                for flow, ftemplate in self.flowTemplates.iteritems():
                    self.histos[channel][flow][cut] = ftemplate.Clone("%s_cutflow_%s:~:%s"%(flow, cut,channel))
                    

    def saveAllHistos(self):
        '''
        Save all histograms to self.outFile, in directories by channel/flow[ or 'control']/cut_histogram
        '''
        f = ROOT.TFile(self.outFile, 'RECREATE')

        dirs = []
        for channel, flowDict in self.histos.iteritems():
            topDir = ROOT.TDirectoryFile(channel, channel+" cutflow and control")
            for flow, cutDict in flowDict.iteritems():
                flowDir = topDir.mkdir(flow)
                for cut, hist in cutDict.iteritems():
                # Change name to be consistent                                                                                                  
                    name = hist.GetName()
                    name = name.split(":~:")[0]
                    hist.SetName(name)
                    flowDir.Append(hist)

            dirs.append(topDir)

        for dir in dirs:
            dir.Write()
        f.Close()



    def fillHistos(self, row, channel, objects):
        '''
        Not needed for cut flows
        '''
        pass


    def passCut(self, row, channel, cut):
        '''
        Overrides ZZAnalyzer.passCut, to fill cut flow histograms
        '''
        self.cutsPassed[channel][cut] += 1
        for flow, flowFunc in self.flows.iteritems():
            self.histos[channel][flow][cut].Fill(flowFunc(row, channel))
            self.histos["Total"][flow][cut].Fill(flowFunc(row, channel))
        
    
    def preCut(self, row, channel, cut):
        '''
        Overrides ZZAnalyzer.preCut, to fill cut flow histograms
        Control functions that return iterables are presumed to want all of them
        added to the histogram (i.e. isolation for all 4 leptons). 
        '''
        if cut in self.controls:
            value = self.controls[cut](row, channel)
            if hasattr(value, '__iter__'):
                for val in value:
                    self.histos[channel]['control'][cut].Fill(val)
                    self.histos["Total"]['control'][cut].Fill(val)
            else:
                self.histos[channel]['control'][cut].Fill(value)
                self.histos["Total"]['control'][cut].Fill(value)


    def getIso(self, row, channel):
        '''
        Get a tuple with the isolation of all objects
        '''
        objects = self.mapObjects(channel)
        results = []
        for obj in objects:
            if obj[0] == 'e':
                results.append(getVar(row, 'RelPFIsoRhoFSR', obj))
            elif obj[0] == 'm':
                results.append(getVar(row, 'RelPFIsoDBDefault', obj))
        return results

        
    def getLepton1Pt(self, row, channel):
        '''
        Pt of highest pt lepton
        '''
        return self.getLeptonNPt(row, channel, 0)


    def getLepton2Pt(self, row, channel):
        '''
        Pt of second highest pt lepton
        '''
        return self.getLeptonNPt(row, channel, 1)


    def getLeptonNPt(self, row, channel, N):
        '''
        Order leptons by Pt, highest to lowest, and return lepton N.
        Zero-indexed, so the highest Pt lepton is lepton 0.
        '''
        objects = self.mapObjects(channel)
        pts = [getVar(row, 'Pt', obj) for obj in objects]
        pts.sort(reverse=True)
        return pts[N]
        

    def getMass(self, row, channel):
        '''
        Get the 4 lepton invariant mass
        '''
        return row.Mass


    def getZ1Mass(self, row, channel):
        '''
        Get the invariant mass of the best Z candidate
        '''
        objectTemplate = self.mapObjects(channel)
        objects = self.getOSSF(row, channel, objectTemplate)
        if len(objects) >= 2:
            return getVar(row, 'Mass', objects[0], objects[1])
        else:
            return getVar(row, 'Mass', objectTemplate[0], objectTemplate[1])


    def getZ2Mass(self, row, channel):
        '''
        Get the invariant mass of the best Z candidate
        '''
        objectTemplate = self.mapObjects(channel)
        objects = self.getOSSF(row, channel, objectTemplate)
        if len(objects) >= 4:
            return getVar(row, 'Mass', objects[2], objects[3])
        else:
            # in 2e2mu case, good Z could be second in template
            if channel == 'eemm':
                if len(objects) == 2 and objects[0][0] == 'm':
                    return getVar(row, 'Mass', objectTemplate[0], objectTemplate[1])
            return getVar(row, 'Mass', objectTemplate[2], objectTemplate[3])
    

            
