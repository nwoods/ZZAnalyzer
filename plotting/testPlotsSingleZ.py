'''

Plot single Zs

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
from ZZHelpers import Z_MASS
from WeightStringMaker import WeightStringMaker, TPFunctionManager

from rootpy.io import root_open

from datetime import date
import os

outdir = '/afs/cern.ch/user/n/nawoods/www/ZZPlots/singleZ_2015silver_{0}'.format(date.today().strftime('%d%b%Y').lower())
link = '/afs/cern.ch/user/n/nawoods/www/ZZPlots/singleZ_latest'

plotter = NtuplePlotter('z', outdir, 
                        {'mc':'/data/nawoods/ntuples/singlez_mc_14feb2016_0/results/*.root'},
                        {'data':'/data/nawoods/ntuples/singlez_data_2015silver_14feb2016_0/results/*.root'},
                        intLumi=2619.)

try:
    os.unlink(link)
except:
    pass

os.symlink(outdir, link)

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
    'e' : '(GenWeight*{0}*{1})'.format(puScaleFactorStr, z1eMCWeight),
    'm' : '(GenWeight*{0}*{1})'.format(puScaleFactorStr, z1mMCWeight),
}

channels = {
    'e' : 'ee',
    'm' : 'mm',
}

units = {
    'MassDREtFSR' : 'GeV',
    'Mass' : 'GeV',
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
    'SIP' : '',
    }

binningZ = {
    'MassDREtFSR' : [30, 60., 120.],
    'Mass' : [30, 60., 120.],
    'EtaDREtFSR' : [20, -5., 5.],
    'PtDREtFSR' : [30, 0., 150.],
    # 'PhiDREtFSR' : [12, -3.15, 3.15],
    }

xTitlesZ = {
    'MassDREtFSR' : 'm_{%s}',
    'Mass' : 'm_{%s}',
    'EtaDREtFSR' : '\\eta_{%s}',
    'PtDREtFSR' : 'p_{T_{%s}}',
    'PhiDREtFSR' : '\\phi_{%s}',
    }

varTempsZ = {
    'e' : 'e1_e2_%s',
    'm' : 'm1_m2_%s',
    }

objectsZ = {
    'z' : ['e', 'm'],
    'ze' : ['e'],
    'zm' : ['m'],
    }

objectTextZ = {
    'z' : '\\ell\\ell',
    'ze' : 'ee\\,',
    'zm' : '\\mu\\mu',
    }

binningL = {
    #'Phi' : [12, -3.15, 3.15],
    'Eta' : [10, -2.5, 2.5],
    'Pt' : [30, 0., 150.],
    'Iso' : [11, 0., 0.55],
    'PVDXY' : [10, -.5, .5],
    'PVDZ' : [10, -1., 1.],
    'SIP' : [10, 0., 5.],
    }

varsL = {
    'Pt' : {lep:'Pt' for lep in ['e', 'm']},
    'Eta' : {lep:'Eta' for lep in ['e', 'm']},
    'Phi' : {lep:'Phi' for lep in ['e', 'm']},
    'PVDXY' : {lep:'PVDXY' for lep in ['e', 'm']},
    'PVDZ' : {lep:'PVDZ' for lep in ['e', 'm']},
    'Iso' : {'e' : 'HZZIsoFSR', 'm' : 'HZZIsoFSR'},
    'SIP' : {lep:'SIP3D' for lep in ['e', 'm']},
    }

xTitlesL = {
    'Phi' : '\\phi_{%s}',
    'Eta' : '\\eta_{%s}',
    'Pt' : 'p_{T_{%s}}',
    'PVDXY' : '\\Delta_{xy} \\text{(%s,PV)}',
    'PVDZ' : '\\Delta_{z} \\text{(%s,PV)}',
    'Iso' : '\\text{Rel. PF Iso. (PU corrected)} (%s)',
    'SIP' : '%s \\text{ SIP}_\\text{3D}',
    }

objectTextL = {
    'z' : '\\ell',
    'ze' : 'e\\,',
    'zm' : '\\mu',
    }

for z, objects in objectsZ.iteritems():
    
    channel = [channels[lep] for lep in objectsZ[z]]
    weight = [mcWeight[lep] for lep in objectsZ[z]]

    s = plotter.makeCategoryStack('mc', channel, '1.', '',
                                  [1,0.,2.], 1., weight)
    h = plotter.makeHist('data', 'data', channel, '1.', '', [1,0.,2.])

    mcScale = h.GetEntries() / s.GetStack().Last().Integral()

    # print z, mcScale
    # continue

    for var, bins in binningZ.iteritems():
        variables = [varTempsZ[lep]%var for lep in objectsZ[z]]
        weight = [('%f*'%mcScale)+mcWeight[lep] for lep in objectsZ[z]]

        plotter.fullPlot('%s%s'%(z, var), channel, variables, 
                         '', bins, 'mc', 'data', canvasX=1000, logy=False, 
                         xTitle=xTitlesZ[var]%objectTextZ[z],
                         xUnits=units[var], outFile='%s%s.png'%(z,var), 
                         mcWeights=weight,
                         widthInYTitle=bool(units[var]),)

    for var, bins in binningL.iteritems():
        variables = ['%s%d%s'%(lep, nLep, varsL[var][lep]) for nLep in range(1,3) for lep in objectsZ[z]]
        channel = [channels[lep] for nLep in range(1,3) for lep in objectsZ[z]]
        weight = [('%f*'%mcScale)+mcWeight[lep] for nLep in range(1,3) for lep in objectsZ[z]]

        if var == "Eta":
            legParams = {'leftmargin':0.3,'rightmargin':0.3,'topmargin':0.5}
            legSolid = True
        else:
            legParams = {}
            legSolid = False

        plotter.fullPlot('%sLep%s'%(z, var), channel, variables, 
                         '', bins, 'mc', 'data', canvasX=1000, logy=False, 
                         xTitle=xTitlesL[var]%objectTextL[z],
                         xUnits=units[var], outFile='%sLep%s.png'%(z,var), 
                         mcWeights=weight, legParams=legParams,
                         legSolid=legSolid,
                         widthInYTitle=bool(units[var]),)

mcWeight_noPU = {
    'e' : '(GenWeight*{0})'.format(z1eMCWeight),
    'm' : '(GenWeight*{0})'.format(z1mMCWeight),
}

plotter.fullPlot('nvtx_noNorm', ['ee','mm'], 'nvtx', 
                 '', [40,0.,40.], 'mc', 'data', canvasX=1000, logy=False, 
                 xTitle="\# PVs",
                 xUnits="", outFile='nvtx_noNorm.png',
                 mcWeights=[mcWeight['e'],mcWeight['m']])

plotter.fullPlot('nvtx_noReweight_noNorm', ['ee','mm'], 'nvtx', 
                 '', [40,0.,40.], 'mc', 'data', canvasX=1000, logy=False, 
                 xTitle="\# PVs",
                 xUnits="", outFile='nvtx_noReweight_noNorm.png',
                 mcWeights=[mcWeight_noPU['e'],mcWeight_noPU['m']])

s = plotter.makeCategoryStack('mc', ['ee','mm'], '1.', '',
                              [1,0.,2.], 1., [mcWeight['e'],mcWeight['m']])
h = plotter.makeHist('data', 'data', ['ee','mm'], '1.', '', [1,0.,2.])

mcScale = h.GetEntries() / s.GetStack().Last().Integral()

s_noPU = plotter.makeCategoryStack('mc', ['ee','mm'], '1.', '',
                                   [1,0.,2.], 1., [mcWeight_noPU['e'],mcWeight_noPU['m']])
mcScale_noPU = h.GetEntries() / s_noPU.GetStack().Last().Integral()

plotter.fullPlot('nvtx', ['ee','mm'], 'nvtx', 
                 '', [40,0.,40.], 'mc', 'data', canvasX=1000, logy=False, 
                 xTitle="\# PVs",
                 xUnits="", outFile='nvtx.png',
                 mcWeights=[mcWeight['e']+'*%f'%mcScale,mcWeight['m']+'*%f'%mcScale])

plotter.fullPlot('nvtx_noReweight', ['ee','mm'], 'nvtx', 
                 '', [40,0.,40.], 'mc', 'data', canvasX=1000, logy=False, 
                 xTitle="\# PVs",
                 xUnits="", outFile='nvtx_noReweight.png',
                 mcWeights=[mcWeight_noPU['e']+'*%f'%mcScale_noPU,mcWeight_noPU['m']+'*%f'%mcScale_noPU])



