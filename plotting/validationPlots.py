from NtuplePlotter import NtuplePlotter
from ZZHelpers import Z_MASS

dataFiles = {
    'CMSSW_7_4_X' : '/data/nawoods/ntuples/validation74X/results_mz/*.root',
    'CMSSW_7_5_X' : '/data/nawoods/ntuples/validation75X/results_mz/*.root',
    }

plotter = NtuplePlotter('zz', './plots/cmssw75x_validation_mz', 
                        {}, dataFiles, intLumi=14.6)

evVars = ['Mass', 'Pt', 'Eta', 'Phi', 'nJets', 'nvtx']
evBins = {
    'Mass' : [20, 0., 400.],
    'Pt' : [20, 0., 100.],
    'Eta' : [10, -4., 4.],
    'Phi' : [10, -3.15, 3.15],
    'nJets' : [6, -0.5, 5.5],
    'nvtx' : [10, 6., 26.],
    }
evTitles = {
    'Mass' : 'm_{4\\ell}',
    'Pt' : 'p_{T_{4\\ell}}',
    'Eta' : '\\eta_{4\\ell}',
    'Phi' : '\\phi_{4\\ell}',
    'nJets' : '\\text{# jets}',
    'nvtx' : '\\text{# Vertices}',
}

lepVars = ['Pt', 'Eta', 'Phi', 'SIP3D']
lepBins = {
    'Pt' : [20, 0., 100.],
    'Eta' : [10, -2.5, 2.5],
    'Phi' : [10, -3.15, 3.15],
    'SIP3D' : [10, 0., 10.],
    }
lepTitles = {
    'Pt' : 'p_{T}',
    'Eta' : '\\eta',
    'Phi' : '\\phi',
    'SIP3D' : '\\text{SIP}_{\\text{3D}}',
}
zVars = ['Mass', 'Pt', 'Eta', 'Phi']
zBins = {
    'Mass' : [20, 0., 120.],
    'Pt' : [20, 0., 60.],
    'Eta' : [10, -4., 4.],
    'Phi' : [10, -3.15, 3.15],
    }
zTitles = {
    'Mass' : 'm_{\\ell\\ell}',
    'Pt' : 'p_{T_{\\ell\\ell}}',
    'Eta' : '\\eta_{\\ell\\ell}',
    'Phi' : '\\phi_{\\ell\\ell}',
}

units = {
    'Pt' : 'GeV',
    'Eta' : '',
    'Phi' : '',
    'Mass' : 'GeV',
    'nJets' : '',
    'SIP3D' : '',
    'nvtx' : '',
}

runSelection = '(run == 251643 || run == 251721)'

channels = ['eeee', 'eemm', 'mmmm', 'zz']

for var in evVars:
    for channel in channels:
        d = plotter.Drawing("validate_%s_%s"%(var,channel), plotter.style, 800, 1000)
        h75x = plotter.makeHist("CMSSW_7_5_X", "CMSSW_7_5_X", channel, 
                                var, "", evBins[var], -1., runSelection, perUnitWidth=False)
        h74x = plotter.makeHist("CMSSW_7_4_X", "CMSSW_7_4_X", channel, 
                                var, "", evBins[var], -1., runSelection, perUnitWidth=False)
        h74x.color = 'red'
        
        d.addObject(h75x, legendStyle="LPE")
        d.addObject(h74x, legendStyle="LPE")
        
        d.addRatio(h75x, h74x, 0.23, yTitle="Ratio")
        
        d.draw(outFile=plotter.outdir+"%s%s.png"%(channel,var), xTitle=evTitles[var],
               xUnits=units[var], yTitle="Events", intLumi=14.6)

channelList = {'e':['eeee' for foo in range(4)] + ['eemm' for foo in range(2)]}
channelList['m'] = ['mmmm' for foo in range(4)] + ['eemm' for foo in range(2)]
channelList['ez14e'] = ['eeee' for foo in range(2)]
channelList['ez24e'] = ['eeee' for foo in range(2)]
channelList['ez12e2m'] = ['eemm' for foo in range(2)]
channelList['ez22e2m'] = ['eemm' for foo in range(2)]
channelList['mz14m'] = ['mmmm' for foo in range(2)]
channelList['mz24m'] = ['mmmm' for foo in range(2)]
channelList['mz12e2m'] = ['eemm' for foo in range(2)]
channelList['mz22e2m'] = ['eemm' for foo in range(2)]
varTemplates = {'e' : ['e%d%%s'%(foo+1) for foo in range(4)] + ['e%d%%s'%(foo+1) for foo in range(2)]}
varTemplates['m'] = ['m%d%%s'%(foo+1) for foo in range(4)] + ['m%d%%s'%(foo+1) for foo in range(2)]
varTemplates['ez14e'] = ['e%d%%s'%(foo+1) for foo in range(2)]
varTemplates['ez24e'] = ['e%d%%s'%(foo+3) for foo in range(2)]
varTemplates['ez12e2m'] = ['e%d%%s'%(foo+1) for foo in range(2)]
varTemplates['ez22e2m'] = ['e%d%%s'%(foo+1) for foo in range(2)]
varTemplates['mz14m'] = ['m%d%%s'%(foo+1) for foo in range(2)]
varTemplates['mz24m'] = ['m%d%%s'%(foo+3) for foo in range(2)]
varTemplates['mz12e2m'] = ['m%d%%s'%(foo+1) for foo in range(2)]
varTemplates['mz22e2m'] = ['m%d%%s'%(foo+1) for foo in range(2)]
lepSelections = {}
lepSelections['e'] = [runSelection for foo in range(6)]
lepSelections['m'] = [runSelection for foo in range(6)]
lepSelections['ez14e'] = [runSelection for foo in range(2)]
lepSelections['ez24e'] = [runSelection for foo in range(2)]
lepSelections['mz14m'] = [runSelection for foo in range(2)]
lepSelections['mz24m'] = [runSelection for foo in range(2)]
lepSelections['ez12e2m'] = [runSelection+'&&(abs(e1_e2_Mass - %f) < abs(m1_m2_Mass - %f))'%(Z_MASS, Z_MASS) for foo in range(2)]
lepSelections['ez22e2m'] = [runSelection+'&&(abs(e1_e2_Mass - %f) > abs(m1_m2_Mass - %f))'%(Z_MASS, Z_MASS) for foo in range(2)]
lepSelections['mz12e2m'] = [runSelection+'&&(abs(m1_m2_Mass - %f) < abs(e1_e2_Mass - %f))'%(Z_MASS, Z_MASS) for foo in range(2)]
lepSelections['mz22e2m'] = [runSelection+'&&(abs(m1_m2_Mass - %f) > abs(e1_e2_Mass - %f))'%(Z_MASS, Z_MASS) for foo in range(2)]


for var in lepVars:
    for lep in channelList.keys():
        d = plotter.Drawing("validate_%s%s"%(lep, var), plotter.style, 800, 1000)
        h75x = plotter.makeHist("CMSSW_7_5_X", "CMSSW_7_5_X", channelList[lep], 
                                [v%var for v in varTemplates[lep]], lepSelections[lep], 
                                lepBins[var], -1., "", perUnitWidth=False)
        h74x = plotter.makeHist("CMSSW_7_4_X", "CMSSW_7_4_X", channelList[lep], 
                                [v%var for v in varTemplates[lep]], lepSelections[lep], 
                                lepBins[var], -1., "", perUnitWidth=False)
        h74x.color = 'red'
        
        d.addObject(h75x, legendStyle="LPE")
        d.addObject(h74x, legendStyle="LPE")
        
        d.addRatio(h75x, h74x, 0.23, yTitle="Ratio")
        
        d.draw(outFile=plotter.outdir+"%s_%s.png"%(lep,var), xTitle=lepTitles[var],
               xUnits=units[var], yTitle="Events", intLumi=14.6)


zChannelList = {
    'e' : ['eeee', 'eemm'],
    'm' : ['mmmm', 'eemm'],
    'e4e' : ['eeee'],
    'm4m' : ['mmmm'],
    'e2e2m' : ['eemm'],
    'm2e2m' : ['eemm'],
    }
zVarTemplates = {
    1 : {
        'e' : ['e1_e2_%s', 'e1_e2_%s'],
        'm' : ['m1_m2_%s', 'm1_m2_%s'],
        'e4e' : ['e1_e2_%s'],
        'm4m' : ['m1_m2_%s'],
        'e2e2m' : ['e1_e2_%s'],
        'm2e2m' : ['m1_m2_%s'],
        },
    2 : {
        'e' : ['e3_e4_%s', 'e1_e2_%s'],
        'm' : ['m3_m4_%s', 'm1_m2_%s'],
        'e4e' : ['e3_e4_%s'],
        'm4m' : ['m3_m4_%s'],
        'e2e2m' : ['e1_e2_%s'],
        'm2e2m' : ['m1_m2_%s'],
        },
    }
zSelections = {
    1 : {
        'e' : [runSelection, runSelection+'&&(abs(e1_e2_Mass - %f) < abs(m1_m2_Mass - %f))'%(Z_MASS, Z_MASS)],
        'm' : [runSelection, runSelection+'&&(abs(m1_m2_Mass - %f) < abs(e1_e2_Mass - %f))'%(Z_MASS, Z_MASS)],
        'e4e' : [runSelection],
        'm4m' : [runSelection],
        'e2e2m' : [runSelection+'&&(abs(e1_e2_Mass - %f) < abs(m1_m2_Mass - %f))'%(Z_MASS, Z_MASS)],
        'm2e2m' : [runSelection+'&&(abs(m1_m2_Mass - %f) < abs(e1_e2_Mass - %f))'%(Z_MASS, Z_MASS)],
        },
    2 : {
        'e' : [runSelection, runSelection+'&&(abs(e1_e2_Mass - %f) > abs(m1_m2_Mass - %f))'%(Z_MASS, Z_MASS)],
        'm' : [runSelection, runSelection+'&&(abs(m1_m2_Mass - %f) > abs(e1_e2_Mass - %f))'%(Z_MASS, Z_MASS)],
        'e4e' : [runSelection],
        'm4m' : [runSelection],
        'e2e2m' : [runSelection+'&&(abs(e1_e2_Mass - %f) > abs(m1_m2_Mass - %f))'%(Z_MASS, Z_MASS)],
        'm2e2m' : [runSelection+'&&(abs(m1_m2_Mass - %f) > abs(e1_e2_Mass - %f))'%(Z_MASS, Z_MASS)],
        },
    }
        

for var in zVars:
    for nZ in [1,2]:
        for lep in zChannelList.keys():
            d = plotter.Drawing("validate_Z%s%d_%s"%(lep, nZ,var), plotter.style, 800, 1000)
            h75x = plotter.makeHist("CMSSW_7_5_X", "CMSSW_7_5_X", zChannelList[lep], 
                                    [v%var for v in zVarTemplates[nZ][lep]], zSelections[nZ][lep], 
                                    zBins[var], -1., "", perUnitWidth=False)
            h74x = plotter.makeHist("CMSSW_7_4_X", "CMSSW_7_4_X", zChannelList[lep], 
                                    [v%var for v in zVarTemplates[nZ][lep]], zSelections[nZ][lep], 
                                    zBins[var], -1., "", perUnitWidth=False)

            h74x.color = 'red'
            
            d.addObject(h75x, legendStyle="LPE")
            d.addObject(h74x, legendStyle="LPE")
            
            d.addRatio(h75x, h74x, 0.23, yTitle="Ratio")

            d.draw(outFile=plotter.outdir+"Z%s%d_%s.png"%(lep, nZ, var), xTitle=zTitles[var],
                   xUnits=units[var], yTitle="Events", intLumi=14.6)


