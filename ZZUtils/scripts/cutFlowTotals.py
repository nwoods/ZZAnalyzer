#!/usr/bin/python
'''

cutFlowTotals.py

Tally the total number of expected events for each cut in a given 
integrated luminosity, tallied from a set of analyzer output txt
files.

Author: Nate Woods, U. Wisconsin

'''


from ZZMetadata import sampleInfo
import argparse
import glob
from collections import OrderedDict
from math import sqrt


parser = argparse.ArgumentParser(description='Count the total number of events expected for a given integrated luminosity at each cut in a set of ZZAnalyzer output text files')
parser.add_argument('input', type=str, nargs=1, 
                    help="Comma separated (no spaces) list of text files. May contain wildcards.")
parser.add_argument('intLumi', type=float, nargs='?', default=10000.,
                    help='Integrated luminosity desired, in pb^-1.')
parser.add_argument('--table', action='store_true', help="Print full table with all samples.")

args = parser.parse_args()

infiles = []
for fileset in args.input[0].split(','):
    if glob.glob(fileset):
        infiles += glob.glob(fileset)
    else:
        print "No files matching %s, moving along"%fileset

assert infiles, "No files found"

lumi = args.intLumi

cuts = []
samples = {} # samples[sampleName] = isSignal
channels = []
numbers = OrderedDict()
firstSample = True # first time through, do setup

for afile in infiles:
    with open(afile) as f:
        sample = afile.split('/')[-1].replace('.txt','')
        sampleName = sampleInfo[sample]["shortName"]
        isSig = sampleInfo[sample]["isSignal"]
        samples[sampleName] = isSig
        chan = ''
        storedLumi = 0
        firstChannel = True
        for line in f:
            words = line.split(":")
            if len(words) == 2:
                if chan:
                    firstChannel = False
                chan = words[0]
                storedLumi = float(words[1].split()[1])
                if firstSample:
                    numbers[chan] = OrderedDict()
                    channels.append(chan)
                continue
            if len(words) == 3:
                cut = words[0]
                if firstSample:
                    if firstChannel:
                        cuts.append(cut)
                    numbers[chan][cut] = OrderedDict()
                numbers[chan][cut][sampleName] = {}
                nEv = float(words[2]) * lumi / storedLumi
                numbers[chan][cut][sampleName]['n'] = nEv
                numbers[chan][cut][sampleName]['raw'] = float(words[1])
    firstSample = False

print "Expected in %0.2f pb^-1:"%lumi

for cut in cuts:
    print "%16s:"%cut
    cutTotals = OrderedDict([(channel, {'sig' : {'n' : 0, 'uncSqr' : 0}, 'bkg' : {'n' : 0, 'uncSqr' : 0}}) for channel in channels])
    printString = '%16s:   '
    for channel in channels:
        printString += '%5s: %-8.1f +/- %-8.1f  '
    for sample in samples:
        if samples[sample]:
            typeName = 'sig' 
        else: 
            typeName = 'bkg'
        namesAndNumbers = [sample]
        for channel in channels:
#            print numbers[channel][cut]
            nChannel = numbers[channel][cut][sample]['n']
            try: # skip if no events
                uncSqrChannel = numbers[channel][cut][sample]['n'] ** 2 / numbers[channel][cut][sample]['raw']
            except ZeroDivisionError:
                uncSqrChannel = 0
            cutTotals[channel][typeName]['n'] += nChannel
            cutTotals[channel][typeName]['uncSqr'] += uncSqrChannel
            if args.table:
                namesAndNumbers += [channel, nChannel, sqrt(uncSqrChannel)]
        if args.table:
            print printString%tuple(namesAndNumbers)
    sigNamesAndNumbers = ["Signal"]
    bkgNamesAndNumbers = ["Background"]
    totNamesAndNumbers = ["Total"]
    for channel, nums in cutTotals.iteritems():
        sigNamesAndNumbers += [channel, nums['sig']['n'], sqrt(nums['sig']['uncSqr'])]
        bkgNamesAndNumbers += [channel, nums['bkg']['n'], sqrt(nums['bkg']['uncSqr'])]
        totNamesAndNumbers += [channel, nums['sig']['n']+nums['bkg']['n'], sqrt(nums['sig']['uncSqr']+nums['bkg']['uncSqr'])]
    print printString%tuple(sigNamesAndNumbers)
    print printString%tuple(bkgNamesAndNumbers)
    print printString%tuple(totNamesAndNumbers)
    print "\n"


