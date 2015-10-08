'''

Metadata needed for plotting samples relevant to 4l

Preferred sample name format is datasetFromDAS_campaign_PUbxScenario[_dataTier if important -- probably won't be]

Info items (key):
    Cross section (xsec)
    Number of events in original dataset before ntuplization (n)
    Boolean for data (true) or Monte Carlo (isData)
    Boolean for whether the sample is signal or background (isSignal)
    Short name for sample (shortName)
    TeX formatted name for plot legends, etc. (prettyName)
    ROOT color for plotting (color)

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
    'color' : 'forestgreen',
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
    'prettyName' : '\\text{ZZ}\\!\\!\\rightarrow \\!\\! 4\\ell',
    'isSignal' : True,
    'color' : 'skyblue',
}

sampleInfo["GluGluHToZZTo4L_M125_13TeV_powheg_JHUgen_pythia8"] = {
    'xsec' : 0.01212,
    'n' : 479600,
    'sumW' : 479600.,
    'isData' : False,
    'shortName' : 'ggHZZ4l',
    'prettyName' : '\\text{gg}\\!\\!\\rightarrow \\!\\! \\text{H} \\!\\!\\rightarrow \\!\\! \\text{ZZ}\\!\\!\\rightarrow \\!\\! 4\\ell',
    'isSignal' : False,
    'color' : 'red',
}

