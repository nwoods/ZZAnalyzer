# include logging stuff first so other imports don't babble at us
import logging
from rootpy import log as rlog; rlog = rlog["/firstICHEPPlot"]
# don't show most silly ROOT messages
logging.basicConfig(level=logging.WARNING)
rlog["/ROOT.TH1F.Add"].setLevel(rlog.ERROR)
rlog["/rootpy.compiled"].setLevel(rlog.WARNING)


from NtuplePlotter import NtuplePlotter
from ZZAnalyzer.utils.helpers import Z_MASS
from ZZAnalyzer.utils import WeightStringMaker, TPFunctionManager

from rootpy.io import root_open

from datetime import date
import os

outdir = '/afs/cern.ch/user/n/nawoods/www/ZZPlots/firstICHEPPlots'

# tpVersionHash = 'v2.0-13-g36fc26c' #'v2.0-11-gafcf7cc' #'v1.1-4-ga295b14-extended'
# 
# TP = TPFunctionManager(tpVersionHash)

z1eMCWeight = 'e1EffScaleFactor * e2EffScaleFactor'
z2eMCWeight = 'e3EffScaleFactor * e4EffScaleFactor'
z1mMCWeight = 'm1EffScaleFactor * m1TrkRecoEffScaleFactor * m2EffScaleFactor * m2TrkRecoEffScaleFactor'
z2mMCWeight = 'm3EffScaleFactor * m3TrkRecoEffScaleFactor * m4EffScaleFactor * m4TrkRecoEffScaleFactor'

wts = WeightStringMaker('puWeight')

fPUScale = root_open(os.path.join(os.environ['zza'],'ZZAnalyzer','data/pileupReweighting/PUScaleFactors_29Feb2016.root'))
puScaleFactorHist = fPUScale.Get("puScaleFactor")
puScaleFactorStr = wts.makeWeightStringFromHist(puScaleFactorHist, 'nTruePU')

mcWeight = {
    'eeee' : '(GenWeight*{0}*{1})'.format(z1eMCWeight, z2eMCWeight),
    'eemm' : '(GenWeight*{0}*{1})'.format(z1eMCWeight, z1mMCWeight),
    'mmmm' : '(GenWeight*{0}*{1})'.format(z1mMCWeight, z2mMCWeight),
}

mcWeight['zz'] = [mcWeight['eeee'], mcWeight['eemm'], mcWeight['mmmm']]


plotters = {}
crs = ['3P1F', '2P2F']

z2dRChan = {
    'eeee': ['eeee','eeee'],
    'eemm': ['eemm','eemm'],
    'mmmm': ['mmmm','mmmm'],
    }
z2dRChan['zz'] = z2dRChan['eeee'] + z2dRChan['eemm'] + z2dRChan['mmmm'] 
z2dRVars = {
    'eeee' : [s%"DR" for s in ['e1_e2_%s', 'e3_e4_%s']],
    'eemm' : [s%"DR" for s in ['e1_e2_%s', 'm1_m2_%s']], 
    'mmmm' : [s%"DR" for s in ['m1_m2_%s', 'm3_m4_%s']]
    }
z2dRVars['zz'] = z2dRVars['eeee'] + z2dRVars['eemm'] + z2dRVars['mmmm'] 
z2dRSels = {
    'eeee' : ['(e1ZZTightID + e2ZZTightID + e1ZZIsoPass + e2ZZIsoPass) < (e3ZZTightID + e4ZZTightID + e3ZZIsoPass + e4ZZIsoPass)', 
              '(e1ZZTightID + e2ZZTightID + e1ZZIsoPass + e2ZZIsoPass) > (e3ZZTightID + e4ZZTightID + e3ZZIsoPass + e4ZZIsoPass)'],
    'eemm' : ['(e1ZZTightID + e2ZZTightID + e1ZZIsoPass + e2ZZIsoPass) < (m1ZZTightID + m2ZZTightID + m1ZZIsoPass + m2ZZIsoPass)',
              '(e1ZZTightID + e2ZZTightID + e1ZZIsoPass + e2ZZIsoPass) > (m1ZZTightID + m2ZZTightID + m1ZZIsoPass + m2ZZIsoPass)'], 
    'mmmm' : ['(m1ZZTightID + m2ZZTightID + m1ZZIsoPass + m2ZZIsoPass) < (m3ZZTightID + m4ZZTightID + m3ZZIsoPass + m4ZZIsoPass)',
              '(m1ZZTightID + m2ZZTightID + m1ZZIsoPass + m2ZZIsoPass) > (m3ZZTightID + m4ZZTightID + m3ZZIsoPass + m4ZZIsoPass)'],
    }
z2dRSels['zz'] = z2dRSels['eeee'] + z2dRSels['eemm'] + z2dRSels['mmmm'] 
z2dRMCWeights = {ch : [mcWeight[ch], mcWeight[ch]] for ch in ['eeee','eemm','mmmm']}
z2dRMCWeights['zz'] = z2dRMCWeights['eeee'] + z2dRMCWeights['eemm'] + z2dRMCWeights['mmmm'] 


for cr in crs:

    plotters[cr] = NtuplePlotter('zz', os.path.join(outdir, 'CR_%s'%cr),
                                 {'mc':'/data/nawoods/ntuples/uwvvNtuples_mc_26jan2016_0/results_full_%s/*.root'%cr}, 
                                 {'data':'/data/nawoods/ntuples/zzNtuples_data_2015silver_26jan2016_0/results_full_%s/data*.root'%cr}, 
                                 2619.,)

    # print "%s:"%cr
    # plotters[cr].printPassingEvents('data')
    # print ""

    for channel in ['zz', 'eeee', 'eemm', 'mmmm']:

        chdir = "_%s"%channel
        if channel == 'zz':
            chdir = ''

        plotters[cr].fullPlot('4lMassFSR_%s'%channel, channel, 'MassDREtFSR', '', [20, 0., 800], 
                              'mc', 'data', canvasX=1000, logy=False, xTitle="m_{4\\ell}", 
                              outFile='m4l%s.png'%chdir, mcWeights=mcWeight[channel],
                              drawRatio=False,
                              widthInYTitle=True,
                              )
        
        if channel == 'eemm':
            plotters[cr].fullPlot('4lMassFSR_%s_eFake'%channel, channel, 
                                  'MassDREtFSR', z2dRSels['eemm'][0], 
                                  [20, 0., 800], 'mc', 'data', canvasX=1000, 
                                  logy=False, xTitle="m_{2\\mu 2\\text{e}}", 
                                  outFile='m4l%s_eFake.png'%chdir, 
                                  mcWeights=mcWeight[channel],
                                  drawRatio=False, widthInYTitle=True,
                                  )
            plotters[cr].fullPlot('4lMassFSR_%s_mFake'%channel, channel, 
                                  'MassDREtFSR', z2dRSels['eemm'][1], 
                                  [20, 0., 800], 'mc', 'data', canvasX=1000, 
                                  logy=False, xTitle="m_{2\\text{e} 2\\mu}", 
                                  outFile='m4l%s_mFake.png'%chdir, 
                                  mcWeights=mcWeight[channel],
                                  drawRatio=False, widthInYTitle=True,
                                  )


        plotters[cr].fullPlot('z2dR_%s'%channel, z2dRChan[channel], z2dRVars[channel], 
                              z2dRSels[channel], [20, 0., 2.], 
                              'mc', 'data', canvasX=1000, logy=False, 
                              xTitle="\\Delta R (\\ell^{\\text{loose}}_1, \\ell^{\\text{loose}}_2 )", 
                              outFile='z2dR%s.png'%chdir, mcWeights=z2dRMCWeights[channel],
                              drawRatio=False,
                              widthInYTitle=True,
                              )
        # plotters[cr].fullPlot('nJets_%s'%channel, channel, 'nJets', '', [8, -0.5, 7.5], 'mc', 'data',
        #                       canvasX=1000, logy=False, xTitle="\\text{#Jets}", xUnits="",
        #                       outFile='nJets%s.png'%chdir, mcWeights=mcWeight[channel],
        #                       drawRatio=False,
        #                       # legParams={'leftmargin':0.6,'rightmargin':0.03,'textsize':0.023,
        #                       #            'entryheight':0.023,'entrysep':0.006} 
        #                       )

try:
    os.unlink(link)
except:
    pass

os.symlink(outdir, link)
