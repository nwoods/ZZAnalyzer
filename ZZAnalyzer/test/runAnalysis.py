#!/usr/bin/python
'''

Run a ZZ->4l analysis on multiple files

Author: Nate Woods, U. Wisconsin

'''

import glob
import multiprocessing
import argparse
import os
import signal
import time

from rootpy.plotting import Hist
from rootpy import ROOT

from ZZAnalyzer.analyzers import Analyzer


ROOT.gROOT.SetBatch(True)


def runAnAnalyzer(channels, cutSet, infile, outdir, resultType, 
                  maxEvents, intLumi, cleanRows, mods):
    '''
    Run an Analyzer.
    Intended for use in threads, such that several processes all do this once.
    '''
    outfile = outdir+'/'+(infile.split('/')[-1])
    analyzer = Analyzer(channels, cutSet, infile, outfile, 
                        resultType, maxEvents, intLumi, 
                        cleanRows, cutModifiers=mods)
    analyzer.analyze()

def init_worker():
    '''
    Ignore interrupt signals.
    Tell worker processes to do this so that the parent process handles keyboard interrupts.
    '''
    signal.signal(signal.SIGINT, signal.SIG_IGN)

assert os.environ["zza"], "Run setup.sh before running analysis"

parser = argparse.ArgumentParser(description='Run the ZZ4l analyzer on multiple samples.')
parser.add_argument('input', type=str, nargs=1, 
                    help='Comma separated (no spaces) list of sample locations. May contain wildcards. For a directory, all .root files will be processed.')
parser.add_argument('channels', nargs='?', type=str, default='zz',
                    help='Comma separated (no spaces) list of channels, or keyword "zz" for eeee,mmmm,eemm')
parser.add_argument('cutSet', nargs='?', type=str, default='BaseCuts2016',
                    help='Name of cut template.')
parser.add_argument('outdir', type=str, nargs='?', default='ZZA_NORMAL',
                    help='Directory to place output (defaults to $zza/results/<cutSet>).')
parser.add_argument('resultType', type=str, nargs='?', default='CopyNtuple',
                    help='Template for saving results')
parser.add_argument('intLumi', type=float, nargs='?', default=10000,
                    help='Integrated luminosity for report in ouput text files. In pb^-1.')
parser.add_argument('--nThreads', type=int,
                    help='Maximum number of threads for simultaneous processing. If unspecified, python figures how many your machine can deal with automatically, to a maximum of 4.')
parser.add_argument('--maxEvents', nargs='?', type=int,
                    help='Maximum number of events to run for each sample in each channel.')
parser.add_argument("--cleanRows", nargs='?', type=str, default='',
                    help="Name of module to clean extra rows from each event. Without this option, no cleaning is performed.")
parser.add_argument("--modifiers", nargs='*', type=str,
                    help="Other cut sets that modify the base cuts.")

# we have to create some ROOT object to get ROOT's metadata system setup before the threads start
# or else we get segfault-causing race conditions
bar = Hist(10,0.,1.,name="foo",title="foo")

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
    outdir = os.environ["zza"] + "/results/"+args.cutSet
else:
    if args.outdir.endswith('/'):
        outdir = args.outdir[:-1]
    else:
        outdir = args.outdir

if not os.path.isdir(outdir):
    os.makedirs(outdir)

if args.channels == 'zz':
    channels = ['eeee', 'eemm', 'mmmm']
else:
    channels = args.channels.split(',')

if args.nThreads:
    nThreads = min(args.nThreads, len(infiles))
else:
    nThreads = min(multiprocessing.cpu_count(), 4)

if args.maxEvents:
    maxEvents = args.maxEvents
else:
    maxEvents = float("inf")

if args.modifiers:
    mods = args.modifiers
else:
    mods = []

intLumi = args.intLumi

pool = multiprocessing.Pool(nThreads, init_worker)
results = []
for infile in infiles:
    results.append(pool.apply_async(runAnAnalyzer, args=(channels, args.cutSet,
                                                         infile, outdir, 
                                                         args.resultType, 
                                                         maxEvents, intLumi, 
                                                         args.cleanRows,
                                                         mods)))

# A little magic to make keyboard interrupts work
try:
    while not all([result.ready() for result in results]):
        time.sleep(3)
except KeyboardInterrupt:
    pool.terminate()
    pool.join()
    print "\nKilled ZZ Analyzers"
    exit(1)
else:
    pool.close()
    pool.join()

print "Done!"


                              






