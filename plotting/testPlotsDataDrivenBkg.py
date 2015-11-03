'''

Make full SMP ZZ plots with data driven backgrounds.

This is a goddamn mess; I'll clean it up later.

'''


# include logging stuff first so other imports don't babble at us
import logging
from rootpy import log as rlog; rlog = rlog["/testPlotsDataDrivenBkg"]
# don't show most silly ROOT messages
logging.basicConfig(level=logging.WARNING)
rlog["/ROOT.TH1F.Add"].setLevel(rlog.ERROR)
rlog["/rootpy.compiled"].setLevel(rlog.WARNING)


from NtuplePlotter import NtuplePlotter
from ZZHelpers import Z_MASS, dictFromJSONFile
from WeightStringMaker import makeWeightStringFromHist, makeWeightHistFromJSONDict

from rootpy.io import root_open
import rootpy.compiled as C
from rootpy.plotting import HistStack, Canvas
from rootpy.ROOT import Double

import os

plotter = NtuplePlotter('zz', './plots/dataBkgMC2015D_2nov2015', 
                        {'mc':'/data/nawoods/ntuples/zzNtuples_mc_29oct2015_0/results/ZZTo4L_13TeV_*.root,/data/nawoods/ntuples/zzNtuples_mc_29oct2015_0/results/GluGluToZZTo4[em]*.root,/data/nawoods/ntuples/zzNtuples_mc_29oct2015_0/results/GluGluToZZTo2e2m*.root'}, 
                        {'data':'/data/nawoods/ntuples/zzNtuples_data_2015d_26oct2015_0/results/data*.root',
                         '3P1F':'/data/nawoods/ntuples/zzNtuples_data_2015d_26oct2015_0/results_3P1F/data*.root',
                         '2P2F':'/data/nawoods/ntuples/zzNtuples_data_2015d_26oct2015_0/results_2P2F/data*.root',}, 
                        intLumi=1263.89)

tpVersionHash = 'v1.1-1-g4cbf52a_v2'

fFake = root_open(os.environ['zza']+'/data/leptonFakeRate/fakeRate_2nov2015_0.root')
eFakeRateHist = fFake.Get('e_FakeRate').clone()
mFakeRateHist = fFake.Get('m_FakeRate').clone()

eFakeRateStrTemp = makeWeightStringFromHist(eFakeRateHist, '{0}Pt', '{0}Eta')
mFakeRateStrTemp = makeWeightStringFromHist(mFakeRateHist, '{0}Pt', '{0}Eta')

eTagProbeJSON = dictFromJSONFile(os.environ['zza']+'/data/tagAndProbe/electronTagProbe_%s.json'%tpVersionHash)
eIDTightTPHist = makeWeightHistFromJSONDict(eTagProbeJSON['passingZZTight'], 'ratio', 'pt', 'abseta')
eIsoFromTightTPHist = makeWeightHistFromJSONDict(eTagProbeJSON['passingZZIso_passingZZTight'], 'ratio', 'pt', 'abseta')
eIDTightTPStrTemp = makeWeightStringFromHist(eIDTightTPHist, '{0}Pt', 'abs({0}Eta)')
eIsoFromTightTPStrTemp = makeWeightStringFromHist(eIsoFromTightTPHist, '{0}Pt', 'abs({0}Eta)')

mTagProbeJSON = dictFromJSONFile(os.environ['zza']+'/data/tagAndProbe/muonTagProbe_%s.json'%tpVersionHash)
mIDTightTPHist = makeWeightHistFromJSONDict(mTagProbeJSON['passingIDZZTight'], 'ratio', 'pt', 'abseta')
mIsoFromTightTPHist = makeWeightHistFromJSONDict(mTagProbeJSON['passingIsoZZ_passingIDZZTight'], 'ratio', 'pt', 'abseta')
mIDTightTPStrTemp = makeWeightStringFromHist(mIDTightTPHist, '{0}Pt', 'abs({0}Eta)')
mIsoFromTightTPStrTemp = makeWeightStringFromHist(mIsoFromTightTPHist, '{0}Pt', 'abs({0}Eta)')

z1eMCWeight = '*'.join(eIDTightTPStrTemp.format('e%d'%ne)+'*'+eIsoFromTightTPStrTemp.format('e%d'%ne) for ne in range(1,3))
z2eMCWeight = '*'.join(eIDTightTPStrTemp.format('e%d'%ne)+'*'+eIsoFromTightTPStrTemp.format('e%d'%ne) for ne in range(3,5))
z1mMCWeight = '*'.join(mIDTightTPStrTemp.format('m%d'%nm)+'*'+mIsoFromTightTPStrTemp.format('m%d'%nm) for nm in range(1,3))
z2mMCWeight = '*'.join(mIDTightTPStrTemp.format('m%d'%nm)+'*'+mIsoFromTightTPStrTemp.format('m%d'%nm) for nm in range(3,5))
#z1emMCWeight = '(abs(e1_e2_MassFSR-{0}) < abs(m1_m2_MassFSR-{0}) ? {1} : {2})'.format(Z_MASS, z1eMCWeight, z1mMCWeight)
#z2emMCWeight = '(abs(e1_e2_MassFSR-{0}) < abs(m1_m2_MassFSR-{0}) ? {1} : {2})'.format(Z_MASS, z1mMCWeight, z1eMCWeight)

fPUScale = root_open(os.environ['zza']+'/data/pileupReweighting/PUScaleFactors_28Oct2015.root')
puScaleFactorHist = fPUScale.Get("puScaleFactor")
puScaleFactorStr = makeWeightStringFromHist(puScaleFactorHist, 'nTruePU')

mcWeight = {
    'eeee' : '(GenWeight*{0}*{1}*{2})'.format(puScaleFactorStr, z1eMCWeight, z2eMCWeight),
    'eemm' : '(GenWeight*{0}*{1}*{2})'.format(puScaleFactorStr, z1eMCWeight, z1mMCWeight),
    'mmmm' : '(GenWeight*{0}*{1}*{2})'.format(puScaleFactorStr, z1mMCWeight, z2mMCWeight),
}

mcWeight['zz'] = [mcWeight['eeee'], mcWeight['eemm'], mcWeight['mmmm']]

cr3PScale = {
    'eeee' : '*'.join('(e{0}HZZTightID+e{0}HZZIsoPass < 1.5 ? {1} : 1.)'.format(ne, eFakeRateStrTemp.format('e%d'%ne)) for ne in range(1,5)),
    'eemm' : '*'.join('(e{0}HZZTightID+e{0}HZZIsoPass < 1.5 ? {1} : 1.)*(m{0}HZZTightID+m{0}HZZIsoPass < 1.5 ? {2} : 1.)'.format(ne, eFakeRateStrTemp.format('e%d'%ne), mFakeRateStrTemp.format('m%d'%ne)) for ne in range(1,3)),
    'mmmm' : '*'.join('(m{0}HZZTightID+m{0}HZZIsoPass < 1.5 ? {1} : 1.)'.format(nm, mFakeRateStrTemp.format('m%d'%nm)) for nm in range(1,5)),
}
cr3PScale['zz'] = [cr3PScale[c] for c in ['eeee','eemm','mmmm']]

cr2PScale = cr3PScale

binning4l = {
    'MassDREtFSR' : [20,0.,800.],
    'EtaDREtFSR' : [16, -5., 5.],
    'PtDREtFSR' : [30, 0., 180.],
    'PhiDREtFSR' : [12, -3.15, 3.15],
    'nJets' : [6, -0.5, 5.5],
    'nvtx' : [40,0.,40.],
    }

vars4l = {v:v for v in binning4l}

xTitle4l = {
    'MassDREtFSR' : 'm_{__PARTICLES__}',
    'EtaDREtFSR' : '\\eta_{__PARTICLES__}',
    'PtDREtFSR' : 'p_{T_{__PARTICLES__}}',
    'PhiDREtFSR' : '\\phi_{__PARTICLES__}',
    'nJets' : '\\text{# Jets}',
    'nvtx' : '\\text{# PVs}',
    }

units = {
    'MassDREtFSR' : 'GeV',
    'PhiDREtFSR' : '',
    'EtaDREtFSR' : '',
    'PtDREtFSR' : 'GeV',
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

    for varName, bins in binning4l.iteritems():
        var = vars4l[varName]
        cr3P1F = plotter.makeHist('3P1F', '3P1F', channel, var, '', 
                                  bins, weights=cr3PScale[channel], 
                                  perUnitWidth=False, nameForLegend='\\text{Z/WZ+X}',
                                  isBackground=True)
        cr2P2F = plotter.makeHist('2P2F', '2P2F', channel, var, '', 
                                  bins, weights=cr2PScale[channel], 
                                  perUnitWidth=False, nameForLegend='\\text{Z/WZ+X}',
                                  isBackground=True)

        cr3P1F -= cr2P2F
        for b in cr3P1F:
            if b.value < 0.:
                b.value = 0.

        cr3P1F.sumw2()

        plotter.fullPlot('4l%s%s'%(varName,chEnding), channel, var, '', 
                         bins, 'mc', 'data', canvasX=1000, logy=False, 
                         xTitle=xTitle4l[varName].replace('__PARTICLES__',particles), 
                         xUnits=units[varName],
                         extraBkgs=[cr3P1F], outFile='%s%s.png'%(varName,chEnding), 
                         mcWeights=mcWeight[channel], drawRatio=False)
binning2l = {
    'MassDREtFSR' : [30, 60., 120.],
    'EtaDREtFSR' : [20, -5., 5.],
    'PtDREtFSR' : [30, 0., 150.],
    'PhiDREtFSR' : [12, -3.15, 3.15],
    }

xTitles2l = {
    'MassDREtFSR' : 'm_{%s}',
    'EtaDREtFSR' : '\\eta_{%s}',
    'PtDREtFSR' : 'p_{T_{%s}}',
    'PhiDREtFSR' : '\\phi_{%s}',
    }

channels2l = {
    'z1' : ['eeee', 'eemm', 'eemm', 'mmmm'],
    'z2' : ['eeee', 'eemm', 'eemm', 'mmmm'],
    'z1e' : ['eeee', 'eemm'],
    'z2e' : ['eeee', 'eemm'],
    'z1m' : ['eemm', 'mmmm'],
    'z2m' : ['eemm', 'mmmm'],
    }

selections2l = {
    'z1' : ['', 'abs(e1_e2_MassDREtFSR-%f) < abs(m1_m2_MassDREtFSR-%f)'%(Z_MASS, Z_MASS), 
            'abs(m1_m2_MassDREtFSR-%f) < abs(e1_e2_MassDREtFSR-%f)'%(Z_MASS, Z_MASS), ''],
    'z2' : ['', 'abs(e1_e2_MassDREtFSR-%f) > abs(m1_m2_MassDREtFSR-%f)'%(Z_MASS, Z_MASS), 
            'abs(m1_m2_MassDREtFSR-%f) > abs(e1_e2_MassDREtFSR-%f)'%(Z_MASS, Z_MASS), ''],
    'z1e' : ['', 'abs(e1_e2_MassDREtFSR-%f) < abs(m1_m2_MassDREtFSR-%f)'%(Z_MASS, Z_MASS)],
    'z2e' : ['', 'abs(e1_e2_MassDREtFSR-%f) > abs(m1_m2_MassDREtFSR-%f)'%(Z_MASS, Z_MASS)],
    'z1m' : ['abs(e1_e2_MassDREtFSR-%f) > abs(m1_m2_MassDREtFSR-%f)'%(Z_MASS, Z_MASS), ''],
    'z2m' : ['abs(e1_e2_MassDREtFSR-%f) < abs(m1_m2_MassDREtFSR-%f)'%(Z_MASS, Z_MASS), ''],
    }

varTemplates2l = {
    'z1' : ['e1_e2_%s', 'e1_e2_%s', 'm1_m2_%s', 'm1_m2_%s'],
    'z2' : ['e3_e4_%s', 'm1_m2_%s', 'e1_e2_%s', 'm3_m4_%s'],
    'z1e' : ['e1_e2_%s' for i in range(2)],
    'z2e' : ['e3_e4_%s', 'e1_e2_%s'],
    'z1m' : ['m1_m2_%s' for i in range(2)],
    'z2m' : [ 'm1_m2_%s', 'm3_m4_%s'],
    }

objects2l = {
    'z1' : 'Z_{1}',
    'z2' : 'Z_{2}',
    'z1e' : 'Z_{1} \\left(ee \\right)',
    'z2e' : 'Z_{2} \\left(ee \\right)',
    'z1m' : 'Z_{1} \\left(\\mu\\mu \\right)',
    'z2m' : 'Z_{2} \\left(\\mu\\mu \\right)',
    }

for z, channels in channels2l.iteritems():
    
    for var, bins in binning2l.iteritems():
        variables = [v%var for v in varTemplates2l[z]]

        cr3P1F = plotter.makeHist('3P1F', '3P1F', channels, variables,
                                  selections2l[z], bins, 
                                  weights=[cr3PScale[c] for c in channels], 
                                  perUnitWidth=False, 
                                  nameForLegend='\\text{Z/WZ+X}',
                                  isBackground=True)
        cr2P2F = plotter.makeHist('2P2F', '2P2F', channels, variables,
                                  selections2l[z], bins,
                                  weights=[cr2PScale[c] for c in channels], 
                                  perUnitWidth=False, 
                                  nameForLegend='\\text{Z/WZ+X}',
                                  isBackground=True)
        cr3P1F -= cr2P2F
        for b in cr3P1F:
            if b.value < 0.:
                b.value = 0.

        plotter.fullPlot('%s%s'%(z, var), channels, variables, 
                         selections2l[z], 
                         bins, 'mc', 'data', canvasX=1000, logy=False, 
                         xTitle=xTitles2l[var]%objects2l[z],
                         xUnits=units[var],
                         extraBkgs=[cr3P1F], outFile='%s%s.png'%(z,var), 
                         mcWeights=[mcWeight[c] for c in channels], 
                         drawRatio=False)


binning1l = {
    'Phi' : [12, -3.15, 3.15],
    'Eta' : [10, -2.5, 2.5],
    'Pt' : [30, 0., 150.],
    'Iso' : [11, 0., 0.55],
    'PVDXY' : [10, -.5, .5],
    'PVDZ' : [10, -1., 1.],
    }

vars1l = {
    'Pt' : {lep:'Pt' for lep in ['e', 'm']},
    'Eta' : {lep:'Eta' for lep in ['e', 'm']},
    'Phi' : {lep:'Phi' for lep in ['e', 'm']},
    'PVDXY' : {lep:'PVDXY' for lep in ['e', 'm']},
    'PVDZ' : {lep:'PVDZ' for lep in ['e', 'm']},
    'Iso' : {'e' : 'RelPFIsoRhoDREtFSR', 'm' : 'RelPFIsoDBDREtFSR'},
    }

xTitles1l = {
    'Phi' : '\\phi_{%s}',
    'Eta' : '\\eta_{%s}',
    'Pt' : 'p_{T_{%s}}',
    'PVDXY' : '\\Delta_{xy} \\text{(%s,PV)}',
    'PVDZ' : '\\Delta_{z} \\text{(%s,PV)}',
    'Iso' : '\\text{Rel. PF Iso. (PU corrected)} (%s)',
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

for lep, channels in channels1l.iteritems():
    
    for var, bins in binning1l.iteritems():
        variables = [v%vars1l[var][lep] for v in varTemplates1l[lep]]

        cr3P1F = plotter.makeHist('3P1F', '3P1F', channels, variables, '', bins,
                                  weights=[cr3PScale[c] for c in channels], 
                                  perUnitWidth=False, 
                                  nameForLegend='\\text{Z/WZ+X}',
                                  isBackground=True)
        cr2P2F = plotter.makeHist('2P2F', '2P2F', channels, variables, '', bins,
                                  weights=[cr2PScale[c] for c in channels], 
                                  perUnitWidth=False, 
                                  nameForLegend='\\text{Z/WZ+X}',
                                  isBackground=True)
        cr3P1F -= cr2P2F
        for b in cr3P1F:
            if b.value < 0.:
                b.value = 0.

        plotter.fullPlot('%s%s'%(lep, var), channels, variables, '',
                         bins, 'mc', 'data', canvasX=1000, logy=False, 
                         xTitle=xTitles1l[var]%objName1l[lep],
                         xUnits=units[var],
                         extraBkgs=[cr3P1F], outFile='%s%s.png'%(lep,var), 
                         mcWeights=[mcWeight[c] for c in channels], 
                         drawRatio=False)





