'''

Dump candidate information in the approved HZZ4l sync format, for the 3 prompt 1 fake control region.

Is most useful when sorted afterwards with a command like

$ sort -t : -k 1n -k 2n -k 3n

It's often useful to get a list of run:lumi:evt only, with something like

$ cut -d ':' -f -3

Author: N. Woods, U. Wisconsin

'''

from ZZAnalyzer.utils.helpers import evVar
from ZZAnalyzer.cuts import getCutClass

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

    kd = evVar(row, 'D_bkg_kin')
    nJets = evVar(row, 'nJets')
    j1pt = max(-1.,evVar(row, 'jet1Pt'))
    j2pt = max(-1.,evVar(row, 'jet2Pt'))
    return ("%d:%d:%d:%.2f:%.2f:%.2f:%.3f:%d:%.2f:%.2f\n"%(run, lumi, evt, mass, mZ1, mZ2, kd, nJets, j1pt, j2pt))


parser = argparse.ArgumentParser(description='Dump information about the 3P1F CR 4l candidates in an ntuple to a text file, for synchronization.')
parser.add_argument('input', type=str, nargs=1, help='Input root file')
parser.add_argument('output', type=str, nargs='?', default='cr3p1fSync.txt',
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
        
cutter = getCutClass('BaseCuts2016', 'HZZ2016', 'ControlRegion_OS_3P1F')()

with root_open(inFile) as fin:
    with open(args.output, 'w') as fout:
        for channel in channels:
            print "\nChannel %s:"%channel
            ntuple = fin.Get(channel+'/ntuple')
            objects = getObjects(channel)
            needReorder = cutter.needReorder(channel)
        
            for n, row in enumerate(ntuple):
                if n % 500 == 0:
                    print "Processing row %d"%n
                obs = cutter.orderLeptons(row, channel, objects) if needReorder else objects
                z1MassVar = "%s_%s_MassFSR"%(obs[0], obs[1])
                z2MassVar = "%s_%s_MassFSR"%(obs[2], obs[3])
                fout.write(getCandInfo(z1MassVar, z2MassVar, row))
                    
print "Done!"







