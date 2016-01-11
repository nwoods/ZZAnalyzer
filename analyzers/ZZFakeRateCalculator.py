'''

Take some Z+l ntuples, save a file of histograms whose contents are
the fake rate in each bin.

If this file is run as a script, it will make a common "default" set of
histograms, but the class is flexible enough to be used for other variables, 
objects, etc.

Author: Nate Woods, U. Wisconsin

'''


# include logging stuff first so other imports don't babble at us
import logging
from rootpy import log as rlog; rlog = rlog["/ZZFakeRateCalculator"]
# don't show most silly ROOT messages
logging.basicConfig(level=logging.WARNING)
rlog["/ROOT.TGraphAsymmErrors.Divide"].setLevel(rlog.ERROR)
rlog["/rootpy.compiled"].setLevel(rlog.WARNING)
rlog["/ROOT.TUnixSystem.SetDisplay"].setLevel(rlog.ERROR)

from rootpy.io import root_open
from rootpy import asrootpy
from rootpy.plotting.hist import _Hist, _Hist2D, _Hist3D

from NtuplePlotter import NtuplePlotter
from ZZHelpers import parseChannels, mapObjects

from itertools import chain as iChain


class ZZFakeRateCalculator(object):
    def __init__(self, looseFilesData, tightFilesData, 
                 looseFilesMC, tightFilesMC, channels, outFile, 
                 intLumi=-1.):
        if looseFilesData:
            assert tightFilesData, "I can only make a fake rate from data with both a tight and loose ntuple"
            self.dataFiles = {'num' : tightFilesData, 'denom' : looseFilesData}
        else:
            assert len(tightFilesData)==0, "I can only make a fake rate from data with both a tight and loose ntuple"
            self.dataFiles = {}
        if looseFilesMC:
            assert tightFilesMC, "I can only make a fake rate from Monte Carlo with both a tight and loose ntuple"
            self.mcFiles = {'numMC' : tightFilesMC, 'denomMC' : looseFilesMC}
        else:
            assert len(tightFilesMC)==0, "I can only make a fake rate from Monte Carlo with both a tight and loose ntuple"
            self.mcFiles = {}
        
        self.hasData = bool(self.dataFiles)
        self.hasMC = bool(self.mcFiles)

        self.outFileName = outFile
        outFileBaseName = self.outFileName.split('/')[-1]
        self.outDir = self.outFileName.replace(outFileBaseName, '')
        self.intLumi = intLumi

        self.plotter = NtuplePlotter(channels, self.outDir, 
                                     self.mcFiles, self.dataFiles, 
                                     self.intLumi)
        self.channels = parseChannels(channels)
        assert len(self.channels) > 0 and \
            all(len(ch) == 3 for ch in self.channels), \
            "Invalid channel %s. Channels must have 3 objects."%channels
        
        self.WrappedHists = [
            self.plotter.WrappedHist,
            self.plotter.WrappedHist2,
            self.plotter.WrappedHist3,
            ]
        self.WrappedStacks = [
            self.plotter.WrappedStack,
            self.plotter.WrappedStack,
            self.plotter.WrappedHist3, # THistStack only goes up to 2-D
            ]
        self.histMakers = [
            lambda *args, **kwargs: self.plotter.makeHist(*args, 
                                                           perUnitWidth=False, 
                                                           **kwargs),
            self.plotter.makeHist2,
            self.plotter.makeHist3,
            ]
        self.stackMakers = [
            lambda *args, **kwargs: self.plotter.makeStack(*args,
                                                            perUnitWidth=False,
                                                            **kwargs),
            self.plotter.makeStack2, # THistStack same for 1- and 2-D
            self.plotter.makeStack3,
            ]
        self.extractHistFromStack = [
            lambda s: self.WrappedHists[0](asrootpy(s.GetStack().Last()),
                                           category=s.getCategory(),
                                           variable=s.getVariable(),
                                           selection=s.getSelection()),
            lambda s: self.WrappedHists[1](asrootpy(s.GetStack().Last()),
                                           category=s.getCategory(),
                                           variable=s.getVariable(),
                                           selection=s.getSelection()),
            lambda s: s, # THistStack only goes up to 2-D
            ]
                                           
        self.outputs = []


    def calculateFakeRate(self, name, channels, *varsAndBinnings, 
                          **kwargs):
        '''
        Make a fake rate histogram. It is stored in self.outputs and returned.
        Channel should be one channel or a list of channels. Correct object to 
        use for each channel is figured out automatically.
        The next 2, 4, or 6 arguments should be one, two, or three variables
        to bin in, each followed immediately by an iterable containing 
        bin edges or [nbins, min, max].
        If keyword argument 'useMC' evaluates to True, MC samples are used 
        instead of data.
        If keyword argument 'draw' evaluates to True, a .png file is created
        in the same directory as the eventual output with a plot of the
        fake rate.
        If a list of subtraction samples is provided, by kwargs['subtractSamples'], 
        the MC contributions of these samples are subtracted from the numerator and 
        denominator before the fake rate is calculated. No bin may be less 
        than 0.
        '''
        subtractSamples = kwargs.pop('subtractSamples', [])

        if len(varsAndBinnings) % 2 == 1 or len(varsAndBinnings) < 2 or len(varsAndBinnings) > 6:
            raise ValueError("Invalid list of variables and their binnings")
        nDims = len(varsAndBinnings) / 2

        varTemplate = ''
        binning = []
        varTemplate = ':'.join("{0}"+varsAndBinnings[2*i] for i in xrange(nDims))
        for i in xrange(nDims):
            ind = 2*i+1
            if len(varsAndBinnings[ind]) == 3 and isinstance(varsAndBinnings[ind][0], int):
                binning += varsAndBinnings[ind] # uniform bins
            else: 
                binning.append(varsAndBinnings[ind]) # variable bins

        if isinstance(channels, str):
            channels = [channels]

        varList = [varTemplate.format(self.fakeObjectForChannel(ch)) for ch in channels]
        selecList = ["" for v in varList]

        outputs = []
        drawablesMC = {}
        if self.hasMC:
            samplesToDraw = [s for s in self.plotter.ntuples['numMC'].keys() if s not in subtractSamples]

            sNum = self.stackMakers[nDims-1]("numMC", samplesToDraw, channels, 
                                             varList, selecList, binning, 
                                             weight="GenWeight")
            drawablesMC['num'] = sNum
            numMC = self.extractHistFromStack[nDims-1](sNum)
            sDenom = self.stackMakers[nDims-1]("denomMC", samplesToDraw, 
                                               channels, varList,
                                               selecList, binning, 
                                               weight="GenWeight")
            drawablesMC['denom'] = sDenom
            denomMC = self.extractHistFromStack[nDims-1](sDenom)
            
            fMC = self.WrappedHists[nDims-1](asrootpy(numMC.Clone()),
                                             name=name+"MC_fakeRate",
                                             isData=False)
            fMC.Divide(denomMC)
            drawablesMC['fakeRate'] = fMC

            # actual scale factor, f/(1-f)
            outMC = self.WrappedHists[nDims-1](asrootpy(numMC.empty_clone()),
                                               name=name+"MC")
            for fb, b in zip(fMC, outMC):
                if b.overflow:
                    continue
                b.value = fb.value / (1. - fb.value)

            outputs.append(outMC)

        drawablesData = {}
        if self.hasData:
            num = self.histMakers[nDims-1]("num", "num", channels, varList, 
                                           selecList, binning)
            denom = self.histMakers[nDims-1]("denom", "denom", channels, varList, 
                                             selecList, binning)

            num.sumw2()
            denom.sumw2()

            for ss in subtractSamples:
                subNum = self.histMakers[nDims-1]("numMC", ss, channels,
                                                  varList, selecList, binning,
                                                  1., weights="GenWeight")
                num -= subNum
                subDenom = self.histMakers[nDims-1]("denomMC", ss, channels,
                                                    varList, selecList, binning,
                                                    1., weights="GenWeight")
                denom -= subDenom

            for bNum, bDenom in zip(num, denom):
                if bNum.value < 0. or bDenom.value <= 0.:
                    bNum.value = 0.
                    bNum.error = 0.
                    bDenom.value = 0.0000001
                    bDenom.error = 0.
            
            num.sumw2()
            denom.sumw2()

            f = self.WrappedHists[nDims-1](asrootpy(num.Clone()),
                                           name=name+"_fakeRate")
            f.Divide(denom)
            drawablesData['num'] = num
            drawablesData['denom'] = denom
            drawablesData['fakeRate'] = f

            out = self.WrappedHists[nDims-1](asrootpy(num.empty_clone()),
                                             name=name)
            for fb, b in zip(f, out):
                if b.overflow:
                    continue
                b.value = fb.value / (1. - fb.value)

            outputs.append(out)

        for o in outputs:
            for i in xrange(nDims):
                o.axis(i).title = varsAndBinnings[i*2]

        if kwargs.pop('draw', False):
            self.drawFakeRate(name, nDims, drawablesData, drawablesMC, **kwargs)

        self.outputs += outputs
        return outputs
        
       
    def drawFakeRate(self, name, nDims, drawablesData, drawablesMC, **kwargs):
        '''
        Create a .png with the fake rate plot, with numbers superimposed over 
        each (1- and 2-D only), and for the numerator and denominator. For 1-D,
        MC and data are drawn on the same plot.
        '''
        drawings = {}
        if nDims == 1 and bool(drawablesData) and bool(drawablesMC):
            for typeToPlot in ['num', 'denom', 'fakeRate']:
                drawings[typeToPlot] = self.plotter.Drawing(name+'_'+typeToPlot, 
                                                            self.plotter.style, 
                                                            1000, 1000)
                if typeToPlot == 'fakeRate':
                    drawablesMC[typeToPlot].drawstyle = 'hist'
                    drawablesMC[typeToPlot].color = 'red'
                    drawings[typeToPlot].addObject(drawablesMC[typeToPlot],
                                                   legendName='MC',
                                                   legendStyle="L")
                else:
                    drawings[typeToPlot].addObject(drawablesMC[typeToPlot])
                # drawings[typeToPlot].addRatio(drawablesData[typeToPlot], 
                #                               drawablesMC[typeToPlot], 0.23, 
                #                               yTitle="Data / MC")

                if typeToPlot == 'fakeRate':
                    fakeRateData = self.plotter.WrappedGraph(type='asymm', 
                                                             title='data')
                    fakeRateData.Divide(drawablesData['num'], drawablesData['denom'])
                else:
                    fakeRateData = drawablesData[typeToPlot]
                
                fakeRateData.color = 'black'
                fakeRateData.drawstyle = 'PE'

                drawings[typeToPlot].addObject(fakeRateData,
                                               legendName='data',
                                               legendStyle='LPE')

                drawings[typeToPlot].draw({}, '%s/%s_%s.png'%(self.outDir, 
                                                              name, typeToPlot), 
                                          xTitle=kwargs.get('xTitle', ''), 
                                          xUnits=kwargs.get('xUnits', ''),
                                          yTitle='Fake Rate',
                                          intLumi=self.intLumi, 
                                          perUnitWidth=False)
        else:
            for maybeMC in ['', 'MC']:
                if maybeMC:
                    drawables = drawablesMC
                else:
                    drawables = drawablesData
                
                if not drawables:
                    continue

                for typeToPlot, plot in drawables.iteritems():
                    ttp = typeToPlot+maybeMC
                    drawings[ttp] = self.plotter.Drawing(name+'_'+ttp, 
                                                         self.plotter.style, 
                                                         800, 800)
                    
                    if isinstance(plot, _Hist2D):
                        plot.drawstyle = plot.drawstyle+"TEXT"
                        if "COLZ" not in plot.drawstyle:
                            plot.drawstyle = plot.drawstyle+"COLZ"
                    if isinstance(plot, _Hist) and maybeMC:
                        plot.drawstyle='hist'
                        plot.color='red'
                    drawings[ttp].addObject(plot,
                                            addToLegend=(bool(maybeMC) and typeToPlot != 'fakeRate' and nDims == 1),
                                            legendName=("MC" if maybeMC else "data"),
                                            legendStyle=("F" if maybeMC else "LPE"))
                    
                    drawings[ttp].draw({}, '%s/%s_%s.png'%(self.outDir, 
                                                           name, ttp), 
                                       xTitle=kwargs.get('xTitle', ''), 
                                       xUnits=kwargs.get('xUnits', ''),
                                       intLumi=self.intLumi,
                                       stackErr=(nDims==1),
                                       perUnitWidth=False)


    _zzFakeRateCalculator_channelObjMap_ = {}
    def fakeObjectForChannel(self, channel):
        '''
        Get the odd object out for this channel (the l in Z+l).
        E.g. 'm3' for channel 'mmm' or 'e' for channel 'emm'.
        '''
        global _zzFakeRateCalculator_channelObjMap_
        try:
            return self._zzFakeRateCalculator_channelObjMap_[channel]
        except KeyError:
            assert len(channel) == 3 and any(channel.count(ob)>1 for ob in channel),\
                "Only Z+l-like channels are allowed, %s will not work!"%channel

            objects = mapObjects(channel)
            for obj in objects:
                if len(obj) == 1: # only object of its type
                    self._zzFakeRateCalculator_channelObjMap_[channel] = obj
                    return obj
                if obj[-1] == '3': # Z always listed first for lll channels
                    self._zzFakeRateCalculator_channelObjMap_[channel] = obj
                    return obj
            else: # shouldn't ever happen
                raise


    def writeOutput(self):
        with root_open(self.outFileName, "RECREATE") as f:
            for op in self.outputs:
                op.Write()


    

if __name__ == '__main__':
    from argparse import ArgumentParser
    from glob import glob

    parser = ArgumentParser(description="Running ZZFakeRateCalculator "
                            "as a script makes 'standard' fake rates in bins "
                            "of pt and eta for eee, eem, emm, and mmm channels.")
    
    parser.add_argument('dataFilesLoose', type=str, 
                        help="ROOT files with Z+l_loose events from data. "
                        "May contain wildcards.")
    parser.add_argument('dataFilesTight', type=str, 
                        help="ROOT files with Z+l_tight events from data. "
                        "May contain wildcards.")
    parser.add_argument('mcFilesLoose', type=str, 
                        help="ROOT files with Z+l_loose events from Monte Carlo. "
                        "May contain wildcards.")
    parser.add_argument('mcFilesTight', type=str, 
                        help="ROOT files with Z+l_tight events from Monte Carlo. "
                        "May contain wildcards.")
    parser.add_argument('outFile', type=str, default='fakeRate.root',
                        help="Name of output file containing "
                        "fake rate histograms.")
    parser.add_argument('--channels', type=str, nargs='?', default='3l',
                        help='Channel(s) to check.')
    parser.add_argument('--intLumi', type=float, nargs='?', default=1.,
                        help='Integrated Luminosity (for MC).')
    parser.add_argument('--paint', action='store_true',
                        help='Plot fake rates as .pngs along with output.')
    
    args = parser.parse_args()
    
    filesDataLoose = glob(args.dataFilesLoose)
    filesDataTight = glob(args.dataFilesTight)
    filesMCLoose = glob(args.mcFilesLoose)
    filesMCTight = glob(args.mcFilesTight)
    
    calc = ZZFakeRateCalculator(filesDataLoose, filesDataTight,
                                filesMCLoose, filesMCTight, args.channels,
                                args.outFile, args.intLumi)
    
    ptBinning=[10.,30.,60.,200.]#20.,40.,60.,100.,200.]
    etaBinning=[0.,0.8,1.47,2.5]#0.5,0.8,1.04,1.2,1.6,2.1,2.5]

    samplesToSubtract = []
    if 'numMC' in calc.plotter.ntuples:
        for s in calc.plotter.ntuples['numMC']:
            if s[:4] == "ZZTo" or "uZZTo" in s or s[:4] == "WZTo":
                samplesToSubtract.append(s)

    channelsByObject = {}
    channelsByType = {}
    for ch in calc.channels:
        obj = calc.fakeObjectForChannel(ch)
        if obj not in channelsByObject:
            channelsByObject[obj] = [ch]
        else:
            channelsByObject[obj].append(ch)
        objType = obj[0]
        if objType not in channelsByType:
            channelsByType[objType] = [ch]
        else:
            channelsByType[objType].append(ch)

    for obj, chs in iChain(channelsByType.iteritems(), channelsByObject.iteritems()):
        if len(chs) == 1:
            continue # speed up because we don't usually care
            objToPrint = obj[0]+'_'+chs[0]
        else:
            objToPrint = obj[0]
        calc.calculateFakeRate(objToPrint+'_FakeRate', chs,
                               'Pt', ptBinning, 'Eta', etaBinning,
                               draw=args.paint,
                               subtractSamples=samplesToSubtract,
                               xTitle='p_{T}', xUnits='GeV',
                               yTitle='\\eta')
        calc.calculateFakeRate(objToPrint+'_FakeRatePt', chs,
                               'Pt', ptBinning,
                               subtractSamples=samplesToSubtract,
                               draw=args.paint,
                               xTitle='p_{T}', xUnits='GeV')
        calc.calculateFakeRate(objToPrint+'_FakeRateEta', chs,
                               'Eta', etaBinning,
                               subtractSamples=samplesToSubtract,
                               draw=args.paint,
                               xTitle='\\eta')

    calc.writeOutput()

    # clean up
    calc.plotter.__del__()

