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

# include logging stuff first so other imports don't babble at us
import logging
from rootpy import log as rlog; rlog = rlog["/NtuplePlotter"]
# don't show most silly ROOT messages
logging.basicConfig(level=logging.WARNING)
rlog["/ROOT.TCanvas.Print"].setLevel(rlog.WARNING)
rlog["/ROOT.TUnixSystem.SetDisplay"].setLevel(rlog.ERROR)
rlog["/rootpy.tree.chain"].setLevel(rlog.WARNING)

from rootpy.io import root_open, File
from rootpy.plotting import Hist, HistStack, Graph, Canvas, Legend
from rootpy.plotting.utils import draw, get_band
from rootpy.ROOT import kTRUE, kFALSE
import rootpy.ROOT as ROOT
from rootpy.tree import Tree, TreeChain
from rootpy.plotting.base import Plottable
from rootpy import asrootpy, QROOT

from ZZPlotStyle import ZZPlotStyle
from ZZMetadata import sampleInfo
from ZZHelpers import makeNumberPretty

ROOT.gROOT.SetBatch(kTRUE)

_tempFileEnding = "_DSNPODKWMDNWCMD"

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
    if not issubclass(C, Plottable):
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


class NtuplePlotter(object):
    def __init__(self, channels, outdir='./plots', mcFiles=[], 
                 dataFiles=[], intLumi=-1.):
        self.intLumi = intLumi
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
        
        self.files = {}
        self.storeFilesFromArg(mcFiles, "mc")
        # don't open data files now; chain will do that
        self.files['data'] = {}

        self.ntuples = {"mc" : {}, 'data' : {'data':{}}}
        for category, samples in self.files.iteritems():
            if 'data' in category:
                for c in self.channels:
                    dataFileList = self.getFileNamesFromArg(dataFiles).values()
                    if len(dataFileList) > 1:
                        n, f = self.mergeDataFiles(c, dataFileList)
                        self.files['data'][c] = f
                        self.ntuples['data']['data'][c] = n
                    elif len(dataFileList) == 1:
                        self.files['data'] = { c : root_open(dataFileList[0]) for c in self.channels }
                        self.ntuples['data']['data'] = { c : self.files['data']['data'].Get('%s/final/Ntuple'%c) for c in self.channels }
                    else:
                        self.files['data'] = {}
                        self.ntuples['data']['data'] = {}
            else:
                for s in samples:
                    self.ntuples[category][s] = { c : samples[s].Get("%s/final/Ntuple"%c) for c in self.channels }

        # but different datasets might
            
        self.drawings = {}

        self.style = ZZPlotStyle()
                 

    def __del__(self):
        '''
        When we're done, delete any temporary root files we created.
        '''
        for f in os.listdir(os.getcwd()):
            if re.search(_tempFileEnding, f):
                os.remove(os.path.join(os.getcwd(), f))


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
                                          
        return { fi.split('/')[-1].rstrip('.root') : fi for fi in files }
                                          

    def mergeDataFiles(self, channel, files):
        '''
        Takes all data files, and for a given channel, combines the relevant
        ntuples into one big ntuple, removing redundant copies of the same
        event if an event appears in multiple files. 
        Returns the new ntuple and a temporary file it's stored in.
        Physics-based redundant row cleaning is assumed already done; that is,
        it is assumed that multiple copies of an event are strictly identical
        and it doesn't matter which is kept.
        '''
        tempFile = root_open("dataTEMP_%s%s.root"%(channel, _tempFileEnding), "recreate")
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
    WrappedStack = WrapPlottable(HistStack)


    class Drawing(object):
        '''
        Simple container for a canvas and all the stuff that is/should be 
        plotted on it.
        '''
        def __init__(self, title, style, width=1000, height=800, logy=False, ipynb=False):
            self.ipynb = ipynb
            if self.ipynb:
                self.c = rootnotes.canvas("x"+title, (width, height))
            else:
                self.c = Canvas(width, height, title=title)
            self.logy = logy
            self.c.cd()
            self.objects = []
            self.legObjects = []
            self.style = style
           
        def addObject(self, obj, addToLegend=True):
            '''
            Puts an object in the list of things to draw.
            addToLegend only counts for histograms, graphs, and stacks.
            '''
            if not isinstance(obj, Plottable):
                addToLegend = False

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

            self.objects.append(obj)
            
            if addToLegend:
                self.addToLegend(obj)

        def addToLegend(self, obj):
            if isinstance(obj, HistStack):
                for h in obj.GetHists():
                    self.addToLegend(h)
                return
            if not hasattr(obj, "sample"):
                raise AttributeError("%s doesn't know what sample it's "
                                     "from, so it can't be added to the "
                                     "legend."%obj.__name__)

            if sampleInfo[obj.getSample()]['isData']:
                obj.legendstyle = "LPE"
            else:
                obj.legendstyle = "F"
            self.legObjects.append(obj)

        def getMinBinWidth(self, obj):
            '''
            Get the width of the narrowest bin in any of the objects.
            '''
            if isinstance(obj, Sequence): # list, etc.
                return min(self.getMinBinWidth(ob) for ob in obj)
            if isinstance(obj, QROOT.TH1):
                return min(obj.GetBinWidth(b) for b in range(1,len(obj)-1))
            if isinstance(obj, HistStack):
                return self.getMinBinWidth(obj.hists)
            if isinstance(obj, Graph):
                return min(abs(obj[i].x-obj[i-1].x) for i in range(1,len(obj)))
            else:
                return float("Inf")

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
                else:
                    minBinWidth = self.getMinBinWidth(self.objects)
                    if minBinWidth != 1:
                        yTitle = "%s / %s"%(yTitle, makeNumberPretty(minBinWidth))
                        if xUnits:
                            yTitle = "%s %s"%(yTitle, xUnitsText if '\\' in yTitle else xUnits)
            else:
                yTitle = None
            
            return xTitle, yTitle

        def draw(self, drawOpts={}, outFile="", drawNow=False, 
                 xTitle="", xUnits="GeV", yTitle="Events", yUnits="",
                 drawLeg=True, legParams={}, stackErr=True,
                 intLumi=40.03, simOnly=False):
            '''
            opts (dict): passed directly to rootpy.plotting.utils.draw
            outFile (str): location to save plot (not saved if empty str)
            drawNow (bool): paint on-screen now?
            drawLeg (bool): paint a legend?
            legParams (dict): passed directly to rootpy.plotting.Legend constructor
            stackErr (bool): draw black hashed region to indicate MC stack error bars?
            '''
            if drawLeg and len(self.legObjects):
                if not len(legParams):
                    if hasattr(self, "legParams"):
                        legParams=self.legParams
                    else:
                        legParams = {
                            'entryheight' : 0.03,
                            'entrysep' : 0.01,
                            'leftmargin' : 0.5,
                            'topmargin' : 0.05,
                            'rightmargin' : 0.05,
                            'textsize' : 0.03,
                        }
                self.leg = Legend(self.legObjects, self.c, **legParams)

            if stackErr:
                for ob in self.objects:
                    if isinstance(ob, HistStack) and len(ob):
                        self.objects.append(self.getStackErrors(ob))

            if drawNow and ROOT.gROOT.IsBatch():
                ROOT.gROOT.SetBatch(kFALSE)
            if not drawNow and not ROOT.gROOT.IsBatch():
                ROOT.gROOT.SetBatch(kTRUE)

            # make a copy to avoid some weird kind of namespace contamination
            opts = {k:v for k,v in drawOpts.iteritems()}

            titleX, titleY = self.getAxisTitles(xTitle, xUnits, yTitle, yUnits)
            if titleX and 'xtitle' not in opts:
                opts['xtitle'] = titleX
            if titleY and 'ytitle' not in opts:
                opts['ytitle'] = titleY

            draw(self.objects, self.c, logy=self.logy, **opts)

            if drawLeg:
                self.leg.Draw("SAME")
            
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
                print "%s is not a category of ntuple, nothing to draw!"%category
                return False
            elif sample not in self.ntuples[category]:
                print "%s is not a sample in category %s, nothing to draw!"%(sample, category)
                return False
            elif channel not in self.ntuples[category][sample]:
                print "No channel %s for sample %s, nothing to draw!"%(channel, sample)
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
                 nbins, lo, hi, scale=1, weight='', formatOpts={}):
        '''
        Make a histogram of variable(s) in channel(s) channel in sample subject
        to selection(s). Histogram will have nbins, going from lo to hi.
        If there is only one variable and selection (each a string),
        a histogram of this combination is made for each channel and these are
        summed.
        If variables and selections are ordered iterables (which must have the 
        same length), channels must be an iterator of the same length as well, 
        a histogram is made for each (channels[i], variables[i], selections[i]),
        and these are summed. The idea is to allow, e.g., a plot of Z1 mass 
        regardless of channel.
        '''
        # weight appropriately
#         if scale > 0.:
#             if selection == "":
#                 selection = "GenWeight"
#             else:
#                 selection = "GenWeight*(%s)"%selection

        h = self.WrappedHist(nbins, lo, hi, 
                             title=sampleInfo[sample]['prettyName'], 
                             sample=sample, variable=variables,
                             selection=selections, category=category)

        if isinstance(variables, str) and isinstance(selections, str):
            for ch in self.expandChannelsFromArg(channels):
                self.addToHist(h, category, sample, ch, variables, selections)

        elif len(variables) == len(selections):
            assert isinstance(channels, Sequence) and \
                len(channels) == len(variables), \
                "Channel, variable, and selections lists must match"
            for i in xrange(len(variables)):
                self.addToHist(h, category, sample, channels[i], variables[i],
                               selections[i])

        self.formatHist(h, **formatOpts)
        self.scaleHist(h, scale)

        return h


    def scaleHist(self, h, scale=1.):
        '''
        If scale is negative, the histogram is scaled by -scale. If scale is 0,
        the histogram is normalized to 1. If scale is positive, the histogram
        (assumed to be MC unless 'data' is in category or sample) is scaled by 
        that factor, for its cross section and the total integrated luminosity.
        '''
        if 'data' in h.getCategory()  or 'data' in h.getSample():
            scale = -1.

        # overall scale
        if scale > 0.:
            scale *= (self.intLumi * sampleInfo[h.getSample()]['xsec'] / sampleInfo[h.getSample()]['n'])
        elif scale < 0.:
            scale = abs(scale)
        else:
            scale = 1./h.Integral()

        h.Scale(scale)
        h.Sumw2()

        return h
        

    def formatHist(self, h, **opts):
        '''
        With no keyword arguments, does standard formatting based on data or MC
        conventions. With keyword arguments, sets formatting variables (color
        etc.) accordingly.
        '''
        if sampleInfo[h.getSample()]['isData']:
            h.drawstyle = 'PEX0'
        else:
            h.drawstyle = 'hist'
            h.fillstyle = 'solid'
            h.fillcolor = sampleInfo[h.getSample()]['color']
           
        for opt, val in opts.iteritems():
            setattr(h, opt, val)
 
        return h

    
    def makeCategoryStack(self, category, channel, variable, selection, nbins,
                          lo, hi, scale=1., sortByMax=True):
        '''
        Makes a stack of all histograms from the samples in category by 
        passing parameters to self.makeHist().
        '''
        hists = []
        for sample in self.ntuples[category]:
            hists.append(self.makeHist(category, sample, channel, variable, 
                                       selection, nbins, lo, hi, scale))

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
        key = lambda h: h.GetBinContent(binGetter(h))

        hists.sort(key=key)

        return hists


    def fullPlot(self, name, channel, variable, selection, nbins, lo, hi,
                 canvasX=800, canvasY=800, logy=False, styleOpts={}, 
                 ipynb=False, xTitle="", xUnits="GeV", yTitle="Events",
                 yUnits="", drawNow=False, outFile='', legParams={}, 
                 drawOpts={}):
        '''
        Make the "normal" plot, i.e. stack of MC compared to data points.
        Store it in self.drawings keyed to name.
        '''
        self.drawings[name] = self.Drawing(name, self.style, canvasX, canvasY, logy, ipynb)
        s = self.makeCategoryStack("mc", channel, variable, selection,
                                   nbins, lo, hi, 1.)
        if len(s):
            self.drawings[name].addObject(s)
        h = self.makeHist('data', 'data', channel, variable, selection,
                          nbins, lo, hi)
        if h.GetEntries():
            self.drawings[name].addObject(h)

        self.drawings[name].draw(drawOpts, self.outdir+outFile, drawNow, 
                                 xTitle, xUnits, yTitle, yUnits, True, 
                                 legParams, True, self.intLumi, 
                                 h.GetEntries()==0)


