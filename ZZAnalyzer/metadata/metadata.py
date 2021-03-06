'''

Metadata needed for plotting samples relevant to 4l

Info items (key):
    xsec: Cross section (pb)
    sumW: Sum of MC weights for dataset (used as fallback if it can't be
        determined from the file)
    n: Number of events in original dataset before ntuplization (used as 
        fallback if sum of weights can't be found)
    isData: Boolean for data (True) or Monte Carlo
    isSignal: Boolean for whether the sample is signal or background (changes
        stacking order)
    shortName: Short name for sample
    prettyName: TeX formatted name for plot legends, etc.
    color: color for plotting. May be any color type supported by rootpy
    kFactor: scale factor for higher order cross section
    group: samples in the same group are plotted together. Groups are defined
        at the bottom of this file

Author: Nate Woods, U. Wisconsin

'''

sampleInfo = {}

sampleInfo['data'] = {
    'isData' : True,
    'color' : 'black',
    'shortName' : 'data',
    'prettyName' : 'data',
}

sampleInfo["DYJetsToLL_M-50_TuneCUETP8M1_13TeV-amcatnloFXFX-pythia8"] = {
    'xsec' : 6104., 
    'n' : 28825132,
    'sumW' : 452776427520.,
    'isData' : False,
    'shortName' : 'DYJets',
    'prettyName' : '\\text{DY+Jets}',
    'isSignal' : False,
    'color' : '#669966', #'forestgreen',
    'group' : 'DYJets',
}

sampleInfo["DYSkim"] = sampleInfo["DYJetsToLL_M-50_TuneCUETP8M1_13TeV-amcatnloFXFX-pythia8"].copy()
sampleInfo["DYSkim"]['shortName'] = 'DYSkim'
sampleInfo["DYSkim"]['prettyName'] = '\\text{qq} \\!\\!\\rightarrow\\!\\! \\text{Z}\\gamma^{*} \\text{(low } m_{Z_2} \\text{)}'
sampleInfo["DYSkim"]['color'] = '#99ccff'
del sampleInfo["DYSkim"]['group']
#sampleInfo["DYSkim"]['group'] = 'qqZZ'

sampleInfo["DYJetsToLL_M-10to50_TuneCUETP8M1_13TeV-amcatnloFXFX-pythia8"] = {
    'xsec' : 18610., 
    'n' : 30535559,
    'sumW' : 905265086464.,
    'isData' : False,
    'shortName' : 'DYJets_M10to50',
    'prettyName' : '\\text{DY+Jets} (m_{\\ell\\ell} < 50)',
    'isSignal' : False,
    'color' : 'forestgreen',
    'group' : 'DYJets',
}

sampleInfo["GluGluToZZTo2e2mu_BackgroundOnly_13TeV_MCFM"] = {
    'xsec' : 0.00319364,
    'n' : 649600,
    'sumW' : 648800.,
    'isData' : False,
    'shortName' : 'ggZZ2e2mu',
    'prettyName' : '\\text{gg}\\!\\!\\rightarrow \\!\\! \\text{ZZ}\\!\\!\\rightarrow \\!\\! 2e2\\mu',
    'isSignal' : True,
    'color' : 'aliceblue',
    'kFactor' : 1.7,
    'group' : 'ggZZ4l',
}

sampleInfo["GluGluToZZTo2mu2tau_BackgroundOnly_13TeV_MCFM"] = {
    'xsec' : 0.00319364,
    'n' : 642000,
    'sumW' : 650000.,
    'isData' : False,
    'shortName' : 'ggZZ2mu2tau',
    'prettyName' : '\\text{gg}\\!\\!\\rightarrow \\!\\! \\text{ZZ}\\!\\!\\rightarrow \\!\\! 2\\mu2\\tau',
    'isSignal' : True,
    'color' : 'gray',
    'kFactor' : 1.7,
    'group' : 'ggZZ4l', #'ggZZ2l2t',
}

sampleInfo["GluGluToZZTo2e2tau_BackgroundOnly_13TeV_MCFM"] = {
    'xsec' : 0.00319364,
    'n' : 647800,
    'sumW' : 646200.,
    'isData' : False,
    'shortName' : 'ggZZ2e2tau',
    'prettyName' : '\\text{gg}\\!\\!\\rightarrow \\!\\! \\text{ZZ}\\!\\!\\rightarrow \\!\\! 2e2\\tau',
    'isSignal' : True,
    'color' : 'slategray',
    'kFactor' : 1.7,
    'group' : 'ggZZ4l', #'ggZZ2l2t',
}

sampleInfo["GluGluToZZTo4mu_BackgroundOnly_13TeV_MCFM"] = {
    'xsec' : 0.00158582,
    'n' : 338800,
    'sumW' : 338800.,
    'isData' : False,
    'shortName' : 'ggZZ4mu',
    'prettyName' : '\\text{gg}\\!\\!\\rightarrow \\!\\! \\text{ZZ}\\!\\!\\rightarrow \\!\\! 4\\mu',
    'isSignal' : True,
    'color' : 'lightblue',
    'kFactor' : 1.7,
    'group' : 'ggZZ4l',
}

sampleInfo["GluGluToZZTo4e_BackgroundOnly_13TeV_MCFM"] = {
    'xsec' : 0.00158582,
    'n' : 348800,
    'sumW' : 348800.,
    'isData' : False,
    'shortName' : 'ggZZ4e',
    'prettyName' : '\\text{gg}\\!\\!\\rightarrow \\!\\! \\text{ZZ}\\!\\!\\rightarrow \\!\\! 4e',
    'isSignal' : True,
    'color' : 'lightsteelblue',
    'kFactor' : 1.7,
    'group' : 'ggZZ4l',
}

sampleInfo["GluGluToZZTo4tau_BackgroundOnly_13TeV_MCFM"] = {
    'xsec' : 0.00158582,
    'n' : 348800,
    'sumW' : 646200.,
    'isData' : False,
    'shortName' : 'ggZZ4tau',
    'prettyName' : '\\text{gg}\\!\\!\\rightarrow \\!\\! \\text{ZZ}\\!\\!\\rightarrow \\!\\! 4\\tau',
    'isSignal' : True,
    'color' : 'darkgray',
    'kFactor' : 1.7,
    'group' : 'ggZZ4l', #'ggZZ2l2t',
}

sampleInfo["TTJets_TuneCUETP8M1_13TeV-amcatnloFXFX-pythia8"] = {
    'xsec' : 670.3,
    'n' : 42730273,
    'sumW' : 90441818112.,
    'isData' : False,
    'shortName' : 'TTJets',
    'prettyName' : 't \\={t}\\text{+Jets}',
    'isSignal' : False,
    'color' : 'limegreen',
}

sampleInfo["WZTo3LNu_TuneCUETP8M1_13TeV-powheg-pythia8"] = {
    'xsec' : 4.42965,
    'n' : 1925000,
    'sumW' : 1925000.,
    'isData' : False,
    'shortName' : 'WZJets',
    'prettyName' : '\\text{WZ+Jets}',
    'isSignal' : False,
    'color' : 'violet'
}

sampleInfo["ZZTo4L_13TeV_powheg_pythia8"] = {
    'xsec' : 1.256,
    'n' : 6652512,
    'sumW' : 6652512.,
    'isData' : False,
    'shortName' : 'ZZ4l',
    'prettyName' : 'q#bar{q} #rightarrow ZZ, Z#gamma*', 
    'isSignal' : False,
    'color' : '#99ccff', 
    'lineColor' : '#000099',
    'kFactor' : 1.1, 
    'group' : 'qqZZ',
}

sampleInfo["GluGluHToZZTo4L_M125_13TeV_powheg_JHUgen_pythia8"] = {
    'xsec' : 0.01212,
    'n' : 479600,
    'sumW' : 479600.,
    'isData' : False,
    'shortName' : 'ggHZZ4l',
    'prettyName' : 'gg #rightarrow H #rightarrow ZZ',
    'isSignal' : False,
    'color' : '#ffafaf', #'red',
}

sampleInfo['WWZ_TuneCUETP8M1_13TeV-amcatnlo-pythia8'] = {
    'xsec' : 0.1651,
    'isData' : False,
    'isSignal' : False,
    'shortName' : 'WWZ',
    'prettyName' : "WWZ",
    'color' : 'purple',
    'group' : 'VVV',
}

sampleInfo['WZZ_TuneCUETP8M1_13TeV-amcatnlo-pythia8'] = {
    'xsec' : 0.05565,
    'isData' : False,
    'isSignal' : False,
    'shortName' : 'WZZ',
    'prettyName' : "WZZ",
    'color' : 'mediumpurple',
    'group' : 'VVV',
}

sampleInfo['ZZZ_TuneCUETP8M1_13TeV-amcatnlo-pythia8'] = {
    'xsec' : 0.01398,
    'isData' : False,
    'isSignal' : False,
    'shortName' : 'ZZZ',
    'prettyName' : "ZZZ",
    'color' : 'violet',
    'group' : 'VVV',
}

sampleInfo['ZZTo4E_doubleres_powheg_pythia8'] = {
    'xsec' : 0.057643,
    'isData' : False,
    'isSignal' : True,
    'shortName' : 'doubleres4e',
    'prettyName' : '\\text{Double Resonant ZZ} \\!\\! \\rightarrow \\!\\! 4\\text{e}',
    'color' : 'gray',
    'group' : 'doubleres',
}

sampleInfo['ZZTo2E2Mu_doubleres_powheg_pythia8'] = {
    'xsec' : 0.1491,
    'isData' : False,
    'isSignal' : True,
    'shortName' : 'doubleres2e2mu',
    'prettyName' : '\\text{Double Resonant ZZ} \\!\\! \\rightarrow \\!\\! 2\\text{e}2\\mu',
    'color' : 'gray',
    'group' : 'doubleres',
}

sampleInfo['ZZTo4Mu_doubleres_powheg_pythia8'] = {
    'xsec' : 0.057643,
    'isData' : False,
    'isSignal' : True,
    'shortName' : 'doubleres4mu',
    'prettyName' : '\\text{Double Resonant ZZ} \\!\\! \\rightarrow \\!\\! 4\\mu',
    'color' : 'gray',
    'group' : 'doubleres',
}


## 80X MC

sampleInfo["GluGluHToZZTo4L_M450_13TeV_powheg2_JHUgenV698_pythia8"] = {
    'xsec' : 6.771*0.00263,
    'isData' : False,
    'shortName' : 'ggH450',
    'prettyName' : 'H(450)',
    'isSignal' : False,
    'color' : 'indigo', #'#ffafaf', #'red',
}

sampleInfo["GluGluHToZZTo4L_M750_13TeV_powheg2_JHUgenV698_pythia8"] = {
    'xsec' : 0.0018874,
    # 'n' : 479600,
    # 'sumW' : 479600.,
    'isData' : False,
    'shortName' : 'ggH750',
    'prettyName' : 'H(750) #times 10',
    'isSignal' : False,
    'color' : 'purple', #'#ffafaf', #'red',
    'kFactor' : 10.,
}

sampleInfo["GluGluHToZZTo4L_M1000_13TeV_powheg2_JHUgenV698_pythia8"] = {
    'xsec' : 0.1233*0.00318,
    # 'n' : 479600,
    # 'sumW' : 479600.,
    'isData' : False,
    'shortName' : 'ggH1000',
    'prettyName' : 'H(1000) #times 10^{2}',
    'isSignal' : False,
    'color' : 'pink', #'#ffafaf', #'red',
    'kFactor' : 100,
}

sampleInfo["GluGluHToZZTo4L_M1500_13TeV_powheg2_JHUgenV698_pythia8"] = {
    'xsec' : 0.008913*0.003,
    # 'n' : 479600,
    # 'sumW' : 479600.,
    'isData' : False,
    'shortName' : 'ggH1500',
    'prettyName' : 'H(1500) #times 2 #lower[-.3]{#scale[0.5]{#bullet}} 10^{3}',
    'isSignal' : False,
    'color' : 'violet', #'#ffafaf', #'red',
    'kFactor' : 2000,
}

sampleInfo["GluGluHToZZTo4L_M2500_13TeV_powheg2_JHUgenV698_pythia8"] = {
    'xsec' : 0.0001778*.003,
    # 'n' : 479600,
    # 'sumW' : 479600.,
    'isData' : False,
    'shortName' : 'ggH2500',
    'prettyName' : 'H(2500) #times 5 #lower[-.3]{#scale[0.5]{#bullet}} 10^{4}',
    'isSignal' : False,
    'color' : 'magenta', #'#ffafaf', #'red',
    'kFactor' : 50000,
}

sampleInfo["GluGluHToZZTo4L_M125_13TeV_powheg2_JHUgenV6_pythia8"] = {
    'xsec' : 0.01212,
    # 'n' : 479600,
    # 'sumW' : 479600.,
    'isData' : False,
    'shortName' : 'ggHZZ4l',
    'prettyName' : 'gg #rightarrow H #rightarrow ZZ',#'\\text{gg}\\!\\!\\rightarrow \\!\\! \\text{H} \\!\\!\\rightarrow \\!\\! \\text{ZZ}',#\\!\\!\\rightarrow \\!\\! 4\\ell',
    'isSignal' : True,
    'color' : '#ffb2b2', #'red',
    'lineColor' : 'cc0000',
    #'kFactor' : 1.3,
}

sampleInfo["GluGluToContinToZZTo4e_13TeV_MCFM701_pythia8"] = {
    'xsec' : 0.001586,
    #'n' : 348800,
    #'sumW' : 348800.,
    'isData' : False,
    'shortName' : 'ggZZ4e',
    'prettyName' : '\\text{gg}\\!\\!\\rightarrow \\!\\! \\text{ZZ}\\!\\!\\rightarrow \\!\\! 4e',
    'isSignal' : False,
    'color' : 'lightsteelblue',
    'kFactor' : 1.7,
    'group' : 'ggZZ4l',
}

sampleInfo["GluGluToContinToZZTo4mu_13TeV_MCFM701_pythia8"] = {
    'xsec' : 0.001586,
    #'n' : 348800,
    #'sumW' : 348800.,
    'isData' : False,
    'shortName' : 'ggZZ4mu',
    'prettyName' : '\\text{gg}\\!\\!\\rightarrow \\!\\! \\text{ZZ}\\!\\!\\rightarrow \\!\\! 4\\mu',
    'isSignal' : False,
    'color' : 'lightsteelblue',
    'kFactor' : 1.7,
    'group' : 'ggZZ4l',
}

sampleInfo["GluGluToContinToZZTo4tau_13TeV_MCFM701_pythia8"] = {
    'xsec' : 0.00158582,
    # 'n' : 348800,
    # 'sumW' : 646200.,
    'isData' : False,
    'shortName' : 'ggZZ4tau',
    'prettyName' : '\\text{gg}\\!\\!\\rightarrow \\!\\! \\text{ZZ}\\!\\!\\rightarrow \\!\\! 4\\tau',
    'isSignal' : False,
    'color' : 'darkgray',
    'kFactor' : 1.7,
    'group' : 'ggZZ4l', #'ggZZ2l2t',
}

sampleInfo["GluGluToContinToZZTo2e2mu_13TeV_MCFM701_pythia8"] = {
    'xsec' : 0.00319364,
    # 'n' : 649600,
    # 'sumW' : 648800.,
    'isData' : False,
    'shortName' : 'ggZZ2e2mu',
    'prettyName' : '\\text{gg}\\!\\!\\rightarrow \\!\\! \\text{ZZ}\\!\\!\\rightarrow \\!\\! 2e2\\mu',
    'isSignal' : False,
    'color' : 'aliceblue',
    'kFactor' : 1.7,
    'group' : 'ggZZ4l',
}

sampleInfo["GluGluToContinToZZTo2e2tau_13TeV_MCFM701_pythia8"] = {
    'xsec' : 0.00319364,
    # 'n' : 649600,
    # 'sumW' : 648800.,
    'isData' : False,
    'shortName' : 'ggZZ2e2tau',
    'prettyName' : '\\text{gg}\\!\\!\\rightarrow \\!\\! \\text{ZZ}\\!\\!\\rightarrow \\!\\! 2e2\\tau',
    'isSignal' : False,
    'color' : 'aliceblue',
    'kFactor' : 1.7,
    'group' : 'ggZZ4l',
}

sampleInfo["GluGluToContinToZZTo2mu2tau_13TeV_MCFM701_pythia8"] = {
    'xsec' : 0.00319364,
    # 'n' : 649600,
    # 'sumW' : 648800.,
    'isData' : False,
    'shortName' : 'ggZZ2mu2tau',
    'prettyName' : '\\text{gg}\\!\\!\\rightarrow \\!\\! \\text{ZZ}\\!\\!\\rightarrow \\!\\! 2\\mu 2\\tau',
    'isSignal' : False,
    'color' : 'aliceblue',
    'kFactor' : 1.7,
    'group' : 'ggZZ4l',
}

sampleInfo["Z+X"] = {
    'isData' : False,
    'shortName' : 'Z+X',
    'prettyName' : 'Z+X',
    'isSignal' : False,
    'color' : '#669966',
    'lineColor' : '#003300',
}





sampleGroups = {}

sampleGroups['ggZZ4l'] = {
    'isSignal' : False,
    'prettyName' : 'gg #rightarrow ZZ, Z#gamma*', 
    'color' : "#4b78ff",#"#3366ff",
    'lineColor' : "#000099",
}

sampleGroups['ggZZ2l2t'] = {
    'isSignal' : False,
    'prettyName' : '\\text{gg}\\!\\!\\rightarrow \\!\\! \\text{ZZ}\\!\\!\\rightarrow \\!\\! 2\\ell 2\\tau',
    'color' : "darkgray",
}

sampleGroups['VVV'] = {
    'isSignal' : False,
    'prettyName' : '\\text{VVV}',
    'color' : "purple",
}

sampleGroups['DYJets'] = {
    'isSignal' : False,
    'prettyName' : '\\text{Z}/\\gamma* \\text{ + jets}',
    'color' : '#669966',
}

sampleGroups['qqZZ'] = {
    'isSignal' : False,
    'prettyName' : 'q#bar{q} #rightarrow ZZ, Z#gamma*', 
    'color' : '#99ccff',
    'lineColor' : '#000099',
}

sampleGroups['doubleres'] = {
    'isSignal' : True,
    'prettyName' : '\\text{Double Resonant}',
    'color' : 'gray',
}

