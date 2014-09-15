'''

Metadata needed for plotting 4l Monte Carlo (and associated backgrounds)

Preferred sample name format is datasetFromDAS_campaign_PUbxScenario[_dataTier if important -- probably won't be]

Info items (key):
    Cross section (xsec)
    Number of events in original dataset (before ntuplization)
    Boolean for data (true) or Monte Carlo (isData)
    Short name for plot legends, etc. (shortName)

Author: Nate Woods, U. Wisconsin

'''

sampleInfo = {}

sampleInfo["DYJetsToLL_M-50_13TeV-madgraph-pythia8-tauola_v2_Spring14miniaod_PU20bx25"] = {
    'xsec' : 6025.2,
    'n' : 43630561,
    'isData' : False,
    'shortName' : 'DYJets',
    'isSignal' : False,
}
sampleInfo["VBF_HToZZTo4L_M-125_13TeV-powheg-pythia6_Spring14miniaod_PU20bx25"] = {
    'xsec' : 3.72 * 0.000294,
    'n' : 193738,
    'isData' : False,
    'shortName' : 'VBFH->ZZ->4l',
    'isSignal' : True,
}
sampleInfo["GluGluToHToZZTo4L_M-125_13TeV-powheg-pythia6_Spring14miniaod_PU20bx25"] = {
    'xsec' : 43.62 * 0.000294,
    'n' : 493461,
    'isData' : False,
    'shortName' : 'ggH->ZZ->4l',
    'isSignal' : True,
}
sampleInfo["TTJets_MSDecaysCKM_central_Tune4C_13TeV-madgraph-tauola_Spring14miniaod_PU20bx25"] = {
    'xsec' : 424.5,
    'n' : 25474122,
    'isData' : False,
    'shortName' : 'TTJets',
    'isSignal' : False,
}
sampleInfo["ZZTo4L_Tune4C_13TeV-powheg-pythia8_Spring14miniaod_PU20bx25"] = {
    'xsec' : 1.2,
    'n' : 1958600,
    'isData' : False,
    'shortName' : 'ZZ->4l',
    'isSignal' : True,
}
