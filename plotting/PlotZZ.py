'''

Plotter for ZZ->4l analysis.

Does result plots only; control plots done separately.

Author: Nate Woods, U. Wisconsin

'''

import ROOT
import glob
import os
from ZZMetadata import sampleInfo
import array
import errno



# Make sure the environment is set up
assert os.environ["zza"], "Run setup.sh before running plotter"

# Don't draw plots now
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



class PlotZZ(object):
    '''
    A plotter for ZZ->4l results
    '''
    def __init__(self, channels, intLumi=20000., outdir='./plots', infiles='ZZA_NORMAL'):
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
            self.infiles = "%s/results/SMPZZ4l2012/*.root"%os.environ["zza"]
        else:
            self.infiles = infiles
        self.infiles = glob.glob(self.infiles)
        self.samples = {}
        for fileName in self.infiles:
            sample = fileName.split('/')[-1].replace('.root','')
            self.samples[sample] = {}
            self.samples[sample]["file"] = ROOT.TFile(fileName)
            for channel in self.channels+['Total']:
                self.samples[sample][channel] = {}
                self.samples[sample][channel]["ntuple"] = self.samples[sample]["file"].Get(channel)
                assert type(self.samples[sample][channel]["ntuple"]).__name__ != 'PyROOT_NoneType', "Oops, no Ntuple %s"%(channel+"/final/Ntuple")
                self.samples[sample][channel]["histos"] = {}

        # Set up output directory
        self.outdir = outdir
        # don't want trailing slash
        if self.outdir[-1] == '/':
            self.outdir = self.outdir[:-1]
        # Assume leading . means ZZA base directory
        if self.outdir[0] == '.':
            self.outdir = os.environ["zza"] + self.outdir[1:]
        for channel in self.channels+['Total']:
            makeDirectory(self.outdir+'/'+channel)

        # Set total luminosity
        self.intLumi = intLumi

        # Make plots non-ugly
        ROOT.gStyle.SetOptStat(0)
        ROOT.gROOT.ForceStyle()


    def getHist(self, sample, channel, variable):
        '''
        Get a histogram from an ntuple created by the ZZ Analyzer
        Places the histogram in self.samples[sample][channel]["histos"][variable]
        '''
        assert type(self.samples[sample][channel]["ntuple"]).__name__ != 'PyROOT_NoneType', "Oops, no Ntuple %s"%(channel+"/final/Ntuple")
        h = self.samples[sample][channel]["ntuple"].Get(variable)
        assert h, "Histgram %s does not exist for sample %s, channel %s"%(variable, sample, channel)
        self.samples[sample][channel]["histos"][variable] = h.Clone()
        if not sampleInfo[sample]["isData"]:
            self.samples[sample][channel]["histos"][variable].Scale(sampleInfo[sample]["xsec"] * self.intLumi / sampleInfo[sample]["n"])


    def makeAllHists(self, channel, variable):
        '''
        Grab and store all the histograms for variable in channel.
        '''
        for sample in self.samples:
            self.getHist(sample, channel, variable)


    def makeStack(self, channel, variable):
        '''
        Make a stack plot of a variable for all MC samples in a channel
        Assumes histograms are already made and in the samples dictionary
        Places background at the bottom of the stack, signal at the top. Within that,
        sorts by max value, so the smallest samples are on the bottom (desirable for
        log scales)
        '''
        # Make a list of samples and sort my maximum
        allSamples = [s for s in self.samples]
        allSamples.sort(key=lambda s: self.samples[s][channel]["histos"][variable].GetMaximum())

        stack = ROOT.THStack('foo', variable)
        # Now plot in that order, with signal on top
        for signal in [False, True]:
            for sample in allSamples:
                if sampleInfo[sample]["isData"] or sampleInfo[sample]["isSignal"] != signal:
                    continue
                if '8TeV' in sample and 'ZZ' in sample:
                    if channel == 'mmmm' and ('2e2mu' in sample or '4e' in sample):
                        continue
                    if channel == 'eeee' and ('2e2mu' in sample or '4mu' in sample):
                        continue
                    if channel == 'eemm' and ('4mu' in sample or '4e' in sample):
                        continue
                    
                self.samples[sample][channel]["histos"][variable].SetMarkerColor(sampleInfo[sample]['color'])
                self.samples[sample][channel]["histos"][variable].SetLineColor(sampleInfo[sample]['color'])
                self.samples[sample][channel]["histos"][variable].SetFillStyle(1001)
                self.samples[sample][channel]["histos"][variable].SetFillColor(sampleInfo[sample]['color'])
                self.samples[sample][channel]["histos"][variable].SetLineColor(ROOT.EColor.kBlack)
                
                stack.Add(self.samples[sample][channel]["histos"][variable])

        return stack


    def rebinHist(self, sample, channel, variable, rebin=[5], reportSmallest=True):
        '''
        Rebin the histogram of variable in channel channel for sample sample according to the 
        list of parameters passed in as rebin
        If len(rebin)==1, rebin[0] bins will be combined to make a single bin. 
        If len(rebin)>1, the elements of rebin are interpreted as bin boundaries, and the new
        histogram will have length len(rebin)-1

        Returns the width of the smallest bin unless reportSmallest is set False
        '''
        if len(rebin) == 1:
            self.samples[sample][channel]["histos"][variable] = self.samples[sample][channel]["histos"][variable].Rebin(rebin[0])
            if reportSmallest:
                widths = [self.samples[sample][channel]["histos"][variable].GetBinWidth(i) for i in xrange(self.samples[sample][channel]["histos"][variable].GetNbinsX()+1)]
                return min(widths)
            else:
                return -1.

        bins = array.array("d", rebin)
        self.samples[sample][channel]["histos"][variable] = self.samples[sample][channel]["histos"][variable].Rebin(len(bins)-1, "", bins)
        # Now we have to fix the bin widths for the fact that we added them together
        widths = [self.samples[sample][channel]["histos"][variable].GetBinWidth(i) for i in xrange(self.samples[sample][channel]["histos"][variable].GetNbinsX()+1)]
        minWidth = min(widths)
        for i in xrange(self.samples[sample][channel]["histos"][variable].GetNbinsX()+1):
            self.samples[sample][channel]["histos"][variable].SetBinContent(i, 
                                                                            self.samples[sample][channel]["histos"][variable].GetBinContent(i)\
                                                                            * minWidth / \
                                                                            self.samples[sample][channel]["histos"][variable].GetBinWidth(i))
            self.samples[sample][channel]["histos"][variable].SetBinError(i, 
                                                                          self.samples[sample][channel]["histos"][variable].GetBinError(i)\
                                                                          * minWidth / \
                                                                          self.samples[sample][channel]["histos"][variable].GetBinWidth(i))
            if reportSmallest:
                return min(widths)
            else:
                return -1.

        

    def rebinAll(self, channel, variable, rebin=[5]):
        '''
        Rebin all histogram of variable in channel channel according to the list of parameters passed in as rebin
        If len(rebin)==1, rebin[0] bins will be combined to make a single bin. 
        If len(rebin)>1, the elements of rebin are interpreted as bin boundaries, and the new
        histogram will have length len(rebin)-1

        Returns the width of the smallest bin
        '''
        minWidth = 0.
        for sample in self.samples:
            if minWidth == 0.:
                minWidth = self.rebinHist(sample, channel, variable, rebin, True)
            else:
                self.rebinHist(sample, channel, variable, rebin, False)

        return minWidth

        
    def makeLegend(self, channel, variable, bounds=[0.6, 0.5, 0.9, 0.8]):
        '''
        Returns a legend for all samples in this channel for variable. 
        The label on the sample is sampleInfo[sample]["shortName"]
        '''
        leg = ROOT.TLegend(*bounds)
        leg.SetFillColor(ROOT.EColor.kWhite)
        for sample in self.samples:

            if '8TeV' in sample and 'ZZ' in sample:
                if channel == 'mmmm' and ('2e2mu' in sample or '4e' in sample):
                    continue
                if channel == 'eeee' and ('2e2mu' in sample or '4mu' in sample):
                    continue
                if channel == 'eemm' and ('4mu' in sample or '4e' in sample):
                    continue
                
            # format correctly
            if sampleInfo[sample]["isData"]:
                formatString = "LPE"
            else:
                formatString = "F"
            leg.AddEntry(self.samples[sample][channel]["histos"][variable], sampleInfo[sample]["shortName"], formatString)

        leg.SetTextSize(0.03)

        return leg


    def getChannels(self):
        '''
        Get channels this plotter can do. Doesn't include "Total"
        '''
        return self.channels
        
    def makePlots(self, channel, variable, rebin=[], logy=False, separate=False):
        '''
        For a channel and variable, plot a stack of MC and data points (when they exist, which 
        won't be for a while), with a legend
        Saves plot to self.outdir/channel/variable.png
        If rebin is empty (the default), the histograms are stacked and plotted as they were 
        saved. 
        If len(rebin)==1, rebin[0] bins will be combined to make a single bin. 
        If len(rebin)>1, the elements of rebin are interpreted as bin boundaries, and the new
        histogram will have length len(rebin)-1
        If logy is True, the y axis will be plotted on a log scale
        '''
        c = ROOT.TCanvas('foo', 'foo', 800, 800)
        
        self.makeAllHists(channel, variable)

        minWidth = -1
        if rebin:
            minWidth = self.rebinAll(channel, variable, rebin)
        
        # Format
        for sample in self.samples:
            yAxisSuffix = ''
            if sampleInfo[sample]["isData"]:
                self.samples[sample][channel]["histos"][variable].SetMarkerStyle(20)
            if not rebin:
                # Assume saved histograms have constant bin size
                minWidth = self.samples[sample][channel]["histos"][variable].GetBinWidth(1)
            if "Mass" in variable or "Mt" in variable or "Pt" in variable:
                yAxisSuffix += " / " + str(minWidth) + " GeV"

            stack = self.makeStack(channel, variable)

        # Legend needs to be placed differently depending on the quantity plotted
        etaDims = [0.375, 0.65, 0.625, 0.9]
        phiDims = [0.375, 0.35, 0.625, 0.6]
        
        if "Eta" in variable:
            legend = self.makeLegend(channel, variable, etaDims)
        elif "Phi" in variable:
            legend = self.makeLegend(channel, variable, phiDims)
        else:
            legend = self.makeLegend(channel, variable)

        # Have to call draw on stack before we can access its axis
        stack.Draw()

        if channel == "eeee":
            leptons = '4e'
        elif channel == 'eemm':
            leptons = '2e2#mu'
        elif channel == 'mmmm':
            leptons = '4#mu'
        elif channel == 'Total':
            leptons = '4l'

        stack.SetTitle("ZZ->%s %s"%(leptons, variable))
        stack.GetXaxis().SetTitle(variable.replace('4l',leptons))
        stack.GetYaxis().SetTitle("Events" + yAxisSuffix)
        stack.GetYaxis().SetTitleOffset(1.5)

        stack.Draw("hist")

        ### Draw data here when it exists

        legend.Draw("same")

        if logy:
            c.SetLogy()

        c.Print("%s/%s/%s.png"%(self.outdir, channel, variable))



if __name__ == "__main__":

    import argparse
    parser = argparse.ArgumentParser(description="Make primary ZZ->4l plots.")

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

    massBins = [i*24. for i in xrange(43)] #[30., 80.] + [129.+i*49. for i in xrange(15)] + [864.+i*98. for i in xrange(3)] + [1500.]
    ptBins = [i*6. for i in xrange(51)] #[i*10. for i in xrange(8)] + [i*20. for i in xrange(4, 19)] # + [300.+i*40. for i in xrange(3)] + [460., 600.]
    etaBins=[5]
    phiBins=[4]

    plotter = PlotZZ(channels, args.intlumi, args.outdir, args.infiles)

    for channel in plotter.getChannels()+["Total"]:
        plotter.makePlots(channel, "4lMass", massBins, args.logy)
        plotter.makePlots(channel, "4lMt", massBins, args.logy)
        plotter.makePlots(channel, "4lPt", ptBins, args.logy)
        plotter.makePlots(channel, "4lEta", etaBins, args.logy)
        plotter.makePlots(channel, "4lPhi", phiBins, args.logy)









