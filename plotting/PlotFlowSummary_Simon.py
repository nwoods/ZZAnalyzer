'''

From a ZZAnalyzer summary text file, make histograms where each bin is the remaining events after a given cut.

Author: Nate Woods, U. Wisconsin

'''

import rootpy.ROOT as ROOT
from rootpy.plotting import Hist, Canvas
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
parser.add_argument('--norm', action='store_true', 
                    help='Nomalize all samples to the total number of events.')
parser.add_argument('--diff', action='store_true', 
                    help='Plot fraction of events kept from one cut to the next. --norm implied.')


args = parser.parse_args()

assert not (args.diff and args.stacks), "You can't stack cut differences!"

infiles = []
rawInputs = args.inputs[0].split(',')
for raw in rawInputs:
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
            words = line.split(":")
#             print "%d (%d): %s (%d)"%(cutCount, cutCountMax, " ".join(words), len(words))
            if len(words) == 2:
                # Make sure the previous channel had the right number of cuts
                if cutCount != 0:
                    if cutCountMax == -1:
                        cutCountMax = cutCount
                    else:
                        assert cutCount == cutCountMax, "Wrong number of cuts (%d instead of %d) in %s %s!"%(cutCount, 
                                                                                                             cutCountMax, sample, channel)
                
                cutCount = 0
                channel = words[0].replace(' ','')
                if channel not in numbers:
                    numbers[channel] = {}
                if sample not in numbers[channel]:
                    numbers[channel][sample] = {}
            if len(words) == 3:
                # Remove whitespace
                cut = words[0].replace(' ','')
                # ignore some cuts, rename others
                if cut == "TotalRows" or cut == "Overlap" or cut == "Lepton1Pt" or cut == "4lMass":
                    continue
                if "ID" in cut or "Kinematics" in cut or cut == "Z1PV" or cut == "Z1SIP" or cut == "Z1Mass" \
                   or cut == "Z2Mass" or "Lepton" in cut or cut == "4lMass" or cut == "Z1Cand" or cut == "Z1Iso" or cut == "CrossClean":
                    continue

                cutCount += 1

                # save the name of the cut, but only if this is the first time through
                if cutCount > cutCountMax:
                    if cut == "Total":
                        cut = "Init."
                    elif cut == "Z2PV":
                        cut = "Good Leps"
                    elif cut == "Z2SIP":
                        cut = "SIP"
                    elif cut == "CrossClean":
                        cut = "Cross Clean"
                    elif cut == "Z2Cand":
                        cut = "2 Zs"
                    elif cut == "Z2Iso":
                        cut = "Isolation"

                    cutNames[cutCount] = cut

                numbers[channel][sample][cutCount] = int(words[1])


for channel in numbers:
    if channel not in histos:
        histos[channel] = {}
    for sample in numbers[channel]:
        if args.diff:
            nBins = cutCountMax - 1
        else:
            nBins = cutCountMax
        histos[channel][sample] = Hist(nBins, 0, nBins)
        for nCut, n in numbers[channel][sample].iteritems():
            if args.diff:
                if nCut == 1: # initial
                    continue
                if numbers[channel][sample][nCut-1] == 0:
                    histos[channel][sample].SetBinContent(nCut-1, 0)
                else:
                    histos[channel][sample].SetBinContent(nCut-1, float(n)/float(numbers[channel][sample][nCut-1]))
                histos[channel][sample].GetXaxis().SetBinLabel(nCut-1, cutNames[nCut])
            else:
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
                histos[channel][sample].SetLineWidth(2)
            if channel == "eeee":
                evType = "4e"
            elif channel == "eemm":
                evType = "2e2#mu"
            elif channel == "mmmm":
                evType = "4#mu"
            else:
                evType = channel
            histos[channel][sample].SetTitle("Cut Flow Summary %s "%evType)

            if args.diff:
                histos[channel][sample].GetYaxis().SetTitle("Fraction of %s Events Retained"%evType)
            elif args.norm:
                histos[channel][sample].GetYaxis().SetTitle("Fraction of %s Events"%evType)
            else:
                histos[channel][sample].GetYaxis().SetTitle("%s Events"%evType)
            
        # Make sure the errors get scaled correctly
        histos[channel][sample].Sumw2()
        # Scale to cross section and lumi
        if not args.diff:
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

c = Canvas()#ROOT.TCanvas("foo", "foo")#, 1200, 1200)
if args.logy:
    c.SetLogy()

for channel in numbers:
    if args.norm or args.diff:
        leg = ROOT.TLegend(0.12, 0.15, 0.37, 0.4)
    else:
        leg = ROOT.TLegend(0.65, 0.65, 0.9, 0.9)
    leg.SetTextSize(0.03)

    channelName = '4l'
    if channel == 'eeee':
        channelName = '4e'
    elif channel == 'eemm':
        channelName = '2e2#mu'
    elif channel == 'mmmm':
        channelName = '4#mu'

    allSamples = sorted([s for s in histos[channel]])
    if args.stacks:
        # sort histograms by size of the last bin so they stack sensibly. Break ties by putting samples with smaller maxima on the bottom
        allSamples.sort(key=lambda s: histos[channel][s].GetMinimum() + histos[channel][s].GetMaximum()/10000000.)
        # Make stacks
        stackB = ROOT.THStack('background', "ZZ#rightarrow%s Cut Flow Summary"%channelName)
        stackS = ROOT.THStack('signal', "ZZ#rightarrow%s Cut Flow Summary"%channelName)

    # We'll make just one histogram out of all the 8TeV samples
    zz8TeVComboExists = False

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
            if "PHYS14" in sample:
                histos[channel][sample].SetMarkerStyle(20)
            elif "Spring14" in sample:
                histos[channel][sample].SetMarkerStyle(21)
            else:
                histos[channel][sample].SetMarkerStyle(22)

            if '8TeV' in sample and 'ZZ' in sample:
                if args.diff and \
                   ((channel == "eeee" and "4e" not in sample) or \
                   (channel == "eemm" and "2e2m" not in sample) or \
                   (channel == "mmmm" and "4m" not in sample)):
                    continue
                if not zz8TeVComboExists:
                    if channel == "Total" and args.diff:
                        totalZZ8TeVXSec = sampleInfo[sample]['xsec']
                        histos[channel][sample].Scale(totalZZ8TeVXSec)
                    zz8TeVCombo = histos[channel][sample].Clone()
                    zz8TeVComboExists = True
                else:
                    if channel == "Total":
                        histos[channel][sample].Scale(sampleInfo[sample]['xsec'])
                        totalZZ8TeVXSec += sampleInfo[sample]['xsec']
                    zz8TeVCombo.Add(histos[channel][sample])
                continue

            if args.stacks:
                legStyle = "F"
            if args.diff:
                legStyle = "P"
            else:
                legStyle = "LPE"

            leg.AddEntry(histos[channel][sample], sampleInfo[sample]["shortName"], legStyle)
            if args.norm and not args.diff:
                histos[channel][sample].Scale(1./histos[channel][sample].GetBinContent(1))
            drawArgs = "p"
            if not args.diff:
                drawArgs = "he%s"%drawArgs
            if not drawnYet:
                if args.diff:
                    histos[channel][sample].SetMaximum(1.05)
                    histos[channel][sample].SetMinimum(0.)
                histos[channel][sample].Draw(drawArgs)
                drawnYet = True
            else:
                histos[channel][sample].Draw("%ssame"%drawArgs)

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
            leg.AddEntry(histos[channel][s], sampleInfo[s]["shortName"], legStyle)
    elif zz8TeVComboExists:
        leg.AddEntry(zz8TeVCombo, "ZZ->4l 8TeV", legStyle)
        if args.norm and not args.diff:
            zz8TeVCombo.Scale(1./zz8TeVCombo.GetBinContent(1))
        if args.diff and channel == "Total":
            zz8TeVCombo.Scale(1/totalZZ8TeVXSec)
        zz8TeVCombo.Draw("%ssame"%drawArgs)

    ROOT.gStyle.SetLineWidth(3)

    leg.Draw("same")

    style.setPrelimStyle(c, 'N. Woods', True, 'Preliminary Simulation', 13, args.intLumi)
    
    outFile = "%s/cutSummary_%s.png"%(outdir, channel)
    c.Print(outFile)

