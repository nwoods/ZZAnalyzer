#!/usr/bin/python
'''

Run a ZZ->4l analysis, all channels, taking a path or wildcard as input

Author: Nate Woods, U. Wisconsin

'''

import glob
import multiprocessing
import argparse
import ZZAnalyzer
import os

def runSomeAnalyzers(channels, cutSet, infiles, outdir):
    '''
    Run one or more ZZAnalyzers serially.
    Intended for use in treads, such that several processes each do this once.
    '''
    for infile in infiles:
        outfile = outdir+'/'+(infile.split('/')[-1])
        analyzer = ZZAnalyzer.ZZAnalyzer(channels, cutSet, infile, outfile)
        analyzer.analyze()



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
                    help='Directory to place output (defaults to $zza/results).')

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
    outdir = os.environ["zza"] + "/results"
else:
    outdir = args.outdir

if not os.path.isdir(outdir):
    os.makedirs(outdir)

if args.channels == 'zz':
    channels = ['eeee', 'eemm', 'mmmm']
else:
    print channels + '?'
    channels = args.channels.split(',')

if len(infiles) < args.nThreads:
    nThreads = len(infiles)
else:
    nThreads = args.nThreads

filesPerThread = len(infiles) / nThreads
extraFiles = len(infiles) % nThreads
fileSets = [ [] for i in range(nThreads) ]
i = 0
for f in infiles:
    fileSets[i].append(f)
    i = (i+1)%nThreads

threads = [multiprocessing.Process(target=runSomeAnalyzers, args=(channels, args.cutSet, ifs, outdir)) for ifs in fileSets]

for t in threads:
    t.start()

for t in threads:
    t.join()

print "Done!"


                              






