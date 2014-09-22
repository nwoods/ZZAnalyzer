#!/usr/bin/python
'''

Run ZZ->4l cutflows, all channels, taking a path or wildcard as input

Author: Nate Woods, U. Wisconsin

'''

import glob
import multiprocessing
import argparse
import ZZCutFlow
import os

def runSomeAnalyzers(channels, cutSet, infiles, outdir, maxEvents):
    '''
    Run one or more ZZCutFlows serially.
    Intended for use in treads, such that several processes each do this at once.
    '''
    for infile in infiles:
        outfile = outdir+'/'+(infile.split('/')[-1]).replace('.root', '_cutflow.root')
        analyzer = ZZCutFlow.ZZCutFlow(channels, cutSet, infile, outfile, maxEvents)
        analyzer.analyze()

assert os.environ["zza"], "Run setup.sh before running analysis"

parser = argparse.ArgumentParser(description='Run the ZZ4l analyzer on multiple samples.')
parser.add_argument('input', type=str, nargs=1, 
                    help='Comma separated (no spaces) list of sample locations. May contain wildcards. For a directory, all .root files will be processed.')
parser.add_argument('channels', nargs='?', type=str, default='zz',
                    help='Comma separated (no spaces) list of channels, or keyword "zz" for eeee,mmmm,eemm')
parser.add_argument('cutSet', nargs='?', type=str, default='HZZ4l2012',
                    help='Name of cut template.')
parser.add_argument('nThreads', nargs='?', type=int, default=2,
                    help='Maximum number of threads for simultaneous processing.')
parser.add_argument('outdir', type=str, nargs='?', default='ZZA_NORMAL',
                    help='Directory to place output (defaults to $zza/results/<cutSet>/cutflow).')
parser.add_argument('--maxEvents', nargs='?', type=int,
                    help='Maximum number of events to run for each sample in each channel.')

args = parser.parse_args()

infiles = []
for path in args.input[0].split(','):
    if path.endswith('.root'):
        if glob.glob(path):
            infiles += glob.glob(path)
    else:
        if glob.glob(path+'*.root'):
            infiles += glob.glob(path+'*.root')


# Remove duplicates from input files, just in case
infiles = list(set(infiles))

if args.outdir == "ZZA_NORMAL":
    outdir = "%s/results/%s/cutflow"%(os.environ["zza"], args.cutSet)
else:
    outdir = args.outdir

if not os.path.isdir(outdir):
    os.makedirs(outdir)

if args.channels == 'zz':
    channels = ['eeee', 'eemm', 'mmmm']
else:
    channels = args.channels.split(',')

# Don't need more than 1 thread/input
nThreads = min(args.nThreads, len(infiles))

filesPerThread = len(infiles) / nThreads
extraFiles = len(infiles) % nThreads
fileSets = [ [] for i in range(nThreads) ]
i = 0
for f in infiles:
    fileSets[i].append(f)
    i = (i+1)%nThreads

if args.maxEvents:
    maxEvents = args.maxEvents
else:
    maxEvents = float("inf")

threads = [multiprocessing.Process(target=runSomeAnalyzers, args=(channels, args.cutSet, ifs, outdir, maxEvents)) for ifs in fileSets]

for t in threads:
    t.start()

for t in threads:
    t.join()

print "Done!"


                              





