'''

Metadata needed for plotting 4l Monte Carlo (and associated backgrounds)

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

from rootpy.ROOT import EColor

sampleInfo = {}

sampleInfo["DYJetsToLL_M-50_13TeV-madgraph-pythia8-tauola_v2_Spring14miniaod_PU20bx25"] = {
    'xsec' : 6025.2,
    'n' : 43630561,
    'isData' : False,
    'shortName' : 'DYJets',
    'prettyName' : 'DY+Jets',
    'isSignal' : False,
    'color' : EColor.kAzure+7,
}
sampleInfo["VBF_HToZZTo4L_M-125_13TeV-powheg-pythia6_Spring14miniaod_PU20bx25"] = {
    'xsec' : 3.72 * 0.000294,
    'n' : 193738,
    'isData' : False,
    'shortName' : 'VBFHZZ4l',
    'prettyName' : '\\text{VBF H}\\!\\!\\rightarrow \\!\\! \\text{ZZ} \\!\\!\\rightarrow \\!\\! 4\\ell',
    'isSignal' : True,
    'color' : EColor.kOrange+7,
}
sampleInfo["GluGluToHToZZTo4L_M-125_13TeV-powheg-pythia6_Spring14miniaod_PU20bx25"] = {
    'xsec' : 43.62 * 0.000294,
    'n' : 493461,
    'isData' : False,
    'shortName' : 'ggHZZ4l',
    'prettyName' : '\\text{gg}\\!\\! \\rightarrow \\!\\! \\text{H} \\!\\! \\rightarrow \\!\\! \\text{ZZ} \\!\\! \\rightarrow \\!\\! 4\\ell',
    'isSignal' : True,
    'color' : EColor.kRed,
}
sampleInfo["TTJets_MSDecaysCKM_central_Tune4C_13TeV-madgraph-tauola_Spring14miniaod_PU20bx25"] = {
    'xsec' : 424.5,
    'n' : 25474122,
    'isData' : False,
    'shortName' : 'TTJets',
    'prettyName' : 't \\={t}\\text{+Jets}',
    'isSignal' : False,
    'color' : EColor.kGreen,
}
sampleInfo["ZZTo4L_Tune4C_13TeV-powheg-pythia8_Spring14miniaod_PU20bx25"] = {
    'xsec' : 1.2,
    'n' : 1958600,
    'isData' : False,
    'shortName' : 'ZZ4l',
    'prettyName' : '\\text{ZZ}\\!\\!\\rightarrow \\!\\! 4\\ell',
    'isSignal' : True,
    'color' : EColor.kViolet,
}
sampleInfo["WZJetsTo3LNu_Tune4C_13TeV-madgraph-tauola_Spring14miniaod_PU20bx25"] = {
    'xsec' : 1.634,
    'n' : 240363,
    'isData' : False,
    'shortName' : 'WZJets',
    'prettyName' : '\\text{WZ+Jets}',
    'isSignal' : False,
    'color' : EColor.kCyan,
}

sampleInfo["DYJetsToLL_M-50_13TeV-madgraph-pythia8_PHYS14DR_PU20bx25"] = {
    'xsec' : 6025.2,
    'n' : 2829164,
    'isData' : False,
    'shortName' : 'DYJets',
    'prettyName' : '\\text{DY+Jets}',
    'isSignal' : False,
    'color' : EColor.kGreen+3,
}
sampleInfo["GluGluToHToZZTo4L_M-125_13TeV-powheg-pythia6_PHYS14DR_PU20bx25"] = {
    'xsec' : 43.62 * 0.000294,
    'n' : 204684,
    'isData' : False,
    'shortName' : 'ggHZZ4l',
    'prettyName' : '\\text{gg}\\!\\! \\rightarrow \\!\\! \\text{H} \\!\\! \\rightarrow \\!\\! \\text{ZZ} \\!\\! \\rightarrow \\!\\! 4\\ell',
    'isSignal' : True,
    'color' : EColor.kRed,
}
sampleInfo["TTJets_MSDecaysCKM_central_Tune4C_13TeV-madgraph-tauola_PHYS14DR_PU20bx25"] = {
    'xsec' : 424.5,
    'n' : 25446993,
    'isData' : False,
    'shortName' : 'TTJets',
    'prettyName' : 't \\={t}\\text{+Jets}',
    'isSignal' : False,
    'color' : EColor.kGreen,
}
sampleInfo["ZZTo4L_Tune4C_13TeV-powheg-pythia8_PHYS14DR_PU20bx25"] = {
    'xsec' : 1.2,
    'n' : 1958600,
    'isData' : False,
    'shortName' : 'ZZ4l',
    'prettyName' : '\\text{ZZ}\\!\\!\\rightarrow \\!\\! 4\\ell',
    'isSignal' : True,
    'color' : EColor.kAzure-9,
}
sampleInfo["WZJetsTo3LNu_Tune4C_13TeV-madgraph-tauola_PHYS14DR_PU20bx25"] = {
    'xsec' : 1.634,
    'n' : 237484,
    'isData' : False,
    'shortName' : 'WZJets',
    'prettyName' : '\\text{WZ+Jets}',
    'isSignal' : False,
    'color' : EColor.kViolet,
}

sampleInfo["WZJetsTo3LNu_TuneZ2_8TeV-madgraph-tauola_Summer12DR53X_PUS10"] = {
    'xsec' : 0.8674,
    'n' : 1900000,
    'isData' : False,
    'shortName' : 'WZJets',
    'prettyName' : '\\text{WZ+Jets}',
    'isSignal' : False,
    'color' : EColor.kTeal-1,
}
sampleInfo["ZZTo4e_8TeV-powheg-pythia6_Summer12DR53X_PUS10"] = {
    'xsec' : 0.07691,
    'n' : 1500000,
    'isData' : False,
    'shortName' : 'ZZ4e',
    'prettyName' : '\\text{ZZ}\\!\\!\\rightarrow \\!\\! 4\\text{e}',
    'isSignal' : True,
    'color' : EColor.kMagenta-4,
}
sampleInfo["ZZTo4mu_8TeV-powheg-pythia6_Summer12DR53X_PUS10"] = {
    'xsec' : 0.07691,
    'n' : 1500000,
    'isData' : False,
    'shortName' : 'ZZ4mu',
    'prettyName' : '\\text{ZZ}\\!\\!\\rightarrow \\!\\! 4\\mu',
    'isSignal' : True,
    'color' : EColor.kMagenta-4,
}
sampleInfo["ZZTo2e2mu_8TeV-powheg-pythia6_Summer12DR53X_PUS10"] = {
    'xsec' : 0.1767,
    'n' : 1500000,
    'isData' : False,
    'shortName' : 'ZZ2e2mu',
    'prettyName' : '\\text{ZZ}\\!\\!\\rightarrow \\!\\! 2e2\\mu',
    'isSignal' : True,
    'color' : EColor.kMagenta-4,
}
sampleInfo["DYJetsToLL_M-50_TuneZ2Star_8TeV-madgraph-tarball_Summer12DR53X_PUS10"] = {
    'xsec' : 2950.0,
    'n' : 500000,
    'isData' : False,
    'shortName' : 'DYJets',
    'prettyName' : '\\text{DY+Jets}',
    'isSignal' : False,
    'color' : EColor.kBlue,
}

sampleInfo["HZZSync"] = {
    'xsec' : 43.62 * 0.000294,
    'n' : 10400,
    'isData' : False,
    'shortName' : 'HZZSync',
    'prettyName' : '\\text{gg}\\!\\! \\rightarrow \\!\\! \\text{H} \\!\\! \\rightarrow \\!\\! \\text{ZZ} \\!\\! \\rightarrow \\!\\! 4\\ell',
    'isSignal' : True,
    'color' : EColor.kRed,
}
sampleInfo["TTBar8TeV"] = {
    'xsec' : 53.2,
    'n' : 30000000,
    'isData' : False,
    'shortName' : 'TTBar',
    'prettyName' : 't \\={t}\\text{+Jets}',
    'isSignal' : False,
    'color' : EColor.kGreen,
}
sampleInfo["ZZJetsTo4L_TuneZ2star_8TeV-madgraph-tauola_Summer12DR53X_PU10"] = {
    'n' : 5000000,
    'isData' : False,
    'isSignal' : True,
    'color' : EColor.kAzure-9,
    'xsec' : 0.1296,
    'shortName' : 'ZZ4l8TeV',
    'prettyName' : '\\text{ZZ}\\!\\!\\rightarrow \\!\\! 4\\ell',    
}
