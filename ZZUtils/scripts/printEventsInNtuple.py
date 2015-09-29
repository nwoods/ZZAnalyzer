'''

Print out run : lumi : evt for all ntuples in some files.

'''

from rootpy.io import root_open
from glob import glob


runs = {}

channels = ['eeee', 'eemm', 'mmmm']
files = glob('/data/nawoods/ntuples/validation75X/results_mz/data_*.root')

for fn in files:
    with root_open(fn) as f:
        for ch in channels:
            n = f.Get("%s/final/Ntuple"%ch)
            for row in n:
                run = row.run
                if run not in runs:
                    runs[run] = {}
                lumi = row.lumi
                if lumi not in runs[run]:
                    runs[run][lumi] = set()
                runs[run][lumi].add(row.evt)

for run in sorted(runs.keys()):
    for lumi in sorted(runs[run].keys()):
        for evt in sorted(list(runs[run][lumi])):
            print "%d:%d:%d"%(run, lumi, evt)
