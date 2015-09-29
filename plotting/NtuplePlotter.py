'''
    
    Class to make plots from FSA-style Ntuples. Give it a set of ntuples for 
    data and another set for MC, and it does the formatting, stacking, error 
    bars, ratios, etc. for you.
    
    Author: Nate Woods, U. Wisconsin
    
'''

import os
assert os.environ["zza"], "Run setup.sh before using this package!"
import re
import errno
from types import MethodType

from glob import glob
from collections import Iterable, Sequence, OrderedDict
from math import sqrt

# include logging stuff first so other imports don't babble at us
import logging
from rootpy import log as rlog; rlog = rlog["/NtuplePlotter"]
# don't show most silly ROOT messages
logging.basicConfig(level=logging.WARNING)
rlog["/ROOT.TCanvas.Print"].setLevel(rlog.WARNING)
rlog["/ROOT.TUnixSystem.SetDisplay"].setLevel(rlog.ERROR)
rlog["/rootpy.tree.chain"].setLevel(rlog.WARNING)

from rootpy.io import root_open, File
from rootpy.plotting import Hist, Hist2D, HistStack, Graph, Canvas, Legend, Pad
from rootpy.plotting.hist import _Hist
from rootpy.plotting.graph import _Graph1DBase
from rootpy.plotting.utils import draw, get_band
from rootpy.ROOT import kTRUE, kFALSE, TLine
import rootpy.ROOT as ROOT
from rootpy.tree import Tree, TreeChain
from rootpy.plotting.base import Plottable
from rootpy import asrootpy, QROOT

from ZZPlotStyle import ZZPlotStyle
from ZZMetadata import sampleInfo
from ZZHelpers import makeNumberPretty

ROOT.gROOT.SetBatch(kTRUE)

_tempFileEnding = "_DSNPODKWMDNWCMD"

### Dumb workaround for a ROOT bug
dummy = Hist(1,0,1)
cdummy = Canvas(10,10)
dummy.xaxis.SetTitle("\\mu\\mu")
dummy.draw()


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

def returnThing(thing):
    ''' stupid lambda scoping... '''
    return lambda _: getattr(_, thing)

def WrapPlottable(C):
    '''
    Create a stupid thin wrapper class that keeps track of a little bit of
    metadata for a plottable object.
    '''
    if not (issubclass(C, Plottable) or isinstance(C(), Plottable)):
        raise TypeError("%s cannot be wrapped for meta info as it is not plottable."%C.__name__)

    class Wrap(C, C.__bases__[-1]):
        def __new__(cls, *args, **kwargs):
            metaInfoDict = {}
            plotArgs = {}
            # Separate metadata from plotting parameters so rootpy doesn't
            # get angry
            for arg, val in kwargs.iteritems():
                if arg in Plottable.EXTRA_ATTRS or arg in ["name", "title", "type"]:
                    plotArgs[arg] = val
                else:
                    metaInfoDict[arg] = val

            new = super(Wrap, cls).__new__(cls, *args, **plotArgs)


            new.__dict__.update(metaInfoDict)

            # Make a nicely named function for every bit of metadata
            for arg, fun in metaInfoDict.iteritems():
                setattr(new,
                        "get%s%s"%(arg[0].upper(), arg[1:]),
                        MethodType(returnThing(arg), new))

            return new

        def __init__(self, *args, **kwargs):
            '''
            Isn't always run; just to keep things from breaking if it is.
            '''
            plotArgs = {arg:val for arg,val in kwargs.iteritems() if arg in Plottable.EXTRA_ATTRS or arg in ["name", "title", "type"]}
            super(Wrap, self).__init__(*args, **plotArgs)
            
    return Wrap


def getMinBinWidth(obj):
    '''
    Get the width of the narrowest bin in any of the objects.
    '''
    if isinstance(obj, Sequence): # list, etc.
        return min(getMinBinWidth(ob) for ob in obj)
    if isinstance(obj, _Hist):
        return min(obj.GetBinWidth(b) for b in range(1,len(obj)-1))
    if isinstance(obj, HistStack):
        return getMinBinWidth(obj.hists)
    if isinstance(obj, _Graph1DBase):
        return min(abs(obj[i][0]-obj[i-1][0]) for i in range(1,len(obj)))
    else:
        return float("Inf")


class NtuplePlotter(object):
    def __init__(self, channels, outdir='./plots', mcFiles={}, 
                 dataFiles={}, intLumi=-1.):
        self.intLumi = float(intLumi)
        if outdir[0] == '.':
            self.outdir = os.environ['zza'] + outdir[1:]
        elif '$zza' in outdir:
            self.outdir = outdir.replace('$zza', os.environ['zza'])
        else:
            self.outdir = outdir
        if self.outdir[-1] != '/':
            self.outdir += '/'
        makeDirectory(self.outdir)

        self.channels = self.expandChannelsFromArg(channels)
        
        self.dataOrMC = {} # True if data, False if MC

        self.files = {}
        for cat, files in mcFiles.iteritems():
            self.dataOrMC[cat] = False
            self.storeFilesFromArg(files, cat)
        # don't open data files now; chain will do that
        for cat in dataFiles:
            self.dataOrMC[cat] = True
            self.files[cat] = {}

        self.ntuples = {cat : {} for cat in mcFiles}
        self.ntuples.update({cat : {cat:{}} for cat in dataFiles})
        for cat, samples in self.files.iteritems():
            if self.isData(cat):
                for c in self.channels:
                    dataFileList = self.getFileNamesFromArg(dataFiles[cat]).values()
                    if len(dataFileList) > 1:
                        n, f = self.mergeDataFiles(c, dataFileList, cat)
                        self.files[cat][c] = f
                        self.ntuples[cat][cat][c] = n
                    elif len(dataFileList) == 1:
                        self.files[cat] = { c : root_open(dataFileList[0]) for c in self.channels }
                        self.ntuples[cat][cat] = { c : self.files[cat][cat].Get('%s/final/Ntuple'%c) for c in self.channels }
                    else:
                        self.files[cat] = {}
                        self.ntuples[cat][cat] = {}
            else:
                for s in samples:
                    self.ntuples[cat][s] = { c : samples[s].Get("%s/final/Ntuple"%c) for c in self.channels }

        self.drawings = {}

        self.style = ZZPlotStyle()
                 


    def __del__(self):
        '''
        When we're done, delete any temporary root files we created.
        '''
        for f in os.listdir(os.getcwd()):
            if re.search(_tempFileEnding, f) is not None:
                os.remove(os.path.join(os.getcwd(), f))


    def isData(self, category):
        '''
        False if MC.
        '''
        return self.dataOrMC[category]


    def expandChannelsFromArg(self, channels):
        if isinstance(channels, str):
            if channels == '4l' or channels == 'zz' or channels == 'ZZ':
                return ['eeee', 'eemm', 'mmmm']
            else:
                assert all(letter in ['e','m','t','g','j'] for letter in channels) and len(channels) <= 4, 'Invalid channel ' + channels
                return [channels]
        else:
            assert isinstance(channels,list), 'Channels must be a list or a string'
            assert all ((all(letter in ['e','m','t','g','j'] for letter in channel) and len(channel) <= 4) for channel in channels), 'Invalid channel in ['+','.join(channels)+']'
            return channels
        

    def storeFilesFromArg(self, files, category):
        '''
        Get files from this argument and store them in group category (data, mc, etc....)
        '''
        if category not in self.files:
            self.files[category] = {}
            
        try:
            self.files[category].update({k:root_open(f) for k,f in self.getFileNamesFromArg(files).iteritems()})
        except TypeError:
            print "Invalid %s file list"%category
            print files
            print "(must be string of paths, list of string of paths, list "+\
                "of files, or dictionary of files)"
            raise
        except:
            print "Failed to open %s files"%category
            print files
            raise


    def getFileNamesFromArg(self, files):
        '''
        If files is a string, it is interpreted as a comma-separated list of 
        wildcards pointing to root files, or directories containing root files
        (which are assumed to have names ending in ',root'). Then a dict is
        returned with the (open) root files keyed to their file names (without
        the path or '.root'). 
        If files is a list of strings, they are assumed to be wildcards or
        paths in the same way.
        If files is a dict of root files keyed to strings, that's all good 
        and we just return that.
        Anything else, we throw an error.
        '''
        out = {}

        if isinstance(files, dict):
            for k, f in files.iteritems():
                if not isinstance(k, str):
                    raise TypeError("Sample name must be a string")
                if isinstance(f, str):
                    try:
                        out[k] = f
                    except:
                        print "%s cannot be opened"%f
                        raise
                else:
                    raise TypeError("Path to file must be a string")

            return out

        if isinstance(files, str):
            return self.getFileNamesFromStr(files)

        if isinstance(files, Sequence):
            for f in files:
                if isinstance(f, str):
                    out.update(self.getFileNamesFromStr(f))
                else:
                    raise TypeError

            return out

        raise TypeError


    def getFileNamesFromStr(self, f):
        '''
        Takes a string and interprets it as a comma-separated list of paths
        to directories of .root files or wildcards pointing to .root files.
        Returns a dict containing all .root files found, open and keyed to the
        (no path, no '.root') name of the file.
        '''
        if not isinstance(f, str):
            raise TypeError
                                          
        f = f.split(",")
        
        files = []
        for path in f:
            path.strip(" ")
            if len(path) < 5 or path[-5:] != ".root":
                path += '*.root'
            files += glob(path)
                                          
        return { fi.split('/')[-1].replace('.root','') : fi for fi in files }
                                          

    def mergeDataFiles(self, channel, files, category):
        '''
        Takes all data files, and for a given channel, combines the relevant
        ntuples into one big ntuple, removing redundant copies of the same
        event if an event appears in multiple files. 
        Returns the new ntuple and a temporary file it's stored in.
        Physics-based redundant row cleaning is assumed already done; that is,
        it is assumed that multiple copies of an event are strictly identical
        and it doesn't matter which is kept.
        '''
        tempFile = root_open("dataTEMP_%s%s%s.root"%(channel, _tempFileEnding, category), "recreate")
        out = Tree("%s/final/Ntuple"%channel)

        if len(files) == 0:
            return out, tempFile
        
        chain = TreeChain('%s/final/Ntuple'%channel, files)

        foundEvents = set()
        out.set_buffer(chain._buffer, create_branches=True)
        for ev in chain:
            evID = (ev.run, ev.lumi, ev.evt)
            if evID in foundEvents:
                continue
            out.fill()
            foundEvents.add(evID)

        return out, tempFile
        

    WrappedHist = WrapPlottable(Hist)
    WrappedHist2 = WrapPlottable(Hist2D)
    WrappedStack = WrapPlottable(HistStack)
    WrappedGraph = WrapPlottable(Graph)


    class Drawing(object):
        '''
        Simple container for a canvas and all the stuff that is/should be 
        plotted on it.
        '''
        def __init__(self, title, style, width=1000, height=800, logy=False, 
                     ipynb=False):
            self.ipynb = ipynb
            if self.ipynb:
                self.c = rootnotes.canvas("x"+title, (width, height))
            else:
                self.c = Canvas(width, height, title=title)
            self.pads = [self.c]

            self.logy = logy
            self.c.cd()
            self.objects = [] # for Hists, HistStacks, and Graphs (objects with axes)
            self.objectsAux = [] # for anything else you want drawn on the canvas
            self.legObjects = []
            self.style = style
            self.uniformBins = True
            self.minBinWidth = -1 # least common denominator of bin widths
            
        def mainPad(self):
            '''
            Returns primary pad where most things are plotted. May or may not
            just be the canvas.
            '''
            return self.pads[0]
            
        def addObject(self, obj, addToLegend=True, legendStyle=''):
            '''
            Puts an object in the list of things to draw.
            addToLegend only counts for histograms, graphs, and stacks.
            If legendStyle is non-empty, that style is used instead of
            "LPE" for data and "F" for MC.
            '''
            # keep track of whether or not everything has the same binning
            try:
                self.uniformBins = (self.uniformBins and obj.uniform())
            except AttributeError:
                pass

            minWidth = getMinBinWidth(obj)
            if self.minBinWidth == -1 or minWidth < self.minBinWidth:
                self.minBinWidth = minWidth
            #### TODO: go from keeping the minimum bin width to keeping the 
            #### least common denominator and scaling appropriately

            # if self.c.GetLogy() and obj.min() == 0:
            #     if isinstance(obj, HistStack):
            #         loopthrough = obj.sum
            #     else:
            #         loopthrough = obj
            # 
            #     nonzeroMin = 0
            #     for b in loopthrough:
            #         if b.value < nonzeroMin:
            #             nonzeroMin = b.value
            #     if nonzeroMin == 0:
            #         return
            # 
            #     obj.SetMinimum(nonzeroMin/2)
            # 
            # elif self.c.GetLogy() and obj.GetMinimum() < 0:
            #     raise ValueError("Can't plot negative values on log scale!")

            if isinstance(obj, (_Hist, _Graph1DBase, HistStack)):
                self.objects.append(obj)
            else:
                self.objectsAux.append(obj)
            
            if addToLegend:
                self.addToLegend(obj, legendStyle)

        def addPadBelow(self, height, bottomMargin=0.3, topMargin=0.085):
            '''
            Add a secondary pad below the main pad.
            If there was already a second pad, it just disappears.
            '''
            self.c.cd()
            pad2 = Pad(0.,0.,1.,height)
            pad2.SetBottomMargin(bottomMargin)
            pad2.SetTopMargin(0.)
            pad1 = Pad(0.,height,1.,1.)
            pad1.SetTopMargin(topMargin)
            pad1.SetBottomMargin(0.01)

            self.pads = [pad1,pad2]

        def addRatio(self, num, denom, height, ratioMin=0.5, ratioMax=1.5,
                     bottomMargin=0.3, topMargin=0.06, yTitle=""):
            self.addPadBelow(height, bottomMargin, topMargin)
            ratio = num.clone()
            ratio.sumw2()
            ratio.Divide(denom)
            ratio.color = 'black'
            opts = {
                'xaxis':ratio.xaxis,
                'yaxis':ratio.yaxis,
                'ylimits':(ratioMin,ratioMax),
                'ydivisions':5,
                }

            unity = TLine(ratio.lowerbound(), 1, ratio.upperbound(), 1)
            unity.SetLineStyle(7)

            self.paintPad(self.pads[1], [ratio], [unity], opts, "", "", yTitle, "")

        def fixPadAxes(self):
            '''
            Set secondary pad axes to look like the primary pad axes, then
            make the primary pad X axis labels and title disappear. Does 
            nothing if there is only one pad.
            '''
            if len(self.pads) <= 1 or not hasattr(self.mainPad(), 'xaxis'):
                return

            desiredX = self.mainPad().xaxis
            desiredY = self.mainPad().yaxis

            for pad in self.pads[1:]:
                if hasattr(pad, 'xaxis'):
                    thisX = pad.xaxis
                    thisY = pad.yaxis
                else:
                    continue

                thisX.title = desiredX.title
                thisX.SetTitleSize(desiredX.GetTitleSize() * self.mainPad().height / pad.height)
                thisX.SetLabelSize(desiredX.GetLabelSize() * self.mainPad().height / pad.height)
                
                #thisY.SetTitleSize(desiredY.GetTitleSize() * self.mainPad().height / pad.height)
                thisY.SetLabelSize(desiredY.GetLabelSize() * self.mainPad().height / pad.height)

            desiredX.SetLabelOffset(999)
            desiredX.SetTitleOffset(999)

        def addToLegend(self, obj, legendStyle=''):
            '''
            If legendStyle is a non-empty string, that style is used.
            Otherwise, the style is "F" for MC and "LPE" for data.
            '''
            if isinstance(obj, HistStack):
                for h in obj.GetHists():
                    self.addToLegend(h)
                return
            if not hasattr(obj, "sample"):
                raise AttributeError("%s doesn't know what sample it's "
                                     "from, so it can't be added to the "
                                     "legend."%obj.__name__)

            if legendStyle:
                obj.legendStyle = legendStyle
            else:
                # Anything that isn't in the sample information is assumed data
                try:
                    thisIsData = sampleInfo[obj.getSample()]['isData']
                except KeyError:
                    thisIsData = True
                if thisIsData:
                    obj.legendstyle = "LPE"
                else:
                    obj.legendstyle = "F"

            self.legObjects.append(obj)

        def getAxisTitles(self, xTitle, xUnits, yTitle, yUnits):
            '''
            Put appropriate units on axis labels, including " / X GeV" if 
            applicable for the y axis.
            '''
            if xTitle:
                if xUnits:
                    if '\\' in xTitle: # TeX style
                        xUnitsText = "\\: [\\text{%s}]"%xUnits
                    else:
                        xUnitsText = " [%s]"%xUnits
                    xTitle = "%s %s"%(xTitle, xUnitsText)
            else:
                xTitle = None
            if yTitle:
                if yUnits:
                    if '\\' in yTitle: # TeX style
                        yUnitsText = "\\: [\\text{%s}]"%yUnits
                    else:
                        yUnitsText = " [%s]"%yUnits
                    yTitle = "%s %s"%(yTitle, yUnitsText)
                elif not self.uniformBins and self.minBinWidth != -1:
                    yTitle = "%s / %s"%(yTitle, makeNumberPretty(self.minBinWidth, 2))
                    if xUnits:
                        yTitle = "%s %s"%(yTitle, xUnitsText if '\\' in yTitle else xUnits)
            else:
                yTitle = None
            
            return xTitle, yTitle

        def paintPad(self, pad, objects, objectsAux, drawOpts={}, xTitle="", 
                     xUnits="GeV", yTitle="Events", yUnits="", logy=False,
                     legObjects=[], legParamsOverride={}, stackErr=True):
            '''
            Draws objects (Hists, HistStacks, and Graphs) and objectsAux
            (anything else) on pad.
            drawLeg (bool): paint a legend?
            legParamsOverride (dict): passed directly to rootpy.plotting.Legend constructor
            stackErr (bool): draw black hashed region to indicate MC stack error bars?
            '''
            if legObjects:
                legParams = {
                    'entryheight' : 0.03,
                    'entrysep' : 0.01,
                    'leftmargin' : 0.5,
                    'topmargin' : 0.05,
                    'rightmargin' : 0.05,
                    'textsize' : 0.03,
                    }
                legParams.update(legParamsOverride)

                leg = Legend(legObjects[::-1], pad, **legParams)

            if stackErr:
                for ob in objects:
                    if isinstance(ob, HistStack) and len(ob):
                        objects.append(self.getStackErrors(ob))

            # make a copy to avoid some weird kind of namespace contamination
            opts = {k:v for k,v in drawOpts.iteritems()}

            titleX, titleY = self.getAxisTitles(xTitle, xUnits, yTitle, yUnits)
            if titleX and 'xtitle' not in opts:
                opts['xtitle'] = titleX
            if titleY and 'ytitle' not in opts:
                opts['ytitle'] = titleY

            if(objects):
                (xaxis, yaxis), axisRanges = draw(objects, pad, logy=logy, **opts)
            pad.cd()
            for obj in objectsAux:
                obj.Draw("SAME")

            if legObjects:
                leg.Draw("SAME")

            pad.Draw()

            pad.xaxis = xaxis
            pad.yaxis = yaxis

        def draw(self, drawOpts={}, outFile="", drawNow=False, 
                 xTitle="", xUnits="GeV", yTitle="Events", yUnits="",
                 drawLeg=True, legParamsOverride={}, stackErr=True,
                 intLumi=40.03, simOnly=False):
            '''
            opts (dict): passed directly to rootpy.plotting.utils.draw
            outFile (str): location to save plot (not saved if empty str)
            drawNow (bool): paint on-screen now?
            drawLeg (bool): paint a legend?
            legParams (dict): passed directly to rootpy.plotting.Legend constructor
            stackErr (bool): draw black hashed region to indicate MC stack error bars?
            '''
            if drawNow and ROOT.gROOT.IsBatch():
                ROOT.gROOT.SetBatch(kFALSE)
            if not drawNow and not ROOT.gROOT.IsBatch():
                ROOT.gROOT.SetBatch(kTRUE)

            legObjs = self.legObjects if drawLeg else []
            
            self.paintPad(self.mainPad(), self.objects, self.objectsAux, drawOpts, 
                          xTitle, xUnits, yTitle, yUnits, self.logy, legObjs, 
                          legParamsOverride, stackErr)

            if len(self.pads) > 1:
                self.c.cd()
                for pad in self.pads:
                    pad.Draw()
                self.fixPadAxes()

            plotType = "Preliminary"
            if simOnly:
                plotType = "%s Simulation"%plotType

            self.style.setCMSStyle(self.c, "", True, plotType, 13, intLumi)
            if drawNow:
                if self.ipynb:
                    self.c
                else:
                    self.c.Update()

            if outFile:
                self.c.Print(outFile)

        def getStackErrors(self, stack):
            '''
            Make a hatched black band to represent the error bars on stack.
            '''
            total = sum(stack.hists)
            total.sumw2()
            lo = total.empty_clone()
            hi = total.empty_clone()
            for i in xrange(1,total.GetNbinsX()+1):
                lo[i].value = total[i].value - total.GetBinErrorLow(i)
                hi[i].value = total[i].value + total.GetBinErrorUp(i)
            err = get_band(lo, hi, total)

            err.fillstyle = 'x'
            err.drawstyle = '2'
            err.fillcolor = 'black'

            return err

    def addToHist(self, hist, category, sample, channel, variable, selection):
        try:
            self.ntuples[category][sample][channel].Draw(variable, selection, "goff", hist)
        except KeyError:
            if category not in self.ntuples:
                print "'%s' is not a category of ntuple, nothing to draw!"%category
                return False
            elif sample not in self.ntuples[category]:
                print "'%s' is not a sample in category '%s', nothing to draw!"%(sample, category)
                return False
            elif channel not in self.ntuples[category][sample]:
                print "No channel '%s' for sample '%s', nothing to draw!"%(channel, sample)
                return False
            else:
                raise
        except AttributeError:
            if isinstance(self.ntuples[category][sample][channel]):
                print "No ntuple found for %s file %s in channel %s, nothing to draw!"%(category, sample, channel)
                return False
            else:
                raise

        hist.sumw2()

        return True


    def makeHist(self, category, sample, channels, variables, selections, 
                 binning, scale=1, weight='', formatOpts={}, perUnitWidth=True,
                 nameForLegend=''):
        '''
        Make a histogram of variable(s) in channel(s) channel in sample subject
        to selection(s). If there is only one variable and selection (each
        a string), a histogram of this combination is made for each channel and
        these are summed.
        If variables and selections are ordered iterables (which must have the 
        same length), channels must be an iterator of the same length as well, 
        a histogram is made for each (channels[i], variables[i], selections[i]),
        and these are summed. The idea is to allow, e.g., a plot of Z1 mass 
        regardless of channel.
        If binning has length 3, it is interpreted as [nbins, lowBin, highBin].
        Otherwise, it is interpreted as the edges of variably-sized bins. In 
        the case of variably sized bins, if perUnitWidth is True, each bin is 
        normalized according to its width so that the height is the counts per 
        x-axis unit.
        If scale is positive and 'data' is not in category or sample, gen 
        weighting is applied (see scaleHist() comment).
        If nameForLegend is a nonempty string, it is used as the legend text
        for the histogram. Otherwise, the category/sample name is used for 
        data, and the sample's prettyName is used for MC.
        '''
        if nameForLegend:
            prettyName = nameForLegend
        else:
            if self.isData(category):
                prettyName = category
            else:
                prettyName = sampleInfo[sample]['prettyName']

        histKWArgs = {
            'title' : prettyName,
            'sample' : sample, 
            'variable' : variables,
            'selection' : selections, 
            'category' : category,
            'channel' : channels,
            }
        if len(binning) == 3:
            h = self.WrappedHist(*binning, **histKWArgs)
        else:
            h = self.WrappedHist(binning, **histKWArgs)

        if isinstance(variables, str) and isinstance(selections, str):
            for ch in self.expandChannelsFromArg(channels):
                self.addToHist(h, category, sample, ch, variables, selections)

        elif len(variables) == len(selections):
            assert isinstance(channels, Sequence) and \
                len(channels) == len(variables), \
                "Channel, variable, and selections lists must match"
            for i in xrange(len(variables)):
                selection = selections[i]
                # weight appropriately
                if scale > 0.:
                    if weight:
                        if selection == "":
                            selection = "%s / abs(%s)"%(weight, weight)
                        else:
                            selection = "(%s / abs(%s)) * (%s)"%(weight, weight, selection)

                self.addToHist(h, category, sample, channels[i], variables[i],
                               selection)

        self.formatHist(h, **formatOpts)
        self.scaleHist(h, scale, perUnitWidth)

        return h


    def scaleHist(self, h, scale=1., perUnitWidth=True):
        '''
        If scale is negative, the histogram is scaled by -scale. If scale is 0,
        the histogram is normalized to 1. If scale is positive and the
        histogram is of Monte Carlo, it is scaled by 
        that factor, for its cross section and the total integrated luminosity.
        If the binning is not constant and perUnitWidth is True, bin content 
        and errors are normalized to be events per x-axis unit.
        '''
        if self.isData(h.getCategory()):
            scale = -1.

        if scale != -1.:
            # overall scale
            if scale > 0.:
                scale *= (self.intLumi * sampleInfo[h.getSample()]['xsec'] / sampleInfo[h.getSample()]['n'])
            elif scale < 0.:
                scale = abs(scale)
            else:
                scale = 1./h.Integral()
    
            h.Scale(scale)
            h.Sumw2()

        if perUnitWidth and not h.uniform():
            binUnit = getMinBinWidth(h)
            for iBin in xrange(1, h.nbins()+1):
                w = h.GetBinWidth(iBin)
                h.SetBinContent(iBin, h.GetBinContent(iBin) * binUnit / w)
                h.SetBinError(iBin, h.GetBinError(iBin) * sqrt(binUnit / w))
            h.Sumw2()

        return h
        

    def formatHist(self, h, **opts):
        '''
        With no keyword arguments, does standard formatting based on data or MC
        conventions. With keyword arguments, sets formatting variables (color
        etc.) accordingly.
        '''
        if self.isData(h.getCategory()):
            h.drawstyle = 'PE1'
        else:
            h.drawstyle = 'hist'
            h.fillstyle = 'solid'
            h.fillcolor = sampleInfo[h.getSample()]['color']
           
        for opt, val in opts.iteritems():
            setattr(h, opt, val)
 
        return h

    
    def formatGraph(self, g, **opts):
        '''
        With no keyword arguments, does standard formatting based on data or MC
        conventions. With keyword arguments, sets formatting variables (color
        etc.) accordingly.
        '''
        g.drawstyle = 'PE'
        g.legendstyle = 'LPE'
        if not self.isData(g.getCategory()):
            g.color = sampleInfo[g.getSample()]['color']
           
        for opt, val in opts.iteritems():
            setattr(g, opt, val)
 
        return g

    
    def makeCategoryStack(self, category, channel, variable, selection,
                          binning, scale=1., sortByMax=True):
        '''
        Makes a stack of all histograms from the samples in category by 
        passing parameters to self.makeHist().
        '''
        assert not self.isData(category), "You can only stack MC, not data!"
        hists = []
        for sample in self.ntuples[category]:
            hists.append(self.makeHist(category, sample, channel, variable, 
                                       selection, binning, scale))

        s = self.WrappedStack(self.orderForStack(hists, sortByMax),
                              category=category, variable=variable,
                              selection=selection)
        
        return s
                  
    
    def orderForStack(self, hists, sortByMax=True):
        '''
        Sort a list of histograms so that the largest is listed last.
        If sortByMax determines whether the sort variable is the histogram's
        largest or smallest bin.
        '''
        if sortByMax:
            binGetter = Hist.GetMaximumBin
        else:
            binGetter = Hist.GetMinimumBin
        key = lambda h: (sampleInfo[h.getSample()]['isSignal'], 
                         h.GetBinContent(binGetter(h)))

        hists.sort(key=key)

        return hists


    def fullPlot(self, name, channel, variable, selection, binning,
                 mcCategory='mc', dataCategory='data',
                 canvasX=800, canvasY=800, logy=False, styleOpts={}, 
                 ipynb=False, xTitle="", xUnits="GeV", yTitle="Events",
                 yUnits="", drawNow=False, outFile='', legParams={}, 
                 drawOpts={}):
        '''
        Make the "normal" plot, i.e. stack of MC compared to data points.
        Store it in self.drawings keyed to name.
        '''
        self.drawings[name] = self.Drawing(name, self.style, canvasX, canvasY, logy, ipynb)
        s = self.makeCategoryStack(mcCategory, channel, variable, selection,
                                   binning, 1.)
        if len(s):
            self.drawings[name].addObject(s)
        h = self.makeHist(dataCategory, dataCategory, channel, variable, selection,
                          binning)
        if h.GetEntries():
            self.drawings[name].addObject(h)

        self.drawings[name].draw(drawOpts, self.outdir+outFile, drawNow, 
                                 xTitle, xUnits, yTitle, yUnits, True, 
                                 legParams, True, self.intLumi, 
                                 h.GetEntries()==0)


    def makeEfficiency(self, category, sample, channels, variables, 
                       selections, selectionsTight, binning, weight,
                       formatOpts={}):
        '''
        Make an efficiency graph (with asymmetric error bars) where the 
        denominator is specified by selections and the numerator is specified
        by the logical and of selections and selectionsTight.
        '''
        eff = self. WrappedGraph(type='asymm', 
                                 title=sampleInfo[sample]['prettyName'], 
                                 sample=sample, variable=variables,
                                 selection=selections, category=category)

        denom = self.makeHist(category, sample, channels, variables, 
                              selections, binning, -1., weight, perUnitWidth=False)

        if isinstance(selections, str):
            selectionsNum = '(' + selections + ') && (' + selectionsTight + ')'
        # otherwise, assume lists of selections
        selectionsNum = map(lambda p: '(' + ') && ('.join(p) + ')', zip(selections, selectionsTight))
        num = self.makeHist(category, sample, channels, variables, 
                            selectionsNum, binning, -1., weight, perUnitWidth=False)

        eff.Divide(num, denom)
        self.formatGraph(eff, **formatOpts)

        return eff

