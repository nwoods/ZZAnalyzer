# include logging stuff first so other imports don't babble at us
import logging
from rootpy import log as rlog; rlog = rlog["/testCRPlotsDataDrivenBkg"]
# don't show most silly ROOT messages
logging.basicConfig(level=logging.WARNING)
rlog["/ROOT.TH1F.Add"].setLevel(rlog.ERROR)
rlog["/rootpy.compiled"].setLevel(rlog.WARNING)


from NtuplePlotter import NtuplePlotter
from ZZHelpers import Z_MASS
from WeightStringMaker import WeightStringMaker, TPFunctionManager

from rootpy.io import root_open

from datetime import date
import os

outdir = '/afs/cern.ch/user/n/nawoods/www/ZZPlots/CR_MCData2015silver_{0}'.format(date.today().strftime('%d%b%Y').lower())
link = '/afs/cern.ch/user/n/nawoods/www/ZZPlots/CR_MCData_latest'

tpVersionHash = 'v2.0-13-g36fc26c' #'v2.0-11-gafcf7cc' #'v1.1-4-ga295b14-extended'

TP = TPFunctionManager(tpVersionHash)

z1eMCWeight = '*'.join(TP.getTPString('e%d'%ne, 'TightID')+'*'+TP.getTPString('e%d'%ne, 'IsoTight') for ne in range(1,3))
z2eMCWeight = '*'.join(TP.getTPString('e%d'%ne, 'TightID')+'*'+TP.getTPString('e%d'%ne, 'IsoTight') for ne in range(3,5))
z1mMCWeight = '*'.join(TP.getTPString('m%d'%nm, 'TightID')+'*'+TP.getTPString('m%d'%nm, 'IsoTight') for nm in range(1,3))
z2mMCWeight = '*'.join(TP.getTPString('m%d'%nm, 'TightID')+'*'+TP.getTPString('m%d'%nm, 'IsoTight') for nm in range(3,5))

wts = WeightStringMaker('puWeight')

fPUScale = root_open(os.environ['zza']+'/data/pileupReweighting/PUScaleFactors_29Feb2016.root')
puScaleFactorHist = fPUScale.Get("puScaleFactor")
puScaleFactorStr = wts.makeWeightStringFromHist(puScaleFactorHist, 'nTruePU')

mcWeight = {
    'eeee' : '(GenWeight*{0}*{1}*{2})'.format(puScaleFactorStr, z1eMCWeight, z2eMCWeight),
    'eemm' : '(GenWeight*{0}*{1}*{2})'.format(puScaleFactorStr, z1eMCWeight, z1mMCWeight),
    'mmmm' : '(GenWeight*{0}*{1}*{2})'.format(puScaleFactorStr, z1mMCWeight, z2mMCWeight),
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
    'eeee' : ['(e1HZZTightID + e2HZZTightID + e1HZZIsoPass + e2HZZIsoPass) < (e3HZZTightID + e4HZZTightID + e3HZZIsoPass + e4HZZIsoPass)', 
              '(e1HZZTightID + e2HZZTightID + e1HZZIsoPass + e2HZZIsoPass) > (e3HZZTightID + e4HZZTightID + e3HZZIsoPass + e4HZZIsoPass)'],
    'eemm' : ['(e1HZZTightID + e2HZZTightID + e1HZZIsoPass + e2HZZIsoPass) < (m1HZZTightID + m2HZZTightID + m1HZZIsoPass + m2HZZIsoPass)',
              '(e1HZZTightID + e2HZZTightID + e1HZZIsoPass + e2HZZIsoPass) > (m1HZZTightID + m2HZZTightID + m1HZZIsoPass + m2HZZIsoPass)'], 
    'mmmm' : ['(m1HZZTightID + m2HZZTightID + m1HZZIsoPass + m2HZZIsoPass) < (m3HZZTightID + m4HZZTightID + m3HZZIsoPass + m4HZZIsoPass)',
              '(m1HZZTightID + m2HZZTightID + m1HZZIsoPass + m2HZZIsoPass) > (m3HZZTightID + m4HZZTightID + m3HZZIsoPass + m4HZZIsoPass)'],
    }
z2dRSels['zz'] = z2dRSels['eeee'] + z2dRSels['eemm'] + z2dRSels['mmmm'] 
z2dRMCWeights = {ch : [mcWeight[ch], mcWeight[ch]] for ch in ['eeee','eemm','mmmm']}
z2dRMCWeights['zz'] = z2dRMCWeights['eeee'] + z2dRMCWeights['eemm'] + z2dRMCWeights['mmmm'] 


for cr in crs:

    plotters[cr] = NtuplePlotter('zz', os.path.join(outdir, 'CR_%s'%cr),
                                 {'mc':'/data/nawoods/ntuples/zzNtuples_mc_26jan2016_0/results_full_%s/*.root'%cr}, 
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
