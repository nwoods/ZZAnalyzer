'''

Plotter for ZZ->4l control plots and cut flows

Author: Nate Woods, U. Wisconsin.

'''

import ROOT
import glob
import os
from ZZMetadata import sampleInfo
import array
import errno
from ZZPlotStyle import ZZPlotStyle


from PlotZZ import PlotZZ, makeDirectory

assert os.environ["zza"], "Run setup.sh before running plotter"

ROOT.gROOT.SetBatch(ROOT.kTRUE)

def makeDirectory(path):
    '''
    Make a directory, don't crash
    '''
    try:
        os.makedirs(path)
    except OSError as e:
        if e.errno == errno.EEXIST and os.path.isdir(path):
            pass
        else: 
            raise



class PlotCutFlow(object):
    '''
    A plotter  for ZZ->4l controls and cut flows
    '''
    def __init__(self, channels, intLumi=19710., outdir='./plots/cutflow', infiles='ZZA_NORMAL'):
        '''
        Setup
        If outdir starts with '.' you are presumed to be giving the path relative to $zza
        '''
        # Get channels
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

        # Setup samples (which are just all ROOT files in the results directory)
        # Makes a dictionary with an entry for each sample, to hold the ntuples (now) and various histograms (later)
        if infiles == 'ZZA_NORMAL':
            self.infiles = "%s/results/SMPZZ4l2012/cutflow/*_cutflow.root"%os.environ["zza"]
        else:
            self.infiles = infiles
        self.infiles = glob.glob(self.infiles)

        # Set up the dictionary structure to hold everything. Figures out variables on the fly.
        self.setupSamples()
        
        # Set up output directory
        self.outdir = outdir
        # don't want trailing slash
        if self.outdir[-1] == '/':
            self.outdir = self.outdir[:-1]
        # Assume leading . means ZZA base directory
        if self.outdir[0] == '.':
            self.outdir = os.environ["zza"] + self.outdir[1:]
        for channel in self.channels+['Total']:
            for flow in self.cutFlows:
                makeDirectory(self.outdir+'/'+channel+'/'+flow)

        print "Plots will be placed in: %s"%self.outdir

        # Set total luminosity
        self.intLumi = intLumi

        self.style = ZZPlotStyle()
#         # Make plots non-ugly
#         ROOT.gStyle.SetOptStat(0)
#         ROOT.gROOT.ForceStyle()


    def setupSamples(self):
        '''
        Setup all the samples, based on what variables are in the files.
        Assumes the files all hold the same variables at the end.
        '''
        self.samples = {}
        self.cutFlows = {}
        for fileName in self.infiles:
            sample = fileName.split('/')[-1].replace('_cutflow','').replace('.root','')
            self.samples[sample] = {}
            self.samples[sample]["file"] = ROOT.TFile(fileName)
            for channel in self.channels:
                self.samples[sample][channel] = {}
                if 'Total' not in self.samples[sample]:
                    self.samples[sample]['Total'] = {}
                flows = [k.GetName() for k in self.samples[sample]["file"].Get(channel).GetListOfKeys()]
                for flow in flows:
                    self.samples[sample][channel][flow] = {}
                    if flow not in self.samples[sample]['Total']:
                        self.samples[sample]['Total'][flow] = {}
                    self.samples[sample][channel][flow]["ntuple"] = self.samples[sample]["file"].Get("%s/%s"%(channel,flow))
                    if flow not in self.cutFlows:
                        self.cutFlows[flow] = []
                        for var in [k.GetName() for k in self.samples[sample][channel][flow]["ntuple"].GetListOfKeys()]:
                            self.cutFlows[flow].append(var)
                    self.samples[sample][channel][flow]["histos"] = {}
                    if 'histos' not in self.samples[sample]['Total'][flow]:
                        self.samples[sample]['Total'][flow]["histos"] = {}



    def getHist(self, sample, channel, flow, variable):
        '''
        Get a histogram from an ntuple created by the ZZ Analyzer
        Places the histogram in self.samples[sample][channel]["histos"][variable]
        '''
        assert type(self.samples[sample][channel][flow]["ntuple"]).__name__ != 'PyROOT_NoneType', "Oops, no Ntuple %s"%(channel+"/final/Ntuple")
        h = self.samples[sample][channel][flow]["ntuple"].Get(variable)
        assert h, "Histgram %s does not exist for sample %s, channel %s"%(variable, sample, channel)
        self.samples[sample][channel][flow]["histos"][variable] = h.Clone()
        if not sampleInfo[sample]["isData"]:
            self.samples[sample][channel][flow]["histos"][variable].Scale(sampleInfo[sample]["xsec"] * self.intLumi / sampleInfo[sample]["n"])
        if variable not in self.samples[sample]['Total'][flow]["histos"]:
            self.samples[sample]['Total'][flow]["histos"][variable] = self.samples[sample][channel][flow]["histos"][variable].Clone()
        else:
            self.samples[sample]['Total'][flow]["histos"][variable].Add(self.samples[sample][channel][flow]["histos"][variable])


    def makeAllHists(self, channel, flow):
        '''
        Grab and store all the histograms for flow in channel.
        '''
        for sample in self.samples:
            for var in self.cutFlows[flow]:
                self.getHist(sample, channel, flow, var)


    def makeStack(self, channel, flow, variable):
        '''
        Make a stack plot of a variable for all MC samples in a channel
        Assumes histograms are already made and in the samples dictionary
        Places background at the bottom of the stack, signal at the top. Within that,
        sorts by max value, so the smallest samples are on the bottom (desirable for
        log scales)
        '''
        # Make a list of samples and sort my maximum
        allSamples = [s for s in self.samples]
        allSamples.sort(key=lambda s: self.samples[s][channel][flow]["histos"][variable].GetMaximum())

        stack = ROOT.THStack('stack_%s_%s_%s'%(channel, flow, variable), variable)
        # Now plot in that order, but with signal on top
#         for signal in [False, True]:
        for sample in allSamples:

#                 if sampleInfo[sample]["isData"] or sampleInfo[sample]["isSignal"] != signal:
#                     continue
                
            self.samples[sample][channel][flow]["histos"][variable].SetMarkerColor(sampleInfo[sample]['color'])
            self.samples[sample][channel][flow]["histos"][variable].SetLineColor(sampleInfo[sample]['color'])
            self.samples[sample][channel][flow]["histos"][variable].SetFillStyle(1001)
            self.samples[sample][channel][flow]["histos"][variable].SetFillColor(sampleInfo[sample]['color'])
            self.samples[sample][channel][flow]["histos"][variable].SetLineColor(ROOT.EColor.kBlack)

            stack.Add(self.samples[sample][channel][flow]["histos"][variable])

        return stack


    def rebinHist(self, sample, channel, flow, variable, rebin=[5], reportSmallest=True):
        '''
        Rebin the histogram of variable in channel channel for sample sample according to the 
        list of parameters passed in as rebin
        If len(rebin)==1, rebin[0] bins will be combined to make a single bin. 
        If len(rebin)>1, the elements of rebin are interpreted as bin boundaries, and the new
        histogram will have length len(rebin)-1

        Returns the width of the smallest bin unless reportSmallest is set False
        '''
        if len(rebin) == 1:
            self.samples[sample][channel][flow]["histos"][variable] = self.samples[sample][channel][flow]["histos"][variable].Rebin(rebin[0])
            if reportSmallest:
                widths = [self.samples[sample][channel][flow]["histos"][variable].GetBinWidth(i) for i in xrange(self.samples[sample][channel][flow]["histos"][variable].GetNbinsX()+1)]
                return min(widths)
            else:
                return -1.

        bins = array.array("d", rebin)
        self.samples[sample][channel][flow]["histos"][variable] = self.samples[sample][flow][channel]["histos"][variable].Rebin(len(bins)-1, "", bins)
        # Now we have to fix the bin widths for the fact that we added them together
        widths = [self.samples[sample][channel][flow]["histos"][variable].GetBinWidth(i) for i in xrange(self.samples[sample][channel][flow]["histos"][variable].GetNbinsX()+1)]
        minWidth = min(widths)
        for i in xrange(self.samples[sample][channel][flow]["histos"][variable].GetNbinsX()+1):
            self.samples[sample][channel][flow]["histos"][variable].SetBinContent(i, 
                                                                            self.samples[sample][channel][flow]["histos"][variable].GetBinContent(i)\
                                                                            * minWidth / \
                                                                            self.samples[sample][channel][flow]["histos"][variable].GetBinWidth(i))
            self.samples[sample][channel][flow]["histos"][variable].SetBinError(i, 
                                                                          self.samples[sample][channel][flow]["histos"][variable].GetBinError(i)\
                                                                          * minWidth / \
                                                                          self.samples[sample][channel][flow]["histos"][variable].GetBinWidth(i))
            if reportSmallest:
                return min(widths)
            else:
                return -1.

        

    def rebinAll(self, channel, flow, variable, rebin=[5]):
        '''
        Rebin all histogram of variable in channel for flow,  according to the list 
        of parameters passed in as rebin.
        If len(rebin)==1, rebin[0] bins will be combined to make a single bin. 
        If len(rebin)>1, the elements of rebin are interpreted as bin boundaries, and the new
        histogram will have length len(rebin)-1

        Returns the width of the smallest bin
        '''
        minWidth = 0.
        for sample in self.samples:
            if minWidth == 0.:
                minWidth = self.rebinHist(sample, channel, flow, variable, rebin, True)
            else:
                self.rebinHist(sample, channel, flow, variable, rebin, False)

        return minWidth

        
    def makeLegend(self, channel, flow, variable, bounds=[0.6, 0.5, 0.9, 0.8]):
        '''
        Returns a legend for all samples in this channel for variable. 
        The label on the sample is sampleInfo[sample]["shortName"]
        '''
        leg = ROOT.TLegend(*bounds)
        for sample in self.samples:
            # format correctly
            if sampleInfo[sample]["isData"]:
                formatString = "LPE"
            else:
                formatString = "F"
            leg.AddEntry(self.samples[sample][channel][flow]["histos"][variable], sampleInfo[sample]["shortName"], formatString)

        leg.SetTextSize(0.03)

        return leg

        
    def makePlots(self, channel, flow, rebin=[], logy=False):
        '''
        For a channel and flow, plot a stack of MC and data points (when they exist, which 
        won't be for a while), with a legend, for all variables
        Saves plot to self.outdir/channel/flow/variable.png
        If rebin is empty (the default), the histograms are stacked and plotted as they were 
        saved. 
        If len(rebin)==1, rebin[0] bins will be combined to make a single bin. 
        If len(rebin)>1, the elements of rebin are interpreted as bin boundaries, and the new
        histogram will have length len(rebin)-1

        If channel is 'Total', no new histograms are made, assuming the other channels were
        done first so the total histograms are filled.
        '''
        c = ROOT.TCanvas('foo', 'foo')#, 1200, 1200)
        
        if channel != 'Total':
            self.makeAllHists(channel, flow)

        minWidth = -1
        if rebin:
            minWidth = self.rebinAll(channel, variable, rebin)
        
        # Format
        for variable in self.cutFlows[flow]:
            for sample in self.samples:
                yAxisSuffix = ''
                if sampleInfo[sample]["isData"]:
                    self.samples[sample][channel][flow]["histos"][variable].SetMarkerStyle(20)
                if not rebin:
                    # Assume saved histograms have constant bin size
                    minWidth = self.samples[sample][channel][flow]["histos"][variable].GetBinWidth(1)
                if "Mass" in variable or "Mt" in variable or "Pt" in variable:
                    yAxisSuffix += " / " + str(minWidth) + " GeV"

            stack = self.makeStack(channel, flow, variable)

            # Legend needs to be placed differently depending on the quantity plotted
            etaDims = [0.375, 0.65, 0.625, 0.9]
            phiDims = [0.375, 0.35, 0.625, 0.6]
            ZMassDims = [0.2, 0.5, 0.45, 0.8]
            Z2MassDimsLog = [0.73, 0.5, 0.93, 0.8]
            
            if "Eta" in variable:
                legend = self.makeLegend(channel, flow, variable, etaDims)
            elif "Phi" in variable:
                legend = self.makeLegend(channel, flow, variable, phiDims)
            elif 'Z1Mass' in variable[:6] or 'Z2Mass' in variable[:6] and not logy:
                legend = self.makeLegend(channel, flow, variable, ZMassDims)
            elif 'Z2Mass' in variable[:6] and logy:
                legend = self.makeLegend(channel, flow, variable, Z2MassDimsLog)
            else:
                legend = self.makeLegend(channel, flow, variable)

            # Have to call draw on stack before we can access its axis
            stack.Draw()

#            stack.SetTitle(self.getTitle(channel,variable))
            stack.GetXaxis().SetTitle(self.getXLabel(channel,flow, variable))
            stack.GetYaxis().SetTitle("Events" + yAxisSuffix)
#            stack.GetYaxis().SetTitleOffset(1.05)

            stack.Draw("hist")

            ### Draw data here when it exists

            legend.Draw("same")

            if logy:
                c.SetLogy()

            self.style.setPrelimStyle(c)

            c.Print("%s/%s/%s/%s.png"%(self.outdir, channel, flow, variable))
#             c.Print("%s/%s/%s/%s.pdf"%(self.outdir, channel, flow, variable))


    def plotAllFlows(self, channel, logy=False):
        '''
        Plot everything for all flows found in the samples, for channel. No rebinning.
        '''
        for flow in self.cutFlows:
            self.makePlots(channel, flow, [], logy)


    def getChannels(self):
        '''
        Return list of channels.
        '''
        return self.channels


    def setOutdir(self, newDir):
        '''
        Set the output directory
        Again, '.' is assumed to mean $zza.
        '''
        self.outdir = newDir
        # don't want trailing slash
        if self.outdir[-1] == '/':
            self.outdir = self.outdir[:-1]
        # Assume leading . means ZZA base directory
        if self.outdir[0] == '.':
            self.outdir = os.environ["zza"] + self.outdir[1:]
        for channel in self.channels+['Total']:
            for flow in self.cutFlows:
                makeDirectory(self.outdir+'/'+channel+'/'+flow)


    def getTitle(self, channel, variable):
        '''
        For a lot of possible variables, get something reasonable to put in the title of the plot
        '''
        words = variable.split('_')
        if channel == 'mmmm':
            search = 'ZZ#rightarrow4#mu'
            particle = '#mu'
        elif channel == 'eemm':
            search = 'ZZ#rightarrow2e2#mu'
            particle = 'l'
        elif channel == 'eeee':
            search = 'ZZ#rightarrow4e'
            particle = 'e'
        elif channel == 'Total':
            search = 'ZZ#rightarrow4l'
            particle = 'l'
        else:
            print "WARNING: channel %s is unusual"%channel
            search = ''
            particle = 'l'

        if words[-1] == 'control':
            if words[0] == 'Z1Iso':
                return '%s %s_{1,2} Isolation'%(search, particle)
            elif words[0] == 'Z2Iso':
                return '%s %s_{3,4} Isolation'%(search, particle)
            elif words[0] == 'Z1Mass':
                return '%s Z_{1} Invariant Mass'%search
            elif words[0] == 'Z2Mass':
                return '%s Z_{2} Invariant Mass'%search
            elif words[0] == 'Lepton1Pt':
                return '%s %s_{1} p_{T}'%(search, particle)
            elif words[0] == 'Lepton2Pt':
                return '%s %s_{2} p_{T}'%(search, particle)

        if words[-2] == 'cutflow':
            cut = words[-1]
            if words[0] == '4lMass':
                return '%s ZZ Invariant Mass after %s cut'%(search, cut.replace('Z1','Z_{1} ').replace('Z2','Z_{2} '))
            if words[0] == 'Z1Mass':
                return '%s Z_{1} Invariant Mass after %s cut'%(search, cut.replace('Z1','Z_{1} ').replace('Z2','Z_{2} '))
            if words[0] == 'Z2Mass':
                return '%s Z_{2} Invariant Mass after %s cut'%(search, cut.replace('Z1','Z_{1} ').replace('Z2','Z_{2} '))


    def getXLabel(self, channel, flow, variable):
        '''
        For a lot of possible variables, get something reasonable to put in the title of the plot
        '''
        if channel == 'mmmm':
            search = 'ZZ#rightarrow4#mu'
            particle = '#mu'
        elif channel == 'eemm':
            search = 'ZZ#rightarrow2e2#mu'
            particle = 'l'
        elif channel == 'eeee':
            search = 'ZZ#rightarrow4e'
            particle = 'e'
        elif channel == 'Total':
            search = 'ZZ#rightarrow4l'
            particle = 'l'
        else:
            print "WARNING: channel %s is unusual"%channel
            search = ''
            particle = 'l'

        if flow == 'control':
            name = variable
        else:
            name = flow

        if name == 'Z1Iso':
            return '%s_{1,2} Rel. Iso.'%(particle)
        elif name == 'Z2Iso':
            return '%s_{3,4} Rel. Iso'%(particle)
        if name == 'l1Iso':
            return '%s_{1} Rel. Iso.'%(particle)
        elif name == 'l2Iso':
            return '%s_{2} Rel. Iso'%(particle)
        elif name == 'l3Iso':
            return '%s_{3} Rel. Iso.'%(particle)
        elif name == 'l4Iso':
            return '%s_{4} Rel. Iso'%(particle)
        elif name == 'Z1Mass':
            return 'm_{Z_{1}}'
        elif name == 'Z2Mass':
            return 'm_{Z_{2}}'
        elif name == 'lepton1Pt':
            return '%s{1} p_{T}'%(particle)
        elif name == 'lepton2Pt':
            return '%s{2} p_{T}'%(particle)
        elif name == '4lMass':
            return '%s Inv. Mass'%search
        elif name == 'Z1Mass':
            return 'm_{Z_{1}}'
        elif name == 'Z2Mass':
            return 'm_{Z_{2}}'
        

#         title = 'ZZ#rightarrow'
#         if channel == 'mmmm':
#             leptons = '4#mu'
#             particle = '#mu'
#         elif channel == 'eemm':
#             leptons = '2e2#mu'
#             particle = 'l'
#         elif channel == 'eeee':
#             leptons = '4e'
#             particle = 'e'
#         elif channel == 'Total':
#             leptons = '4l'
#             particle = 'l'
#         else:
#             leptons = ''
#             particle = 'l'
# 
#         title += leptons
# 
#         if 'Lepton1' in variable:
#             particle += '_{1}'
#         if 'Lepton2' in variable:
#             particle += '_{2}'
#         if 'Z1' in invariable:
#             particle += '_{1,2}'
#         if 'Z2' in invariable:
#             particle += '_{3,4}'
#         title += ' %s'%particle
# 
#         if 'Iso' in variable:
#             title += 'Isolation'
#         if '



# massBins = [] #[30., 80.] + [129.+i*49. for i in xrange(15)] + [864.+i*98. for i in xrange(3)] + [1500.]
# ptBins = [i*10. for i in xrange(31)] #[i*10. for i in xrange(8)] + [i*20. for i in xrange(4, 19)] # + [300.+i*40. for i in xrange(3)] + [460., 600.]
# plotter = PlotZZ("zz")
# doLogy = False #True
# for channel in ["eeee","eemm","mmmm","Total"]:
#     plotter.makePlots(channel, "4lMass", massBins, doLogy)
#     plotter.makePlots(channel, "4lMt", massBins, doLogy)
#     plotter.makePlots(channel, "4lPt", ptBins, doLogy)
#     plotter.makePlots(channel, "4lEta", [])
#     plotter.makePlots(channel, "4lPhi", [2])


if __name__ == "__main__":

    import argparse
    parser = argparse.ArgumentParser(description="Make ZZ->4l cut flow and control plots.")

    parser.add_argument("channels", type=str, default='zz', nargs='?', help='Comma separated channels')
    parser.add_argument("outdir", type=str, default='./plots/HZZ4l2012', nargs='?', help='Location for output plots')
    parser.add_argument("infiles", type=str, default='./results/HZZ4l2012/*.root', nargs='?', help='Input files (may contain wildcards)')
    parser.add_argument("intlumi", type=float, default=19710, nargs='?', help="Integrated luminosity")
    parser.add_argument("--logy", action="store_true", help="Plot with log scale on y axis")

    args = parser.parse_args()

    if ',' in args.channels:
        channels = args.channels.split(',')
    else:
        channels = args.channels

    plotter = PlotCutFlow(channels, args.intlumi, args.outdir, args.infiles)

    for channel in plotter.getChannels()+["Total"]:
        plotter.plotAllFlows(channel, args.logy)






