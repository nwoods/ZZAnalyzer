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
from ZZPlotStyle import ZZPlotStyle

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
parser.add_argument('--stacks', action='store_true', 
                    help='Plot two stacks (signal overlayed on top of background) instead of plotting samples separately as points.')

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

makeDirectory(outdir)

# Look decent
style = ZZPlotStyle()

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
                if cut == "Total" or cut == "Overlap" or cut == "Lepton1Pt" or cut == "4lMass":
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

            if args.stacks:
                histos[channel][sample].SetLineWidth(4)
                if not sampleInfo[sample]['isData'] and sampleInfo[sample]['isSignal']:
                    histos[channel][sample].SetFillColorAlpha(sampleInfo[sample]['color'], 0.4)
                    histos[channel][sample].SetLineColor(sampleInfo[sample]['color'])
                elif not sampleInfo[sample]['isData'] and not sampleInfo[sample]['isSignal']:
                    histos[channel][sample].SetFillStyle(1001)
                    histos[channel][sample].SetFillColor(sampleInfo[sample]['color'])
                    histos[channel][sample].SetLineColor(ROOT.EColor.kBlack)
            else:
                histos[channel][sample].SetMarkerStyle(4)
                histos[channel][sample].SetMarkerColor(sampleInfo[sample]['color'])
                histos[channel][sample].SetMarkerSize(2)
                histos[channel][sample].SetLineColor(sampleInfo[sample]['color'])
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
            
        # Make sure the errors get scaled correctly
        histos[channel][sample].Sumw2()
        # Scale to cross section and lumi
        histos[channel][sample].Scale(sampleInfo[sample]['xsec'] * args.intLumi / sampleInfo[sample]['n'])

    # Make sure the viewing range is big enough to see all the histograms
    if not args.stacks:
        maxMax = max([h.GetMaximum() for s, h in histos[channel].iteritems()])
        if args.logy:
            maxMax *= 3
        else:
            maxMax *= 1.2
        for sample in histos[channel]:
            histos[channel][sample].SetMaximum(maxMax)

# don't draw in a graphical window right now
ROOT.gROOT.SetBatch(ROOT.kTRUE)

c = ROOT.TCanvas("foo", "foo")#, 1200, 1200)
if args.logy:
    c.SetLogy()

for channel in numbers:
    leg = ROOT.TLegend(0.65, 0.6, 0.9, 0.9)
    leg.SetTextSize(0.03)

    channelName = '4l'
    if channel == 'eeee':
        channelName = '4e'
    elif channel == 'eemm':
        channelName = '2e2#mu'
    elif channel == 'mmmm':
        channelName = '4#mu'

    allSamples = [s for s in histos[channel]]
    if args.stacks:
        # sort histograms by size of the last bin so they stack sensibly. Break ties by putting samples with smaller maxima on the bottom
        allSamples.sort(key=lambda s: histos[channel][s].GetMinimum() + histos[channel][s].GetMaximum()/10000000.)
        # Make stacks
        stackB = ROOT.THStack('background', "ZZ#rightarrow%s Cut Flow Summary"%channelName)
        stackS = ROOT.THStack('signal', "ZZ#rightarrow%s Cut Flow Summary"%channelName)

    drawnYet = False
    sigs = []
    bkgs = []
    for sample in allSamples:
        if sampleInfo[sample]['isData']:
            continue
        if args.stacks:
            if sampleInfo[sample]['isSignal']:
                stackS.Add(histos[channel][sample])
                sigs.append(sample)
            else:
                stackB.Add(histos[channel][sample])
                bkgs.append(sample)
        else:
            leg.AddEntry(histos[channel][sample], sampleInfo[sample]["shortName"], "LPE")
            if not drawnYet:
                histos[channel][sample].Draw("e")
                drawnYet = True
            else:
                histos[channel][sample].Draw("esame")

    if args.stacks:
        if args.logy:
            minmin = 999999999.
            for s in allSamples:
                if histos[channel][s].GetMinimum() > 0 and histos[channel][s].GetMinimum() < minmin:
                    minmin = histos[channel][s].GetMinimum()
            stackB.SetMinimum(0.5 * minmin)
        # Have to draw before we can get axes, for some reason
        stackB.Draw()
        stackB.GetYaxis().SetTitle("%s Events"%channelName)
        for i in range(stackB.GetHistogram().GetNbinsX()):
            stackB.GetXaxis().SetBinLabel(i+1, histos[channel][allSamples[0]].GetXaxis().GetBinLabel(i+1))
        stackB.GetXaxis().SetLabelSize(0.04)
        c.SetRightMargin(0.04)
        stackB.Draw("HIST")
        stackS.Draw("HISTSAMENOCLEAR")
        for s in reversed(sigs+bkgs):
            leg.AddEntry(histos[channel][s], sampleInfo[s]["shortName"], "F")

    ROOT.gStyle.SetLineWidth(3)

    leg.Draw("same")

    style.setPrelimStyle(c)
    
    c.Print("%s/cutSummary_%s.png"%(outdir, channel))
    c.Print("%s/cutSummary_%s.pdf"%(outdir, channel))

