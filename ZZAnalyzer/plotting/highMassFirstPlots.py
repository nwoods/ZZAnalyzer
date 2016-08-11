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
parser.add_argument('--test', action='store_true', help='Make just one plot as a test.')
parser.add_argument('--unblind', action='store_true', help='Remove blinding on 700-800 GeV')
parser.add_argument('--pas', action='store_true', help='Only make plots used in the PAS')
parser.add_argument('--an', action='store_true', help='Only make plots used in the analysis note')
parser.add_argument('--link', action='store_true', 
                    help='Make the latest plots directory link to these plots')
parser.add_argument('--ntupleVersion', type=str, nargs='?', default='16jun2016_2',
                    help='Version for desired 2016 ntuples')

args = parser.parse_args()

analyses = []

plotType = "Preliminary"

if args.an:
    if args.pas:
        args.pas = False

mcWeight = {
    'eeee' : '(genWeight)',
    'eemm' : '(genWeight)',
    'mmmm' : '(genWeight)',
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
    

def joinSelections(*selections):
    return ' && '.join([s for s in selections if bool(s)])


if args.smp:
    ana = 'smp'
else:
    ana = 'hzz'

outdir = '/afs/cern.ch/user/n/nawoods/www/ZZPlots/highMassComb_{0}_{1}'.format(date.today().strftime('%d%b%Y').lower(), ana)

if args.link:
    link = '/afs/cern.ch/user/n/nawoods/www/ZZPlots/highMassComb_{}_latest'.format(ana)
    print "Putting plots in {}".format(link)
else:
    print "Putting plots in {}".format(outdir)
sampleID = ana

#ntupleVersion2015 = args.ntupleVersion2015
ntupleVersion2016 = args.ntupleVersion

plotter = NtuplePlotter('zz', outdir, 
                        {'mc':'/data/nawoods/ntuples/zzNtuples_mc_16jun2016_0/results_{0}/ZZTo4L_13TeV_*.root,/data/nawoods/ntuples/zzNtuples_mc_16jun2016_0/results_{0}/GluGlu*.root'.format(sampleID),},
                        {'data':'/data/nawoods/ntuples/zzNtuples_data_2016b_{0}/results_{1}/*.root'.format(ntupleVersion2016, sampleID),},
                        intLumi=2600.)

if args.link:
    try:
        os.unlink(link)
    except:
        pass    
    os.symlink(outdir, link)

constSelection = 'MassFSR > 250.'

binning4l = {
    'MassFSR' : [23,250.,1400.],
    'EtaFSR' : [16, -5., 5.],
    'PtFSR' : [30, 0., 180.],
    # 'PhiFSR' : [12, -3.15, 3.15],
    # 'nJets' : [6, -0.5, 5.5],
    # 'nvtx' : [40,0.,40.],
    }

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


        if (not args.unblind) and ana != 'smp' and 'Mass' in var:
            blinding = [[600.,900.]]
        else:
            blinding = []

        legParams={}

        plotter.fullPlot('4l%s%s'%(varName,chEnding), channel, var, constSelection, 
                         bins, 'mc', 'data', canvasX=1000, logy=False, 
                         xTitle=xTitle4l[varName].replace('__PARTICLES__',particles), 
                         xUnits=units[varName],
                         outFile='%s%s.png'%(varName,chEnding), 
                         mcWeights=mcWeight[channel], drawRatio=False,
                         widthInYTitle=bool(units[var]),
                         blinding=blinding,
                         legParams=legParams,
                         plotType=plotType)

        if args.test:
            exit()


binning2l = {
    'MassFSR#1' : [40, 40., 120.],
    'MassFSR#2' : [60, 0., 120.],
    'EtaFSR' : [20, -5., 5.],
    'PtFSR' : [70, 0., 700.],
    # 'PhiFSR' : [12, -3.15, 3.15],
    }
if ana == 'smp':
    binning2l['MassFSR#1'] = [30, 60., 120.]
    binning2l['MassFSR#2'] = [30, 60., 120.]

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
                         bins, 'mc', 'data', canvasX=1000, logy=False, 
                         xTitle=xTitles2l[var]%objects2l[z],
                         xUnits=units[var],
                         yTitle=yAxisTitle,
                         outFile='%s%s.png'%(z,var), 
                         mcWeights=[mcWeight[c] for c in channels], 
                         drawRatio=False,
                         widthInYTitle=bool(units[var]),
                         legParams=legParams,
                         plotType=plotType)


binning1l = {
    # 'Phi' : [12, -3.15, 3.15],
    'Eta' : [10, -2.5, 2.5],
    'Pt' : [20, 0., 600.],
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

        plotter.fullPlot('%s%s'%(lep, var), channels, variables, constSelection,
                         bins, 'mc', 'data', canvasX=1000, logy=False, 
                         xTitle=xTitles1l[var]%objName1l[lep],
                         xUnits=units[var],
                         yTitle='Electrons' if lep == 'e' else 'Muons',
                         outFile='%s%s.png'%(lep,var), 
                         mcWeights=[mcWeight[c] for c in channels], 
                         drawRatio=False,
                         widthInYTitle=bool(units[var]),
                         plotType=plotType)

    
    


