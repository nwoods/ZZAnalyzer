#!/usr/bin/python
'''

Run some or all parts of the ZZ analysis

Author: Nate Woods, U. Wisconsin

'''

import glob
import multiprocessing
import argparse
import ZZAnalyzer
import os
import signal
import time
from rootpy.plotting import Hist
from rootpy import ROOT
from analyses import *
from AnalysisManager import AnalysisManager

ROOT.gROOT.SetBatch(True)


def init_worker():
    '''
    Ignore interrupt signals.
    Tell worker processes to do this so that the parent process handles keyboard interrupts.
    '''
    signal.signal(signal.SIGINT, signal.SIG_IGN)

assert os.environ["zza"], "Run setup.sh before running analysis"

parser = argparse.ArgumentParser(description='Run the ZZ4l analyzer on multiple samples.')
parser.add_argument('--zzData', type=str, nargs='?',
                    help='Identifier for ZZ data files (located in /data/nawoods/ntuples/zzNtuples_data_2015silver_<this variable>).')
parser.add_argument('--zlData', type=str, nargs='?',
                    help='Identifier for Z+l data files (located in /data/nawoods/ntuples/zPlusl_data_2015gold_<this variable>).')
parser.add_argument('--zData', type=str, nargs='?',
                    help='Identifier for Z data files (located in /data/nawoods/ntuples/singlez_data_2015silver_<this variable>).')
parser.add_argument('--zzMC', type=str, nargs='?',
                    help='Identifier for ZZ MC files (located in /data/nawoods/ntuples/zzNtuples_mc_<this variable>).')
parser.add_argument('--zlMC', type=str, nargs='?',
                    help='Identifier for Z+l MC files (located in /data/nawoods/ntuples/zPlusl_mc_<this variable>).')
parser.add_argument('--zMC', type=str, nargs='?',
                    help='Identifier for Z MC files (located in /data/nawoods/ntuples/singlez_mc_<this variable>).')
parser.add_argument('--smp', action='store_true', help='Do the on-shell analysis')
parser.add_argument('--hzz', action='store_true', help='Do the Higgs analysis')
parser.add_argument('--full', action='store_true', help='Do the Z to 4l analysis')
parser.add_argument('--SR', action='store_true', help='Do signal region cuts')
parser.add_argument('--CR2P2F', action='store_true', help='Do 2P2F control region cuts')
parser.add_argument('--CR3P1F', action='store_true', help='Do 3P1F control region cuts')
parser.add_argument('--nThreads', type=int, default=12,
                    help='Maximum number of threads for simultaneous processing. If unspecified, python figures how many your machine can deal with automatically, to a maximum of 12.')

# we have to create some ROOT object to get ROOT's metadata system setup before the threads start
# or else we get segfault-causing race conditions
bar = Hist(10,0.,1.,name="foo",title="foo")

args = parser.parse_args()

nThreads = min(multiprocessing.cpu_count(), args.nThreads)

pool = multiprocessing.Pool(nThreads, init_worker)


pathStart = '/data/nawoods/ntuples'

managers = []

if (args.zzData or args.zzMC) and not (args.SR or args.CR2P2F or args.CR3P1F):
    args.SR = True
    args.CR2P2F = True
    args.CR3P1F = True

desiredZZResultsData = []
desiredZZResultsMC = []

if args.smp:
    if args.SR:
        desiredZZResultsData.append('smp')
        desiredZZResultsMC.append('smp')
    if args.CR2P2F:
        desiredZZResultsData.append('smp_2P2F')
        desiredZZResultsMC.append('smp_2P2F')
    if args.CR3P1F:
        desiredZZResultsData.append('smp_3P1F')
        desiredZZResultsMC.append('smp_3P1F')
if args.full:
    if args.SR:
        desiredZZResultsData.append('fullSpectrum_blind')
        desiredZZResultsMC.append('fullSpectrum')
    if args.CR2P2F:
        desiredZZResultsData.append('fullSpectrum_2P2F')
        desiredZZResultsMC.append('fullSpectrum_2P2F')
    if args.CR3P1F:
        desiredZZResultsData.append('fullSpectrum_3P1F')
        desiredZZResultsMC.append('fullSpectrum_3P1F')
if args.hzz:
    if args.SR:
        desiredZZResultsData.append('hzz_blind')
        desiredZZResultsMC.append('hzz')
    if args.CR2P2F:
        desiredZZResultsData.append('hzz_2P2F')
        desiredZZResultsMC.append('hzz_2P2F')
    if args.CR3P1F:
        desiredZZResultsData.append('hzz_3P1F')
        desiredZZResultsMC.append('hzz_3P1F')
    
desiredZLResults = ['zPluslLoose', 'zPluslTight']
desiredZResults = []

if args.zzData:
    inputs = os.path.join(pathStart, "zzNtuples_data_2015silver_"+args.zzData)
    man = AnalysisManager(zzAnalyses, inputs, pool)
    man.addAnalyses(*desiredZZResultsData)
    managers.append(man)

if args.zlData:
    inputs = os.path.join(pathStart, "zPlusl_data_2015gold_"+args.zlData)
    man = AnalysisManager(zlAnalyses, inputs, pool)
    man.addAnalyses(*desiredZLResults)
    managers.append(man)

if args.zData:
    inputs = os.path.join(pathStart, "singlez_data_2015silver_"+args.zData)
    man = AnalysisManager(zAnalyses, inputs, pool)
    man.addAnalyses(*desiredZResults)
    managers.append(man)

if args.zzMC:
    inputs = os.path.join(pathStart, "zzNtuples_mc_"+args.zzMC)
    man = AnalysisManager(zzAnalyses, inputs, pool)
    man.addAnalyses(*desiredZZResultsMC)
    managers.append(man)

if args.zlMC:
    inputs = os.path.join(pathStart, "zPlusl_mc_"+args.zlMC)
    man = AnalysisManager(zlAnalyses, inputs, pool)
    man.addAnalyses(*desiredZLResults)
    managers.append(man)

if args.zMC:
    inputs = os.path.join(pathStart, "singlez_mc_"+args.zMC)
    man = AnalysisManager(zAnalyses, inputs, pool)
    man.addAnalyses(*desiredZResults)
    managers.append(man)



# A little trickery to make keyboard interrupts work
try:
    while True:
        results = [m.runReady() for m in managers]
        if not any(results):
            break
        time.sleep(5)
except KeyboardInterrupt:
    pool.terminate()
    pool.join()
    print "\nKilled ZZ Analyzers"
    exit(1)
else:
    pool.close()
    pool.join()

print "Done!"


                              






