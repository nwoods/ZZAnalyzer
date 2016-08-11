

# include logging stuff first so other imports don't babble at us
import logging
from rootpy import log as rlog; rlog = rlog["/muonHighPtIDPlots"]
# don't show most silly ROOT messages
logging.basicConfig(level=logging.WARNING)
rlog["/ROOT.TCanvas.Print"].setLevel(rlog.WARNING)
rlog["/ROOT.TUnixSystem.SetDisplay"].setLevel(rlog.ERROR)

from rootpy.io import root_open
from rootpy.plotting import Hist, Canvas, Legend, Pad, Graph
from rootpy.ROOT import TLine
from rootpy.plotting.utils import draw
from rootpy import asrootpy

from glob import glob
from os import path

from PlotStyle import PlotStyle


style = PlotStyle()

masses = [125, 300, 750, 1000, 1500, 2500]


outdir = '/afs/cern.ch/user/n/nawoods/www/muonHighMassResults/'


fileList = glob('/data/nawoods/ntuples/zzNtuples_mc_76HighPtID_0/results/*.root')
fileListLeg = glob('/data/nawoods/ntuples/zzNtuples_mc_76HighPtID_0/results_legacy/*.root')
files = {}
filesLeg = {}
for m in masses:
    for f in fileList:
        if str(m) in f:
            files[m] = root_open(f)
            break
    else:
        raise ValueError("No file found for m={} (high-pt ID)".format(m))
    for f in fileListLeg:
        if str(m) in f:
            filesLeg[m] = root_open(f)
            break
    else:
        raise ValueError("No file found for m={} (legacy ID)".format(m))

smProcesses = ['qqZZ', 'ggZZ2e2m', 'ggZZ4m']
smXSecs = { # units are fb
    'qqZZ' : 1256.,
    'ggZZ2e2m' : 3.19,
    'ggZZ4m' : 1.59,
    }

for f in fileList:
    if f.split('/')[-1].startswith('ZZTo4L'):
        files['qqZZ'] = root_open(f)
    elif '2e2mu' in f:
        files['ggZZ2e2m'] = root_open(f)
    elif '4mu' in f:
        files['ggZZ4m'] = root_open(f)
if len(files) < len(masses) + len(smProcesses):
    raise ValueError("Missing one or more SM samples (high-pt ID)")

for f in fileListLeg:
    if f.split('/')[-1].startswith('ZZTo4L'):
        filesLeg['qqZZ'] = root_open(f)
    elif '2e2mu' in f:
        filesLeg['ggZZ2e2m'] = root_open(f)
    elif '4mu' in f:
        filesLeg['ggZZ4m'] = root_open(f)
if len(filesLeg) < len(masses) + len(smProcesses):
    raise ValueError("Missing one or more SM samples (legacy ID)")

channels = ['eemm', 'mmmm']

ntuples = {}
ntuplesLeg = {}
for c in channels:
    ntuples[c] = {}
    ntuplesLeg[c] = {}
    for m in masses+smProcesses:
        ntuples[c][m] = files[m].Get(c+'/final/Ntuple')
        ntuplesLeg[c][m] = filesLeg[m].Get(c+'/final/Ntuple')

ntuplesNew = {}
ntuplesNew['mmmm'] = {m:asrootpy(n.CopyTree("(m1IsPFMuon + m2IsPFMuon + m3IsPFMuon + m4IsPFMuon) < 4.")) for m,n in ntuples['mmmm'].iteritems()}
ntuplesNew['eemm'] = {m:asrootpy(n.CopyTree("(m1IsPFMuon + m2IsPFMuon) < 2.")) for m,n in ntuples['eemm'].iteritems()}


varsAll = {
    '4lMass' : ['MassDREtFSR'],
    '4lMassNoFSR' : ['Mass'],
    '4lEta' : ['abs(EtaDREtFSR)'],
    'D_bkg' : ['D_bkg'],
    'D_bkg_kin' : ['D_bkg_kin'],
    }

vars2e2m = varsAll.copy()
vars2e2m.update({
        'zMass' : ['m1_m2_MassDREtFSR'],
        'zEta' : ['abs(m1_m2_EtaDREtFSR)'],
        'zPt' : ['m1_m2_PtDREtFSR'],
        'mPt' : ['m1Pt', 'm2Pt'],
        'mEta' : ['abs(m1Eta)', 'abs(m2Eta)'],
        })

vars4m = varsAll.copy()
vars4m.update({
        'zMass' : ['m1_m2_MassDREtFSR', 'm3_m4_MassDREtFSR'],
        'zEta' : ['abs(m1_m2_EtaDREtFSR)', 'abs(m3_m4_EtaDREtFSR)'],
        'zPt' : ['m1_m2_PtDREtFSR', 'm3_m4_PtDREtFSR'],
        'z1Mass' : ['m1_m2_MassDREtFSR'],
        'z1Eta' : ['abs(m1_m2_EtaDREtFSR)'],
        'z1Pt' : ['m1_m2_PtDREtFSR'],
        'z2Mass' : ['m3_m4_MassDREtFSR'],
        'z2Eta' : ['abs(m3_m4_EtaDREtFSR)'],
        'z2Pt' : ['m3_m4_PtDREtFSR'],
        'mPt' : ['m1Pt', 'm2Pt', 'm3Pt', 'm4Pt'],
        'mEta' : ['abs(m1Eta)', 'abs(m2Eta)', 'abs(m3Eta)', 'abs(m4Eta)'],
        })

vars = {'eemm' : vars2e2m, 'mmmm' : vars4m}

# selectors for objects rescued by the new idea in events we're already 
# sure were rescued (i.e. we don't check the whole event again)
newObjectSelectorsAll = {v:['1'] for v in varsAll}

newObjectSelectors2e2m = newObjectSelectorsAll.copy()
newObjectSelectors2e2m.update({
        'zMass' : ['1'],
        'zEta' : ['1'],
        'zPt' : ['1'],
        'mPt' : ['m1IsPFMuon < 1.', 'm2IsPFMuon < 1.'],
        'mEta' : ['m1IsPFMuon < 1.', 'm2IsPFMuon < 1.'],
        })

newObjectSelectors4m = newObjectSelectorsAll.copy()
newObjectSelectors4m.update({
        'zMass' :  ['(m1IsPFMuon + m2IsPFMuon) < 2.', '(m3IsPFMuon + m4IsPFMuon) < 2.'],
        'zEta' :   ['(m1IsPFMuon + m2IsPFMuon) < 2.', '(m3IsPFMuon + m4IsPFMuon) < 2.'],
        'zPt' :    ['(m1IsPFMuon + m2IsPFMuon) < 2.', '(m3IsPFMuon + m4IsPFMuon) < 2.'],
        'z1Mass' : ['(m1IsPFMuon + m2IsPFMuon) < 2.'],
        'z1Eta' :  ['(m1IsPFMuon + m2IsPFMuon) < 2.'],
        'z1Pt' :   ['(m1IsPFMuon + m2IsPFMuon) < 2.'],
        'z2Mass' : ['(m3IsPFMuon + m4IsPFMuon) < 2.'],
        'z2Eta' :  ['(m3IsPFMuon + m4IsPFMuon) < 2.'],
        'z2Pt' :   ['(m3IsPFMuon + m4IsPFMuon) < 2.'],
        'mPt' :    ['m1IsPFMuon < 1.', 'm2IsPFMuon < 1.', 'm3IsPFMuon < 1.', 'm4IsPFMuon < 1.'],
        'mEta' :   ['m1IsPFMuon < 1.', 'm2IsPFMuon < 1.', 'm3IsPFMuon < 1.', 'm4IsPFMuon < 1.'],
        })

newObjectSelectors = {'eemm' : newObjectSelectors2e2m, 'mmmm' : newObjectSelectors4m}


binning = {}
for m in masses:
    binning[m] = {}
    binning[m]['4lMass'] = [35, 0., 1.4*m]
    binning[m]['4lMassNoFSR'] = binning[m]['4lMass']
    binning[m]['4lEta'] = [50, 0., 5.]
    binning[m]['mPt'] = [25, 0., m*.3]
    binning[m]['mEta'] = [24, 0., 2.4]
    binning[m]['zMass'] = [30,60.,120.]
    binning[m]['zEta'] = [30,0.,3.]
    binning[m]['zPt'] = [25, 0., m*.6]
    binning[m]['z1Mass'] = [30,60.,120.]
    binning[m]['z1Eta'] = [30,0.,3.]
    binning[m]['z1Pt'] = [25, 0., m*.6]
    binning[m]['z2Mass'] = [30,60.,120.]
    binning[m]['z2Eta'] = [30,0.,3.]
    binning[m]['z2Pt'] = [25, 0., m*.6]
    binning[m]['D_bkg_kin'] = [20, 0., 1.]
    binning[m]['D_bkg'] = [20, -0, 1.]

binning['sm'] = binning[750].copy()

xTitles = {
    '4lMass' : 'm_{4\\ell}',
    '4lMassNoFSR' : 'm_{4\\ell} \\text{ (no FSR)}',
    '4lEta' : '\\left|\\eta_{4\\ell}\\right|',
    'mPt' : 'p_{T\\mu}',
    'mEta' : '\\left|\\eta_{\\mu}\\right|',
    'zMass' : 'm_{\\mu\\mu}',
    'zEta' : '\\left|\\eta_{\\mu\\mu}\\right|',
    'zPt' : 'p_{T\\mu\\mu}',
    'z1Mass' : 'm_{\\text{Z}_1}',
    'z1Eta' : '\\left|\\eta_{\\text{Z}_1}\\right|',
    'z1Pt' : 'p_{T_{\\text{Z}_1}}',
    'z2Mass' : 'm_{\\text{Z}_2}',
    'z2Eta' : '\\left|\\eta_{\\text{Z}_2}\\right|',
    'z2Pt' : 'p_{T_{\\text{Z}_2}}',
    'D_bkg' : 'D_\\text{bkg}',
    'D_bkg_kin' : 'D_{\\text{bkg}}^{\\text{kin}}',
}


# parameters for legend placement (passed to Legend constructor)
legRight = {}
legLeft = {
    'leftmargin' : .1,
    'rightmargin' : .45,
    }
legBot = {
    'leftmargin' : .3,
    'rightmargin' : .25,
    'topmargin' : .75,
    }

legPlacement = {v:legRight for v in vars['mmmm']}
legPlacement['4lMass'] = legLeft
legPlacement['4lMassNoFSR'] = legLeft
legPlacement['zPt'] = legBot
legPlacement['z1Pt'] = legBot
legPlacement['z2Pt'] = legBot
legPlacement['D_bkg_kin'] = legLeft



sumW = {}
for m in masses+smProcesses:
    metaTree = files[m].Get(channels[0]+'/metaInfo')
    sumW[m] = metaTree.Draw('1', 'summedWeights').Integral()
weight = '(GenWeight)'




def addRatio(canvas, num, denom, height=0.23, ratioMin=1., ratioMax=1.4,
             bottomMargin=0.34, topMargin=0.06, yTitle="Ratio", mainXAxis=None,
             mainYAxis=None, yRange=(.95,1.3), xRange=None):
    newCanvas = Canvas(canvas.GetWw(), canvas.GetWh())
    newCanvas.Divide(1,2)

    pad2 = asrootpy(newCanvas.GetPad(2))
    pad2.SetPad(0.,0.,1.,height)
    pad2.SetBottomMargin(bottomMargin)
    pad2.SetTopMargin(0.)

    canvas.SetTopMargin(topMargin)
    canvas.SetBottomMargin(0.01)
    pad1 = asrootpy(newCanvas.GetPad(1))
    pad1.SetPad(0.,height,1.,1.)
    pad1.SetTopMargin(topMargin)
    pad1.SetBottomMargin(0.01)
    
    hNum = num.clone()
    hNum.sumw2()
    numerator = Graph(hNum)
    hDenom = denom.clone()
    hDenom.sumw2()
    denominator = Graph(hDenom)

    nRemoved = 0
    for i in range(numerator.GetN()):
        if hDenom[i+1].value <= 0. or hNum[i+1].value <= 0.:
            numerator.RemovePoint(i - nRemoved)
            denominator.RemovePoint(i - nRemoved)
            nRemoved += 1

    ratio = numerator / denominator

    ratio.drawstyle = 'PE'
    ratio.color = 'black'

    unity = TLine(hNum.lowerbound(), 1, hNum.upperbound(), 1)
    unity.SetLineStyle(7)

    if yRange:
        ylimits = yRange
    else:
        ylimits = (1.-((ratio.GetMaximum()-1.)*.15), 1.+((ratio.GetMaximum()-1.)*1.2))
        if ylimits[0] >= ylimits[1]:
            ylimits = (.95, 1.3)

    (xaxis,yaxis),axisRange = draw(ratio, pad2, ytitle=yTitle, 
                                   ylimits=ylimits, xlimits=xRange)
    pad2.cd()
    unity.Draw("SAME")

    # correct placement of axes and label/titles
    if mainXAxis is not None and mainYAxis is not None:
        mainX = mainXAxis
        mainY = mainYAxis
        
        ratioX = xaxis
        ratioY = yaxis
            
        ratioX.title = mainX.title
        ratioX.SetTitleSize(mainX.GetTitleSize() * pad1.height / pad2.height)
        ratioX.SetLabelSize(mainX.GetLabelSize() * pad1.height / pad2.height)
        
        ratioY.SetTitleSize(mainY.GetTitleSize() * pad1.height / (2*pad2.height))
        ratioY.SetTitleOffset(0.6)
        ratioY.SetLabelSize(mainY.GetLabelSize() * pad1.height / (2*pad2.height))
        
        mainX.SetLabelOffset(999)
        mainX.SetTitleOffset(999)

    pad1.cd()
    canvas.DrawClonePad()

    return newCanvas


for c in ['mmmm']:
    for v in vars[c]:
        print "plotting {}".format(v)
        for m in masses:
            hOr = Hist(*binning[m][v], title='New ID')
            hLeg = Hist(*binning[m][v], title='Legacy ID')
            hNew = Hist(*binning[m][v])
            for i, expr in enumerate(vars[c][v]):
                ntuples[c][m].Draw(expr, weight, "goff", hOr)
                ntuplesLeg[c][m].Draw(expr, weight, "goff", hLeg)
                ntuplesNew[c][m].Draw(expr, '*'.join([weight, newObjectSelectors[c][v][i]]), "goff", hNew)

            if hOr.Integral():
                hLeg.scale(1./hOr.Integral()) # scale so hOr has area 1, hLeg is proportionally smaller
                hOr.scale(1./hOr.Integral())
            if hNew.Integral():
                hNew.scale(1./hNew.Integral())

            hOr.color = 'b'
            hOr.drawstyle = 'LPE'
            hOr.legendstyle = "LPE"
            hLeg.color = 'r'
            hLeg.drawstyle = 'LPE'
            hLeg.legendstyle = "LPE"

            hNew.color = 'b'
            hNew.drawstyle = 'hist'

            cCompare = Canvas(1000,1200)
            (xaxis, yaxis), axisRanges = draw([hOr, hLeg], cCompare, ytitle='arb.', xtitle=xTitles[v])
            legCompare = Legend([hOr, hLeg], **legPlacement[v])
            legCompare.Draw("SAME")
            cCompare = addRatio(cCompare, hOr, hLeg, mainXAxis=xaxis, 
                                mainYAxis=yaxis, xRange=axisRanges[:2])
            style.setCMSStyle(cCompare, "", True, "Preliminary Simulation", 13, -1)
            cCompare.Print(path.join(outdir, 'compare', '{}_m{}_{}.png'.format(v,m,c)))


            cNew = Canvas(1000,1000)
            draw(hNew, cNew, ytitle='arb', xtitle=xTitles[v])
            style.setCMSStyle(cNew, "", True, "Preliminary Simulation", 13, -1)
            cNew.Print(path.join(outdir, 'rescued', '{}_m{}_{}.png'.format(v,m,c)))
        
        
        hOrQQ = Hist(*binning['sm'][v], title='\\text{qq} \\!\\! \\rightarrow \\!\\! \\text{ZZ New ID}')
        hOrGG = Hist(*binning['sm'][v], title='\\text{gg} \\!\\! \\rightarrow \\!\\! \\text{ZZ New ID}')
        hLegQQ = Hist(*binning['sm'][v], title='\\text{qq} \\!\\! \\rightarrow \\!\\! \\text{ZZ Legacy ID}')
        hLegGG = Hist(*binning['sm'][v], title='\\text{gg} \\!\\! \\rightarrow \\!\\! \\text{ZZ Legacy ID}')

        for i, expr in enumerate(vars[c][v]):
            ntuples[c]['qqZZ'].Draw(expr, '*'.join([weight, str(1./sumW['qqZZ']), str(smXSecs['qqZZ'])]), "goff", hOrQQ)
            ntuples[c]['ggZZ2e2m'].Draw(expr, '*'.join([weight, str(1./sumW['ggZZ2e2m']), str(smXSecs['ggZZ2e2m'])]), "goff", hOrGG)
            ntuples[c]['ggZZ4m'].Draw(expr, '*'.join([weight, str(1./sumW['ggZZ4m']), str(smXSecs['ggZZ4m'])]), "goff", hOrGG)

            ntuplesLeg[c]['qqZZ'].Draw(expr, '*'.join([weight, str(1./sumW['qqZZ']), str(smXSecs['qqZZ'])]), "goff", hLegQQ)
            ntuplesLeg[c]['ggZZ2e2m'].Draw(expr, '*'.join([weight, str(1./sumW['ggZZ2e2m']), str(smXSecs['ggZZ2e2m'])]), "goff", hLegGG)
            ntuplesLeg[c]['ggZZ4m'].Draw(expr, '*'.join([weight, str(1./sumW['ggZZ4m']), str(smXSecs['ggZZ4m'])]), "goff", hLegGG)

        hOrSum = hOrQQ.clone()
        hOrSum.SetTitle("\\text{SM ZZ New ID}")
        hOrSum += hOrGG
        hLegSum = hLegQQ.clone()
        hLegSum.SetTitle("\\text{SM ZZ Legacy ID}")
        hLegSum += hLegGG

        hOrQQ.color = 'b'
        hOrQQ.drawstyle = 'LPE'
        hOrQQ.legendstyle = 'LPE'
        hLegQQ.color = 'lightblue'
        hLegQQ.drawstyle = 'LPE'
        hLegQQ.legendstyle = 'LPE'
        hOrGG.color = 'r'
        hOrGG.drawstyle = 'LPE'
        hOrGG.legendstyle = 'LPE'
        hLegGG.color = 'pink'
        hLegGG.drawstyle = 'LPE'
        hLegGG.legendstyle = 'LPE'
        hOrSum.color = 'green'
        hOrSum.drawstyle = 'LPE'
        hOrSum.legendstyle = 'LPE'
        hLegSum.color = 'limegreen'
        hLegSum.drawstyle = 'LPE'
        hLegSum.legendstyle = 'LPE'

        cSM = Canvas(1000,1200)
        (xaxis, yaxis), axisRanges = draw([hLegQQ, hOrQQ, hLegGG, hOrGG, hLegSum, hOrSum], cSM, 
                                          ytitle='\\text{Events} / \\text{fb}^{-1}', xtitle=xTitles[v])
        legSM = Legend([hOrSum, hLegSum, hOrQQ, hLegQQ, hOrGG, hLegGG], textsize=.025, entryheight=.025)
        legSM.Draw("SAME")
        cSM = addRatio(cSM, hOrSum, hLegSum, mainXAxis=xaxis, mainYAxis=yaxis, yTitle="Total Ratio")
        style.setCMSStyle(cSM, "", True, "Preliminary Simulation", 13, -1)
        cSM.Print(path.join(outdir, 'sm', '{}_{}.png'.format(v,c)))





