'''

Make all ZZ plots with data driven backgrounds.

This is a goddamn mess; I'll clean it up later.

'''


# include logging stuff first so other imports don't babble at us
import logging
from rootpy import log as rlog; rlog = rlog["/ichepHighMassSBIPlot"]
# don't show most silly ROOT messages
logging.basicConfig(level=logging.WARNING)
rlog["/ROOT.TH1F.Add"].setLevel(rlog.ERROR)
rlog["/rootpy.compiled"].setLevel(rlog.WARNING)
rlog["/ROOT.TClassTable.Add"].setLevel(rlog.ERROR)


from NtuplePlotter import NtuplePlotter
from ZZAnalyzer.utils.helpers import Z_MASS
from ZZAnalyzer.utils import WeightStringMaker

from rootpy import asrootpy
from rootpy.io import root_open
from rootpy.ROOT import R, TF1, gStyle
from rootpy.plotting import HistStack

import os
from datetime import date
from glob import glob

from math import sqrt

from argparse import ArgumentParser


outdir = '/afs/cern.ch/user/n/nawoods/www/ZZPlots/firstICHEPPlots'

# tpVersionHash = 'v2.0-13-g36fc26c' #'v2.0-11-gafcf7cc' #'v1.1-4-ga295b14-extended'
# 
# TP = TPFunctionManager(tpVersionHash)

z1eMCWeight = 'e1EffScaleFactor * e2EffScaleFactor * e1EffScaleFactor * e2EffScaleFactor'
z2eMCWeight = 'e3EffScaleFactor * e4EffScaleFactor'
#z1mMCWeight = 'm1EffScaleFactor * m1TrkRecoEffScaleFactor * m2EffScaleFactor * m2TrkRecoEffScaleFactor'
#z2mMCWeight = 'm3EffScaleFactor * m3TrkRecoEffScaleFactor * m4EffScaleFactor * m4TrkRecoEffScaleFactor'
z1mMCWeight = 'm1EffScaleFactor *  m2EffScaleFactor'
z2mMCWeight = 'm3EffScaleFactor *  m4EffScaleFactor'

puWt = WeightStringMaker('puWeight')
fPUScale = root_open(os.path.join(os.environ['zza'], 'ZZAnalyzer', 
                                  'data', 'pileupReweighting', 
                                  'pileup_MC_80x_271036-276811_69200.root'))
puSFHist = fPUScale.puweight
puSFStr = puWt.makeWeightStringFromHist(puSFHist, 'nTruePU')

mcWeight = {
    'eeee' : '(genWeight*{0}*{1}*{2})'.format(puSFStr, z1eMCWeight, z2eMCWeight),
    'eemm' : '(genWeight*{0}*{1}*{2})'.format(puSFStr, z1eMCWeight, z1mMCWeight),
    'mmmm' : '(genWeight*{0}*{1}*{2})'.format(puSFStr, z1mMCWeight, z2mMCWeight),
}

mcWeight['zz'] = [mcWeight['eeee'], mcWeight['eemm'], mcWeight['mmmm']]

units = {
    'Mass' : 'GeV',
    'MassFSR' : 'GeV',
    'PhiFSR' : '',
    'EtaFSR' : '',
    'PtFSR' : 'GeV',
    'nJets' : '',
    'Mass' : 'GeV',
    'Phi' : '',
    'Eta' : '',
    'Pt' : '',
    'Iso' : '',
    'PVDXY' : '',
    'PVDZ' : '',
    'nvtx' : '',
    }
    
print "Initializing plotter"

# cut that is always applied, in case it's needed
constSelection = ''

print "Putting plots in {}".format(outdir)

# signalMasses = [450,750,1500,2500]
# otherSignalSamples = {'m{}'.format(m) : glob('/data/nawoods/ntuples/uwvvNtuples_ggH_26jul2016/results_hzz/*M{}*.root'.format(m))[0] for m in signalMasses}

#mcFiles = {'mc':'/data/nawoods/ntuples/uwvvNtuples_ggH_26jul2016/results_hzz/*M125*.root,/data/nawoods/ntuples/uwvvNtuples_smzz_26jul2016/results_hzz/*.root',}
mcFiles = {'mc':'/data/nawoods/ntuples/uwvvNtuples_smzz_26jul2016/results_hzz/ZZ*.root',}
# mcFiles.update(otherSignalSamples)

ntuplePlotter = NtuplePlotter('zz', outdir, 
                        mcFiles,
                        {'data'  :'/data/nawoods/ntuples/uwvvNtuples_data2016b*26jul*/results_hzz/*.root',
                         'data ' :'/data/nawoods/ntuples/uwvvNtuples_data2016c*26jul*/results_hzz/*.root',
                         'data  ':'/data/nawoods/ntuples/uwvvNtuples_data2016d*26jul*/results_hzz/*.root',
                         }, 
                        intLumi=12900.)

# remove box from around legend
gStyle.SetLegendBorderSize(0)

# ntuplePlotter.printPassingEvents('data')
# ntuplePlotter.printPassingEvents('data ')
# ntuplePlotter.printPassingEvents('data  ')


binning = [200.5+i*40. for i in range(12)] + [680.5+i*80. for i in range(12)] + [1640.5+i*160. for i in range(9)]
#binning = [70,200.,3000.]
#[70. + 10. * i for i in xrange(23)] + [300. + 20. * i for i in xrange(10)] + [500. + 40. * i for i in xrange(5)] + [700.,800.,900.],


fBkg = {}
errBkg = {}
fBkg['eeee'] = TF1('fBkg4e', '[0]*TMath::Landau(x,[1],[2])', 70.,3000.)
fBkg['eeee'].SetParameters(9.8,141.9,21.3)
errBkg['eeee'] = 4.1 / 9.8

fBkg['mmmm'] = TF1('fBkg4m', '[0]*TMath::Landau(x,[1],[2])', 70.,3000.)
fBkg['mmmm'].SetParameters(10.2,130.4,15.6)
errBkg['mmmm'] = 4.6 / 10.2

fBkg['eemm'] = TF1('fBkg2e2m', '[0]*(0.45*TMath::Landau(x,[1],[2]) + 0.55*TMath::Landau(x,[3],[4]))', 70.,3000.)
fBkg['eemm'].SetParameters(20.4,131.1,18.1,133.8,18.9)
errBkg['eemm'] = 11.1 / 20.4

ntuplePlotter.dataOrMC['Z+X'] = False

hBkg = {}
bkgKWArgs = {
    'title' : 'Z/WZ+X',
    'sample' : 'Z+X',
    'variable' : 'MassFSR',
    'selection' : '',
    'category' : 'Z+X',
    'isData' : False,
    'isSignal' : False,
    }

for c,f in fBkg.iteritems():
    if len(binning) == 3:
        hBkg[c] = ntuplePlotter.WrappedHist(*binning, channel=c, **bkgKWArgs)
    else:
        hBkg[c] = ntuplePlotter.WrappedHist(binning, channel=c, **bkgKWArgs)
    hBkg[c].legendstyle = "F"
    ntuplePlotter.formatHist(hBkg[c], background=True)

    for b in hBkg[c]:
        b.value = fBkg[c](hBkg[c].GetBinCenter(b.idx))
        b.error = b.value * errBkg['eeee']

if len(binning) == 3:
    hBkg['zz'] = ntuplePlotter.WrappedHist(*binning, channel='zz', **bkgKWArgs)
else:
    hBkg['zz'] = ntuplePlotter.WrappedHist(binning, channel='zz', **bkgKWArgs)
hBkg['zz'].legendstyle = "F"
ntuplePlotter.formatHist(hBkg['zz'], background=True)
for b in hBkg['zz']:
    b.value = sum(fBkg[c](hBkg['zz'].GetBinCenter(b.idx)) for c in fBkg)
    b.error = sqrt(sum(errBkg[c]**2. for c in errBkg))

sigShapeDir = os.path.join(os.environ['zza'], 'ZZAnalyzer', 'data', 
                           'signalShapes')
sigShapeFiles = {
    1000 : root_open(os.path.join(sigShapeDir, 'histf_1030_40.0.root')),
    2500 : root_open(os.path.join(sigShapeDir, 'histf_2530_40.0.root')),
    }

sigColors = {
    1000 : 'indigo',
    2500 : 'magenta',
}

sigShapeHists = {}
for m, f in sigShapeFiles.iteritems():
    sigKWArgs = {
        'title' : '#splitline{{X(m_{{X}}={} GeV, #Gamma_{{X}}=40 GeV) + }}{{gg #rightarrow ZZ + qq #rightarrow ZZqq + Int.}}'.format(m),
        'sample' : 'signal_{}_40'.format(m+30),
        'variable' : 'MassFSR',
        'selection' : '',
        'category' : 'signal',
        'isData' : False,
        'isSignal' : True,
        'channel' : 'zz',
        }
    ntuplePlotter.dataOrMC['signal'] = False
    h = asrootpy(f.Get('dataset__mreco'))
    # don't have time to figure out why this seems to be necessary
    hNew = h.empty_clone()
    for b,bNew in zip(h, hNew):
        bNew.value = b.value
        bNew.error = b.error
    if len(binning) == 3:
        temp = Hist(*binning)
        sigShapeHists[m] = ntuplePlotter.WrappedHist(hNew.rebinned([e for e in temp._edges(0)]), **sigKWArgs)
    else:
        sigShapeHists[m] = ntuplePlotter.WrappedHist(hNew.rebinned(binning), **sigKWArgs)
    sigShapeHists[m].fillstyle = 'hollow'
    sigShapeHists[m].linestyle = 'dashed'
    sigShapeHists[m].linecolor = sigColors[m]
    sigShapeHists[m].legendstyle = 'L'
    sigShapeHists[m].drawstyle = 'HIST'
    sigShapeHists[m].SetLineWidth(3 * sigShapeHists[m].GetLineWidth())
    if len(binning) != 3:
        ntuplePlotter.scaleHist(sigShapeHists[m], -1., True)

    # overflow bin going to zero looks weird
    sigShapeHists[m][0].value = sigShapeHists[m][1].value
    sigShapeHists[m][-1].value = sigShapeHists[m][-2].value


def makePlot(plotter, name, channel, variable, selection, binning,
             mcCategory='mc', dataCategory='data', extraBkgs=[],
             canvasX=800, canvasY=1000, logy=False, styleOpts={}, 
             ipynb=False, xTitle="", xUnits="GeV", yTitle="Events",
             yUnits="", drawNow=False, outFile='', legParams={}, 
             mcWeights='GenWeight', drawOpts={}, drawRatio=True,
             legSolid=False, widthInYTitle=False,
             mcSystFracUp=0., mcSystFracDown=0.,
             blinding=[], extraObjects=[], plotType="Preliminary",
             stackErr=True, logx=False, 
             finishingFuncData=None,finishingFuncMC=None,
             noPointWidth=False, addToExtra=False):
    '''
    Make the "normal" plot, i.e. stack of MC compared to data points.
    extraBkgs may be a list of other background histograms (e.g. a data-
    driven background estimation) to be included in the stack with the MC.
    Store it in self.drawings keyed to name, and save the plot if outFile
    is specified.
    finishingFunc* arguments allow a function to be passed in which takes
    a hist/graph/hist stack as an argument, which will be run just before
    the data points and MC stack are plotted
    '''
    plotter.drawings[name] = plotter.Drawing(name, plotter.style, canvasX, canvasY, 
                                       logy, ipynb, logx=logx)

    s = plotter.makeCategoryStack(mcCategory, channel, variable, selection,
                                  binning, 1., mcWeights,
                                  extraHists=extraBkgs)

    if hasattr(finishingFuncMC, '__call__'):
        finishingFuncMC(s)

    if len(s):
        plotter.drawings[name].addObject(s)

    for ob in extraObjects:
        if addToExtra:
            ob += sum(hst for hst in s)
        plotter.drawings[name].addObject(ob, hasattr(ob, 'legendstyle'))
        
    if isinstance(dataCategory, str):
        dataCategory = [dataCategory]

    h = None
    for dc in dataCategory:
        hTemp = plotter.makeHist(dc, dc, channel, variable, selection,
                                 binning)
        if h is None:
            h = hTemp
        else:
            h += hTemp

    if h.GetEntries():
        if hasattr(finishingFuncData, '__call__'):
            finishingFuncData(h)

        plotter.drawings[name].addObject(h)
        
        # add data/MC ratio plot
        if drawRatio:
            plotter.drawings[name].addRatio(h, s, yTitle="Data / MC")

    if outFile:
        plotter.drawings[name].draw(drawOpts, plotter.outdir+outFile, drawNow, 
                                 xTitle, xUnits, yTitle, yUnits, True, 
                                 legParams, stackErr, plotter.intLumi, 
                                 h.GetEntries()==0, legSolid=legSolid,
                                 widthInYTitle=widthInYTitle,
                                 mcSystFracUp=mcSystFracUp, 
                                 mcSystFracDown=mcSystFracDown,
                                 blinding=blinding, plotType=plotType,
                                 noPointWidth=noPointWidth)

    

xTitle = 'm_{__PARTICLES__}'

def formatDataHZZ(h):
    h.drawstyle = 'PEX0'
    h.legendstyle = 'P'

var = 'MassFSR'
varName = var

for channel in ['zz']:#, 'eeee', 'eemm', 'mmmm']:
    
    chEnding = ''
    if channel != 'zz':
        chEnding = '_%s'%channel
    if channel == 'zz':
        particles = '4\\ell'
    elif channel == 'eeee':
        particles = '4e'
    elif channel == 'eemm':
        particles = '2e2\\mu'
    elif channel == 'mmmm':
        particles = '4\\mu'

    extraSignal = [sigShapeHists[m] for m in sorted(sigShapeHists.keys())]

    legParams = {'leftmargin' : .42, 'entryheight' : .004, 'textsize' : .025,
                 'entrysep' : .08, 'topmargin' : .01, 'rightmargin' : .22}

    kwargs = {
        'canvasX' : 1000, 
        'xTitle' : xTitle.replace('__PARTICLES__',particles), 
        'xUnits' : 'GeV',
        'extraBkgs' : [hBkg[channel]], 
        'mcWeights' : mcWeight[channel], 
        'drawRatio' : False,
        'widthInYTitle' : True,
        'extraObjects' : extraSignal,
        'plotType' : 'Preliminary',
        'logx' : True,
        'stackErr' : False,
        'legParams' : legParams,
        'finishingFuncData' : formatDataHZZ,
        'noPointWidth' : True,
        'plotType' : 'Supplemental',
        }

    makePlot(ntuplePlotter, 'HighMass{}Log'.format(chEnding), channel, var, constSelection, 
             binning, 'mc', ['data','data ','data  '], 
             drawOpts={'logy_crop_value':5e-03}, logy=True,
             outFile='HighMassSBILog{}.png'.format(chEnding), addToExtra=True,
             **kwargs)
    makePlot(ntuplePlotter, 'HighMass{}'.format(chEnding), channel, var, constSelection, 
             binning, 'mc', ['data','data ','data  '], 
             outFile='HighMassSBI{}.png'.format(chEnding), addToExtra=False,
             **kwargs)


