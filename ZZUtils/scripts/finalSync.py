'''

Dump candidate information in the approved HZZ4l sync format.

Is most useful when sorted afterwards with a command like

$ sort -t : -k 1n -k 2n -k 3n

Author: N. Woods, U. Wisconsin

'''

from ZZHelpers import *
from rootpy.io import root_open
import argparse

        
def getObjects(channel):
    nObj = {}
    for letter in channel:
        if letter not in nObj:
            nObj[letter] = 1
        else:
            nObj[letter] += 1
    out = []
    for letter in nObj:
        if nObj[letter] == 1:
            out.append(letter)
        else:
            out += [letter+str(n+1) for n in range(nObj[letter])]
    return out


def getCandInfo(z1Var, z2Var, row):
    run = evVar(row, 'run')
    evt = evVar(row, 'evt')
    lumi = evVar(row, 'lumi')
    mass = evVar(row, 'MassFSR')
    mZ1 = evVar(row, z1Var)
    mZ2 = evVar(row, z2Var)
    kd = 0 #evVar(row, 'KD')
    nJets = evVar(row, 'nJets')
    j1pt = max(-1.,evVar(row, 'jet1Pt'))
    j2pt = max(-1.,evVar(row, 'jet2Pt'))
    return ("%d:%d:%d:%.2f:%.2f:%.2f:%.3f:%d:%.2f:%.2f\n"%(run, lumi, evt, mass, mZ1, mZ2, kd, nJets, j1pt, j2pt))


parser = argparse.ArgumentParser(description='Dump information about the 4l candidates in an ntuple to a text file, for synchronization.')
parser.add_argument('input', type=str, nargs=1, help='Input root file')
parser.add_argument('output', type=str, nargs='?', default='candSync.txt',
                    help='Name of the text file to output.')
parser.add_argument('channels', nargs='?', type=str, default='zz',
                    help='Comma separated (no spaces) list of channels, or keyword "zz" for eeee,mmmm,eemm')
# parser.add_argument('--nThreads', type=int,  # just left to remind myself how if needed
#                     help='Maximum number of threads for simultaneous processing. If unspecified, python figures how many your machine can deal with automatically, to a maximum of 4.')

args = parser.parse_args()
        
if args.channels == 'zz':
    channels = ['eeee', 'eemm', 'mmmm']
else:
    channels = args.channels.split(',')
        
inFile = args.input[0]
        
with root_open(inFile) as fin:
    with open(args.output, 'w') as fout:
        for channel in channels:
            print "\nChannel %s:"%channel
            ntuple = fin.Get(channel+'/final/Ntuple')
            objects = getObjects(channel)
            z1MassVar = "%s_%s_MassFSR"%(objects[0], objects[1])
            z2MassVar = "%s_%s_MassFSR"%(objects[2], objects[3])
        
            for n, row in enumerate(ntuple):
                if n % 500 == 0:
                    print "Processing row %d"%n
                fout.write(getCandInfo(z1MassVar, z2MassVar, row))
                    
print "Done!"







