# Script to plot gen dilepton mass 
# Nate Woods, U. Wisconsin


import logging
from rootpy import log as rlog; rlog = rlog["/plotGenZMass"]
# don't show most silly ROOT messages
logging.basicConfig(level=logging.WARNING)
rlog["/ROOT.TH1F.Add"].setLevel(rlog.ERROR)
rlog["/rootpy.compiled"].setLevel(rlog.WARNING)

from NtuplePlotter import NtuplePlotter
from ZZAnalyzer.utils import WeightStringMaker, TPFunctionManager
from ZZAnalyzer.utils.helpers import Z_MASS

import rootpy.compiled as RC
from rootpy.io import root_open

import os

RC.register_code('''
#include "TLorentzVector.h"

float dileptonMass(float pt1, float eta1, float phi1, float m1,
                   float pt2, float eta2, float phi2, float m2)
{
  TLorentzVector v1, v2;

  if(abs(pt1) > 998. || abs(pt2) > 998.)
    return 9999.;

  v1.SetPtEtaPhiM(pt1, eta1, phi1, m1);
  v2.SetPtEtaPhiM(pt2, eta2, phi2, m2);

  return (v1 + v2).M();
}
''', ['dileptonMass'])

# force to compile
foo = getattr(RC, 'dileptonMass')

tpVersionHash = 'v2.0-13-g36fc26c' #'v2.0-11-gafcf7cc' #'v1.1-4-ga295b14-extended'

TP = TPFunctionManager(tpVersionHash)

z1eMCWeight = '*'.join(TP.getTPString('e%d'%ne, 'TightID')+'*'+TP.getTPString('e%d'%ne, 'IsoTight') for ne in range(1,3))
z2eMCWeight = '*'.join(TP.getTPString('e%d'%ne, 'TightID')+'*'+TP.getTPString('e%d'%ne, 'IsoTight') for ne in range(3,5))
z1mMCWeight = '*'.join(TP.getTPString('m%d'%nm, 'TightID')+'*'+TP.getTPString('m%d'%nm, 'IsoTight') for nm in range(1,3))
z2mMCWeight = '*'.join(TP.getTPString('m%d'%nm, 'TightID')+'*'+TP.getTPString('m%d'%nm, 'IsoTight') for nm in range(3,5))

wts = WeightStringMaker('puWeight')

fPUScale = root_open(os.path.join(os.environ['zza'],'ZZAnalyzer','data/pileupReweighting/PUScaleFactors_29Feb2016.root'))
puScaleFactorHist = fPUScale.Get("puScaleFactor")
puScaleFactorStr = wts.makeWeightStringFromHist(puScaleFactorHist, 'nTruePU')

mcWeight = {
    'eeee' : '(GenWeight*{0}*{1}*{2})'.format(puScaleFactorStr, z1eMCWeight, z2eMCWeight),
    'eemm' : '(GenWeight*{0}*{1}*{2})'.format(puScaleFactorStr, z1eMCWeight, z1mMCWeight),
    'mmmm' : '(GenWeight*{0}*{1}*{2})'.format(puScaleFactorStr, z1mMCWeight, z2mMCWeight),
}

channels = {
    'z'   : ['eeee','eeee','eemm','eemm','mmmm','mmmm'],
    'z1'  : ['eeee','eemm','eemm','mmmm'],
    'z2'  : ['eeee','eemm','eemm','mmmm'],
    'ze'  : ['eeee','eeee','eemm'],
    'zm'  : ['mmmm','mmmm','eemm'],
    'z1e' : ['eeee','eemm'],
    'z1m' : ['mmmm','eemm'],
    'z2e' : ['eeee','eemm'],
    'z2m' : ['mmmm','eemm'],
    }

wts = {z:[mcWeight[c] for c in channels[z]] for z in channels}

selTemp = '(abs({{0}}1_{{0}}2_MassDREtFSR - {0}) < abs({{1}}1_{{1}}2_MassDREtFSR - {0}))'.format(Z_MASS)
eBetter = selTemp.format('e', 'm')
mBetter = selTemp.format('m', 'e')
sels = {
    'z'   : '',
    'z1'  : ['', eBetter, mBetter, ''],
    'z2'  : ['', eBetter, mBetter, ''],
    'ze'  : '',
    'zm'  : '',
    'z1e' : ['', eBetter],
    'z1m' : ['', mBetter],
    'z2e' : ['', mBetter],
    'z2m' : ['', eBetter],
    }

genMassTemp = 'dileptonMass({0}GenPt, {0}GenEta, {0}GenPhi, {0}Mass, {1}GenPt, {1}GenEta, {1}GenPhi, {1}Mass)'
genMassZ1e = genMassTemp.format('e1', 'e2')
genMassZ2e = genMassTemp.format('e3', 'e4')
genMassZ1m = genMassTemp.format('m1', 'm2')
genMassZ2m = genMassTemp.format('m3', 'm4')

massCutTemp = '(%s < {0})'
massCutZ1e = massCutTemp%genMassZ1e
massCutZ2e = massCutTemp%genMassZ2e
massCutZ1m = massCutTemp%genMassZ1m
massCutZ2m = massCutTemp%genMassZ2m
massCuts = {
    'z'   : [massCutZ1e, massCutZ2e, massCutZ1e, massCutZ1m, massCutZ1m, massCutZ2m], 
    'z1'  : [massCutZ1e, massCutZ1e, massCutZ1m, massCutZ1m], 
    'z2'  : [massCutZ2e, massCutZ1m, massCutZ1e, massCutZ2m], 
    'ze'  : [massCutZ1e, massCutZ2e, massCutZ1e], 
    'zm'  : [massCutZ1m, massCutZ2m, massCutZ1m], 
    'z1e' : [massCutZ1e, massCutZ1e], 
    'z2e' : [massCutZ2e, massCutZ1e], 
    'z1m' : [massCutZ1m, massCutZ1m], 
    'z2m' : [massCutZ2m, massCutZ1m], 
    }

varTemp = '(({{0}}_{{1}}_MassDREtFSR - {0}) / {0})'.format(genMassTemp)
z1eVar = varTemp.format('e1', 'e2')
z2eVar = varTemp.format('e3', 'e4')
z1mVar = varTemp.format('m1', 'm2')
z2mVar = varTemp.format('m3', 'm4')
var = {
    'z'   : [z1eVar, z2eVar, z1eVar, z1mVar, z1mVar, z2mVar],
    'z1'  : [z1eVar, z1eVar, z1mVar, z1mVar],
    'z2'  : [z2eVar, z1mVar, z1eVar, z2mVar],
    'ze'  : [z1eVar, z2eVar, z1eVar],
    'zm'  : [z1mVar, z2mVar, z1mVar],
    'z1e' : [z1eVar, z1eVar],
    'z2e' : [z2eVar, z1eVar],
    'z1m' : [z1mVar, z1mVar],
    'z2m' : [z2mVar, z1mVar],
    }

plotter = NtuplePlotter('zz', '/afs/cern.ch/user/n/nawoods/www/ZZPlots/genZMass/',
                        {'mc':'/data/nawoods/ntuples/zzNtuples_mc_26jan2016_0/results_full/*ZZTo*.root'}, 
                        {},
                        2619.)

for massCut in [10., 40., 60., 120.]:

    print 'Making plots for mll < {}'.format(int(massCut))

    for z in channels:

        d = plotter.Drawing('{}GenMassRes_m-{}'.format(z, int(massCut)), 
                            plotter.style, 1000, 1000,
                            False, False)
    
        if isinstance(sels[z], str):
            if sels[z]:
                sel = [' && '.join([sels[z], mc.format(massCut)]) for mc in massCuts[z]]
            else:
                sel = [mc.format(massCut) for mc in massCuts[z]]
        else:
            sel = [' && '.join([s, mc.format(massCut)]) if s else mc.format(massCut) 
                   for s, mc in zip(sels[z], massCuts[z])]

        s = plotter.makeCategoryStack('mc', channels[z], var[z], sel,
                                      [11, -.1, .1], 1., wts[z])
        d.addObject(s)
    
        d.draw({}, os.path.join(plotter.outdir, 
                                '{}GenMassRes_m-{}.png'.format(z, 
                                                               int(massCut))
                                ), 
               False, 'm_{\\ell\\ell} \\text{ resolution}', '', 'Events', '', 
               True, {}, True, plotter.intLumi, True, widthInYTitle=True)

        

selOverTemp = '({0}_{1}_MassDREtFSR < 10. && ({0}GenPt < 0. || {1}GenPt < 0.))'
selOverE = [selOverTemp.format('e1', 'e2'), selOverTemp.format('e3', 'e4'), selOverTemp.format('e1', 'e2')]
selOverM = [selOverTemp.format('m1', 'm2'), selOverTemp.format('m3', 'm4'), selOverTemp.format('m1', 'm2')]

overE = plotter.makeCategoryStack('mc', channels['ze'], '1.', selOverE,
                                  [1, 0, 2.], 1., wts['ze'])

print "Unmatched ee with mass below 10: {}".format(sum(overE.hists).Integral())

overM = plotter.makeCategoryStack('mc', channels['zm'], '1.', selOverM,
                                  [1, 0, 2.], 1., wts['zm'])

print "Unmatched mumu with mass below 10: {}".format(sum(overM.hists).Integral())
