#!/usr/bin/python
'''

Run some or all parts of the ZZ analysis

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

from ZZAnalyzer.metadata.analyses import *
from ZZAnalyzer.analyzers import AnalysisManager

ROOT.gROOT.SetBatch(True)


def init_worker():
    '''
    Ignore interrupt signals.
    Tell worker processes to do this so that the parent process handles keyboard interrupts.
    '''
    signal.signal(signal.SIGINT, signal.SIG_IGN)

assert os.environ["zza"], "Run setup.sh before running analysis"

parser = argparse.ArgumentParser(description='Run the ZZ4l analyzer on multiple samples.')
parser.add_argument('--zzData', type=str, nargs='*', default=[],
                    help='Identifier for ZZ data files (located in /data/nawoods/ntuples/uwvvNtuples_data_<this variable>).')
parser.add_argument('--zlData', type=str, nargs='*', default=[],
                    help='Identifier for Z+l data files (located in /data/nawoods/ntuples/uwvvZPlusl_data_<this variable>).')
parser.add_argument('--zData', type=str, nargs='*', default=[],
                    help='Identifier for Z data files (located in /data/nawoods/ntuples/uwvvSingleZ_data_<this variable>).')
parser.add_argument('--zzMC', type=str, nargs='*', default=[],
                    help='Identifier for ZZ MC files (located in /data/nawoods/ntuples/uwvvNtuples_mc_<this variable>).')
parser.add_argument('--zlMC', type=str, nargs='*', default=[],
                    help='Identifier for Z+l MC files (located in /data/nawoods/ntuples/uwvvZPlusl_mc_<this variable>).')
parser.add_argument('--zMC', type=str, nargs='*', default=[],
                    help='Identifier for Z MC files (located in /data/nawoods/ntuples/uwvvSingleZ_mc_<this variable>).')
parser.add_argument('--smp', action='store_true', help='Do the on-shell analysis')
parser.add_argument('--hzz', action='store_true', help='Do the Higgs analysis')
parser.add_argument('--full', action='store_true', help='Do the full spectrum analysis')
parser.add_argument('--z4l', action='store_true', help='Do the Z to 4l analysis')
parser.add_argument('--SR', action='store_true', help='Do signal region cuts')
parser.add_argument('--CR2P2F', action='store_true', help='Do 2P2F control region cuts')
parser.add_argument('--CR3P1F', action='store_true', help='Do 3P1F control region cuts')
parser.add_argument('--channels', type=str, nargs='?', default='zz',
                    help='Channels to run for 4l.')
parser.add_argument('--nThreads', type=int, default=12,
                    help='Maximum number of threads for simultaneous processing. If unspecified, python figures how many your machine can deal with automatically, to a maximum of 12.')
parser.add_argument('--assumeInputExists', action='store_true',
                    help='Only run the requested analyses, assuming the prerequisite analyses have already been done.')
parser.add_argument('--blind', action='store_true', help='Apply HZZ blinding to data')
parser.add_argument('--Spring16', action='store_true',
                    help='Skip trigger for MC samples that didn\'t have it in the Spring16 campaign.')
parser.add_argument('--noSIP', action='store_true',
                    help="Don't do lepton SIP cuts.")
parser.add_argument('--looseSIP', action='store_true',
                    help="Use looser lepton SIP cut (currently 10 instead of 4).")

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

if args.noSIP:
    if args.looseSIP:
        raise RuntimeError("I can't apply the loose SIP cut if I'm not applying any SIP cut!")

    for ana in zzAnalyses:
        if 'full' in ana.lower():
            zzAnalyses[ana]['cutModifiers'].insert(0,'NoSIP')
    for ana in zlAnalyses:
        zlAnalyses[ana]['cutModifiers'].insert(0,'NoSIP')
    for ana in zAnalyses:
        zAnalyses[ana]['cutModifiers'].insert(0,'NoSIP')

if args.looseSIP:
    for ana in zzAnalyses:
        if 'full' in ana.lower():
            zzAnalyses[ana]['cutModifiers'].insert(0,'LooseSIP')
    for ana in zlAnalyses:
        zlAnalyses[ana]['cutModifiers'].insert(0,'LooseSIP')
    for ana in zAnalyses:
        zAnalyses[ana]['cutModifiers'].insert(0,'LooseSIP')

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
        if args.blind:
            desiredZZResultsData.append('fullSpectrum_blind')
        else:
            desiredZZResultsData.append('fullSpectrum')
        desiredZZResultsMC.append('fullSpectrum')
    if args.CR2P2F:
        desiredZZResultsData.append('fullSpectrum_2P2F')
        desiredZZResultsMC.append('fullSpectrum_2P2F')
    if args.CR3P1F:
        desiredZZResultsData.append('fullSpectrum_3P1F')
        desiredZZResultsMC.append('fullSpectrum_3P1F')
if args.hzz:
    if args.SR:
        if args.blind:
            desiredZZResultsData.append('hzz_blind')
        else:
            desiredZZResultsData.append('hzz')
        desiredZZResultsMC.append('hzz')
    if args.CR2P2F:
        desiredZZResultsData.append('hzz_2P2F')
        desiredZZResultsMC.append('hzz_2P2F')
    if args.CR3P1F:
        desiredZZResultsData.append('hzz_3P1F')
        desiredZZResultsMC.append('hzz_3P1F')
if args.z4l:
    if args.SR:
        desiredZZResultsData.append('z4l')
        desiredZZResultsMC.append('z4l')
    if args.CR2P2F:
        desiredZZResultsData.append('z4l_2P2F')
        desiredZZResultsMC.append('z4l_2P2F')
    if args.CR3P1F:
        desiredZZResultsData.append('z4l_3P1F')
        desiredZZResultsMC.append('z4l_3P1F')

desiredZLResults = ['zPluslLoose',]
desiredZLResults.append('zPluslTight')

desiredZResults = ['singleZ']

for sampleID in args.zzData:
    inputs = os.path.join(pathStart, "uwvvNtuples_data_"+sampleID)
    man = AnalysisManager(zzAnalyses, inputs, pool, args.channels,
                          args.assumeInputExists, args.Spring16)
    man.addAnalyses(*desiredZZResultsData)
    managers.append(man)

for sampleID in args.zlData:
    inputs = os.path.join(pathStart, "uwvvZPlusl_data_"+sampleID)
    man = AnalysisManager(zlAnalyses, inputs, pool, '3l',
                          args.assumeInputExists, args.Spring16)
    man.addAnalyses(*desiredZLResults)
    managers.append(man)

for sampleID in args.zData:
    inputs = os.path.join(pathStart, "uwvvSingleZ_data_"+sampleID)
    man = AnalysisManager(zAnalyses, inputs, pool, 'z',
                          args.assumeInputExists, args.Spring16)
    man.addAnalyses(*desiredZResults)
    managers.append(man)

for sampleID in args.zzMC:
    inputs = os.path.join(pathStart, "uwvvNtuples_mc_"+sampleID)
    man = AnalysisManager(zzAnalyses, inputs, pool, args.channels,
                          args.assumeInputExists, args.Spring16)
    man.addAnalyses(*desiredZZResultsMC)
    managers.append(man)

for sampleID in args.zlMC:
    inputs = os.path.join(pathStart, "uwvvZPlusl_mc_"+sampleID)
    man = AnalysisManager(zlAnalyses, inputs, pool, '3l',
                          args.assumeInputExists, args.Spring16)
    man.addAnalyses(*desiredZLResults)
    managers.append(man)

for sampleID in args.zMC:
    inputs = os.path.join(pathStart, "uwvvSingleZ_mc_"+sampleID)
    man = AnalysisManager(zAnalyses, inputs, pool, 'z',
                          args.assumeInputExists, args.Spring16)
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









