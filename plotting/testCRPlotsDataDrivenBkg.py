# include logging stuff first so other imports don't babble at us
import logging
from rootpy import log as rlog; rlog = rlog["/testCRPlotsDataDrivenBkg"]
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
eIDLooseTPHist = makeWeightHistFromJSONDict(eTagProbeJSON['passingZZLoose'], 'ratio', 'pt', 'abseta')
eIsoFromLooseTPHist = makeWeightHistFromJSONDict(eTagProbeJSON['passingZZIso_passingZZLoose'], 'ratio', 'pt', 'abseta')
eIDLooseTPStrTemp = makeWeightStringFromHist(eIDLooseTPHist, '{0}Pt', 'abs({0}Eta)')
eIsoFromLooseTPStrTemp = makeWeightStringFromHist(eIsoFromLooseTPHist, '{0}Pt', 'abs({0}Eta)')

mTagProbeJSON = dictFromJSONFile(os.environ['zza']+'/data/tagAndProbe/muonTagProbe_%s.json'%tpVersionHash)
mIDTightTPHist = makeWeightHistFromJSONDict(mTagProbeJSON['passingIDZZTight'], 'ratio', 'pt', 'abseta')
mIsoFromTightTPHist = makeWeightHistFromJSONDict(mTagProbeJSON['passingIsoZZ_passingIDZZTight'], 'ratio', 'pt', 'abseta')
mIDTightTPStrTemp = makeWeightStringFromHist(mIDTightTPHist, '{0}Pt', 'abs({0}Eta)')
mIsoFromTightTPStrTemp = makeWeightStringFromHist(mIsoFromTightTPHist, '{0}Pt', 'abs({0}Eta)')
mIDLooseTPHist = makeWeightHistFromJSONDict(mTagProbeJSON['passingIDZZLoose'], 'ratio', 'pt', 'abseta')
mIsoFromLooseTPHist = makeWeightHistFromJSONDict(mTagProbeJSON['passingIsoZZ_passingIDZZLoose'], 'ratio', 'pt', 'abseta')
mIDLooseTPStrTemp = makeWeightStringFromHist(mIDLooseTPHist, '{0}Pt', 'abs({0}Eta)')
mIsoFromLooseTPStrTemp = makeWeightStringFromHist(mIsoFromLooseTPHist, '{0}Pt', 'abs({0}Eta)')

singleLepTPStr = '({0}HZZTightID > 0.5 ? %s * ({0}HZZIsoPass ? %s : 1.) : %s * ({0}HZZIsoPass ? %s : 1.))'
singleETPStrTemp = singleLepTPStr%(eIDTightTPStrTemp, eIsoFromTightTPStrTemp, eIDLooseTPStrTemp, eIsoFromLooseTPStrTemp)
singleMuTPStrTemp = singleLepTPStr%(mIDTightTPStrTemp, mIsoFromTightTPStrTemp, mIDLooseTPStrTemp, mIsoFromLooseTPStrTemp)

z1eMCWeight = '*'.join(singleETPStrTemp.format('e%d'%ne) for ne in range(1,3))
z2eMCWeight = '*'.join(singleETPStrTemp.format('e%d'%ne) for ne in range(3,5))
z1mMCWeight = '*'.join(singleMuTPStrTemp.format('m%d'%ne) for ne in range(1,3))
z2mMCWeight = '*'.join(singleMuTPStrTemp.format('m%d'%ne) for ne in range(3,5))
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


plotters = {}
crs = ['3P1F', '2P2F']

for cr in crs:

    plotters[cr] = NtuplePlotter('zz', './plots/CR_MCData2015D_3nov2015/CR_%s'%cr,
                                 {'mc':'/data/nawoods/ntuples/zzNtuples_mc_29oct2015_0/results_%s/*.root'%cr}, 
                                 {'data':'/data/nawoods/ntuples/zzNtuples_data_2015d_26oct2015_0/results_%s/data*.root'%cr}, 
                                 1263.89)

    print "%s:"%cr
    plotters[cr].printPassingEvents('data')
    print ""

    for channel in ['zz', 'eeee', 'eemm', 'mmmm']:

        chdir = "_%s"%channel
        if channel == 'zz':
            chdir = ''

        plotters[cr].fullPlot('4lMassFSR_%s'%channel, channel, 'MassDREtFSR', '', [20, 0., 800], 
                              'mc', 'data', canvasX=1000, logy=False, xTitle="m_{4\\ell}", 
                              outFile='m4l%s.png'%chdir, mcWeights=mcWeight[channel],
                              drawRatio=False)
        plotters[cr].fullPlot('nJets_%s'%channel, channel, 'nJets', '', [8, -0.5, 7.5], 'mc', 'data',
                              canvasX=1000, logy=False, xTitle="\\text{#Jets}", xUnits="",
                              outFile='nJets%s.png'%chdir, mcWeights=mcWeight[channel],
                              drawRatio=False
                              # legParams={'leftmargin':0.6,'rightmargin':0.03,'textsize':0.023,
                              #            'entryheight':0.023,'entrysep':0.006} 
                              )

# zPlotChannels = ['eeee', 'eemm', 'eemm', 'mmmm']
# z1PlotVariables = ['e1_e2_MassFSR', 'e1_e2_MassFSR', 
#                    'm1_m2_MassFSR', 'm1_m2_MassFSR']
# z2PlotVariables = ['e3_e4_MassFSR', 'm1_m2_MassFSR', 
#                    'e1_e2_MassFSR', 'm3_m4_MassFSR']
# zPlotSelections = ['', 'abs(e1_e2_MassFSR-%f) < abs(m1_m2_MassFSR-%f)'%(Z_MASS, Z_MASS), 
#                    'abs(m1_m2_MassFSR-%f) < abs(e1_e2_MassFSR-%f)'%(Z_MASS, Z_MASS), '']
# 
# plotter.fullPlot('mZ1_total', zPlotChannels, z1PlotVariables, zPlotSelections, 
#                  30, 60., 120, logy=False, xTitle="m_{Z_{1}}", outFile='mZ1.png', )
# plotter.fullPlot('mZ2_total', zPlotChannels, z2PlotVariables, zPlotSelections, 
#                  30, 60., 120, logy=False, xTitle="m_{Z_{2}}", outFile='mZ2.png', )
