'''

Take histograms of true pileup distribution (with and without scalings for 
use in systematics calculations) and combine them with the pileup distribution
used in MC production to make and save histograms to use in PU reweighting.

Author: Nate Woods, U. Wisconsin

'''


from rootpy.io import root_open
from rootpy.plotting import Hist
import os
import imp

assert os.environ["zza"], "Run setup.sh before running analysis"


#### 
# Change this if/when MC changes
####
puDistName = "pileupDist_2015mix25ns_startup"

####
# Inputs and outputs (change as necessary)
####
puDataSetID = "13Nov2015" # identifier for all PU data root files
histname = 'pileup'
baseFileName = os.path.join(os.environ["zza"], 'data/pileupReweighting', "PileUpData_%s{0}.root"%puDataSetID)
scaleSuffixes = {
    '' : '', # no scaling
    'ScaleUp' : '_up',
    'ScaleDown' : '_down',
}
outputFile = os.path.join(os.environ["zza"], 'data/pileupReweighting', "PUScaleFactors_{0}.root".format(puDataSetID))


# Get PU distribution used in simulation
puDistPath = os.environ["zza"]+"/data/pileupReweighting"
puDistFile, puDistPathName, puDistDesc = imp.find_module(puDistName, [puDistPath])
assert puDistFile, 'PU distribution %s does not exist in %s'%(puDistName, puDistPath)
puDistMod = imp.load_module(puDistName, puDistFile, puDistPathName, puDistDesc)
puDist = getattr(puDistMod, puDistName)

puDistMC = Hist(len(puDist), 0., 1.*len(puDist))
for i,v in zip(range(1,puDistMC.nbins()+1), puDist):
    puDistMC[i].value = v

puDistDataFiles = {}
puDistData = {}
for scale, suffix in scaleSuffixes.iteritems():
    puDistDataFiles[scale] = root_open(baseFileName.format(suffix))
    puDistData[scale] = puDistDataFiles[scale].Get(histname).clone()
    puDistData[scale].scale(1./puDistData[scale].Integral())

scaleHists = {}
with root_open(outputFile, "recreate") as f:
    for scale, distData in puDistData.iteritems():
        nbins = min(puDistMC.nbins(), distData.nbins())
        name = "puScaleFactor"
        if scale:
            name += "_"+scale
        scaleHists[scale] = Hist(nbins, 0., 1.*nbins, name=name)
        for i in range(1,nbins+1):
            scaleHists[scale][i].value = distData[i].value / puDistMC[i].value
        scaleHists[scale].Write()
