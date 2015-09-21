###############################################################################
### Make HZZ plots using a bunch of different FSR methods, after full analysis
###############################################################################


from collections import Sequence

from NtuplePlotter import *
from rootpy.ROOT import TLine

fsrTypes = ['DREt', 'DREt2', 'Et4DR01', 'Et4DR03'] # 'DREt15',
isoTypes = ['', 'Iso']
dmTypes = ['', 'DM']
fsrs = ['%s%s%s'%(fsr, iso, dm) for fsr in fsrTypes \
            for iso in isoTypes \
            for dm in dmTypes]
dREtCuts = {
    'DREtIso' : .0372,
    'DREt2Iso' : .0110,
    #'DREt15IsoDM' : .0450,
    #'DREt15DM' : .0048,
    'DREt2IsoDM' : 0.03,
    'DREt2' : .0031,
    #'DREt15' : .0031,
    'DREt' : .0152,
    'DREtIsoDM' : 0.05,
    'DREtDM' : .02,
    'DREt2DM' : .00476,
    #'DREt15Iso' : .011,
    }

prettyname_base = {
    'DREt' : '\\frac{\\Delta R}{E_{T}} < %.4f ',
    #'DREt15' : '\\frac{\\Delta R}{E_{T}^{1.5}} < %.4f ',
    'DREt2' : '\\frac{\\Delta R}{E_{T}^{2}} < %.4f ',
    'Legacy' : '\\text{Legacy}',
    'Et4DR01' : 'E_{T} > 4, \\: \\Delta R < 0.1 ',
    'Et4DR03' : 'E_{T} > 4, \\: \\Delta R < 0.3 ',
    'NoFSR' : '\\text{No FSR}',
}

fsr_colors = {
    'Legacy' : 'black',
    'Et4DR03' : 'red',
    'Et4DR01' : 'blue',
    'DREt' : 'forestgreen',
    #'DREt15' : 'plum',
    'DREt2' : 'magenta',
    'Iso' : 'orange',
    'DM' : 'springgreen',
    'IsoDM' : 'purple',
    'NoFSR' : 'turquoise',
    }

channels = ['mmmm']

for fsr in ['Legacy', "NoFSR"] + fsrTypes:
    for iso in isoTypes:
        for dm in dmTypes:
            if (fsr == 'Legacy' or fsr == "NoFSR") and (bool(iso) or bool(dm)):
                continue
            key = fsr+iso+dm
            sampleInfo[key] = sampleInfo["GluGluHToZZTo4L_M125_13TeV_powheg_JHUgen_pythia8"].copy()
            sampleInfo[key]['shortName'] = key
            prettyName = prettyname_base[fsr]
            if 'DREt' in fsr:
                prettyName = prettyName % dREtCuts[key]
            if iso:
                prettyName += "\\text{ (Iso.)}"
            if dm:
                prettyName += "(\\Delta m_Z)"
            sampleInfo[key]['prettyName'] = prettyName
            sampleInfo[key]['color'] = fsr_colors[fsr]
            sampleInfo[key]['isSignal'] = True


plotter = NtuplePlotter('zz', './plots/FSRComparison_effpur_withGen', 
                        '/data/nawoods/ntuples/dREtNtuples_7/results/*.root')


def plotSomeHists(name, sampleList, varList, selectionList, binning,
                  xTitle, xUnits, colors=[], legParams={}, drawOpts={}):

    assert len(varList) == len(selectionList) and len(varList) == len(sampleList), \
        "Must specify the same number of samples, variables and selections"
    assert len(colors) == 0 or len(colors) == len(varList),\
        "Must specify one color per histogram, or no colors."

    d = plotter.Drawing(name, plotter.style, 1000, 800)

    for i in xrange(len(sampleList)):
        h = plotter.makeHist('mc', sampleList[i], channels, varList[i],
                             selectionList[i], binning, -1.)

        if not h.GetEntries():
            print "nothing to do for %s, %s"%(sampleList[i], varList[i])
            continue

        h.fillstyle = 'hollow'
        if len(colors):
            h.color = colors[i]
        else:
            h.color = sampleInfo[h.getSample()]['color']
        h.SetLineWidth(2)

        d.addObject(h)

        h.legendstyle = "L"

    plotter.drawings[name] = d
    plotter.drawings[name].draw(drawOpts, plotter.outdir+'/'+name+'.png', False,
                                xTitle, xUnits, "Events", "", True, legParams,
                                False, -1., True)


def plotOneMethod(method, simpleVarName, varTemplate, selectionTemplate, 
                  binning, xTitle, xUnits, plotLegacy=True, 
                  plotNoFSR=False, legParams={}, drawOpts={}):
    '''
    varTemplate and selectionTemplate will have instances of the string 
    "#FSRTYPE#" replaced with the FSR type.
    '''
    varList = []
    selecList = []
    colList = []
    sampleList = []

    if plotLegacy:
        varList.append(varTemplate.replace("#FSRTYPE#", "FSR"))
        selecList.append(selectionTemplate.replace("#FSRTYPE#", "FSR"))
        colList.append(fsr_colors["Legacy"])
        sampleList.append("Legacy")
    if plotNoFSR:
        varList.append(varTemplate.replace("#FSRTYPE#", ""))
        selecList.append(selectionTemplate.replace("#FSRTYPE#", ""))
        colList.append(fsr_colors["NoFSR"])
        sampleList.append("NoFSR")

    for iso in isoTypes:
        for dm in dmTypes:
            fsrType = "%s%sFSR%s"%(method, iso, dm)
            sampleList.append("%s%s%s"%(method, iso, dm))
            varList.append(varTemplate.replace("#FSRTYPE#", fsrType))
            selecList.append(selectionTemplate.replace("#FSRTYPE#", fsrType))
            if not (iso or dm):
                colList.append(fsr_colors[method])
            else:
                colList.append(fsr_colors[iso+dm])
            
    plotSomeHists(simpleVarName+"_"+method, sampleList, varList, selecList, 
                  binning, xTitle, xUnits, colList, 
                  legParams, drawOpts)


modStrs = {
    '' : 'FSR',
    'Iso' : 'IsoFSR',
    'DM' : 'FSRDM',
    'IsoDM' : 'IsoFSRDM',
    }
def plotOneModifier(mod, simpleVarName, varTemplate, selectionTemplate,
                    binning, xTitle, xUnits, plotLegacy=True,
                    plotNoFSR=False, legParams={}, drawOpts={}):
    '''
    varTemplate and selectionTemplate will have instances of the string 
    "#FSRTYPE#" replaced with the FSR type.
    '''
    varList = []
    selecList = []
    sampleList = []

    if plotLegacy:
        varList.append(varTemplate.replace("#FSRTYPE#", "FSR"))
        selecList.append(selectionTemplate.replace("#FSRTYPE#", "FSR"))
        sampleList.append("Legacy")
    if plotNoFSR:
        varList.append(varTemplate.replace("#FSRTYPE#", ""))
        selecList.append(selectionTemplate.replace("#FSRTYPE#", ""))
        sampleList.append("NoFSR")

        
    for method in fsrTypes:
        fsrType = method+modStrs[mod]
        varList.append(varTemplate.replace("#FSRTYPE#", fsrType))
        selecList.append(selectionTemplate.replace("#FSRTYPE#", fsrType))
        sampleList.append(method+mod)

    plotSomeHists(simpleVarName+"_allTypes"+mod, sampleList, varList, 
                  selecList, binning, xTitle, xUnits, [], 
                  legParams, drawOpts)


def plotSomeDifferences(name, baseSample, baseVar, baseSelection,
                        sampleList, varList, selectionList, binning,
                        xTitle, xUnits, colors=[], legParams={}, drawOpts={}):
    assert len(varList) == len(selectionList) and len(varList) == len(sampleList), \
        "Must specify the same number of samples, variables and selections"
    assert len(colors) == 0 or len(colors) == len(varList),\
        "Must specify one color per histogram, or no colors."

    d = plotter.Drawing(name, plotter.style, 1000, 800)

    hBase = plotter.makeHist('mc', baseSample, channels, baseVar,
                             baseSelection, binning, -1.)

    if not hBase.GetEntries():
        print "WARNING: Nothing found for %s, %s, %s, so there's nothing to subtract"%(baseSample, baseVar, baseSelection)

    for i in xrange(len(sampleList)):
        h = plotter.makeHist('mc', sampleList[i], channels, varList[i],
                             selectionList[i], binning, -1.)

        if not h.GetEntries():
            print "nothing to do for %s, %s"%(sampleList[i], varList[i])
            continue

        h.Add(hBase, -1.)

        h.fillstyle = 'hollow'
        if len(colors):
            h.color = colors[i]
        else:
            h.color = sampleInfo[h.getSample()]['color']
        h.SetLineWidth(2)

        d.addObject(h)

        h.legendstyle = "L"

    y0 = TLine(h.lowerbound(), 0, h.upperbound(), 0)
    d.addObject(y0, False)

    plotter.drawings[name] = d
    plotter.drawings[name].draw(drawOpts, plotter.outdir+'/'+name+'.png', False,
                                xTitle, xUnits, "\\text{Events}_{\\text{FSR}} - \\text{Events}_{\\text{No FSR}}", "", True, legParams,
                                False, -1., True)


def plotDifferenceOneMethod(method, simpleVarName, baseSample, baseVar, 
                            baseSelection, varTemplate, selectionTemplate, 
                            binning, xTitle, xUnits, plotLegacy=True, 
                            legParams={}, drawOpts={}):
    '''
    varTemplate and selectionTemplate will have instances of the string 
    "#FSRTYPE#" replaced with the FSR type.
    '''
    varList = []
    selecList = []
    colList = []
    sampleList = []

    if plotLegacy:
        varList.append(varTemplate.replace("#FSRTYPE#", "FSR"))
        selecList.append(selectionTemplate.replace("#FSRTYPE#", "FSR"))
        colList.append(fsr_colors["Legacy"])
        sampleList.append("Legacy")

    for iso in isoTypes:
        for dm in dmTypes:
            fsrType = "%s%sFSR%s"%(method, iso, dm)
            sampleList.append("%s%s%s"%(method, iso, dm))
            varList.append(varTemplate.replace("#FSRTYPE#", fsrType))
            selecList.append(selectionTemplate.replace("#FSRTYPE#", fsrType))
            if not (iso or dm):
                colList.append(fsr_colors[method])
            else:
                colList.append(fsr_colors[iso+dm])
            
    plotSomeDifferences(simpleVarName+"_"+method+"_Difference", baseSample, baseVar,
                        baseSelection, sampleList, varList, selecList, 
                        binning, xTitle, xUnits, colList, 
                        legParams, drawOpts)


def plotDifferenceOneModifier(mod, simpleVarName, baseSample, baseVar,
                              baseSelection, varTemplate, selectionTemplate,
                              binning, xTitle, xUnits, plotLegacy=True,
                              legParams={}, drawOpts={}):
    '''
    varTemplate and selectionTemplate will have instances of the string 
    "#FSRTYPE#" replaced with the FSR type.
    '''
    varList = []
    selecList = []
    sampleList = []

    if plotLegacy:
        varList.append(varTemplate.replace("#FSRTYPE#", "FSR"))
        selecList.append(selectionTemplate.replace("#FSRTYPE#", "FSR"))
        sampleList.append("Legacy")
        
    for method in fsrTypes:
        fsrType = method+modStrs[mod]
        varList.append(varTemplate.replace("#FSRTYPE#", fsrType))
        selecList.append(selectionTemplate.replace("#FSRTYPE#", fsrType))
        sampleList.append(method+mod)

    plotSomeDifferences(simpleVarName+"_allTypes"+mod+"_Difference", baseSample, baseVar,
                        baseSelection, sampleList, varList, 
                        selecList, binning, xTitle, xUnits, [], 
                        legParams, drawOpts)


def countPassing(varTemplate, selectionTemplate, low, hi):
    varList = {"NoFSR" : varTemplate.replace("#FSRTYPE#", ""),
               "Legacy" : varTemplate.replace("#FSRTYPE#", "FSR")}
    selectionList = {"NoFSR" : selectionTemplate.replace("#FSRTYPE#", ""),
                     "Legacy" : selectionTemplate.replace("#FSRTYPE#", "FSR")}

    for fsr in fsrTypes:
        for iso in isoTypes:
            for dm in dmTypes:
                fsrType = "%s%sFSR%s"%(fsr, iso, dm)
                varList["%s%s%s"%(fsr, iso, dm)] = varTemplate.replace("#FSRTYPE#", fsrType)
                selectionList["%s%s%s"%(fsr, iso, dm)] = selectionTemplate.replace("#FSRTYPE#", fsrType)

    n = {}
    for s in varList:
        h = plotter.makeHist('mc', s, channels, varList[s],
                             selectionList[s], [1, low, hi], -1.)
        n[s] = h.GetEntries()

    print "%s entries passing %s"%(varList['NoFSR'], selectionList['NoFSR'])
    for s in sorted(n.keys(), key=lambda x: n[x], reverse=True):
        print "    %s: %d"%(s, n[s])
    print ""


def plotSomeEfficiencies(name, sampleList, varList, selectionList, 
                         selectionListTight, binning,
                         xTitle, xUnits, yTitle="Efficiency", yUnits='', 
                         colors=[], legParams={}, drawOpts={}):

    assert len(varList) == len(selectionList) and \
        len(selectionList) == len(selectionListTight) and \
        len(varList) == len(sampleList), \
        "Must specify the same number of samples, variables and selections"
    assert len(colors) == 0 or len(colors) == len(varList),\
        "Must specify one color per graph, or no colors."

    d = plotter.Drawing(name, plotter.style, 1000, 800)

    for i in xrange(len(sampleList)):
        if isinstance(varList[i], Sequence):
            ch = [channels[0] for ich in xrange(len(varList[i]))]
        else:
            ch = channels

        g = plotter.makeEfficiency('mc', sampleList[i], ch, varList[i],
                                   selectionList[i], selectionListTight[i], 
                                   binning, '')

        if not g.GetN():
            print "nothing to do for %s, %s"%(sampleList[i], varList[i])
            continue

        if len(colors) > i:
            g.color = colors[i]

        d.addObject(g)

    plotter.drawings[name] = d
    plotter.drawings[name].draw(drawOpts, plotter.outdir+'/'+name+'.png', False,
                                xTitle, xUnits, yTitle, yUnits, True, legParams,
                                False, -1., True)


def plotEffOneMethod(method, simpleVarName, varTemplate, selectionTemplate, 
                     selectionTemplateTight, binning, xTitle, xUnits,
                     yTitle="Efficiency", yUnits='', 
                     legacyVars='', legacySelection='', legacySelectionTight='',
                     legParams={}, drawOpts={}):
    '''
    varTemplate, selectionTemplate, and selectionTemplateTight will have 
    instances of the string "#FSRTYPE#" replaced with the FSR type.
    '''
    varList = []
    selecList = []
    selecListTight = []
    colList = []
    sampleList = []

    if bool(legacySelection) or bool(legacySelectionTight):
        varList.append(legacyVars)
        selecList.append(legacySelection)
        selecListTight.append(legacySelectionTight)
        colList.append(fsr_colors["Legacy"])
        sampleList.append("Legacy")

    for iso in isoTypes:
        for dm in dmTypes:
            fsrType = "%s%sFSR%s"%(method, iso, dm)
            sampleList.append("%s%s%s"%(method, iso, dm))
            if isinstance(varTemplate, Sequence):
                thisVar = [v.replace("#FSRTYPE#", fsrType) for v in varTemplate]
                thisSel = [s.replace("#FSRTYPE#", fsrType) for s in selectionTemplate]
                thisSelT = [s.replace("#FSRTYPE#", fsrType) for s in selectionTemplateTight]
            else:
                thisVar = varTemplate.replace("#FSRTYPE#", fsrType)
                thisSel = selectionTemplate.replace("#FSRTYPE#", fsrType)
                thisSelT = selectionTemplateTight.replace("#FSRTYPE#", fsrType)
            varList.append(thisVar)
            selecList.append(thisSel)
            selecListTight.append(thisSelT)
            if not (iso or dm):
                colList.append(fsr_colors[method])
            else:
                colList.append(fsr_colors[iso+dm])
            
    plotSomeEfficiencies(simpleVarName+"_"+method, sampleList, varList, 
                         selecList, selecListTight,
                         binning, xTitle, xUnits, yTitle, yUnits,
                         colList, legParams, drawOpts)


def plotEffOneModifier(mod, simpleVarName, varTemplate, selectionTemplate,
                       selectionTemplateTight, binning, xTitle, xUnits,
                       yTitle="Efficiency", yUnits='',
                       legacyVars='', legacySelection='', legacySelectionTight='',
                       legParams={}, drawOpts={}):
    '''
    varTemplate, selectionTemplate, and selectionTemplateTight will have 
    instances of the string "#FSRTYPE#" replaced with the FSR type.
    '''
    varList = []
    selecList = []
    selecListTight = []
    sampleList = []

    if bool(legacySelection) or bool(legacySelectionTight):
        varList.append(legacyVars)
        selecList.append(legacySelection)
        selecListTight.append(legacySelectionTight)
        sampleList.append("Legacy")

    for method in fsrTypes:
        fsrType = method+modStrs[mod]
        if isinstance(varTemplate, Sequence):
            thisVar = [v.replace("#FSRTYPE#", fsrType) for v in varTemplate]
            thisSel = [s.replace("#FSRTYPE#", fsrType) for s in selectionTemplate]
            thisSelT = [s.replace("#FSRTYPE#", fsrType) for s in selectionTemplateTight]
        else:
            thisVar = varTemplate.replace("#FSRTYPE#", fsrType)
            thisSel = selectionTemplate.replace("#FSRTYPE#", fsrType)
            thisSelT = selectionTemplateTight.replace("#FSRTYPE#", fsrType)
        varList.append(thisVar)
        selecList.append(thisSel)
        selecListTight.append(thisSelT)
        sampleList.append(method+mod)

    plotSomeEfficiencies(simpleVarName+"_allTypes"+mod, sampleList, varList, 
                         selecList, selecListTight, binning,
                         xTitle, xUnits, yTitle, yUnits, [], 
                         legParams, drawOpts)


def printPurityEfficiency(pVarTemplate, eVarTemplate, pSelectionTemplate, 
                          eSelectionTemplate, selectionTemplateTight, low, hi,
                          pLegacyVar='', eLegacyVar='', pLegacySelection='', 
                          eLegacySelection='', legacySelectionTight=''):
    eVar = {}
    pVar = {}
    pSelec = {}
    eSelec = {}
    selecTight = {}
    sample = {}

    if bool(eLegacySelection) or bool(pLegacySelection) or bool(legacySelectionTight):
        pVar['Legacy'] = pLegacyVar
        eVar['Legacy'] = eLegacyVar
        pSelec['Legacy'] = pLegacySelection
        eSelec['Legacy'] = eLegacySelection
        selecTight['Legacy'] = legacySelectionTight
        sample['Legacy'] = "Legacy"

    for fsrType in fsrTypes:
        for iso in isoTypes:
            for dm in dmTypes:
                fsr = "%s%sFSR%s"%(fsrType, iso, dm)
                sample[fsr] = "%s%s%s"%(fsrType, iso, dm)
                if isinstance(pVarTemplate, Sequence):
                    thisVarP = [v.replace("#FSRTYPE#",  fsr) for v in pVarTemplate]
                    thisVarE = [v.replace("#FSRTYPE#",  fsr) for v in eVarTemplate]
                    thisSelP = [s.replace("#FSRTYPE#", fsr) for s in pSelectionTemplate]
                    thisSelE = [s.replace("#FSRTYPE#", fsr) for s in eSelectionTemplate]
                    thisSelT = [s.replace("#FSRTYPE#", fsr) for s in selectionTemplateTight]
                else:
                    thisVarP = pVarTemplate.replace("#FSRTYPE#", fsr)
                    thisVarE = eVarTemplate.replace("#FSRTYPE#", fsr)
                    thisSelP = pSelectionTemplate.replace("#FSRTYPE#", fsr)
                    thisSelE = eSelectionTemplate.replace("#FSRTYPE#", fsr)
                    thisSelT = selectionTemplateTight.replace("#FSRTYPE#", fsr)
                pVar[fsr] = thisVarP
                eVar[fsr] = thisVarE
                pSelec[fsr] = thisSelP
                eSelec[fsr] = thisSelE
                selecTight[fsr] = thisSelT
            
    p = {}
    e = {}

    for fsr in sample.keys():
        if len(pVar[fsr]) > 1: 
            ch = [channels[0] for ich in xrange(len(pVar[fsr]))]
        else:
            ch = channels
        purG = plotter.makeEfficiency('mc', sample[fsr], ch, pVar[fsr],
                                      pSelec[fsr], selecTight[fsr], 
                                      [1, low, hi], '')
        p[fsr] = purG[0][1]
        effG = plotter.makeEfficiency('mc', sample[fsr], ch, eVar[fsr],
                                      eSelec[fsr], selecTight[fsr], 
                                      [1, low, hi], '')
        e[fsr] = effG[0][1]

    printedOnce = set()
    for fsr in sorted(p.keys()):
        baseType = fsr.replace("Iso", "").replace("DM", "").replace("FSR", "")
        if baseType in printedOnce:
            print "    %s:"%fsr.replace(baseType, "").replace("FSR", "")
        else:
            print "%s:"%baseType
            printedOnce.add(baseType)
        print "        %0.3f pure, %0.3f efficient"%(p[fsr], e[fsr])



baseVars = ['m4l', 'mZ1', 'mZ2']
varTemplates = {
    'm4l' : 'Mass#FSRTYPE#',
    'mZ1' : 'm1_m2_Mass#FSRTYPE#',
    'mZ2' : 'm3_m4_Mass#FSRTYPE#',
    'm4lChange' : 'abs(Mass-125.) - abs(Mass#FSRTYPE#-125.)',
    'mZ1Change' : 'abs(m1_m2_Mass-91.1876) - abs(m1_m2_Mass#FSRTYPE#-91.1876)',
    'mZ2Change' : 'abs(m3_m4_Mass-91.1876) - abs(m3_m4_Mass#FSRTYPE#-91.1876)',
    }
selectionTemplates = {
    'm4l' : 'abs(Mass - Mass#FSRTYPE#) > 0.1', # 'Mass != Mass#FSRTYPE#',
    'mZ1' : 'abs(m1_m2_Mass - m1_m2_Mass#FSRTYPE#) > 0.1', # 'm1_m2_Mass != m1_m2_Mass#FSRTYPE#',
    'mZ2' : 'abs(m3_m4_Mass - m3_m4_Mass#FSRTYPE#) > 0.1', #'m3_m4_Mass != m3_m4_Mass#FSRTYPE#',
    }

purVarTemplates = {
    'fsrPt' : ['m%d#FSRTYPE#Pt'%(mn+1) for mn in range(4)],
    'fsrDR' : ['m%d#FSRTYPE#DR'%(mn+1) for mn in range(4)],
    'dM4l' : ['abs(Mass - 125.) - abs(Mass + m%d#FSRTYPE#MassChange - 125.)'%(mn+1) for mn in range(4)],
    }
effVarTemplates = {
    'fsrPt' : ['m%dGenFSRPt'%(mn+1) for mn in range(4)],
    'fsrDR' : ['m%dGenFSRDR'%(mn+1) for mn in range(4)],
    'dM4l' : ['abs(Mass - 125.) - abs(Mass + m%dGenFSRMassChange - 125.)'%(mn+1) for mn in range(4)],
    }
purSelectionTemplate = ['m%d#FSRTYPE#Pt > 0.1'%(mn+1) for mn in range(4)]
purEffSelectionTemplateTight = ['m%d#FSRTYPE#GenMatch > 0.5'%(mn+1) for mn in range(4)]
effSelectionTemplate = ['m%dHasGenFSR'%(mn+1) for mn in range(4)]

legPurVars = {
    'fsrPt' : ['m1_m2_FSRPt', 'm1_m2_FSRPt', 'm3_m4_FSRPt', 'm3_m4_FSRPt'],
    'fsrDR' : ['m1_m2_FSRDR', 'm1_m2_FSRDR', 'm3_m4_FSRDR', 'm3_m4_FSRDR'],
    'dM4l' : ['abs(Mass - 125.) - abs(Mass + m1_m2_FSRMassChange - 125.)', 
              'abs(Mass - 125.) - abs(Mass + m1_m2_FSRMassChange - 125.)', 
              'abs(Mass - 125.) - abs(Mass + m3_m4_FSRMassChange - 125.)', 
              'abs(Mass - 125.) - abs(Mass + m3_m4_FSRMassChange - 125.)',],
    }
legEffVars = effVarTemplates.copy()
legPurSelection = ['m%dHasFSR'%(nm+1) for nm in range(4)]
legPurEffSelectionTight = ['m1HasFSR && m1_m2_FSRGenMatch > 0.5', 'm2HasFSR && m1_m2_FSRGenMatch > 0.5', 
                           'm3HasFSR && m3_m4_FSRGenMatch > 0.5', 'm4HasFSR && m3_m4_FSRGenMatch > 0.5']
legEffSelection = ['m%dHasGenFSR'%(nm+1) for nm in range(4)]


bins = {
    'm4l' : [80, 80., 160.],
    'mZ1' : [40, 40., 120.],
    'mZ2' : [37, 9., 120.],
    'Change' : [40, -9.75, 50.25],
    'fsrPt' : [20, 0., 60],
    'fsrPtPur' : [3.*xs for xs in range(5)]+[15.+6.*xs for xs in range(4)]+[60.],
    'fsrPtEff' : [3.*xstep for xstep in range(7)] + [24.+6.*xstep for xstep in range(4)] + [51., 60.],
    'fsrDR' : [15, 0., 1.],
    'fsrDREff' : [0.04*xstep for xstep in range(7)] + [.28+0.08*xstep for xstep in range(4)] + \
        [0.76, 1.],
    'fsrDRPur' : [.05*xs for xs in range(4)]+[.2+.1*xs for xs in range(4)]+[.75, 1.],
    'ChangeEffPur' : [-12.+4.*xs for xs in range(9)]+[24.+8.*xs for xs in range(3)]+[64.],
    }
xTitles = {
    'm4l' : 'm_{4\\mu}',
    'mZ1' : 'm_{\\mu_{1}\\mu_{2}}',
    'mZ2' : 'm_{\\mu_{3}\\mu_{4}}',
    'm4lChange' : '\\left| m_{4\\mu} - m_{H} \\right| - \\left| m_{4\\mu + \\gamma} - m_{H} \\right|',
    'mZ1Change' : '\\left| m_{\\mu_{1}\\mu_{2}} - m_{Z} \\right| - \\left| m_{\\mu_{1}\\mu_{2}\\gamma} - m_{Z} \\right|',
    'mZ2Change' : '\\left| m_{\\mu_{3}\\mu_{4}} - m_{Z} \\right| - \\left| m_{\\mu_{3}\\mu_{4}\\gamma} - m_{Z} \\right|',
    'fsrPt' : 'E_{T_{\\gamma}}',
    'fsrDR' : '\\Delta R \\left(\\ell, \\gamma \\right)',
    'm4lChangeEff' : '\\left| m_{4\\mu} - m_{H} \\right| - \\left| m_{4\\mu + \\gamma_{\\text{gen}}} - m_{H} \\right|',
    }

xUnits = {
    'fsrPt' : 'GeV',
    'fsrDR' : '',
    'Change' : 'GeV',
    }

yLimits = {
    'm4lDiff' : (-70., 280.),
    'mZ1Diff' : (-30., 250.),
    'mZ2Diff' : (-10., 85.),
    'm4lChange' : (0., 175.),
    'mZ1Change' : (0., 125.),
    'mZ2Change' : (0., 125.),
}

legParamsTemplate = {
    'textsize' : 0.02,
    'leftmargin' : 0.1,
    'rightmargin' : 0.5,
    'entrysep' : 0.008,
    }
legParams = {var : legParamsTemplate.copy() for var in baseVars+effVarTemplates.keys()}
legParams['mZ2']['leftmargin'] = 0.5
legParams['mZ2']['rightmargin'] = 0.1
legParams['Change'] = legParams['mZ2'].copy()
legParams['fsrPt']['leftmargin'] = 0.3
legParams['fsrPt']['rightmargin'] = 0.3
legParams['fsrPt']['topmargin'] = 0.6
legParams['fsrPt']['textsize'] = 0.021
legParams['fsrDR']['leftmargin'] = 0.5
legParams['fsrDR']['rightmargin'] = 0.05
legParams['fsrDR']['topmargin'] = 0.1
legParams['dM4l']['leftmargin'] = 0.1
legParams['dM4l']['rightmargin'] = 0.5


for var in baseVars:
    for fsr in fsrTypes:
        plotOneMethod(fsr, var, varTemplates[var], selectionTemplates[var],
                      bins[var], xTitles[var],
                      "GeV", legParams=legParams[var])
        plotOneMethod(fsr, var+"_allEvents_", varTemplates[var], "",
                      bins[var], xTitles[var],
                      "GeV", plotNoFSR=True, legParams=legParams[var])
        plotDifferenceOneMethod(fsr, var+"_allEvents_", "NoFSR", 
                                varTemplates[var].replace("#FSRTYPE#",""), "",
                                varTemplates[var], "",
                                bins[var], 
                                xTitles[var], "GeV", legParams=legParams[var],
                                drawOpts={'ylimits':yLimits[var+"Diff"]})
        plotOneMethod(fsr, var+"Change", varTemplates[var+"Change"], selectionTemplates[var],
                      bins['Change'], 
                      xTitles[var+"Change"], "GeV", legParams=legParams['Change'], 
                      drawOpts={'ylimits':yLimits[var+"Change"]})

    for mod in modStrs:
        plotOneModifier(mod, var, varTemplates[var], selectionTemplates[var],
                        bins[var], xTitles[var],
                        "GeV", legParams=legParams[var])
        plotOneModifier(mod, var+"_allEvents_", varTemplates[var], "",
                        bins[var], xTitles[var],
                        "GeV", plotNoFSR=True, legParams=legParams[var])
        plotDifferenceOneModifier(mod, var+"_allEvents_", "NoFSR", 
                                  varTemplates[var].replace("#FSRTYPE#",""), "",
                                  varTemplates[var], "",
                                  bins[var],
                                  xTitles[var], "GeV", legParams=legParams[var],
                                  drawOpts={'ylimits':yLimits[var+"Diff"]})
        plotOneModifier(mod, var+"Change", varTemplates[var+"Change"], selectionTemplates[var],
                        bins["Change"],
                        xTitles[var+"Change"], "GeV", legParams=legParams['Change'], 
                        drawOpts={'ylimits':yLimits[var+"Change"]})
        
for fsrVar in ['fsrPt', 'fsrDR']:
    for fsr in fsrTypes:
        plotEffOneMethod(fsr, 'eff_'+fsrVar, effVarTemplates[fsrVar],
                         effSelectionTemplate, purEffSelectionTemplateTight,
                         bins[fsrVar+"Eff"],
                         "\\text{Gen } "+xTitles[fsrVar], xUnits[fsrVar], 
                         "Efficiency", "", legEffVars[fsrVar], 
                         legEffSelection, legPurEffSelectionTight,
                         legParams[fsrVar])
        plotEffOneMethod(fsr, 'pur_'+fsrVar, purVarTemplates[fsrVar],
                         purSelectionTemplate, purEffSelectionTemplateTight,
                         bins[fsrVar+"Pur"],
                         xTitles[fsrVar], xUnits[fsrVar], "Purity", "",
                         legPurVars[fsrVar], legPurSelection, legPurEffSelectionTight,
                         legParams[fsrVar])

    for mod in modStrs:
        plotEffOneModifier(mod, 'eff_'+fsrVar, effVarTemplates[fsrVar],
                           effSelectionTemplate, purEffSelectionTemplateTight,
                           bins[fsrVar+"Eff"],
                           "\\text{Gen } "+xTitles[fsrVar], xUnits[fsrVar], 
                           "Efficiency", "", legEffVars[fsrVar], 
                           legEffSelection, legPurEffSelectionTight,
                           legParams[fsrVar])
        plotEffOneModifier(mod, 'pur_'+fsrVar, purVarTemplates[fsrVar],
                           purSelectionTemplate, purEffSelectionTemplateTight,
                           bins[fsrVar+"Pur"],
                           xTitles[fsrVar], xUnits[fsrVar], "Purity", "",
                           legPurVars[fsrVar], legPurSelection, legPurEffSelectionTight,
                           legParams[fsrVar])

for mod in modStrs:
    plotEffOneModifier(mod, 'eff_m4lChange', effVarTemplates['dM4l'],
                       effSelectionTemplate, purEffSelectionTemplateTight,
                       bins["ChangeEffPur"],
                       xTitles["m4lChangeEff"], "GeV", 
                       "Efficiency", "", legEffVars['dM4l'], 
                       legEffSelection, legPurEffSelectionTight,
                       legParams['dM4l'])
    plotEffOneModifier(mod, 'pur_m4lChange', purVarTemplates['dM4l'],
                       purSelectionTemplate, purEffSelectionTemplateTight,
                       bins["ChangeEffPur"],
                       xTitles["m4lChange"], "GeV", "Purity", "",
                       legPurVars["dM4l"], legPurSelection, legPurEffSelectionTight,
                       legParams['dM4l'])


countPassing("Mass#FSRTYPE#", "abs(Mass#FSRTYPE# - 125.) < 2.5", 120., 130.)
print ""
printPurityEfficiency(purVarTemplates['fsrDR'], effVarTemplates['fsrDR'], purSelectionTemplate, 
                      effSelectionTemplate, purEffSelectionTemplateTight, 0., 4.,
                      legPurVars['fsrDR'], legEffVars['fsrDR'], legPurSelection, 
                      legEffSelection, legPurEffSelectionTight)

hGenDR = plotter.makeHist('mc', "Legacy", ["mmmm" for immmm in range(4)], 
                          ['m%dGenFSRDR'%(nm+1) for nm in range(4)],
                          ['m%dHasGenFSR'%(nm+1) for nm in range(4)],
                          [30, 0., 3.], -1.)
hGenDR.style = "P"
hGenDR.color = "blue"
d = plotter.Drawing("genDR", plotter.style, 1000, 800, True)
d.addObject(hGenDR)
d.draw({}, plotter.outdir+'/genDR.png', False,
       "\\text{Gen } "+xTitles['fsrDR'], "", "Events", "", 
       False, {}, False, -1., True)


