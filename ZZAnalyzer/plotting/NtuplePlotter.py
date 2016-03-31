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

from rootpy.io import root_open, File, DoesNotExist
from rootpy.plotting import Hist, Hist2D, Hist3D, HistStack, Graph, Canvas, Legend, Pad
from rootpy.plotting.hist import _Hist, _Hist2D, _Hist3D
from rootpy.plotting.graph import _Graph1DBase
from rootpy.plotting.utils import draw, get_band
from rootpy.ROOT import kTRUE, kFALSE, TLine
from rootpy.ROOT import gROOT, TBox
from rootpy.tree import Tree, TreeChain, Cut
from rootpy.plotting.base import Plottable
from rootpy import asrootpy, QROOT

from PlotStyle import PlotStyle
from ZZAnalyzer.metadata import sampleInfo, sampleGroups
from ZZAnalyzer.utils.helpers import makeNumberPretty, parseChannels

gROOT.SetBatch(kTRUE)

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
            new._extraVars = []
            for arg, fun in metaInfoDict.iteritems():
                new._extraVars.append(arg)
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

        # def transferMetaInfo(self, other):
        #     '''
        #     Take all of this object's custom metadata and stick it in a 
        #     different thing.
        #     '''
        #     for arg in self._extraVars:
        #         val = getattr(self, "get%s%s"%(arg[0].upper(), arg[1:]))()
        #         setattr(other, arg, val)
        #         setattr(other,
        #                 "get%s%s"%(arg[0].upper(), arg[1:]),
        #                 MethodType(returnThing(arg), other))
            
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
    else:
        return float("Inf")


class NtuplePlotter(object):
    def __init__(self, channels, outdir='./plots', mcFiles={}, 
                 dataFiles={}, intLumi=-1.):
        self.intLumi = float(intLumi)
        if not outdir or outdir[:1] == './':
            self.outdir = os.path.join(os.environ['zza'], 'ZZAnalyzer', outdir[2:])
        elif '$zza' in outdir:
            self.outdir = outdir.replace('$zza', os.environ['zza'])
        else:
            self.outdir = outdir
        if self.outdir[-1] != '/':
            self.outdir += '/'
        makeDirectory(self.outdir)

        self.channels = parseChannels(channels)
        
        self.dataOrMC = {} # True if data, False if MC

        self.files = {}
        for cat, files in mcFiles.iteritems():
            self.dataOrMC[cat] = False
            self.storeMCFileNamesFromArg(files, cat)
        # don't open data files now; chain will do that
        for cat in dataFiles:
            self.dataOrMC[cat] = True
            self.files[cat] = {}

        self.sumOfWeights = {} # for MC

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
                self.sumOfWeights[cat] = {}
                for sample, fileNames in samples.iteritems():
                    self.sumOfWeights[cat][sample] = self.getWeightSum(fileNames, sample)
                    if len(fileNames) == 1:
                        self.files[cat][sample] = root_open(fileNames[0])
                        self.ntuples[cat][sample] = { c : self.files[cat][sample].Get("%s/final/Ntuple"%c) for c in self.channels }
                    else:
                        self.ntuples[cat][sample] = { c : TreeChain("%s/final/Ntuple"%c, fileNames) for c in self.channels }

        self.drawings = {}

        self.style = PlotStyle()
                 

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
        
    # string ends with an underscore followed by an integer
    subSampleEnding = re.compile('_\d+$') 
    def storeMCFileNamesFromArg(self, files, category):
        '''
        Extract MC file names from a string, and store them in lists for each
        sample. A file name like 'XXX_N.root' where N is some integer, is 
        taken to be one of several files in sample XXX.
        '''
        if category not in self.files:
            self.files[category] = {}
            
        for k,f in self.getFileNamesFromArg(files).iteritems():
            sampleName = self.subSampleEnding.sub("", k)
            if sampleName in self.files[category]:
                self.files[category][sampleName].append(f)
            else:
                self.files[category][sampleName] = [f]


    def getFileNamesFromArg(self, files):
        '''
        If files is a string, it is interpreted as a comma-separated list of 
        wildcards pointing to root files, or directories containing root files
        (which are assumed to have names ending in '.root'). Then a dict is
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

        assert files, "No files found for path %s !"%f
                                          
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
        

    def printPassingEvents(self, category, sample=''):
        '''
        If sample is blank, it is taken to be the same as category (as for
        data).
        '''
        if not sample:
            sample = category

        for channel, ntuple in self.ntuples[category][sample].iteritems():
            passing = set()
            for row in ntuple:
                passing.add((row.run, row.lumi, row.evt))

            print "%s (%d):"%(channel, ntuple.GetEntries())
            for ev in sorted(sorted(sorted(passing, key=lambda t: t[2]), key=lambda u: u[1]), key=lambda v: v[0]):
                print "    {}:{}:{}".format(*ev)
            print ''


    def getWeightSum(self, inFiles, sample):
        '''
        Take the list of input file names for a sample, and use the metaInfo 
        trees to calculate
        the sum of the MC weights originally generated. This is assumed to be 
        the same for all channels, so they are tried in a ~random order until
        an appropriate tree is found. If none is found, the value from 
        ZZMetadata.py is used, but this is dangerous because I don't trust
        myself to keep it up to date.
        '''
        for ch in self.channels:
            if len(inFiles) == 1:
                try:
                    with root_open(inFiles[0]) as f:
                        metaTree = f.Get("%s/metaInfo"%ch)
                        return metaTree.Draw('1', 'summedWeights').Integral()
                except DoesNotExist:
                    continue
            else:
                try:
                    metaChain = TreeChain('%s/metaInfo'%ch, inFiles)
                    return metaChain.Draw('1', 'summedWeights').Integral()
                except DoesNotExist:
                    continue
            
        else: # no tree in any channel
            return sampleInfo[sample]['sumW']


    WrappedHist = WrapPlottable(Hist)
    WrappedHist2 = WrapPlottable(Hist2D)
    WrappedHist3 = WrapPlottable(Hist3D)
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
            
        def addObject(self, obj, addToLegend=True, legendStyle='', legendName=''):
            '''
            Puts an object in the list of things to draw.
            addToLegend only counts for histograms, graphs, and stacks.
            If legendStyle is non-empty, that style is used instead of
            "LPE" for data and "F" for MC.
            If legendName is non-empty, that name is used instead of "data" for
            data or the ZZMetadata default for MC. For a HistStack, it should
            be an iterable of (possibly empty) strings with length equal to the
            number of histograms.
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

            if isinstance(obj, (_Hist, _Graph1DBase)):
                self.objects.append(obj)
            elif isinstance(obj, HistStack):
                if isinstance(asrootpy(obj.GetStack().Last()), _Hist):
                    self.objects.append(obj)
                else:
                    self.objectsAux.append(obj)
            else:
                self.objectsAux.append(obj)
            
            if addToLegend:
                self.addToLegend(obj, legendStyle, legendName)

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

        def addRatio(self, num, denom, height=0.23, ratioMin=0.5, ratioMax=1.5,
                     bottomMargin=0.3, topMargin=0.06, yTitle=""):
            self.addPadBelow(height, bottomMargin, topMargin)
            if isinstance(num, HistStack):
                for h in num.hists:
                    h.sumw2()
                hNum = sum(num.hists)
            else:
                hNum = num.clone()
            hNum.sumw2()
            numerator = Graph(hNum)
            if isinstance(denom, HistStack):
                hDenom = sum(denom.hists)
            else:
                hDenom = denom.clone()
            hDenom.sumw2()
            denominator = Graph(hDenom)

            nRemoved = 0
            for i in range(numerator.GetN()):
                if hDenom[i+1].value <= 0. or hNum[i+1].value <= 0.:
                    numerator.RemovePoint(i - nRemoved)
                    denominator.RemovePoint(i - nRemoved)
                    nRemoved += 1

            ratio = numerator / denominator

            ratio.drawstyle = 'PE'
            ratio.color = 'black'
            opts = {
                'xaxis':ratio.xaxis,
                'yaxis':ratio.yaxis,
                'ylimits':(ratioMin,ratioMax),
                'ydivisions':5,
                }

            unity = TLine(hNum.lowerbound(), 1, hNum.upperbound(), 1)
            unity.SetLineStyle(7)

            self.paintPad(self.pads[1], [ratio], [unity], opts, "", "", 
                          yTitle, "", perUnitWidth=False)

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

        def addToLegend(self, obj, legendStyle='', legendName=''):
            '''
            If legendStyle is a non-empty string, that style is used.
            Otherwise, the style is "F" for MC and "LPE" for data.
            If legendName is non-empty, that name is used instead of "data" for
            data or the ZZMetadata default for MC. For a HistStack, it should
            be an iterable of (possibly empty) strings with length equal to the
            number of histograms.
            '''
            if obj.GetTitle() == '___DONOTADDTOLEGEND': return # don't ask
            if isinstance(obj, _Hist2D) or isinstance(obj, _Hist3D): 
                # no legend for 2- or 3D Hist
                return
            if isinstance(obj, HistStack):
                if (not bool(legendName)) or isinstance(legendName, str):
                    legendName = ['' for h in obj]
                else:
                    assert len(legendName) == len(obj), "Must have the same number of names as histograms."
                for h, name in zip(obj, legendName):
                    self.addToLegend(h, '', name)
                return
            # if not hasattr(obj, "sample"):
            #     raise AttributeError("%s doesn't know what sample it's "
            #                          "from, so it can't be added to the "
            #                          "legend."%obj.__name__)

            if legendStyle:
                obj.legendstyle = legendStyle
            elif not hasattr(obj, 'legendstyle'):
                if obj.getIsData() and obj.getIsSignal():
                    obj.legendstyle = "LPE"
                else:
                    obj.legendstyle = "F"

            if legendName:
                obj.SetTitle(legendName)

            self.legObjects.append(obj)

        def getAxisTitles(self, xTitle, xUnits, yTitle, yUnits, perUnitWidth=True):
            '''
            Put appropriate units on axis labels, including " / X GeV" if 
            applicable for the y axis.
            If perUnitWidth evaluates to True and the binning is not uniform, 
            the y-axis title will say something like 'Title / xAxisBinWidth'.
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
                elif perUnitWidth and self.minBinWidth != -1:
                    yTitle = "%s / %s"%(yTitle, makeNumberPretty(self.minBinWidth, 2))
                    if xUnits:
                        yTitle = "%s %s"%(yTitle, xUnitsText if '\\' in yTitle else xUnits)
            else:
                yTitle = None
            
            return xTitle, yTitle

        def blindData(self, h, (lo, hi)):
            '''
            Zero any bins that have any overlap with the range (lo, hi).
            '''
            for ib, (elo, ehi) in enumerate(zip(h.xedgesl(), h.xedgesh())):
                if (elo >= lo and elo < hi) or (ehi > lo and ehi <= hi):
                    h[ib+1].value = 0
                    h[ib+1].error = 0

            h.Sumw2()

        def getBlindBox(self, (lo, hi), (xMin, xMax, yMin, yMax)):
            '''
            Return a box to blind a plot with these axis ranges from lo to hi.
            '''
            b = TBox(max(lo, xMin), yMin, min(hi, xMax), yMax)
            b.SetFillColor(1)
            b.SetFillStyle(3002)
            # SetFillColorAlpha seems to only work for pdf, not png images
            #b.SetFillColorAlpha(2, 0.35)
            return b

        def paintPad(self, pad, objects, objectsAux, drawOpts={}, xTitle="", 
                     xUnits="GeV", yTitle="Events", yUnits="", logy=False,
                     legObjects=[], legParamsOverride={}, stackErr=True, 
                     perUnitWidth=True, legSolid=False, widthInYTitle=False,
                     mcSystFracUp=0., mcSystFracDown=0., blinding=[]):
            '''
            Draws objects (Hists, HistStacks, and Graphs) and objectsAux
            (anything else) on pad.
            drawLeg (bool): paint a legend?
            legParamsOverride (dict): passed directly to rootpy.plotting.Legend
                                      constructor
            stackErr (bool): draw black hashed region to indicate MC stack 
                             error bars?
            legSolid (bool): Make the legend background a solid white box 
                             instead of transparent
            mcSystFrac* (float): systematic errors on MC yield given as a 
                                 fraction (i.e. 0.1 for 10%)
            blinding (list of length-2 iterables): Blind on this list of 
                                                   (xMin, xMax)
            '''
            if legObjects:
                legParams = {
                    'entryheight' : 0.03,
                    'entrysep' : 0.01,
                    'leftmargin' : 0.5,
                    'topmargin' : 0.05,
                    'rightmargin' : 0.05,
                    'textsize' : 0.033,
                    }
                legParams.update(legParamsOverride)

                leg = Legend(legObjects[::-1], pad, **legParams)
                
                if legSolid:
                    leg.SetFillStyle(1001)

            if stackErr:
                for ob in objects:
                    if isinstance(ob, HistStack) and len(ob):
                        objects.append(self.getStackErrors(ob, mcSystFracUp,
                                                           mcSystFracDown)
                                       )

            yTitlePerUnitWidth = widthInYTitle or \
                (perUnitWidth and not any(isinstance(obX, _Hist2D) or isinstance(obX, _Hist3D) for obX in objectsAux))

            # make a copy to avoid some weird kind of namespace contamination
            opts = {k:v for k,v in drawOpts.iteritems()}

            titleX, titleY = self.getAxisTitles(xTitle, xUnits, yTitle, yUnits, yTitlePerUnitWidth)
            if titleX and 'xtitle' not in opts:
                opts['xtitle'] = titleX
            if titleY and 'ytitle' not in opts:
                opts['ytitle'] = titleY

            toDraw = []
            for iObj, obj in enumerate(objects):
                if isinstance(obj, _Hist) and obj.getIsData():
                    # Apply blinding if any
                    for b in blinding:
                        self.blindData(obj, b)

                    # An unweighted histogram should be drawn with Poisson errors. 
                    # Since that doesn't seem to work in rootpy (:-(), we'll replace 
                    # it with a TGraphAsymmErrors that has the correct error bars
                    if obj.GetEffectiveEntries() == obj.GetEntries():
                        # if this is the first item, make sure the axes don't get messed up
                        if iObj == 0:
                            toDraw.append(obj.empty_clone())
                        pois = obj.poisson_errors()
                        pois.drawstyle = "PE"
                        pois.linecolor = obj.linecolor
                        pois.markercolor = obj.markercolor
                        toDraw.append(pois)
                    else:
                        toDraw.append(obj)
                else:
                    toDraw.append(obj)

            auxDrawOpt = '' # draw option for all auxiliary plotted objects
            axisRanges = (-1000.,1000.,-1000.,1000.)
            if(toDraw):
                (xaxis, yaxis), axisRanges = draw(toDraw, pad, logy=logy, **opts)
                auxDrawOpt = "SAME"
                pad.xaxis = xaxis
                pad.yaxis = yaxis

            for blind in blinding:
                objectsAux.append(self.getBlindBox(blind, axisRanges))

            pad.cd()
            for obj in objectsAux:
                # if isinstance(obj, (_Hist2D, _Hist3D, HistStack)):
                #     if titleX:
                #         obj.xaxis.title = titleX
                #     xaxis = obj.xaxis
                #     if titleY:
                #         obj.yaxis.title = titleY
                #     yaxis = obj.yaxis

                obj.Draw(auxDrawOpt)
                auxDrawOpt = "SAME"

            if legObjects:
                leg.Draw(auxDrawOpt)

            pad.Draw()

        def draw(self, drawOpts={}, outFile="", drawNow=False, 
                 xTitle="", xUnits="GeV", yTitle="Events", yUnits="",
                 drawLeg=True, legParamsOverride={}, stackErr=True,
                 intLumi=40.03, simOnly=False, perUnitWidth=True,
                 legSolid=False, widthInYTitle=False,
                 mcSystFracUp=0., mcSystFracDown=0.,
                 blinding=[]):
            '''
            opts (dict): passed directly to rootpy.plotting.utils.draw
            outFile (str): location to save plot (not saved if empty str)
            drawNow (bool): paint on-screen now?
            drawLeg (bool): paint a legend?
            legParams (dict): passed directly to rootpy.plotting.Legend 
                              constructor
            stackErr (bool): draw black hashed region to indicate MC stack 
                             error bars?
            perUnitWidth affects only the y-axis title
            legSolid (bool): Make the legend background a solid white box 
                             instead of transparent
            widthInYTitle (bool): Append " / [binsize] [units]" to y axis title
            mcSystFrac* (float): systematic errors on MC yield given as a 
                                 fraction (i.e. 0.1 for 10%)
            blinding (list of length-2 iterables): Blind on this list of 
                                                   (xMin, xMax)
            '''
            if drawNow and gROOT.IsBatch():
                gROOT.SetBatch(kFALSE)
            if not drawNow and not gROOT.IsBatch():
                gROOT.SetBatch(kTRUE)

            legObjs = self.legObjects if drawLeg else []
            
            self.paintPad(self.mainPad(), self.objects, self.objectsAux, drawOpts, 
                          xTitle, xUnits, yTitle, yUnits, self.logy, legObjs, 
                          legParamsOverride, stackErr, perUnitWidth, legSolid,
                          widthInYTitle, mcSystFracUp, mcSystFracDown,
                          blinding=blinding)

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

        def getStackErrors(self, stack, systErrFracUp=0.,systErrFracDown=0.):
            '''
            Make a hatched black band to represent the error bars on stack.
            Systematic errors are taken to be systErrFracX x bin height and 
            are added to the statistical error in quadrature.
            '''
            total = sum(stack.hists)
            total.sumw2()
            lo = total.empty_clone()
            hi = total.empty_clone()
            for i in xrange(1,total.GetNbinsX()+1):
                errUp = sqrt(total.GetBinErrorUp(i) ** 2 + 
                             (total[i].value * systErrFracUp) ** 2)
                errDn = sqrt(total.GetBinErrorLow(i) ** 2 + 
                             (total[i].value * systErrFracDown) ** 2)
                lo[i].value = total[i].value - errDn
                hi[i].value = total[i].value + errUp
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
                 binning, scale=1, weights='', formatOpts={}, perUnitWidth=True,
                 nameForLegend='', isBackground=False):
        '''
        Make a histogram of variable(s) in channel(s) channel in sample subject
        to selection(s). If there is only one variable and selection (each
        a string), a histogram of this combination is made for each channel and
        these are summed.
        If variables and selections are ordered iterables (which must have the 
        same length), channels must be an iterator of the same length as well, 
        a histogram is made for each (channels[i], variables[i], selections[i]),
        and these are summed. The idea is to allow, e.g., a plot of Z1 mass 
        regardless of channel. If either is a string, it is applied to all 
        channels.
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
        If weights is a string, it is applied to all channels. If it is an 
        iterable of strings, each item is expected to correspond to one channel
        as with variables and selections.
        isBackground forces the histogram to be formatted like MC even if it 
        is data.
        '''
        if nameForLegend:
            prettyName = nameForLegend
        else:
            if self.isData(category):
                if category == 'data':
                    prettyName = '\\text{Data}'
                else:
                    prettyName = category
            else:
                prettyName = sampleInfo[sample]['prettyName']

        if self.isData(category):
            isSignal = not isBackground
        else:
            isSignal = sampleInfo[sample]['isSignal']

        histKWArgs = {
            'title' : prettyName,
            'sample' : sample, 
            'variable' : variables,
            'selection' : selections, 
            'category' : category,
            'channel' : channels,
            'isData' : self.isData(category),
            'isSignal' : isSignal,
            }
        if len(binning) == 3 or (len(binning) == 1 and isinstance(binning[0], Sequence)):
            h = self.WrappedHist(*binning, **histKWArgs)
            if self.isData(category) and isSignal:
                h.legendstyle = 'LPE'
            else:
                h.legendstyle = "F"
        else:
            h = self.WrappedHist(binning, **histKWArgs)

        channels = parseChannels(channels)

        if isinstance(variables, str):
            variables = [variables for c in channels]
        if isinstance(selections, str):
            selections = [selections for c in channels]
        if isinstance(weights, str):
            weights = [weights for c in channels]

        assert len(channels) == len(variables) and \
            len(variables) == len(selections) and\
            len(selections) == len(weights), \
                "Channel, variable, selection, and weight lists must match"
        for i in xrange(len(variables)):
            variable = variables[i]
            selection = selections[i]
            weight = weights[i]
            channel = channels[i]
            # weight appropriately
            if scale > 0.:
                if weight:
                    if selection == "":
                        selection = weight
                    else:
                        selection = "({0})*({1})".format(weight,selection)
                        
            self.addToHist(h, category, sample, channel, variable,
                           selection)

        self.formatHist(h, background=isBackground, **formatOpts)
        self.scaleHist(h, scale, perUnitWidth)

        return h


    def makeGroupHist(self, category, samples, *args, **kwargs):
        '''
        For a few samples in a category (assumed to all be in the same group),
        make a single combined histogram for the group, scaling each sample 
        correctly, etc.
        args and kwargs are all makeHist() arguments except category and 
        sample.
        '''
        group = sampleInfo[samples[0]]['group']
        sampleHists = [self.makeHist(category, s, *args, **kwargs) for s in samples]
        for s in sampleHists:
            s.sumw2()
        histKWArgs = {
            'title' : sampleGroups[group]['prettyName'],
            'group' : group,
            'sample' : samples,
            'variable' : sampleHists[0].getVariable(),
            'selection' : sampleHists[0].getSelection(), 
            'category' : category,
            'channel' : sampleHists[0].getChannel(),
            'isData' : self.isData(category),
            'isSignal' : sampleHists[0].getIsSignal(),
            }
        h = self.WrappedHist(sampleHists[0].empty_clone(), **histKWArgs)

        for s in sampleHists:
            h.Add(s)
        h.sumw2()

        h.drawstyle = 'hist'
        h.fillstyle = 'solid'
        h.fillcolor = sampleGroups[group]['color']
        h.linecolor = 'black'
        h.legendstyle = "F"

        return h


    def makeHist2(self, category, sample, channels, variables, selections, 
                  binning, scale=1., weights='', formatOpts={}):
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
        The binning is passed directly to Rootpy's Hist2D constructor.
        If weights is a string, it is applied to all channels. If it is an 
        iterable of strings, each item is expected to correspond to one channel
        as with variables and selections.
        '''
        if self.isData(category):
            prettyName = category
        else:
            prettyName = sampleInfo[sample]['prettyName']

        if self.isData(category):
            isSignal = True
        else:
            isSignal = sampleInfo[sample]['isSignal']

        histKWArgs = {
            'title' : prettyName,
            'sample' : sample, 
            'variable' : variables,
            'selection' : selections, 
            'category' : category,
            'isSignal' : isSignal,
            }
        h = self.WrappedHist2(*binning, **histKWArgs)

        channels = parseChannels(channels)

        if isinstance(variables, str):
            variables = [variables for c in channels]
        if isinstance(selections, str):
            selections = [selections for c in channels]
        if isinstance(weights, str):
            weights = [weights for c in channels]

        assert len(channels) == len(variables) and \
            len(variables) == len(selections) and\
            len(selections) == len(weights), \
                "Channel, variable, selection, and weight lists must match"

        for i in xrange(len(variables)):
            variable = variables[i]
            selection = selections[i]
            weight = weights[i]
            channel = channels[i]
            # weight appropriately
            if weight:
                if selection == "":
                    selection = weight
                else:
                    selection = "({0})*({1})".format(weight,selection)

            self.addToHist(h, category, sample, channels[i], variables[i],
                           selection)

        self.formatHist2(h, **formatOpts)
        self.scaleHist2(h, scale)

        return h


    def makeHist3(self, category, sample, channels, variables, selections, 
                  binning, scale=1., weights='', formatOpts={}):
        '''
        Make a 3D histogram of variable(s) in channel(s) channel in sample subject
        to selection(s). If there is only one variable and selection (each
        a string), a histogram of this combination is made for each channel and
        these are summed.
        If variables and selections are ordered iterables (which must have the 
        same length), channels must be an iterator of the same length as well, 
        a histogram is made for each (channels[i], variables[i], selections[i]),
        and these are summed. The idea is to allow, e.g., a plot of Z1 mass 
        regardless of channel.
        The binning is passed directly to Rootpy's Hist3D constructor.
        If weight is a string, it is applied to all channels. If it is an 
        iterable of strings, each item is expected to correspond to one channel
        as with variables and selections.
        '''
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
            }
        h = self.WrappedHist3(*binning, **histKWArgs)

        channels = parseChannels(channels)

        if isinstance(variables, str):
            variables = [variables for c in channels]
        if isinstance(selections, str):
            selections = [selections for c in channels]
        if isinstance(weights, str):
            weights = [weights for c in channels]

        assert len(channels) == len(variables) and \
            len(variables) == len(selections) and\
            len(selections) == len(weights), \
                "Channel, variable, selection, and weight lists must match"

        for i in xrange(len(variables)):
            variable = variables[i]
            selection = selections[i]
            weight = weights[i]
            channel = channels[i]
            # weight appropriately
            if weight:
                if selection == "":
                    selection = weight
                else:
                    selection = "({0})*({1})".format(weight,selection)

            self.addToHist(h, category, sample, channels[i], variables[i],
                           selection)

        self.formatHist3(h, **formatOpts)
        self.scaleHist3(h, scale)

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
                scale *= (self.intLumi * sampleInfo[h.getSample()]['xsec'] / self.sumOfWeights[h.getCategory()][h.getSample()])
                if 'kFactor' in sampleInfo[h.getSample()]:
                    scale *= sampleInfo[h.getSample()]['kFactor']
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
        

    def scaleHist2(self, h, scale=1.):
        return self.scaleHist(h, scale, False)


    def scaleHist3(self, h, scale=1.):
        return self.scaleHist(h, scale, False)


    def formatHist(self, h, **opts):
        '''
        With no keyword arguments, does standard formatting based on data or MC
        conventions. With keyword arguments, sets formatting variables (color
        etc.) accordingly.
        '''
        if self.isData(h.getCategory()) and not opts.get('background', False):
            h.drawstyle = 'PE1'
        else:
            h.drawstyle = 'hist'
            h.fillstyle = 'solid'
            if self.isData(h.getCategory()):
                h.fillcolor = '#669966'
            else:
                h.fillcolor = sampleInfo[h.getSample()]['color']
           
        for opt, val in opts.iteritems():
            setattr(h, opt, val)
 
        return h

    
    def formatHist2(self, h, **opts):
        '''
        With no keyword arguments, makes a temperature plot.
        With keyword arguments, sets formatting variables (color
        etc.) accordingly.
        '''
        h.drawstyle = 'COLZ'
           
        for opt, val in opts.iteritems():
            setattr(h, opt, val)
 
        return h

    
    def formatHist3(self, h, **opts):
        '''
        With no keyword arguments, does nothing.
        With keyword arguments, sets formatting variables (color
        etc.) accordingly.
        '''
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

    
    def makeStack(self, category, samples, channel, variable, selection,
                  binning, scale=1., weight='', sortByMax=True, 
                  perUnitWidth=True, extraHists=[]):
        '''
        Makes a stack of histograms from several samples from the same category
        by passing parameters to self.makeHist().
        If extraHists are specified, these hists are also stacked.
        '''
        hists = []
        groups = {}
        for sample in samples:
            if 'group' in sampleInfo[sample]:
                group = sampleInfo[sample]['group']
                if group in groups:
                    groups[group].append(sample)
                else:
                    groups[group] = [sample]
            else:
                hists.append(self.makeHist(category, sample, channel, variable, 
                                           selection, binning, scale, weight, 
                                           perUnitWidth=perUnitWidth))

        for group in groups:
            hists.append(self.makeGroupHist(category, groups[group], channel,
                                            variable, selection, binning, 
                                            scale, weight, 
                                            perUnitWidth=perUnitWidth))

        hists = extraHists + self.orderForStack(hists, sortByMax)

        # workaround for bizarre ROOT bug
        emptyHist = hists[0].empty_clone(title="___DONOTADDTOLEGEND") #Hist([e for e in hists[0]._edges(0)], title='___DONOTADDTOLEGEND') #
        hists.append(emptyHist)

        s = self.WrappedStack(hists,
                              category=category, variable=variable,
                              selection=selection, sample=samples)
        s.drawstyle = 'histnoclear'
        
        return s
                  
    
    def makeCategoryStack(self, category, channel, variable, selection,
                          binning, scale=1., weight='', sortByMax=True, 
                          perUnitWidth=True, extraHists=[]):
        '''
        Makes a stack of all histograms from the samples in category by 
        passing parameters to self.makeStack() (which in turn passes them
        to self.makeHist()).
        If extraHists are specified, these hists are also stacked.
        '''
        assert not self.isData(category), "You can only stack MC, not data!"
        samples = self.ntuples[category].keys()

        return self.makeStack(category, samples, channel, variable, 
                              selection, binning, scale, weight, sortByMax,
                              perUnitWidth, extraHists)

    
    def makeStack2(self, category, samples, channel, variable, selection,
                   binning, scale=1., weight='', sortByMax=True):
        '''
        Makes a stack of 2D histograms from samples in the same category by 
        passing parameters to self.makeHist2().
        '''
        hists = []
        for sample in samples:
            hists.append(self.makeHist2(category, sample, channel, variable, 
                                        selection, binning, scale, weight))

        s = self.WrappedStack(self.orderForStack(hists, sortByMax),
                              category=category, variable=variable,
                              selection=selection)
        
        return s
                  
    
    def makeCategoryStack2(self, category, channel, variable, selection,
                           binning, scale=1., weight='', sortByMax=True):
        '''
        Makes a stack of all 2D histograms from the samples in category by 
        passing parameters to self.makeStack2() (which passes them on to 
        self.makeHist2()).
        '''
        assert not self.isData(category), "You can only stack MC, not data like %s!"%category

        samples = self.ntuples[category].keys()
        return self.makeStack2(category, samples, channel, variable, selection,
                               binning, scale=1., weight='', sortByMax=True)

    
    def makeStack3(self, category, samples, channel, variable, selection,
                   binning, scale=1., weight='', sortByMax=True):
        '''
        Sums 3D histograms from samples in the same category by 
        passing parameters to makeHist3().
        '''
        hists = []
        for sample in samples:
            hists.append(self.makeHist3(category, sample, channel, variable, 
                                        selection, binning, scale, weight))

        s = hists[0].empty_clone()
        for h in hists:
            s += h
        
        return s
    
    
    def makeCategoryStack3(self, category, channel, variable, selection,
                           binning, scale=1., weight='', sortByMax=True):
        '''
        Sums all 3D histograms from the samples in category by 
        passing parameters to self.makeStack2() (which passes them on to
        self.makeHist3()).
        '''
        assert not self.isData(category), "You can only stack MC, not data!"
        samples =  self.ntuples[category].keys()
        
        return makeStack3(self, category, samples, channel, variable, selection,
                          binning, scale, weight, sortByMax)

                  
    
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

        # lazy way to prevent data hist from reaching sampleInfo query
        key = lambda h: (not(self.isData(h.getCategory()) or not h.getIsSignal()), 
                         h.GetBinContent(binGetter(h)))

        hists.sort(key=key)

        return hists


    def fullPlot(self, name, channel, variable, selection, binning,
                 mcCategory='mc', dataCategory='data', extraBkgs=[],
                 canvasX=800, canvasY=1000, logy=False, styleOpts={}, 
                 ipynb=False, xTitle="", xUnits="GeV", yTitle="Events",
                 yUnits="", drawNow=False, outFile='', legParams={}, 
                 mcWeights='GenWeight', drawOpts={}, drawRatio=True,
                 legSolid=False, widthInYTitle=False,
                 mcSystFracUp=0., mcSystFracDown=0.,
                 blinding=[], extraObjects=[]):
        '''
        Make the "normal" plot, i.e. stack of MC compared to data points.
        extraBkgs may be a list of other background histograms (e.g. a data-
        driven background estimation) to be included in the stack with the MC.
        Store it in self.drawings keyed to name, and save the plot if outFile
        is specified.
        '''
        self.drawings[name] = self.Drawing(name, self.style, canvasX, canvasY, 
                                           logy, ipynb)
        s = self.makeCategoryStack(mcCategory, channel, variable, selection,
                                   binning, 1., mcWeights,
                                   extraHists=extraBkgs)
        if len(s):
            self.drawings[name].addObject(s)
        h = self.makeHist(dataCategory, dataCategory, channel, variable, selection,
                          binning)
        if h.GetEntries():
            self.drawings[name].addObject(h)
            
            # add data/MC ratio plot
            if drawRatio:
                self.drawings[name].addRatio(h, s, yTitle="Data / MC")

        if not hasattr(extraObjects, '__iter__'): # non-string iterable
            extraObjects = [extraObjects]
        for ob in extraObjects:
            self.drawings[name].addObject(ob, hasattr(ob, "legendstyle"))

        if outFile:
            self.drawings[name].draw(drawOpts, self.outdir+outFile, drawNow, 
                                     xTitle, xUnits, yTitle, yUnits, True, 
                                     legParams, True, self.intLumi, 
                                     h.GetEntries()==0, legSolid=legSolid,
                                     widthInYTitle=widthInYTitle,
                                     mcSystFracUp=mcSystFracUp, 
                                     mcSystFracDown=mcSystFracDown,
                                     blinding=blinding)


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

