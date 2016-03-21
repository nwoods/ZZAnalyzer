'''

Dump candidate information in the approved HZZ4l sync format.

It's often useful to get a list of run:lumi:evt only, with something like

$ cut -d ':' -f -3

The events are sorted by run, then lumi, then event, the same as processing
the same-but-unsorted output with the Unix command

$ sort -t : -k 1n -k 2n -k 3n

Author: N. Woods, U. Wisconsin

'''

from ZZAnalyzer.utils.helpers import evVar

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


def getEventInfo(row):
    run = evVar(row, 'run')
    evt = evVar(row, 'evt')
    lumi = evVar(row, 'lumi')

    return ':'.join(str(n) for n in [run,lumi,evt])


def getCandInfo(z1Var, z2Var, row):
    evt = getEventInfo(row)
    mass = evVar(row, 'MassDREtFSR')
    mZ1 = evVar(row, z1Var)
    mZ2 = evVar(row, z2Var)

    # eemm channel may have masses swapped
    if zMassDist(mZ1) > zMassDist(mZ2):
        temp = mZ2
        mZ2 = mZ1
        mZ1 = temp

    D_bkg_kin = evVar(row, 'D_bkg_kin')
    D_bkg = evVar(row, 'D_bkg')
    D_gg = evVar(row, 'D_gg')
    D_HJJ_VBF = evVar(row, 'Djet_VAJHU')
    D_g4 = evVar(row, 'D_g4')
    nJets = evVar(row, 'nJets')
    j1pt = max(-1.,evVar(row, 'jet1Pt'))
    j2pt = max(-1.,evVar(row, 'jet2Pt'))
    cat = int(evVar(row, "HZZCategory"))
    return ("%s:%.2f:%.2f:%.2f:%.3f:%.3f:%.3f:%.3f:%.3f:%d:%.2f:%.2f:%d"%(evt, mass,
                                                                          mZ1, mZ2, D_bkg_kin,
                                                                          D_bkg, D_gg, D_HJJ_VBF,
                                                                          D_g4, nJets, j1pt, j2pt, cat))



parser = argparse.ArgumentParser(description='Dump information about the 4l candidates in an ntuple to a text file, for synchronization.')
parser.add_argument('input', type=str, nargs=1, help='Input root file')
parser.add_argument('output', type=str, nargs='?', default='candSync.txt',
                    help='Name of the text file to output.')
parser.add_argument('channels', nargs='?', type=str, default='zz',
                    help='Comma separated (no spaces) list of channels, or keyword "zz" for eeee,mmmm,eemm')
parser.add_argument('--listOnly', action='store_true', 
                    help='Print only run:lumi:event with no further info')

args = parser.parse_args()

channels = parseChannels(args.channels)        
        
inFile = args.input[0]

outStrings = {}

if args.listOnly:
    getInfo = lambda row, *args: getEventInfo(row)
else:
    getInfo = lambda row, z1MassVar, z2MassVar: getCandInfo(z1MassVar, z2MassVar, row)
        
with root_open(inFile) as fin:
    for channel in channels:
        print "\nChannel %s:"%channel
        ntuple = fin.Get(channel+'/final/Ntuple')
        objects = getObjects(channel)
        z1MassVar = "%s_%s_MassDREtFSR"%(objects[0], objects[1])
        z2MassVar = "%s_%s_MassDREtFSR"%(objects[2], objects[3])
    
        for n, row in enumerate(ntuple):
            if n % 500 == 0:
                print "Processing row %d"%n
    
            evStr = getInfo(row, z1MassVar, z2MassVar)
            run = row.run
            lumi = row.lumi
            evt = row.evt
            if run not in outStrings:
                outStrings[run] = {lumi : {evt : evStr}}
            elif lumi not in outStrings[run]:
                outStrings[run][lumi] = {evt : evStr}
            else:
                outStrings[run][lumi][evt] = evStr

with open(args.output, 'w') as fout:
    for r in sorted(outStrings.keys()):
        runStrings = outStrings[r]
        for l in sorted(runStrings.keys()):
            lumiStrings = runStrings[l]
            for e in sorted(lumiStrings.keys()):
                fout.write(lumiStrings[e])
                fout.write('\n')
                    
print "Done!"







