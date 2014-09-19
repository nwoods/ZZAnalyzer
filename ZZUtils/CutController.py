'''

CutController.py

A class to make, fill, and save control and cut flow histograms.

Typically used by a Cutter (or derived class) to histrogram cut variables
to allow tuning, and will histogram "result" variables (4l mass or whatever)
to show the effect of each cut.

In the cut template, if cuts[cut] does not contain the key 'cutFlow', it 
will be ignored and no histogram will be made. If it exists, cuts[cut]['cutFlow']
is a dictionary with entries 'nbins', 'low', and 'high', mapped to the last
three arguments of a ROOT.TH1* constructor. 

The special entry cuts['cutFlows'] is a dictionary of signal variables keyed
to tuples indicating (nbins, low, high), e.g.:

>>> cuts['cutFlows'] = {
>>>     'Mass' : (100, 0., 1500.),
>>>     '{object1}_{object2}_Mass' : (20, 0., 120.),
>>> }


Author: Nate Woods, U. Wisconsin


'''


from ROOT import TH1F, TFile, TDirectoryFile



class CutController(object):
    def __init__(self, channels, outfile='./results/output_cutflow.root'):
        assert type(channels) == list and all((all(letter in ['e','m','t','g','j'] for letter in channel) and len(channel) <= 4) for channel in channels), 'Invalid channel'
        self.channels = channels
        # Always want overall plots, regardless for channels
        if "Total" not in self.channels:
            self.channels += ["Total"]

        self.outfile=outfile

        # Keep (ordered) track of what cuts and flows we have
        self.cuts = []
        self.flows = []

        # template histograms for result variables to be cloned for each cut
        self.flowTemplates = {}

        # template histograms for cut variables to be cloned for each flow
        self.cutTemplates = {}

        # Remember which variable to plot for each cut and flow 
        self.flowVars = {}
        self.cutVars = {}       

        # self.control stores the histograms of variables cut on
        # self.cutFlow stores the histograms of signal variables between cuts
        self.control = {}
        self.cutFlow = {}
        for channel in self.channels:
            self.control[channel] = {}
            self.cutFlow[channel] = {}

        # Once we've prepared the histograms for running, no more flows or cuts
        # may be added
        self.frozen = False


    def addFlow(self, flowName, var, nBins, low, high):
        '''
        Add a variable (e.g. 'Mass' or 'e1_e2_Mass') to self.cutFlow for plotting 
        between cuts
        If var is the special keyword "USER"
        '''
        if self.frozen:
            print "WARNING: cutflows frozen, flow of %s not added"%flowName
            return

        self.flowTemplates[var] = TH1F("%s_cutFlow_%s_TEMPLATE"%(flowName, cut), 
                                       "%s after %s cut"%(var, cut),
                                       nBins, low, high)
        
        self.flows.append(flowName)
        self.flowVars[flowName] = var


    def addCut(self, cutName, var, nBins, low, high):
        '''
        Add a cut, from which control plots will be made of the appropriate variable
        If var is the special keyword "USER", the histogram will be filled with passed 
        values rather than just pulling var from the ntuple
        '''
        if self.frozen:
            print "WARNING: cutflows frozen, cut %s not added"%cutName
            return
            
        self.cutTemplates[cutName] = TH1F("%s_FoM_TEMPLATE"%(cutName, var), 
                                          "%s: %s"%(cutName, FoM)
                                          nBins, low, high)
                
        self.cuts.append(cutName)
        self.cutVars[cutName] = var

        
    def freezeFlows(self):
        '''
        Prepares all histograms for filling
        The weird ':~:' thing is to keep ROOT from freaking out over two histograms
        with the same name. Will be removed (along with channel) before saving
        (see comment on ZZAnalyzer.getHistoDict)
        '''
        for channel in self.channels:
            for flow in self.flows:
                self.cutFlow[channel][flow] = {}
            
            for cut in self.cuts:
                self.control[channel][cut] = self.cutTemplates[cut].Clone("%s_control:~:%s"%(cut,channel))
                for flow in self.flows:
                    self.cutFlow[channel][flow][cut] = self.flowTemplates[flow].Clone("%s_cutflow_%s:~:%s"%(flow, cut, channel))
                    
        self.frozen = True


    def cutFlowFill(self, row, cut, evPass, **userVars):
        '''
        Fills all the histograms relevant to one cut. 

        For that cut, it fills the relevant control histogram, and if the event passed
        the cut, all flow histograms. 
        
        If any cut or flow has variable USER, the CutController expects 
        userVars[cut/flow name] to be a float it can fill the histogram with. 
        '''

        if self.cutVars[cut] == "USER":
            self.control[cut].Fill(userVars[cut])
        else:
            self.control[cut].Fill(getattr(row, self.cutVars[cut]))

        if evPass:
            for flow in self.flows:
                if self.flowVars[flow] == "USER":
                    self.cutFlow[channel][flow][cut].Fill(userVars[flow])
                else:
                    self.cutFlow[channel][flow][cut].Fill(getattr(row, self.flowVars[flow]))


     def saveAllCutFlows(self):
        '''                                                                                                                                     
        Save all histograms to self.outFile, in directories by channel
        '''
        f = TFile(self.outFile, 'RECREATE')

        dirs = []
        for channel in self.channels:
            topDir = TDirectoryFile(channel, channel+" cutflow")
            
            cutDir = topDir.mkdir("control")
            for cut, hist in self.control[channel].iteritems():
                # Change name to be consistent
                name = hist.GetName()
                name = name.split(":~:")[0]
                hist.SetName(name)
                cutDir.Append(hist)

            flowDir = topDir.mkdir("cutFlow")
            for flow in self.flows:
                thisDir = flowDir.mkdir("flow")
                for cut, hist in self.cutFlow[channel][flow].iteritems():
                    name = hist.GetName()
                    name = name.split(":~:")[0]
                    hist.SetName(name)
                    thisDir.Append(hist)
                    
            dirs.append(topDir)
                    
        for dir in dirs:
            dir.Write()
        f.Close()










