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


parser = argparse.ArgumentParser(description='Count the total number of events expected for a given integrated luminosity at each cut in a set of ZZAnalyzer output text files')
parser.add_argument('input', type=str, nargs=1, 
                    help="Comma separated (no spaces) list of text files. May contain wildcards.")
parser.add_argument('intLumi', type=float, nargs='?', default=10000.,
                    help='Integrated luminosity desired, in pb^-1.')

args = parser.parse_args()

infiles = []
for fileset in args.input[0].split(','):
    if glob.glob(fileset):
        infiles += glob.glob(fileset)
    else:
        print "No files matching %s, moving along"%fileset

assert infiles, "No files found"

lumi = args.intLumi

expected = OrderedDict()
sig = OrderedDict()
bkg = OrderedDict()

for afile in infiles:
    with open(afile) as f:
        sample = afile.split('/')[-1].replace('.txt','')
        chan = ''
        storedLumi = 0
        for line in f:
            words = line.split(":")
            if len(words) == 2:
                chan = words[0]
                storedLumi = float(words[1].split()[1])
                if chan not in expected:
                    expected[chan] = OrderedDict()
                    sig[chan] = OrderedDict()
                    bkg[chan] = OrderedDict()                    
                continue
            if len(words) == 3:
                cut = words[0]
                if cut not in expected[chan]:
                    expected[chan][cut] = 0
                    sig[chan][cut] = 0
                    bkg[chan][cut] = 0
                nEv = float(words[2]) * lumi / storedLumi
                expected[chan][cut] += nEv
                if sampleInfo[sample]['isSignal']:
                    sig[chan][cut] += nEv
                else:
                    bkg[chan][cut] += nEv


print "Expected in %0.2f pb^-1:"%lumi
for channel, cuts in expected.iteritems():
    print "\n%s:"%channel
    for cut, n in cuts.iteritems():
        print "%16s:   %-10.2f   (%-10.2f signal,  %-10.2f background)"%(cut, n, sig[channel][cut], bkg[channel][cut])
