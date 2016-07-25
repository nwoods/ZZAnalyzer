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
        'MassFSR' : [70. + 10. * i for i in xrange(23)] + [300. + 20. * i for i in xrange(10)] + [500. + 40. * i for i in xrange(5)] + [700.,800.,900.],
        'EtaFSR' : [16, -5., 5.],
        'PtFSR' : [30, 0., 180.],
        # 'PhiFSR' : [12, -3.15, 3.15],
        # 'nJets' : [6, -0.5, 5.5],
        # 'nvtx' : [40,0.,40.],
        }
    if ana == 'z4l':
        binning4l['MassFSR'] = [25, 60., 110.]

    if args.pas or args.an:
        del binning4l['EtaFSR']
        del binning4l['PtFSR']

    vars4l = {v:v for v in binning4l}
    
    xTitle4l = {
        'Mass' : 'm_{__PARTICLES__}',
        'MassFSR' : 'm_{__PARTICLES__}',
        'EtaFSR' : '\\eta_{__PARTICLES__}',
        'PtFSR' : 'p_{T_{__PARTICLES__}}',
        'PhiFSR' : '\\phi_{__PARTICLES__}',
        'nJets' : '\\text{# Jets}',
        'nvtx' : '\\text{# PVs}',
        }
    
    for varName, bins in binning4l.iteritems():
        var = vars4l[varName]

        if args.test:
            varName = 'MassFSR'
            var = vars4l[varName]
            bins = binning4l[varName]

        print "    Plotting 4l {}".format(var)
    
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
                             extraBkgs=extraBkgs, outFile='%s%s.png'%(varName,chEnding), 
                             mcWeights=mcWeight[channel], drawRatio=False,
                             widthInYTitle=bool(units[var]),
                             blinding=blinding,
                             legParams=legParams,
                             extraObjects=extraObjects,
                             plotType=plotType)

            if args.test:
                exit()
    
    
    binning2l = {
        'MassFSR#1' : [40, 40., 120.],
        'MassFSR#2' : [60, 0., 120.],
        'EtaFSR' : [20, -5., 5.],
        'PtFSR' : [60, 0., 600.],
        # 'PhiFSR' : [12, -3.15, 3.15],
        }
    if ana == 'smp':
        binning2l['MassFSR#1'] = [30, 60., 120.]
        binning2l['MassFSR#2'] = [30, 60., 120.]
    elif ana == 'z4l':
        binning2l['MassFSR#1'] = [30, 60., 120.]
        binning2l['MassFSR#2'] = [40, 0., 40.]

    if args.an or args.pas:
        for v in binning2l.keys():
            if 'Mass' not in v:
                del binning2l[v]
    
    xTitles2l = {
        'Mass' : 'm_{%s}',
        'MassFSR' : 'm_{%s}',
        'EtaFSR' : '\\eta_{%s}',
        'PtFSR' : 'p_{T_{%s}}',
        'PhiFSR' : '\\phi_{%s}',
        }
    
    channels2l = {
        'z' : ['eeee', 'eeee', 'eemm', 'eemm', 'mmmm', 'mmmm',],
        'z1' : ['eeee', 'eemm', 'eemm', 'mmmm'],
        'z2' : ['eeee', 'eemm', 'eemm', 'mmmm'],
        'z1e' : ['eeee', 'eemm'],
        'z2e' : ['eeee', 'eemm'],
        'z1m' : ['eemm', 'mmmm'],
        'z2m' : ['eemm', 'mmmm'],
        'ze' : ['eeee', 'eeee', 'eemm'],
        'zm' : ['eemm', 'mmmm', 'mmmm'],
        }

    if args.pas:
        for zee in channels2l.keys():
            if 'e' in zee or 'm' in zee:
                del channels2l[zee]
    
    selections2l = {
        'z' : '',
        'z1' : ['', 'abs(e1_e2_MassFSR-%f) < abs(m1_m2_MassFSR-%f)'%(Z_MASS, Z_MASS), 
                'abs(m1_m2_MassFSR-%f) < abs(e1_e2_MassFSR-%f)'%(Z_MASS, Z_MASS), ''],
        'z2' : ['', 'abs(e1_e2_MassFSR-%f) > abs(m1_m2_MassFSR-%f)'%(Z_MASS, Z_MASS), 
                'abs(m1_m2_MassFSR-%f) > abs(e1_e2_MassFSR-%f)'%(Z_MASS, Z_MASS), ''],
        'z1e' : ['', 'abs(e1_e2_MassFSR-%f) < abs(m1_m2_MassFSR-%f)'%(Z_MASS, Z_MASS)],
        'z2e' : ['', 'abs(e1_e2_MassFSR-%f) > abs(m1_m2_MassFSR-%f)'%(Z_MASS, Z_MASS)],
        'z1m' : ['abs(e1_e2_MassFSR-%f) > abs(m1_m2_MassFSR-%f)'%(Z_MASS, Z_MASS), ''],
        'z2m' : ['abs(e1_e2_MassFSR-%f) < abs(m1_m2_MassFSR-%f)'%(Z_MASS, Z_MASS), ''],
        'ze' : '',
        'zm' : '',
        }
    for foo, sels in selections2l.iteritems():
        if isinstance(sels, str):
            sels = joinSelections(sels, constSelection)
        else:
            sels = [joinSelections(s,constSelection) for s in sels]
    
    varTemplates2l = {
        'z' : ['e1_e2_%s', 'e3_e4_%s', 'e1_e2_%s', 'm1_m2_%s', 'm1_m2_%s', 'm3_m4_%s'],
        'z1' : ['e1_e2_%s', 'e1_e2_%s', 'm1_m2_%s', 'm1_m2_%s'],
        'z2' : ['e3_e4_%s', 'e1_e2_%s', 'm1_m2_%s', 'm3_m4_%s'],
        'z1e' : ['e1_e2_%s' for i in range(2)],
        'z2e' : ['e3_e4_%s', 'e1_e2_%s'],
        'z1m' : ['m1_m2_%s' for i in range(2)],
        'z2m' : ['m1_m2_%s', 'm3_m4_%s'],
        'ze' : ['e1_e2_%s', 'e3_e4_%s', 'e1_e2_%s'],
        'zm' : ['m1_m2_%s', 'm3_m4_%s', 'm1_m2_%s'],
        }
    
    objects2l = {
        'z' : '\\ell\\ell',
        'z1' : 'Z_{1}',
        'z2' : 'Z_{2}',
        'z1e' : 'Z_{1} \\left(ee \\right)',
        'z2e' : 'Z_{2} \\left(ee \\right)',
        'z1m' : 'Z_{1} \\left(\\mu\\mu \\right)',
        'z2m' : 'Z_{2} \\left(\\mu\\mu \\right)',
        'ze' : 'Z \\left(ee \\right)',
        'zm' : 'Z \\left(\\mu\\mu \\right)',
        }

    for vbl, bins in binning2l.iteritems():
        
        print "    Plotting Z {}".format(vbl)

        for z, channels in channels2l.iteritems():
        
            var = vbl.split("#")[0]
            if len(vbl.split("#")) > 1:
                if z == 'z' or z == 'ze' or z == 'zm':
                    if vbl.split("#")[1] != '2':
                        continue
                elif vbl.split("#")[1] not in z:
                    continue
    
            variables = [v%var for v in varTemplates2l[z]]
    
            if noBKG:
                extraBkgs = []
            else:
                cr3P1F = plotter.makeHist('3P1F', '3P1F', channels, variables,
                                          selections2l[z], bins, 
                                          weights=[cr3PScale[c] for c in channels], 
                                          perUnitWidth=False, 
                                          nameForLegend='Z/WZ+X',
                                          isBackground=True)
                cr2P2F = plotter.makeHist('2P2F', '2P2F', channels, variables,
                                          selections2l[z], bins,
                                          weights=[cr2PScale[c] for c in channels], 
                                          perUnitWidth=False, 
                                          nameForLegend='Z/WZ+X',
                                          isBackground=True)
        
                cr3P1F.sumw2()
                cr2P2F.sumw2()
        
                for ss in subtractSamples:
                    sub3P = plotter.makeHist("mc3P1F", ss, channels,
                                             variables, selections2l[z], bins,
                                             weights=[cr3PScaleMC[c] for c in channels],
                                             perUnitWidth=False)
                    cr3P1F -= sub3P
                    sub2P = plotter.makeHist("mc2P2F", ss, channels,
                                             variables, selections2l[z], bins,
                                             weights=[cr2PScaleMC[c] for c in channels],
                                             perUnitWidth=False)
                    cr2P2F -= sub2P
                
                if args.smooth:
                    cr3P1F.Smooth(1)
                    cr2P2F.Smooth(1)
                    
                    if 'Mass' in var:
                        mMax = 120.
                        if ana == 'smp':
                            mMin = 60.
                        elif '1' in z:
                            mMin = 40.
                        else:
                            mMin = 4.

                        for i in range(1,cr3P1F.nbins()+1):
                            if cr3P1F.GetBinLowEdge(i) >= mMax:
                                cr3P1F[i].value = 0
                            if cr3P1F.GetBinLowEdge(i) + cr3P1F.GetBinWidth(i) <= mMin:
                                cr3P1F[i].value = 0
                            if cr2P2F.GetBinLowEdge(i) >= mMax:
                                cr2P2F[i].value = 0
                            if cr2P2F.GetBinLowEdge(i) + cr2P2F.GetBinWidth(i) <= mMin:
                                cr2P2F[i].value = 0
                    
                cr3P1F.sumw2()
                cr2P2F.sumw2()
                    
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
                    
                cr3P1F -= cr2P2F
        
                cr3P1F.sumw2()
    
                extraBkgs = [cr3P1F]
    
            if ana != 'smp' and 'Mass' in var:
                legParams = {'leftmargin' : 0.2, 'rightmargin' : 0.35}
            else:
                legParams = {}

            if '1' in z or '2' in z:
                yAxisTitle = 'Events'
            elif ana == 'smp':
                yAxisTitle = 'Z candidates'
            else:
                yAxisTitle = "Dilepton candidates" 

            plotter.fullPlot('%s%s'%(z, var), channels, variables, 
                             selections2l[z], 
                             bins, 'mc', ['datab','datac','datad'], canvasX=1000, logy=False, 
                             xTitle=xTitles2l[var]%objects2l[z],
                             xUnits=units[var],
                             yTitle=yAxisTitle,
                             extraBkgs=extraBkgs, outFile='%s%s.png'%(z,var), 
                             mcWeights=[mcWeight[c] for c in channels], 
                             drawRatio=False,
                             widthInYTitle=bool(units[var]),
                             legParams=legParams,
                             plotType=plotType)
    
    
    binning1l = {
        # 'Phi' : [12, -3.15, 3.15],
        'Eta' : [10, -2.5, 2.5],
        'Pt' : [30, 0., 300.],
        'Iso' : [16, 0., 0.4],
        # 'PVDXY' : [10, -.5, .5],
        # 'PVDZ' : [10, -1., 1.],
        }

    if args.pas:
        binning1l = {}
    
    vars1l = {
        'Pt' : {lep:'Pt' for lep in ['e', 'm']},
        'Eta' : {lep:'Eta' for lep in ['e', 'm']},
        'Phi' : {lep:'Phi' for lep in ['e', 'm']},
        'PVDXY' : {lep:'PVDXY' for lep in ['e', 'm']},
        'PVDZ' : {lep:'PVDZ' for lep in ['e', 'm']},
        'Iso' : {lep:'ZZIso' for lep in ['e', 'm']},
        #'Iso' : {'e' : 'RelPFIsoRhoFSR', 'm' : 'RelPFIsoDBFSR'},
        }
    
    xTitles1l = {
        'Phi' : '\\phi_{%s}',
        'Eta' : '\\eta_{%s}',
        'Pt' : 'p_{T_{%s}}',
        'PVDXY' : '\\Delta_{xy} \\text{(%s,PV)}',
        'PVDZ' : '\\Delta_{z} \\text{(%s,PV)}',
        'Iso' : '\\text{Rel. PF Iso. (PU and FSR corrected)} (%s)',
        }
    
    channels1l = {
        'e' : ['eeee' for i in range(4)] + ['eemm' for i in range(2)],
        'm' : ['eemm' for i in range(2)] + ['mmmm' for i in range(4)],
        }
    
    varTemplates1l = {
        'e' : ['e%d%%s'%nl for nl in range(1,5)] + ['e%d%%s'%nl for nl in range(1,3)],
        'm' : ['m%d%%s'%nl for nl in range(1,3)] + ['m%d%%s'%nl for nl in range(1,5)],
        }
    
    objName1l = {
        'e' : 'e',
        'm' : '\\mu',
        }
    
    for var, bins in binning1l.iteritems():

        print '    Plotting lepton {}'.format(var)
    
        for lep, channels in channels1l.iteritems():
        
            variables = [v%vars1l[var][lep] for v in varTemplates1l[lep]]
    
            if noBKG:
                extraBkgs = []
            else:
                cr3P1F = plotter.makeHist('3P1F', '3P1F', channels, variables, 
                                          constSelection, bins, 
                                          weights=[cr3PScale[c] for c in channels], 
                                          perUnitWidth=False, 
                                          nameForLegend='Z/WZ+X',
                                          isBackground=True)
                cr2P2F = plotter.makeHist('2P2F', '2P2F', channels, variables, 
                                          constSelection, bins,
                                          weights=[cr2PScale[c] for c in channels], 
                                          perUnitWidth=False, 
                                          nameForLegend='Z/WZ+X',
                                          isBackground=True)
        
                cr3P1F.sumw2()
                cr2P2F.sumw2()
        
                for ss in subtractSamples:
                    sub3P = plotter.makeHist("mc3P1F", ss, channels,
                                             variables, constSelection, bins,
                                             weights=[cr3PScaleMC[c] for c in channels],
                                             perUnitWidth=False)
                    cr3P1F -= sub3P
                    sub2P = plotter.makeHist("mc2P2F", ss, channels,
                                             variables, constSelection, bins,
                                             weights=[cr2PScaleMC[c] for c in channels],
                                             perUnitWidth=False)
                    cr2P2F -= sub2P
        
                cr3P1F.sumw2()
                cr2P2F.sumw2()
                    
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
                    
                cr3P1F -= cr2P2F
        
                cr3P1F.sumw2()
    
                extraBkgs = [cr3P1F]
    
            plotter.fullPlot('%s%s'%(lep, var), channels, variables, constSelection,
                             bins, 'mc', ['datab','datac','datad'], canvasX=1000, logy=False, 
                             xTitle=xTitles1l[var]%objName1l[lep],
                             xUnits=units[var],
                             yTitle='Electrons' if lep == 'e' else 'Muons',
                             extraBkgs=extraBkgs, outFile='%s%s.png'%(lep,var), 
                             mcWeights=[mcWeight[c] for c in channels], 
                             drawRatio=False,
                             widthInYTitle=bool(units[var]),
                             plotType=plotType)
    
    
    


