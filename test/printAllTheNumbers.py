'''

Print lots of numbers related the the ZZ4l analysis.

This is a goddamn mess; I'll clean it up later.

'''


# include logging stuff first so other imports don't babble at us
import logging
from rootpy import log as rlog; rlog = rlog["/printAllTheNumbers"]
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
from math import sqrt

plotter = NtuplePlotter('zz', './plots/counting_2nov2015', 
                        {'mc':'/data/nawoods/ntuples/zzNtuples_mc_29oct2015_0/results/ZZTo*.root,/data/nawoods/ntuples/zzNtuples_mc_29oct2015_0/results/GluGluToZZTo4[em]*.root,/data/nawoods/ntuples/zzNtuples_mc_29oct2015_0/results/GluGluToZZTo2e2m*.root,/data/nawoods/ntuples/zzNtuples_mc_29oct2015_0/results/*HToZZ*.root'}, 
                        {'data':'/data/nawoods/ntuples/zzNtuples_data_2015d_26oct2015_0/results/data*.root',
                         '3P1F':'/data/nawoods/ntuples/zzNtuples_data_2015d_26oct2015_0/results_3P1F/data*.root',
                         '2P2F':'/data/nawoods/ntuples/zzNtuples_data_2015d_26oct2015_0/results_2P2F/data*.root',}, 
                        intLumi=1263.89)

plotter.printPassingEvents('data')

print ""
print "3P1F CR (data):"
print '    eeee: %d'%plotter.ntuples['3P1F']['3P1F']['eeee'].GetEntries()
print '    eemm: %d'%plotter.ntuples['3P1F']['3P1F']['eemm'].GetEntries()
print '    mmmm: %d'%plotter.ntuples['3P1F']['3P1F']['mmmm'].GetEntries()

print ""
print "2P2F CR (data):"
print '    eeee: %d'%plotter.ntuples['2P2F']['2P2F']['eeee'].GetEntries()
print '    eemm: %d'%plotter.ntuples['2P2F']['2P2F']['eemm'].GetEntries()
print '    mmmm: %d'%plotter.ntuples['2P2F']['2P2F']['mmmm'].GetEntries()
print ''

tpVersionHash = 'v1.1-1-g4cbf52a_v2'

fFake = root_open(os.environ['zza']+'/data/leptonFakeRate/fakeRate_26oct2015_0.root')
eFakeRateHist = fFake.Get('e_FakeRate').clone()
mFakeRateHist = fFake.Get('m_FakeRate').clone()

eFakeRateStrTemp = makeWeightStringFromHist(eFakeRateHist, '{0}Pt', '{0}Eta')
mFakeRateStrTemp = makeWeightStringFromHist(mFakeRateHist, '{0}Pt', '{0}Eta')

scales=['', 'down', 'up']

eTagProbeJSON = dictFromJSONFile(os.environ['zza']+'/data/tagAndProbe/electronTagProbe_%s.json'%tpVersionHash)
eIDTightTPHist = {s:makeWeightHistFromJSONDict(eTagProbeJSON['passingZZTight'], 'ratio', 'pt', 'abseta', scale=s) for s in scales}
eIsoFromTightTPHist = {s:makeWeightHistFromJSONDict(eTagProbeJSON['passingZZIso_passingZZTight'], 'ratio', 'pt', 'abseta', scale=s) for s in scales}

eIDTightTPStrTemp = {s:makeWeightStringFromHist(h, '{0}Pt', 'abs({0}Eta)') for s,h in eIDTightTPHist.iteritems()}
eIsoFromTightTPStrTemp = {s:makeWeightStringFromHist(h, '{0}Pt', 'abs({0}Eta)') for s,h in eIsoFromTightTPHist.iteritems()}

mTagProbeJSON = dictFromJSONFile(os.environ['zza']+'/data/tagAndProbe/muonTagProbe_%s.json'%tpVersionHash)
mIDTightTPHist = {s:makeWeightHistFromJSONDict(mTagProbeJSON['passingIDZZTight'], 'ratio', 'pt', 'abseta', scale=s) for s in scales}
mIsoFromTightTPHist = {s:makeWeightHistFromJSONDict(mTagProbeJSON['passingIsoZZ_passingIDZZTight'], 'ratio', 'pt', 'abseta', scale=s) for s in scales}

mIDTightTPStrTemp = {s:makeWeightStringFromHist(h, '{0}Pt', 'abs({0}Eta)') for s,h in mIDTightTPHist.iteritems()}
mIsoFromTightTPStrTemp = {s:makeWeightStringFromHist(h, '{0}Pt', 'abs({0}Eta)') for s,h in mIsoFromTightTPHist.iteritems()}

fPUScale = root_open(os.environ['zza']+'/data/pileupReweighting/PUScaleFactors_28Oct2015.root')
puScaleFactorHist = {
    '' : fPUScale.Get("puScaleFactor"),
    'up' : fPUScale.Get("puScaleFactor_ScaleUp"),
    'down' : fPUScale.Get("puScaleFactor_ScaleDown"),
}
puScaleFactorStr = {s:makeWeightStringFromHist(h, 'nTruePU') for s,h in puScaleFactorHist.iteritems()}

cr3PScale = {
    'eeee' : '*'.join('(e{0}HZZTightID+e{0}HZZIsoPass < 1.5 ? {1} : 1.)'.format(ne, eFakeRateStrTemp.format('e%d'%ne)) for ne in range(3,5)),
    'eemm' : '*'.join('(e{0}HZZTightID+e{0}HZZIsoPass < 1.5 ? {1} : 1.)*(m{0}HZZTightID+m{0}HZZIsoPass < 1.5 ? {2} : 1.)'.format(ne, eFakeRateStrTemp.format('e%d'%ne), mFakeRateStrTemp.format('m%d'%ne)) for ne in range(1,3)),
    'mmmm' : '*'.join('(m{0}HZZTightID+m{0}HZZIsoPass < 1.5 ? {1} : 1.)'.format(nm, mFakeRateStrTemp.format('m%d'%nm)) for nm in range(3,5)),
}
cr3PScale['zz'] = [cr3PScale[c] for c in ['eeee','eemm','mmmm']]

cr2PScale = {
    'eeee' : '*'.join(eFakeRateStrTemp.format('e%d'%ne) for ne in range(3,5)),
    'eemm' : cr3PScale['eemm'],
    'mmmm' : '*'.join(mFakeRateStrTemp.format('m%d'%nm) for nm in range(3,5)),
}
cr2PScale['zz'] = [cr2PScale[c] for c in ['eeee','eemm','mmmm']]


for scaleSet in [['', '', ''], # [id, iso, PU]
                 ['up', '', ''], ['down', '', ''],
                 ['', 'up', ''], ['', 'down', ''],
                 ['', '', 'up'], ['', '', 'down']]:

    z1eMCWeight = '*'.join(eIDTightTPStrTemp[scaleSet[0]].format('e%d'%ne)+'*'+eIsoFromTightTPStrTemp[scaleSet[1]].format('e%d'%ne) for ne in range(1,3))
    z2eMCWeight = '*'.join(eIDTightTPStrTemp[scaleSet[0]].format('e%d'%ne)+'*'+eIsoFromTightTPStrTemp[scaleSet[1]].format('e%d'%ne) for ne in range(3,5))
    z1mMCWeight = '*'.join(mIDTightTPStrTemp[scaleSet[0]].format('m%d'%nm)+'*'+mIsoFromTightTPStrTemp[scaleSet[1]].format('m%d'%nm) for nm in range(1,3))
    z2mMCWeight = '*'.join(mIDTightTPStrTemp[scaleSet[0]].format('m%d'%nm)+'*'+mIsoFromTightTPStrTemp[scaleSet[1]].format('m%d'%nm) for nm in range(3,5))
    #z1emMCWeight = '(abs(e1_e2_MassFSR-{0}) < abs(m1_m2_MassFSR-{0}) ? {1} : {2})'.format(Z_MASS, z1eMCWeight, z1mMCWeight)
    #z2emMCWeight = '(abs(e1_e2_MassFSR-{0}) < abs(m1_m2_MassFSR-{0}) ? {1} : {2})'.format(Z_MASS, z1mMCWeight, z1eMCWeight)
    
    mcWeight = {
        'eeee' : '(GenWeight*{0}*{1}*{2})'.format(puScaleFactorStr[scaleSet[2]], z1eMCWeight, z2eMCWeight),
        'eemm' : '(GenWeight*{0}*{1}*{2})'.format(puScaleFactorStr[scaleSet[2]], z1eMCWeight, z1mMCWeight),
        'mmmm' : '(GenWeight*{0}*{1}*{2})'.format(puScaleFactorStr[scaleSet[2]], z1mMCWeight, z2mMCWeight),
    }
                 
    mcWeight['zz'] = [mcWeight['eeee'], mcWeight['eemm'], mcWeight['mmmm']]

    print ''
    if scaleSet[0]:
        print "ID efficiency scale %s:"%scaleSet[0].upper()
    elif scaleSet[1]:
        print "Iso efficiency scale %s:"%scaleSet[1].upper()
    elif scaleSet[2]:
        print "PU scale %s:"%scaleSet[2].upper()
    else:
        print "MEAN VALUE:"
                 

    bins=[1,0.,2.]
    for channel in ['zz', 'eeee', 'eemm', 'mmmm']:

        cr3P1F = plotter.makeHist('3P1F', '3P1F', channel, '1.', '', 
                                  bins, weights=cr3PScale[channel], 
                                  perUnitWidth=False, nameForLegend='Z+X (From Data)',
                                  isBackground=True)
        cr3P1F.sumw2()
        expectedError3P1F = Double(0)
        integral3P1F = cr3P1F.IntegralAndError(0,cr3P1F.GetNbinsX(), expectedError3P1F)

        cr2P2F = plotter.makeHist('2P2F', '2P2F', channel, '1.', '', 
                                  bins, weights=cr2PScale[channel], 
                                  perUnitWidth=False, nameForLegend='Z+X (From Data)',
                                  isBackground=True)
        cr2P2F.sumw2()
        expectedError2P2F = Double(0)
        integral2P2F = cr2P2F.IntegralAndError(0,cr2P2F.GetNbinsX(), expectedError2P2F)

        cr3P1F -= cr2P2F
        for b in cr3P1F:
            if b.value < 0.:
                b.value = 0.

        cr3P1F.sumw2()
        expectedErrorBkg = Double(0)
        integralBkg = cr3P1F.IntegralAndError(0,cr3P1F.GetNbinsX(), expectedErrorBkg)

        plotter.fullPlot('count_%s_ID%s_Iso%s_PU%s'%(channel,scaleSet[0], scaleSet[1], scaleSet[2]), 
                         channel, '1.', '', 
                         bins, 'mc', 'data', canvasX=1000, logy=False, 
                         xTitle="one", 
                         xUnits="",
                         extraBkgs=[cr3P1F], outFile='count_%s_ID%s_Iso%s_PU%s.png'%(channel,scaleSet[0], scaleSet[1], scaleSet[2]), 
                         mcWeights=mcWeight[channel])
        for ob in plotter.drawings['count_%s_ID%s_Iso%s_PU%s'%(channel,scaleSet[0], scaleSet[1], scaleSet[2])].objects:
            if isinstance(ob, HistStack):
                mcStack = ob
                break

        expectedTotal = sum(mcStack.hists)
        expectedTotal.sumw2()
        expectedError = Double(0)
        integralSig = expectedTotal.IntegralAndError(0,expectedTotal.GetNbinsX(), expectedError)
        print "    %4s:"%channel
        print "        Tot  : %f +/- %f"%(integralSig, expectedError)
        print "        SR   : %f +/- %f"%(integralSig-integralBkg, sqrt(expectedError**2 - expectedErrorBkg**2))
        print "        Bkg  : %f +/- %f"%(integralBkg, expectedErrorBkg)
        print "        3P1F : %f +/- %f"%(integral3P1F, expectedError3P1F)
        print "        2P2F : %f +/- %f"%(integral2P2F, expectedError2P2F)
        for h in mcStack:
            try:
                sample = h.getSample()
            except:
                continue
            if isinstance(sample, list): # group hist
                sample = h.getGroup()
            sampleError = Double(0)
            sampleInt = h.IntegralAndError(0, h.GetNbinsX(), sampleError)
            if sample == '3P1F':
                sNameToPrint = 'Bkg (data driven)'
            else:
                sNameToPrint = sample
            print "        %s: %f +/- %f"%(sNameToPrint, sampleInt, sampleError)


