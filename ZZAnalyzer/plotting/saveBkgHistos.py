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


from NtuplePlotter import NtuplePlotter
from ZZAnalyzer.utils import WeightStringMaker, TPFunctionManager, BkgManager

from rootpy.io import root_open
from rootpy.plotting import Hist

import os

# lots of prep things
tpVersionHash = 'v2.0-13-g36fc26c' #'v2.0-11-gafcf7cc' #'v1.1-4-ga295b14-extended'

TP = TPFunctionManager(tpVersionHash)

z1eMCWeight = '*'.join(TP.getTPString('e%d'%ne, 'TightID')+'*'+TP.getTPString('e%d'%ne, 'IsoTight') for ne in range(1,3))
z2eMCWeight = '*'.join(TP.getTPString('e%d'%ne, 'TightID')+'*'+TP.getTPString('e%d'%ne, 'IsoTight') for ne in range(3,5))
z1mMCWeight = '*'.join(TP.getTPString('m%d'%nm, 'TightID')+'*'+TP.getTPString('m%d'%nm, 'IsoTight') for nm in range(1,3))
z2mMCWeight = '*'.join(TP.getTPString('m%d'%nm, 'TightID')+'*'+TP.getTPString('m%d'%nm, 'IsoTight') for nm in range(3,5))

wts = WeightStringMaker('puWeight')

fPUScale = root_open(os.environ['zza']+'/ZZAnalyzer/data/pileupReweighting/PUScaleFactors_29Feb2016.root')
puScaleFactorHist = fPUScale.Get("puScaleFactor")
puScaleFactorStr = wts.makeWeightStringFromHist(puScaleFactorHist, 'nTruePU')

mcWeight = {
    'eeee' : '(GenWeight*{0}*{1}*{2})'.format(puScaleFactorStr, z1eMCWeight, z2eMCWeight),
    'eemm' : '(GenWeight*{0}*{1}*{2})'.format(puScaleFactorStr, z1eMCWeight, z1mMCWeight),
    'mmmm' : '(GenWeight*{0}*{1}*{2})'.format(puScaleFactorStr, z1mMCWeight, z2mMCWeight),
}

mcWeight['zz'] = [mcWeight['eeee'], mcWeight['eemm'], mcWeight['mmmm']]

bkg = BkgManager('01mar2016')

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


cr3PScale_noCor = {
    ch : bkg.fullString3P1F(ch, False) for ch in ['eeee','eemm','mmmm']
}

cr3PScaleMC_noCor = {c:'*'.join([cr3PScale_noCor[c], mcWeight[c]]) for c in cr3PScale_noCor}

cr3PScale_noCor['zz'] = [cr3PScale_noCor[c] for c in ['eeee','eemm','mmmm']]
cr3PScaleMC_noCor['zz'] = [cr3PScaleMC_noCor[c] for c in ['eeee','eemm','mmmm']]

cr2PScale_noCor = {
    ch : bkg.fullString2P2F(ch, False) for ch in ['eeee','eemm','mmmm']
}

cr2PScaleMC_noCor = {c:'*'.join([cr2PScale_noCor[c], mcWeight[c]]) for c in cr2PScale_noCor}

cr2PScale_noCor['zz'] = [cr2PScale_noCor[c] for c in ['eeee','eemm','mmmm']]
cr2PScaleMC_noCor['zz'] = [cr2PScaleMC_noCor[c] for c in ['eeee','eemm','mmmm']]


def joinSelections(*selections):
    return ' && '.join([s for s in selections if bool(s)])


for ana in ['z4l']:#'full']:
    sampleID = ana

    js = 'silver'
    latest = '26jan2016_0'

    plotter = NtuplePlotter('zz', '', 
                            {'mc3P1F':'/data/nawoods/ntuples/zzNtuples_mc_26jan2016_0/results_{0}_3P1F/*.root'.format(sampleID),
                             'mc2P2F':'/data/nawoods/ntuples/zzNtuples_mc_26jan2016_0/results_{0}_2P2F/*.root'.format(sampleID),}, 
                            {'3P1F':'/data/nawoods/ntuples/zzNtuples_data_2015{1}_{2}/results_{0}_3P1F/data*.root'.format(sampleID,
                                                                                                                          js,
                                                                                                                          latest),
                             '2P2F':'/data/nawoods/ntuples/zzNtuples_data_2015{1}_{2}/results_{0}_2P2F/data*.root'.format(sampleID,
                                                                                                                          js,
                                                                                                                          latest),
                             }, 
                            intLumi=2619.)
    
    # samples to subtract off of CRs based on MC
    subtractSamples = []
    for s in plotter.ntuples['mc3P1F']:
        if s[:3] == 'ZZT' or s[:10] == 'GluGluToZZ' and 'tau' not in s:
            subtractSamples.append(s)

    if ana == 'z4l':
        binning4l = {
            'MassDREtFSR' : [5,80.,100.],
            }
    else:
        binning4l = {
            'MassDREtFSR' : [35,10.,710.],
            }
    
    vars4l = {v:v for v in binning4l}
    
    xTitle4l = {
        'Mass' : 'm_{__PARTICLES__}',
        'MassDREtFSR' : 'm_{__PARTICLES__}',
        'EtaDREtFSR' : '\\eta_{__PARTICLES__}',
        'PtDREtFSR' : 'p_{T_{__PARTICLES__}}',
        'PhiDREtFSR' : '\\phi_{__PARTICLES__}',
        'nJets' : '\\text{# Jets}',
        'nvtx' : '\\text{# PVs}',
        }
    
    varName = 'MassDREtFSR'
    var = varName
    bins = binning4l[var]

    with root_open(os.path.join(os.environ["zza"], "ZZAnalyzer", "data", 'uw_reducible_30mar2016.root'), 'recreate') as f:

        init2P2F = {}
        init3P1F = {}
        sigSub2P2F = {}
        sigSub3P1F = {}
        noNeg2P2F = {}
        noNeg3P1F = {}
        redBkg = {}

        init2P2F_noCor = {}
        init3P1F_noCor = {}
        sigSub2P2F_noCor = {}
        sigSub3P1F_noCor = {}
        noNeg2P2F_noCor = {}
        noNeg3P1F_noCor = {}
        redBkg_noCor = {}

        for channel in ['eeee', 'eemm', 'mmmm']:
            
            cr3P1F = plotter.makeHist('3P1F', '3P1F', channel, var, '', 
                                      bins, weights=cr3PScale[channel], 
                                      perUnitWidth=False, nameForLegend='\\text{Z/WZ+X}',
                                      isBackground=True)


            cr2P2F = plotter.makeHist('2P2F', '2P2F', channel, var, '', 
                                      bins, weights=cr2PScale[channel], 
                                      perUnitWidth=False, nameForLegend='\\text{Z/WZ+X}',
                                      isBackground=True)
        

            cr3P1F.sumw2()
            cr2P2F.sumw2()

            init2P2F[channel] = Hist(cr2P2F, name='CR2P2F_{}'.format(channel))
            init2P2F[channel].Write()
            init3P1F[channel] = Hist(cr3P1F, name='CR3P1F_{}'.format(channel))
            init3P1F[channel].Write()


            cr3P1F_noCor = plotter.makeHist('3P1F', '3P1F', channel, var, '', 
                                            bins, weights=cr3PScale_noCor[channel], 
                                            perUnitWidth=False, nameForLegend='\\text{Z/WZ+X}',
                                            isBackground=True)


            cr2P2F_noCor = plotter.makeHist('2P2F', '2P2F', channel, var, '', 
                                            bins, weights=cr2PScale_noCor[channel], 
                                            perUnitWidth=False, nameForLegend='\\text{Z/WZ+X}',
                                            isBackground=True)
        

            cr3P1F_noCor.sumw2()
            cr2P2F_noCor.sumw2()

            init2P2F_noCor[channel] = Hist(cr2P2F_noCor, name='CR2P2F_noCor_{}'.format(channel))
            init2P2F_noCor[channel].Write()
            init3P1F_noCor[channel] = Hist(cr3P1F, name='CR3P1F_noCor_{}'.format(channel))
            init3P1F_noCor[channel].Write()

            for ss in subtractSamples:
                sub3P = plotter.makeHist("mc3P1F", ss, channel,
                                         var, '', bins,
                                         weights=cr3PScaleMC[channel],
                                         perUnitWidth=False)
                cr3P1F -= sub3P
                sub2P = plotter.makeHist("mc2P2F", ss, channel,
                                         var, '', bins,
                                         weights=cr2PScaleMC[channel],
                                         perUnitWidth=False)
                cr2P2F -= sub2P
        
                cr3P1F.sumw2()
                cr2P2F.sumw2()

            sigSub2P2F[channel] = Hist(cr2P2F, name='CR2P2F_signalSubtracted_{}'.format(channel))
            sigSub2P2F[channel].Write()
            sigSub3P1F[channel] = Hist(cr3P1F, name='CR3P1F_signalSubtracted_{}'.format(channel))
            sigSub3P1F[channel].Write()
        
            for ss in subtractSamples:
                sub3P_noCor = plotter.makeHist("mc3P1F", ss, channel,
                                               var, '', bins,
                                               weights=cr3PScaleMC_noCor[channel],
                                               perUnitWidth=False)
                cr3P1F_noCor -= sub3P_noCor
                sub2P_noCor = plotter.makeHist("mc2P2F", ss, channel,
                                               var, '', bins,
                                               weights=cr2PScaleMC_noCor[channel],
                                               perUnitWidth=False)
                cr2P2F_noCor -= sub2P_noCor
        
                cr3P1F_noCor.sumw2()
                cr2P2F_noCor.sumw2()

            sigSub2P2F_noCor[channel] = Hist(cr2P2F_noCor, name='CR2P2F_noCor_signalSubtracted_{}'.format(channel))
            sigSub2P2F_noCor[channel].Write()
            sigSub3P1F_noCor[channel] = Hist(cr3P1F_noCor, name='CR3P1F_noCor_signalSubtracted_{}'.format(channel))
            sigSub3P1F_noCor[channel].Write()
        
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
                
            noNeg2P2F[channel] = Hist(cr2P2F, name='CR2P2F_signalSubtracted_noNegatives_{}'.format(channel))
            noNeg2P2F[channel].Write()
            noNeg3P1F[channel] = Hist(cr3P1F, name='CR3P1F_signalSubtracted_noNegatives_{}'.format(channel))
            noNeg3P1F[channel].Write()
        
            for b3P, b2P in zip(cr3P1F_noCor, cr2P2F_noCor):
                if b3P.value <= 0 or b2P.value > b3P.value:
                    b3P.value = 0.
                    b3P.error = 0.
                    b2P.value = 0.
                    b2P.error = 0.
                if b2P.value < 0.:
                    b2P.value = 0.
            
            cr3P1F_noCor.sumw2()
            cr2P2F_noCor.sumw2()
                
            noNeg2P2F_noCor[channel] = Hist(cr2P2F_noCor, name='CR2P2F_noCor_signalSubtracted_noNegatives_{}'.format(channel))
            noNeg2P2F_noCor[channel].Write()
            noNeg3P1F_noCor[channel] = Hist(cr3P1F_noCor, name='CR3P1F_noCor_signalSubtracted_noNegatives_{}'.format(channel))
            noNeg3P1F_noCor[channel].Write()
        
            cr3P1F -= cr2P2F
        
            cr3P1F.sumw2()
    
            redBkg[channel] = Hist(cr3P1F, name='ReducibleBkg_{}'.format(channel))
            redBkg[channel].Write()


            cr3P1F_noCor -= cr2P2F_noCor
        
            cr3P1F_noCor.sumw2()
    
            redBkg_noCor[channel] = Hist(cr3P1F_noCor, name='ReducibleBkg_noCor_{}'.format(channel))
            redBkg_noCor[channel].Write()

