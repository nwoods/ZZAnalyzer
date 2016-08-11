'''

Make all ZZ plots with data driven backgrounds.

This is a goddamn mess; I'll clean it up later.

'''


# include logging stuff first so other imports don't babble at us
import logging
from rootpy import log as rlog; rlog = rlog["/testPlotsDataDrivenBkg"]
# don't show most silly ROOT messages
logging.basicConfig(level=logging.WARNING)
rlog["/ROOT.TH1F.Add"].setLevel(rlog.ERROR)
rlog["/rootpy.compiled"].setLevel(rlog.WARNING)
rlog["/ROOT.TClassTable.Add"].setLevel(rlog.ERROR)


from NtuplePlotter import NtuplePlotter
from ZZAnalyzer.utils.helpers import Z_MASS
from ZZAnalyzer.utils import WeightStringMaker, TPFunctionManager, BkgManager

from rootpy.io import root_open
from rootpy.ROOT import R

import os
from datetime import date

from math import sqrt

from argparse import ArgumentParser

parser = ArgumentParser(description="Make lots of plots for ZZ analyses.")
parser.add_argument('--smp', action='store_true', help='SMP ZZ plots')
parser.add_argument('--hzz', action='store_true', help='HZZ plots')
parser.add_argument('--full', action='store_true', help='Full 4l spectrum plots')
parser.add_argument('--z4l', action='store_true', help='SMP Z->4l plots')
parser.add_argument('--massFit', type=str, nargs='?',
                    help='Root file with workspace containting data and pdf for Z4l mass fit')
parser.add_argument('--test', action='store_true', help='Make just one plot as a test.')
parser.add_argument('--goldv2', action='store_true', help='Use JSON from December 2015.')
parser.add_argument('--blind', action='store_true', help='Apply HZZ blinding')
parser.add_argument('--smooth', action='store_true', help='Smooth reducible background histogram')
parser.add_argument('--pas', action='store_true', help='Only make plots used in the PAS')
parser.add_argument('--an', action='store_true', help='Only make plots used in the analysis note')
parser.add_argument('--paper', action='store_true', 
                    help='Only make plots used in the paper, and don\'t label them "preliminary"')
parser.add_argument('--link', action='store_true', 
                    help='Make the latest plots directory link to these plots')
parser.add_argument('--tpVersion', type=str, nargs='?', default='v2.0-13-g36fc26c',
                    help='Version hash for desired scale factors')
parser.add_argument('--bkgVersion', type=str, nargs='?', default='01mar2016',
                    help='Version for desired fake rates')
parser.add_argument('--puVersion', type=str, nargs='?', default='29Feb2016',
                    help='Version for desired pileup scale factors')
parser.add_argument('--ntupleVersion', type=str, nargs='?', default='26jan2016_0',
                    help='Version for desired ntuples')

args = parser.parse_args()

analyses = []

if not (args.smp or args.hzz or args.full or args.z4l):
    args.smp = True
    args.hzz = True
    args.full = True
    args.z4l = True

if args.smp:
    analyses.append('smp')
if args.hzz:
    analyses.append('hzz')
if args.full:
    analyses.append('full')
if args.z4l:
    analyses.append('z4l')

if args.paper:
    args.pas = True
    plotType = ""
else:
    plotType = "Preliminary"

if args.an:
    if args.paper:
        print "WARNING: argument --paper ignored. Remove --an to make paper-formatted plots."
    if args.pas:
        args.pas = False

outdir = '/afs/cern.ch/user/n/nawoods/www/ZZPlots/firstICHEPPlots'

# tpVersionHash = 'v2.0-13-g36fc26c' #'v2.0-11-gafcf7cc' #'v1.1-4-ga295b14-extended'
# 
# TP = TPFunctionManager(tpVersionHash)

z1eMCWeight = 'e1EffScaleFactor * e2EffScaleFactor'
z2eMCWeight = 'e3EffScaleFactor * e4EffScaleFactor'
#z1mMCWeight = 'm1EffScaleFactor * m1TrkRecoEffScaleFactor * m2EffScaleFactor * m2TrkRecoEffScaleFactor'
#z2mMCWeight = 'm3EffScaleFactor * m3TrkRecoEffScaleFactor * m4EffScaleFactor * m4TrkRecoEffScaleFactor'
z1mMCWeight = 'm1EffScaleFactor *  m2EffScaleFactor'
z2mMCWeight = 'm3EffScaleFactor *  m4EffScaleFactor'

mcWeight = {
    'eeee' : '(genWeight*{0}*{1})'.format(z1eMCWeight, z2eMCWeight),
    'eemm' : '(genWeight*{0}*{1})'.format(z1eMCWeight, z1mMCWeight),
    'mmmm' : '(genWeight*{0}*{1})'.format(z1mMCWeight, z2mMCWeight),
}

mcWeight['zz'] = [mcWeight['eeee'], mcWeight['eemm'], mcWeight['mmmm']]

bkg = BkgManager(args.bkgVersion)

cr3PScale = {
    ch : bkg.fullString3P1F(ch) for ch in ['eeee','eemm','mmmm']
}

cr3PScaleMC = {c:'*'.join([cr3PScale[c], mcWeight[c]]) for c in cr3PScale}

cr3PScale['zz'] = [cr3PScale[c] for c in ['eeee','eemm','mmmm']]
cr3PScaleMC['zz'] = [cr3PScaleMC[c] for c in ['eeee','eemm','mmmm']]

cr2PScale = {
    ch : bkg.fullString2P2F(ch) for ch in ['eeee','eemm','mmmm']
}

cr2PScaleMC = {c:'*'.join([cr2PScale[c], mcWeight[c]]) for c in cr2PScale}

cr2PScale['zz'] = [cr2PScale[c] for c in ['eeee','eemm','mmmm']]
cr2PScaleMC['zz'] = [cr2PScaleMC[c] for c in ['eeee','eemm','mmmm']]

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
    

noBKG = False

def joinSelections(*selections):
    return ' && '.join([s for s in selections if bool(s)])


for ana in analyses:
    print "Initializing plotter for {} analysis".format(ana.upper())

    # cut that is always applied, in case it's needed
    constSelection = ''
    if ana == 'z4l':
        constSelection = 'MassFSR < 110.'

    print "Putting plots in {}".format(outdir)

    sampleID = ana
    if ana == 'z4l':
        sampleID = 'full'

    plotter = NtuplePlotter('zz', outdir, 
                            {'mc':'/data/nawoods/ntuples/uwvvNtuples_ggH_18jul2016/results_{0}/*.root,/data/nawoods/ntuples/uwvvNtuples_smzz_19jul2016/results_{0}/*.root'.format(sampleID),},
                             # 'mc3P1F':'/data/nawoods/ntuples/uwvvNtuples_smzz_19jul2016/results_{0}_3P1F/*.root'.format(sampleID),
                             # 'mc2P2F':'/data/nawoods/ntuples/uwvvNtuples_smzz_19jul2016/results_{0}_2P2F/*.root'.format(sampleID),}, 
                            {'datab':'/data/nawoods/ntuples/uwvvNtuples_data2016b*/results_{0}/*.root'.format(sampleID),
                             'datac':'/data/nawoods/ntuples/uwvvNtuples_data2016c*/results_{0}/*.root'.format(sampleID),
                             'datad':'/data/nawoods/ntuples/uwvvNtuples_data2016d*/results_{0}/*.root'.format(sampleID),
                             '3P1F':'/data/nawoods/ntuples/uwvvNtuples_data2016*/results_{0}_3P1F/*.root'.format(sampleID),
                             '2P2F':'/data/nawoods/ntuples/uwvvNtuples_data2016*/results_{0}_2P2F/*.root'.format(sampleID),
                             }, 
                            intLumi=9200.)
    
    plotter.printPassingEvents('datab')
    plotter.printPassingEvents('datac')
    plotter.printPassingEvents('datad')

    # samples to subtract off of CRs based on MC
    subtractSamples = []
    # for s in plotter.ntuples['mc3P1F']:
    #     if s[:3] == 'ZZT' or 'GluGluToContin' in s and 'tau' not in s:
    #         subtractSamples.append(s)


    binning4l = {
        'hi' : [5,120,130],
        'lo' : [10,80,100],
        }

    var = 'MassFSR'
    varName = 'MassFSR'

    for region, bins in binning4l.iteritems():
    
        xTitle4l = {
            'Mass' : 'm_{__PARTICLES__}',
            'MassFSR' : 'm_{__PARTICLES__}',
            'EtaFSR' : '\\eta_{__PARTICLES__}',
            'PtFSR' : 'p_{T_{__PARTICLES__}}',
            'PhiFSR' : '\\phi_{__PARTICLES__}',
            'nJets' : '\\text{# Jets}',
            'nvtx' : '\\text{# PVs}',
            }
        
        for channel in ['zz', 'eeee', 'eemm', 'mmmm']:
                
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
        
            if noBKG:
                extraBkgs = []
            else:
                cr3P1F = plotter.makeHist('3P1F', '3P1F', channel, var, constSelection, 
                                          bins, weights=cr3PScale[channel], 
                                          perUnitWidth=False, nameForLegend='Z/WZ+X',
                                          isBackground=True)
        
        
                cr2P2F = plotter.makeHist('2P2F', '2P2F', channel, var, constSelection, 
                                          bins, weights=cr2PScale[channel], 
                                          perUnitWidth=False, nameForLegend='Z/WZ+X',
                                          isBackground=True)
            
        
                # print '\n', channel, ":" 
                # print "    Init:"
                # print "        3P1F: %f  2P2F: %f"%(cr3P1F.Integral(), cr2P2F.Integral())
            
                cr3P1F.sumw2()
                cr2P2F.sumw2()
            
                for ss in subtractSamples:
                    sub3P = plotter.makeHist("mc3P1F", ss, channel,
                                             var, constSelection, bins,
                                             weights=cr3PScaleMC[channel],
                                             perUnitWidth=False)
                    cr3P1F -= sub3P
                    sub2P = plotter.makeHist("mc2P2F", ss, channel,
                                             var, constSelection, bins,
                                             weights=cr2PScaleMC[channel],
                                             perUnitWidth=False)
                    cr2P2F -= sub2P
            
                    # print "    Subtracted %s:"%ss
                    # print "        3P1F: %f  2P2F: %f"%(cr3P1F.Integral(), cr2P2F.Integral())
            
                    cr3P1F.sumw2()
                    cr2P2F.sumw2()
            
                if args.smooth:
                    cr2P2F.Smooth(2)
                    cr3P1F.Smooth(2)
        
                for b3P, b2P in zip(cr3P1F, cr2P2F):
                    if b3P.value <= 0 or b2P.value > b3P.value:
                        b3P.value = 0.
                        b3P.error = 0.
                        b2P.value = 0.
                        b2P.error = 0.
                    if b2P.value < 0.:
                        b2P.value = 0.
                
                cr3P1F.sumw2()
                cr2P2F.sumw2()
                    
                # print "    Negatives zeroed:"
                # print "        3P1F: %f  2P2F: %f"%(cr3P1F.Integral(), cr2P2F.Integral())
            
                cr3P1F -= cr2P2F
            
                # print "    3P1F-2P2F:"
                # print "        3P1F: %f  2P2F: %f"%(cr3P1F.Integral(), cr2P2F.Integral())
                # break
            
                cr3P1F.sumw2()
        
                extraBkgs = [cr3P1F]
        
            if args.blind and ana != 'smp' and 'Mass' in var:
                blinding = [[110.,150.]]
            else:
                blinding = []
        
            if ana == 'z4l' and varName == 'MassFSR':
                legParams = {'leftmargin' : 0.1, 'rightmargin' : 0.45}
        
                if args.massFit:
                    from rootpy.stats import mute_roostats
                    mute_roostats()
        
                    fFit = root_open(args.massFit)
                    w = fFit.Get("w") # RooFit workspace
                    nbins = int(20 / ((bins[2] - bins[1])/bins[0]))
                    fitFrame = w.var("MassFSR").frame(80., 100., nbins)
                    w.data("data").plotOn(fitFrame)
                    w.pdf('pdf').plotOn(fitFrame, R.RooFit.Range(80.,100.))
                    fit = fitFrame.getObject(1)
                    fit.SetTitle("\\text{Mass Fit}")
                    fit.legendstyle = "L"
                    extraObjects = [fit]
                else:
                    extraObjects = []
            else:
                legParams = {}
                extraObjects = []
        
            plotter.fullPlot('4l%s%s'%(varName,chEnding), channel, var, constSelection, 
                             bins, 'mc', ['datab','datac','datad'], canvasX=1000, logy=False, 
                             xTitle=xTitle4l[varName].replace('__PARTICLES__',particles), 
                             xUnits=units[varName],
                             extraBkgs=extraBkgs, outFile='MassFSR_%s_%s.png'%(region,chEnding), 
                             mcWeights=mcWeight[channel], drawRatio=False,
                             widthInYTitle=bool(units[var]),
                             blinding=blinding,
                             legParams=legParams,
                             extraObjects=extraObjects,
                             plotType=plotType)
        
