'''

From a ZZAnalyzer summary text file, make histograms where each bin is the remaining events after a given cut.

Author: Nate Woods, U. Wisconsin

'''

import ROOT
import argparse
import glob
import os
from ZZMetadata import sampleInfo
import errno


assert os.environ["zza"], "Run setup.sh before making cut flow summary plots"

def makeDirectory(path):
    '''
    Make a directory, don't crash
    '''
    try:
        os.makedirs(path)
    except OSError as e:
        if e.errno == errno.EEXIST and os.path.isdir(path):
            pass
        else:
            raise


parser = argparse.ArgumentParser(description='Make histograms whose bins are the number of events remaining after each cut in a flow')

parser.add_argument('inputs', type=str, nargs=1,
                    help='Comma-separated list of summary text file location(s). May contain wildcards.')
parser.add_argument('outdir', type=str, nargs='?', default='ZZA_NORMAL',
                    help='Location to place output histograms')
parser.add_argument('intLumi', type=float, nargs='?', default=19710.,
                    help='Integrated luminosity, in inverse picobarns')
parser.add_argument('--logy', action="store_true", help='Plot with log scale on y axis.')
parser.add_argument('--saveHists', action="store_true", help='Save the underlying histograms in addition to making an image')

args = parser.parse_args()

infiles = []
rawInputs = args.inputs[0].split(',')
for raw in rawInputs:
    print raw
    if raw[0] == '.':
        inputs = os.environ["zza"]+raw[1:].replace("$zza",os.environ["zza"])
    else:
        inputs = raw.replace("$zza", os.environ["zza"])
    if inputs.endswith('.txt'):
        if glob.glob(inputs):
            infiles += glob.glob(inputs)
    else:
        if glob.glob(path+'*.txt'):
            infiles += glob.glob(inputs+'*.txt')

# remove duplicates, just in case
infiles = list(set(infiles))

if args.outdir == 'ZZA_NORMAL':
    outdir = os.environ["zza"] + '/plots/cutSummary'
else:
    # remove trailing slash
    if args.outdir.endswith('/'):
        outdir = args.outdir[:-1]
    else:
        outdir = args.outdir

if args.saveHists:
    saveFile = ROOT.TFile("%s/cutSummary_hists.root"%outdir, "RECREATE")

makeDirectory(outdir)

# Make colors the same as the old plot
colors = {
    "GluGluToHToZZTo4L_M-125_13TeV-powheg-pythia6_Spring14miniaod_PU20bx25" : ROOT.EColor.kRed,
    "ZZTo4L_Tune4C_13TeV-powheg-pythia8_Spring14miniaod_PU20bx25" : ROOT.EColor.kViolet,
    "WZJetsTo3LNu_Tune4C_13TeV-madgraph-tauola_Spring14miniaod_PU20bx25" : ROOT.EColor.kCyan,
    "VBF_HToZZTo4L_M-125_13TeV-powheg-pythia6_Spring14miniaod_PU20bx25" : ROOT.EColor.kPink+10,
    "TTJets_MSDecaysCKM_central_Tune4C_13TeV-madgraph-tauola_Spring14miniaod_PU20bx25" : ROOT.EColor.kGreen,
    "DYJetsToLL_M-50_13TeV-madgraph-pythia8-tauola_v2_Spring14miniaod_PU20bx25" : ROOT.EColor.kAzure+7,
    "ZZTo2e2mu_8TeV-powheg-pythia6_Summer12DR53X_PUS10" : ROOT.EColor.kMagenta-4,
    "ZZTo4mu_8TeV-powheg-pythia6_Summer12DR53X_PUS10"   : ROOT.EColor.kMagenta-4,
    "ZZTo4e_8TeV-powheg-pythia6_Summer12DR53X_PUS10"    : ROOT.EColor.kMagenta-4,
    "DYJetsToLL_M-50_TuneZ2Star_8TeV-madgraph-tarball_Summer12DR53X_PUS10" : ROOT.EColor.kBlue,
    "WZJetsTo3LNu_TuneZ2_8TeV-madgraph-tauola_Summer12DR53X_PUS10": ROOT.EColor.kTeal-1,
}

markers = {
    "GluGluToHToZZTo4L_M-125_13TeV-powheg-pythia6_Spring14miniaod_PU20bx25" : 21,
    "ZZTo4L_Tune4C_13TeV-powheg-pythia8_Spring14miniaod_PU20bx25" : 21, 
    "WZJetsTo3LNu_Tune4C_13TeV-madgraph-tauola_Spring14miniaod_PU20bx25" : 21,
    "VBF_HToZZTo4L_M-125_13TeV-powheg-pythia6_Spring14miniaod_PU20bx25" : 21, 
    "TTJets_MSDecaysCKM_central_Tune4C_13TeV-madgraph-tauola_Spring14miniaod_PU20bx25" : 21, 
    "DYJetsToLL_M-50_13TeV-madgraph-pythia8-tauola_v2_Spring14miniaod_PU20bx25" : 21, 
    "ZZTo2e2mu_8TeV-powheg-pythia6_Summer12DR53X_PUS10" : 4, 
    "ZZTo4mu_8TeV-powheg-pythia6_Summer12DR53X_PUS10" : 4,
    "ZZTo4e_8TeV-powheg-pythia6_Summer12DR53X_PUS10" : 4, 
    "DYJetsToLL_M-50_TuneZ2Star_8TeV-madgraph-tarball_Summer12DR53X_PUS10" : 4,
    "WZJetsTo3LNu_TuneZ2_8TeV-madgraph-tauola_Summer12DR53X_PUS10": 4, 
}

histos = {}
numbers = {}
cutNames = {}
cutCountMax = -1

# Loop over inputs, making one histogram for each channel in each input
for infile in infiles:
    sample = infile.replace('_cutflow','').replace('.txt','').split('/')[-1]

    with open(infile, 'r') as f:
        channel = ''
        cutCount = 0
        # loop over lines
        for line in f:
            words = line.split()
#             print "%d (%d): %s (%d)"%(cutCount, cutCountMax, " ".join(words), len(words))
            if len(words) == 1:
                # Make sure the previous channel had the right number of cuts
                if cutCount != 0:
                    if cutCountMax == -1:
                        cutCountMax = cutCount
                    else:
                        assert cutCount == cutCountMax, "Wrong number of cuts (%d instead of %d) in %s %s!"%(cutCount, 
                                                                                                             cutCountMax, sample, channel)
                
                cutCount = 0
                channel = words[0].replace(':','')
                if channel not in numbers:
                    numbers[channel] = {}
                if sample not in numbers[channel]:
                    numbers[channel][sample] = {}
            if len(words) == 2:
                # remove colon when finding cut name
                cut = words[0][:-1]
                # ignore some cuts, rename others
                if cut == "Total" or cut == "Overlap" or cut == "Lepton1Pt":
                    continue

                cutCount += 1

                # save the name of the cut, but only if this is the first time through
                if cutCount > cutCountMax:
                    if cut == "Combinatorics":
                        cut = "Init."
                    elif cut == "Lepton2Pt":
                        cut = "Lepton Pt"
                    elif cut == "Z1Mass":
                        cut = "Z1 Mass"
                    elif cut == "Z2Mass":
                        cut = "Z2 Mass"
                    elif cut == "LeptonPairMass":
                        cut = "2l Mass"
                    elif cut == "4lMass":
                        cut = "4l Mass"

                    cutNames[cutCount] = cut

                numbers[channel][sample][cutCount] = int(words[1])


for channel in numbers:
    if channel not in histos:
        histos[channel] = {}
    for sample in numbers[channel]:
        histos[channel][sample] = ROOT.TH1F("hCutFlow%s%s"%(sample,channel), "Cut flow summary %s"%channel, cutCountMax, 0, cutCountMax)
        for nCut, n in numbers[channel][sample].iteritems():
            histos[channel][sample].SetBinContent(nCut, float(n))
            histos[channel][sample].GetXaxis().SetBinLabel(nCut, cutNames[nCut])
            histos[channel][sample].SetMarkerStyle(markers[sample])
            histos[channel][sample].SetMarkerColor(colors[sample])
            histos[channel][sample].SetMarkerSize(2)
            histos[channel][sample].SetLineColor(colors[sample])
            if channel == "eeee":
                evType = "4e"
            elif channel == "eemm":
                evType = "2e2#mu"
            elif channel == "mmmm":
                evType = "4#mu"
            else:
                evType = channel
            histos[channel][sample].SetTitle("Cut Flow Summary %s "%evType)
            histos[channel][sample].GetYaxis().SetTitle("%s Events"%evType)
            histos[channel][sample].GetYaxis().SetTitleOffset(1.3)
            
        # Make sure the errors get scaled correctly
        histos[channel][sample].Sumw2()
        # Scale to cross section and lumi
        histos[channel][sample].Scale(sampleInfo[sample]['xsec'] * args.intLumi / sampleInfo[sample]['n'])

    # Make sure the viewing range is big enough to see all the histograms
    maxMax = max([h.GetMaximum() for s, h in histos[channel].iteritems()])
    if args.logy:
        maxMax *= 3
    else:
        maxMax *= 1.2
    for sample in histos[channel]:
        histos[channel][sample].SetMaximum(maxMax)

# don't draw in a graphical window right now
ROOT.gROOT.SetBatch(ROOT.kTRUE)
# don't look like shit
ROOT.gStyle.SetOptStat(0)
ROOT.gROOT.ForceStyle()

c = ROOT.TCanvas("foo", "foo", 1200, 1200)
if args.logy:
    c.SetLogy()

for channel in numbers:
    leg = ROOT.TLegend(0.65, 0.55, 0.9, 0.85)
    leg.SetFillColor(ROOT.EColor.kWhite)
    leg.SetTextSize(0.02)

    drawnYet = False
    for sample in histos[channel]: 
#                    ['WZJetsTo3LNu_TuneZ2_8TeV-madgraph-tauola_Summer12DR53X_PUS10',
#                    'WZJetsTo3LNu_Tune4C_13TeV-madgraph-tauola_Spring14miniaod_PU20bx25',
#                    'DYJetsToLL_M-50_TuneZ2Star_8TeV-madgraph-tarball_Summer12DR53X_PUS10',
#                    'DYJetsToLL_M-50_13TeV-madgraph-pythia8-tauola_v2_Spring14miniaod_PU20bx25',
#                    'ZZTo2e2mu_8TeV-powheg-pythia6_Summer12DR53X_PUS10',
#                    'ZZTo4e_8TeV-powheg-pythia6_Summer12DR53X_PUS10',
#                    'ZZTo4mu_8TeV-powheg-pythia6_Summer12DR53X_PUS10',
#                    'ZZTo4L_Tune4C_13TeV-powheg-pythia8_Spring14miniaod_PU20bx25',
#                    ]:
        if '8TeV' in sample and 'ZZ' in sample:
            if channel == 'mmmm' and ('4e' in sample or '2e2mu' in sample):
                continue
            if channel == 'eemm' and ('4e' in sample or '4mu' in sample):
                continue
            if channel == 'eeee' and ('4mu' in sample or '2e2m' in sample):
                continue

        if '8TeV' in sample:
            energy = '8TeV'
        else:
            energy = '13TeV'

        leg.AddEntry(histos[channel][sample], "%s %s"%(sampleInfo[sample]["shortName"],energy), "LPE")
        
        if not drawnYet:
            histos[channel][sample].Draw("e")
            drawnYet = True
        else:
            histos[channel][sample].Draw("esame")

    leg.Draw("same")
    
    c.Print("%s/cutSummary_%s.png"%(outdir, channel))

if args.saveHists:
    saveFile.Write()
