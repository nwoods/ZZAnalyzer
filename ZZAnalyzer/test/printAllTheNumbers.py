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


from ZZAnalyzer.plotting import NtuplePlotter
from ZZAnalyzer.utils import WeightStringMaker, TPFunctionManager, BkgManager

from rootpy.io import root_open
import rootpy.compiled as C
from rootpy.plotting import HistStack, Canvas
from rootpy.ROOT import Double

import os
from math import sqrt
from datetime import date

from argparse import ArgumentParser

parser = ArgumentParser(description="Make lots of numbers for ZZ analyses.")
parser.add_argument('--smp', action='store_true', help='SMP ZZ numbers')
parser.add_argument('--hzz', action='store_true', help='HZZ numbers')
parser.add_argument('--full', action='store_true', help='Full 4l spectrum numbers')
parser.add_argument('--z4l', action='store_true', help='SMP Z->4l numbers')
parser.add_argument('--printData', action='store_true', help='Print all signal events from data')
parser.add_argument('--print2P2F', action='store_true', help='Print all 2P2F events from data')
parser.add_argument('--print3P1F', action='store_true', help='Print all 3P1F events from data')
parser.add_argument('--eventsOnly', action='store_true', help='Just print the list(s) of events, don\'t calculate numbers')
parser.add_argument('--dySkim', action='store_true', help='Include the low-mZ2 DY skim.')
args = parser.parse_args()

if args.smp:
    ana = 'smp'
    assert not any([args.hzz, args.full, args.z4l]), "Only do one analysis at a time, please!"
if args.hzz:
    ana = 'hzz'
    assert not any([args.smp, args.full, args.z4l]), "Only do one analysis at a time, please!"
if args.full:
    ana = 'full'
    assert not any([args.hzz, args.smp, args.z4l]), "Only do one analysis at a time, please!"
if args.z4l:
    ana = 'z4l'
    assert not any([args.hzz, args.full, args.smp]), "Only do one analysis at a time, please!"

sampleID = ana

ntupleSet = '26jan2016_0'
ntupleSet3P1F = '26jan2016_0'
ntupleSet2P2F = '26jan2016_0'

mcSamples = {
    'mc':'/data/nawoods/ntuples/zzNtuples_mc_{1}/results_{0}/ZZTo4L_13TeV_*.root,/data/nawoods/ntuples/zzNtuples_mc_{1}/results_{0}/GluGlu*.root'.format(sampleID, ntupleSet),
    'mc3P1F':'/data/nawoods/ntuples/zzNtuples_mc_{1}/results_{0}_3P1F/*.root'.format(sampleID, ntupleSet3P1F),
    'mc2P2F':'/data/nawoods/ntuples/zzNtuples_mc_{1}/results_{0}_2P2F/*.root'.format(sampleID, ntupleSet2P2F),
    } 
if args.dySkim:
    mcSamples['mc'] += ',/data/nawoods/ntuples/zzNtuples_mc_dySkim_10feb2016_0/results_{0}/DYSkim_*.root'.format(sampleID, ntupleSet)

dataSamples = {
    'data':'/data/nawoods/ntuples/zzNtuples_data_2015silver_{1}/results_{0}/data*.root'.format(sampleID, ntupleSet),
    '3P1F':'/data/nawoods/ntuples/zzNtuples_data_2015silver_{1}/results_{0}_3P1F/data*.root'.format(sampleID, ntupleSet3P1F),
    '2P2F':'/data/nawoods/ntuples/zzNtuples_data_2015silver_{1}/results_{0}_2P2F/data*.root'.format(sampleID, ntupleSet2P2F),
    }

plotter = NtuplePlotter('zz', '/afs/cern.ch/user/n/nawoods/www/ZZPlots/counting_{0}_{1}'.format(date.today().strftime('%d%b%Y').lower(), ana),
                        mcSamples, dataSamples,
                        intLumi=2619.)

basicSelection = ''

print ""
if args.printData:
    print "Signal (data):"
    plotter.printPassingEvents('data')
elif not args.eventsOnly:
    print "Signal (data):"
    print '    eeee: %d'%plotter.ntuples['data']['data']['eeee'].GetEntries()
    print '    eemm: %d'%plotter.ntuples['data']['data']['eemm'].GetEntries()
    print '    mmmm: %d'%plotter.ntuples['data']['data']['mmmm'].GetEntries()
print ""
if args.print3P1F:
    print "3P1F CR (data):"
    plotter.printPassingEvents('3P1F')
elif not args.eventsOnly:
    print "3P1F CR (data):"
    print '    eeee: %d'%plotter.ntuples['3P1F']['3P1F']['eeee'].GetEntries()
    print '    eemm: %d'%plotter.ntuples['3P1F']['3P1F']['eemm'].GetEntries()
    print '    mmmm: %d'%plotter.ntuples['3P1F']['3P1F']['mmmm'].GetEntries()
    
print ""
if args.print2P2F:
    print "2P2F CR (data):"
    plotter.printPassingEvents('2P2F')
elif not args.eventsOnly:
    print "2P2F CR (data):"
    print '    eeee: %d'%plotter.ntuples['2P2F']['2P2F']['eeee'].GetEntries()
    print '    eemm: %d'%plotter.ntuples['2P2F']['2P2F']['eemm'].GetEntries()
    print '    mmmm: %d'%plotter.ntuples['2P2F']['2P2F']['mmmm'].GetEntries()
print ''

if args.eventsOnly:
    exit(0)

tpVersionHash = 'v2.0-13-g36fc26c' #'v1.1-4-ga295b14-extended' #v1.1-1-g4cbf52a_v2'

TP = TPFunctionManager(tpVersionHash)

scales=['', 'down', 'up']

fPUScale = root_open(os.path.join(os.environ['zza'],'ZZAnalyzer','data/pileupReweighting/PUScaleFactors_29Feb2016.root'))
puScaleFactorHist = {
    '' : fPUScale.Get("puScaleFactor"),
    'up' : fPUScale.Get("puScaleFactor_ScaleUp"),
    'down' : fPUScale.Get("puScaleFactor_ScaleDown"),
}

wts = WeightStringMaker('puWeight')

puScaleFactorStr = {s:wts.makeWeightStringFromHist(h, 'nTruePU') for s,h in puScaleFactorHist.iteritems()}

bkg = BkgManager('01mar2016')

cr3PScale = {
    ch : bkg.fullString3P1F(ch) for ch in ['eeee','eemm','mmmm']
}

cr3PScale['zz'] = [cr3PScale[c] for c in ['eeee','eemm','mmmm']]

cr2PScale = {
    ch : bkg.fullString2P2F(ch) for ch in ['eeee','eemm','mmmm']
}

cr2PScale['zz'] = [cr2PScale[c] for c in ['eeee','eemm','mmmm']]

cr2PMigrationScale = {
    ch : bkg.fullString2P2FMigration(ch) for ch in ['eeee','eemm','mmmm']
}

# print cr2PScale['eeee']
# print ''
# print cr2PMigrationScale['eeee']
# exit()

cr2PMigrationScale['zz'] = [cr2PMigrationScale[c] for c in ['eeee',
                                                            'eemm',
                                                            'mmmm']]


# samples to subtract off of CRs based on MC
subtractSamples = []
for s in plotter.ntuples['mc3P1F']:
    if s[:3] == 'ZZT' or s[:10] == 'GluGluToZZ' and 'tau' not in s:
    #if s[:7] == 'GluGluT' or s[:3] == 'ZZT':
        subtractSamples.append(s)

central = {}        
for scaleSet in [['', '', ''], # [id, iso, PU]
                 ['down', '', ''], ['up', '', ''],
                 ['', 'down', ''], ['', 'up', ''],
                 ['', '', 'down'], ['', '', 'up']]:

    z1eMCWeight = '*'.join(TP.getTPString('e%d'%ne, 'TightID', scaleSet[0])+'*'+TP.getTPString('e%d'%ne, 'IsoTight', scaleSet[1]) for ne in range(1,3))
    z2eMCWeight = '*'.join(TP.getTPString('e%d'%ne, 'TightID', scaleSet[0])+'*'+TP.getTPString('e%d'%ne, 'IsoTight', scaleSet[1]) for ne in range(3,5))
    z1mMCWeight = '*'.join(TP.getTPString('m%d'%nm, 'TightID', scaleSet[0])+'*'+TP.getTPString('m%d'%nm, 'IsoTight', scaleSet[1]) for nm in range(1,3))
    z2mMCWeight = '*'.join(TP.getTPString('m%d'%nm, 'TightID', scaleSet[0])+'*'+TP.getTPString('m%d'%nm, 'IsoTight', scaleSet[1]) for nm in range(3,5))
    
    
    mcWeight = {
        'eeee' : '(GenWeight*{0}*{1}*{2})'.format(puScaleFactorStr[scaleSet[2]], z1eMCWeight, z2eMCWeight),
        'eemm' : '(GenWeight*{0}*{1}*{2})'.format(puScaleFactorStr[scaleSet[2]], z1eMCWeight, z1mMCWeight),
        'mmmm' : '(GenWeight*{0}*{1}*{2})'.format(puScaleFactorStr[scaleSet[2]], z1mMCWeight, z2mMCWeight),
    }

    cr3PScaleMC = {c:'*'.join([mcWeight[c], cr3PScale[c]]) for c in mcWeight}
    cr2PScaleMC = {c:'*'.join([mcWeight[c], cr2PScale[c]]) for c in mcWeight}
    cr2PMigrationScaleMC = {c:'*'.join([mcWeight[c], 
                                        cr2PMigrationScale[c]])
                            for c in mcWeight}
                 
    mcWeight['zz'] = [mcWeight['eeee'], mcWeight['eemm'], mcWeight['mmmm']]
    cr3PScaleMC['zz'] = [cr3PScaleMC[c] for c in ['eeee','eemm','mmmm']]
    cr2PScaleMC['zz'] = [cr2PScaleMC[c] for c in ['eeee','eemm','mmmm']]
    cr2PMigrationScaleMC['zz'] = [cr2PMigrationScaleMC[c] for c in ['eeee',
                                                                    'eemm',
                                                                    'mmmm']]

    print ''
    if scaleSet[0]:
        print "ID efficiency scale %s:"%scaleSet[0].upper()
    elif scaleSet[1]:
        print "Iso efficiency scale %s:"%scaleSet[1].upper()
    elif scaleSet[2]:
        print "PU scale %s:"%scaleSet[2].upper()
    else:
        print "MEAN VALUE:"
                 
    checkMigration = not any(scaleSet)

    bins=[1,0.,2.]
    for channel in ['zz', 'eeee', 'eemm', 'mmmm']:

        cr3P1F = plotter.makeHist('3P1F', '3P1F', channel, '1.', basicSelection, 
                                  bins, weights=cr3PScale[channel], 
                                  perUnitWidth=False, nameForLegend='Z+X (From Data)',
                                  isBackground=True)
        cr2P2F = plotter.makeHist('2P2F', '2P2F', channel, '1.', basicSelection, 
                                  bins, weights=cr2PScale[channel], 
                                  perUnitWidth=False, nameForLegend='Z+X (From Data)',
                                  isBackground=True)
        
        cr3P1F.sumw2()
        cr2P2F.sumw2()

        # print '\n', channel, ":" 
        # print "    Init:"
        # print "        3P1F: %f  2P2F: %f"%(cr3P1F.Integral(), cr2P2F.Integral())

        if checkMigration:
            cr2P2FMigration = plotter.makeHist('2P2F', '2P2F', channel, '1.', 
                                               basicSelection, bins, 
                                               weights=cr2PMigrationScale[channel],
                                               perUnitWidth=False, 
                                               nameForLegend='Z+X (From Data)',
                                               isBackground=True)
            cr2P2FMigration.sumw2()

        for ss in subtractSamples:
            sub3P = plotter.makeHist("mc3P1F", ss, channel,
                                     '1.', basicSelection, bins,
                                     weights=cr3PScaleMC[channel],
                                     perUnitWidth=False)
            cr3P1F -= sub3P
            sub2P = plotter.makeHist("mc2P2F", ss, channel,
                                     '1.', basicSelection, bins,
                                     weights=cr2PScaleMC[channel],
                                     perUnitWidth=False)
            cr2P2F -= sub2P

            if checkMigration:
                sub2PMigration = plotter.makeHist("mc2P2F", ss, channel,
                                                  '1.', basicSelection, bins,
                                                  weights=cr2PMigrationScaleMC[channel],
                                                  perUnitWidth=False)
                cr2P2FMigration -= sub2PMigration
                cr2P2FMigration.sumw2()

            cr3P1F.sumw2()
            cr2P2F.sumw2()
            
            # print "    Subtracted %s:"%ss
            # print "        3P1F: %f  2P2F: %f"%(cr3P1F.Integral(), cr2P2F.Integral())

        for b3P, b2P in zip(cr3P1F, cr2P2F):
            if b3P.value <= 0 or b2P.value > b3P.value:
                b3P.value = 0.
                #b3P.error = 0.
                b2P.value = 0.
                #b2P.error = 0.
            if b2P.value < 0.:
                b2P.value = 0.
        
        cr3P1F.sumw2()
        cr2P2F.sumw2()
            
        if checkMigration:
            for b2P, bMig in zip(cr2P2F, cr2P2FMigration):
                if b2P.value > bMig.value:
                    bMig.value = b2P.value
            
            cr2P2FMigration.sumw2()

        # print "    Negatives zeroed:"
        # print "        3P1F: %f  2P2F: %f"%(cr3P1F.Integral(), cr2P2F.Integral())

        expectedError3P1F = Double(0)
        integral3P1F = cr3P1F.IntegralAndError(0,cr3P1F.GetNbinsX(), expectedError3P1F)
        expectedError2P2F = Double(0)
        integral2P2F = cr2P2F.IntegralAndError(0,cr2P2F.GetNbinsX(), expectedError2P2F)

        cr3P1F -= cr2P2F

        cr3P1F.sumw2()

        # print "    3P1F-2P2F:"
        # print "        3P1F: %f  2P2F: %f"%(cr3P1F.Integral(), cr2P2F.Integral())
        # continue

        expectedErrorBkg = Double(0)
        integralBkg = cr3P1F.IntegralAndError(0,cr3P1F.GetNbinsX(), expectedErrorBkg)
        bkgPoisson = cr3P1F.poisson_errors()
        expectedErrorBkgUp = bkgPoisson.GetErrorYhigh(0)
        expectedErrorBkgDown = bkgPoisson.GetErrorYlow(0)

        if checkMigration:
            expectedError2P2FMigration = Double(0)
            integral2P2FMigration = cr2P2FMigration.IntegralAndError(0, cr2P2FMigration.GetNbinsX(), expectedError2P2FMigration)
            expectedMigration = integral2P2FMigration - integral2P2F
            expectedErrorMigration = sqrt(expectedError2P2FMigration**2. + expectedError2P2F**2)

        plotter.fullPlot('count_%s_ID%s_Iso%s_PU%s'%(channel,scaleSet[0], 
                                                     scaleSet[1], scaleSet[2]),
                         channel, '1.', basicSelection, 
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
        integralTot = expectedTotal.IntegralAndError(0,expectedTotal.GetNbinsX(), expectedError)
        integralSig = integralTot - integralBkg
        print "    %4s:"%channel

        if checkMigration:
            print "        2P2F migration to 3P1F: %f +/- %f"%(expectedMigration,
                                                               expectedErrorMigration)
            print ''

        print "        Tot  : %f +/- %f"%(integralTot, expectedError)
        print "        SR   : %f +/- %f"%(integralSig, sqrt(expectedError**2 - expectedErrorBkg**2))

        if not any(scaleSet):
            central[channel] = integralSig
        else:
            fracChange = (integralSig - central[channel]) / central[channel]
            print "            SR scale effect: {0:.3f}".format(fracChange)

        print "        Bkg  : %f +/- %f (+%f / -%f)"%(integralBkg, 
                                                      expectedErrorBkg, 
                                                      expectedErrorBkgUp, 
                                                      expectedErrorBkgDown)
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


    #break
