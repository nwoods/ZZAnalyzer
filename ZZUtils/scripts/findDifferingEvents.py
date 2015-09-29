'''

Given two ntuples, a variable, and an acceptable degree of difference, 
find events where the ntuples differ.

Nate Woods, U. Wisconsin

'''

from ZZHelpers import Z_MASS

from rootpy.io import root_open
from collections import OrderedDict
from itertools import combinations



var = 'Mass'
maxDifference = 5.

def selectRow(row):
    '''
    Define a boolean function here if you want to consider only certain rows.
    '''
    return True #abs(row.m1_m2_Mass - Z_MASS) < abs(row.e1_e2_Mass - Z_MASS)

channel = 'eemm'

fns = {
    '75x' : '/data/nawoods/ntuples/validation75X/results_mz/data_MuonEG_Run2015B_05Aug2015_50ns.root',
    '74x' : '/data/nawoods/ntuples/validation74X/results_mz/data_MuonEG_Run2015B_PromptReco_50ns.root',
    }
fs = {s : root_open(fn) for s,fn in fns.iteritems()}

ns = {s : f.Get("%s/final/Ntuple"%channel) for s,f in fs.iteritems()}

results = {}

for sample, n in ns.iteritems():
    for row in n:
        if not selectRow(row):
            continue
        run = row.run
        if run not in results:
            results[run] = {}
        lumi = row.lumi
        if lumi not in results[run]:
            results[run][lumi] = {}
        evt = row.evt
        if evt not in results[run][lumi]:
            results[run][lumi][evt] = OrderedDict()
        results[run][lumi][evt][sample] = getattr(row, var)

for run in sorted(results.keys()):
    dRun = results[run]
    for lumi in sorted(dRun.keys()):
        dLumi = dRun[lumi]
        for evt in sorted(dLumi.keys()):
            dEvt = dLumi[evt]
            if len(dEvt) != len(ns) or\
                    any(abs(a-b) > maxDifference for (a,b) in combinations(dEvt.values(), 2)):
                print "%d:%d:%d:"%(run, lumi, evt)
                for sample, value in dEvt.iteritems():
                    print "    %s: %f"%(sample, value)

