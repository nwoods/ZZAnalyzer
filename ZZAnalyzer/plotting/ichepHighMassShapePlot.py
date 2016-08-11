'''

Make all ZZ plots with data driven backgrounds.

This is a goddamn mess; I'll clean it up later.

'''


# include logging stuff first so other imports don't babble at us
import logging
from rootpy import log as rlog; rlog = rlog["/ichepHighMassShapePlot"]
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
mcFiles = {'mc':'/data/nawoods/ntuples/uwvvNtuples_smzz_26jul2016/results_hzz/*.root',}
# mcFiles.update(otherSignalSamples)

plotter = NtuplePlotter('zz', outdir, 
                        mcFiles,
                        {'data'  :'/data/nawoods/ntuples/uwvvNtuples_data2016b*26jul*/results_hzz/*.root',
                         'data ' :'/data/nawoods/ntuples/uwvvNtuples_data2016c*26jul*/results_hzz/*.root',
                         'data  ':'/data/nawoods/ntuples/uwvvNtuples_data2016d*26jul*/results_hzz/*.root',
                         }, 
                        intLumi=12900.)

# remove box from around legend
gStyle.SetLegendBorderSize(0)

# plotter.printPassingEvents('data')
# plotter.printPassingEvents('data ')
# plotter.printPassingEvents('data  ')


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

plotter.dataOrMC['Z+X'] = False

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
        hBkg[c] = plotter.WrappedHist(*binning, channel=c, **bkgKWArgs)
    else:
        hBkg[c] = plotter.WrappedHist(binning, channel=c, **bkgKWArgs)
    hBkg[c].legendstyle = "F"
    plotter.formatHist(hBkg[c], background=True)

    for b in hBkg[c]:
        b.value = fBkg[c](hBkg[c].GetBinCenter(b.idx))
        b.error = b.value * errBkg['eeee']

if len(binning) == 3:
    hBkg['zz'] = plotter.WrappedHist(*binning, channel='zz', **bkgKWArgs)
else:
    hBkg['zz'] = plotter.WrappedHist(binning, channel='zz', **bkgKWArgs)
hBkg['zz'].legendstyle = "F"
plotter.formatHist(hBkg['zz'], background=True)
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
        'title' : 'ggZZ + X(m_{{X}}={}, #Gamma_{{X}}=40)'.format(m),
        'sample' : 'signal_{}_40'.format(m+30),
        'variable' : 'MassFSR',
        'selection' : '',
        'category' : 'signal',
        'isData' : False,
        'isSignal' : True,
        'channel' : 'zz',
        }
    plotter.dataOrMC['signal'] = False
    h = asrootpy(f.Get('dataset__mreco'))
    # don't have time to figure out why this seems to be necessary
    hNew = h.empty_clone()
    for b,bNew in zip(h, hNew):
        bNew.value = b.value
        bNew.error = b.error
    if len(binning) == 3:
        temp = Hist(*binning)
        sigShapeHists[m] = plotter.WrappedHist(hNew.rebinned([e for e in temp._edges(0)]), **sigKWArgs)
    else:
        sigShapeHists[m] = plotter.WrappedHist(hNew.rebinned(binning), **sigKWArgs)
    sigShapeHists[m].fillstyle = 'hollow'
    sigShapeHists[m].linestyle = 'dashed'
    sigShapeHists[m].linecolor = sigColors[m]
    sigShapeHists[m].legendstyle = 'L'
    sigShapeHists[m].drawstyle = 'HIST'
    sigShapeHists[m].SetLineWidth(3 * sigShapeHists[m].GetLineWidth())
    if len(binning) != 3:
        plotter.scaleHist(sigShapeHists[m], -1., True)

    # overflow bin going to zero looks weird
    sigShapeHists[m][0].value = sigShapeHists[m][1].value
    sigShapeHists[m][-1].value = sigShapeHists[m][-2].value


    

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

    # extraSignal = []
    # for mNum in reversed(signalMasses):
    #     m = "m{}".format(mNum)
    #     sample = otherSignalSamples[m]
    #     extraSignal.append(
    #         plotter.makeHist(m, sample.split('/')[-1].replace('.root',''), channel, var, constSelection,
    #                          binning, weights=mcWeight[channel], 
    #                          #nameForLegend=m.replace('m', 'm_\\text{H} = ')+'\\text{ GeV}',
    #                          isBackground=False))
    #     extraSignal[-1].fillstyle = 'hollow'
    #     extraSignal[-1].linestyle = 'dashed'
    #     extraSignal[-1].linecolor = extraSignal[-1].fillcolor
    #     extraSignal[-1].SetLineWidth(3 * extraSignal[-1].GetLineWidth())
    #     extraSignal[-1].legendstyle = "L"
    # 
    #     for b in extraSignal[-1]:
    #         if b.value < 0:
    #             b.value = 0.
    #             b.error = 0.
        
    extraSignal = [sigShapeHists[m] for m in sorted(sigShapeHists.keys())]

    legParams = {'leftmargin' : .3}#'topmargin' : 0.03, 'leftmargin' : .45, 'rightmargin' : .03, 'entryheight' : .025}

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
        }

    plotter.fullPlot('HighMass{}'.format(chEnding), channel, var, constSelection, 
                     binning, 'mc', ['data','data ','data  '], 
                     drawOpts={'logy_crop_value':5e-03}, logy=True,
                     outFile='HighMassShapeLog{}.png'.format(chEnding), 
                     **kwargs)
    plotter.fullPlot('HighMass{}'.format(chEnding), channel, var, constSelection, 
                     binning, 'mc', ['data','data ','data  '], 
                     outFile='HighMassShape{}.png'.format(chEnding), 
                     **kwargs)


