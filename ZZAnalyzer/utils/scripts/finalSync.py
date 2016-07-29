'''

Dump candidate information in the approved HZZ4l sync format.

It's often useful to get a list of run:lumi:evt only, with something like

$ cut -d ':' -f -3

The events are sorted by run, then lumi, then event, the same as processing
the same-but-unsorted output with the Unix command

$ sort -t : -k 1n -k 2n -k 3n

Author: N. Woods, U. Wisconsin

'''

from ZZAnalyzer.utils.helpers import evVar, objVar, nObjVar, parseChannels, zMassDist

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


def getCandInfo(zMassVar, row, *objects):
    numbers = {}
    numbers['run'] = row.run
    numbers['lumi'] = row.lumi
    numbers['event'] = row.evt
    numbers['mass4l'] = evVar(row, 'MassFSR')
    numbers['mZ1'] = nObjVar(row, zMassVar, objects[0], objects[1])
    numbers['mZ2'] = nObjVar(row, zMassVar, objects[2], objects[3])

    # eemm channel may have masses swapped
    if zMassDist(numbers['mZ1']) > zMassDist(numbers['mZ2']):
        temp = numbers['mZ2']
        numbers['mZ2'] = numbers['mZ1']
        numbers['mZ1'] = temp

    numbers['D_bkg^kin'] = evVar(row, 'D_bkg_kin')
    numbers['D_bkg'] = evVar(row, 'D_bkg')
    numbers['D_gg'] = evVar(row, 'D_gg')
    numbers['Dkin_HJJ^VBF'] = evVar(row, 'D_VBF2j')
    numbers['D_0-'] = evVar(row, 'D_g4')
    numbers['Dkin_HJ^VBF-1'] = evVar(row, 'D_VBF1j')
    numbers['Dkin_HJJ^WH-h'] = evVar(row, 'D_WHh')
    numbers['Dkin_HJJ^ZH-h'] = evVar(row, 'D_ZHh')
    numbers['njets30'] = evVar(row, 'nJets')
    numbers['jet1pt'] = max(-1.,evVar(row, 'jet1Pt'))
    numbers['jet2pt'] = max(-1.,evVar(row, 'jet2Pt'))
    numbers['jet1qgl'] = evVar(row, 'jet1QGLikelihood')
    numbers['jet2qgl'] = evVar(row, 'jet2QGLikelihood')
    numbers['Dfull_HJJ^VBF'] = evVar(row, 'D_VBF2j_QG')
    numbers['Dfull_HJ^VBF-1'] = evVar(row, 'D_VBF1j_QG')
    numbers['Dfull_HJJ^WH-h'] = evVar(row, 'D_WHh_QG')
    numbers['Dfull_HJJ^ZH-h'] = evVar(row, 'D_ZHh_QG')
    numbers['category'] = evVar(row, "ZZCategory")
    # numbers['m4lRefit'] = evVar(row, 'MassRefit')
    # numbers['m4lRefitError'] = evVar(row, 'MassRefitError')

    if not args.data:
        numbers['weight'] = evVar(row, 'genWeight')
        numbers['weight'] /= abs(numbers['weight'])

        for ob in objects:
            numbers['weight'] *= objVar(row, 'EffScaleFactor', ob)

    outTemp = ('{run}:{lumi}:{event}:{mass4l:.2f}:{mZ1:.2f}:{mZ2:.2f}:{D_bkg^kin:'
               '.3f}:{D_bkg:.3f}:{D_gg:.3f}:{Dkin_HJJ^VBF:.3f}:{D_0-:.3f}:'
               '{Dkin_HJ^VBF-1:.3f}:{Dkin_HJJ^WH-h:.3f}:{Dkin_HJJ^ZH-h:.3f}:'
               '{njets30:d}:{jet1pt:.2f}:{jet2pt:.2f}:{jet1qgl:.3f}:{jet2qgl:.3f}:'
               '{Dfull_HJJ^VBF:.3f}:{Dfull_HJ^VBF-1:.3f}:{Dfull_HJJ^WH-h:.3f}:'
               '{Dfull_HJJ^ZH-h:.3f}:{category}') #:{m4lRefit:.2f}:{m4lRefitError:.2f}:'
    if not args.data:
        outTemp += ':{weight:.3f}'

    return outTemp.format(**numbers)


parser = argparse.ArgumentParser(description='Dump information about the 4l candidates in an ntuple to a text file, for synchronization.')
parser.add_argument('input', type=str, nargs=1, help='Input root file')
parser.add_argument('output', type=str, nargs='?', default='candSync.txt',
                    help='Name of the text file to output.')
parser.add_argument('channels', nargs='?', type=str, default='zz',
                    help='Comma separated (no spaces) list of channels, or keyword "zz" for eeee,mmmm,eemm')
parser.add_argument('--listOnly', action='store_true', 
                    help='Print only run:lumi:event with no further info')
parser.add_argument('--printChannel', action='store_true',
                    help='Print the name of the channel for each event')
parser.add_argument('--data', action='store_true',
                    help="Treat as data (don't print weight).")

args = parser.parse_args()

channels = parseChannels(args.channels)        
        
inFile = args.input[0]

outStrings = {}

if args.listOnly:
    getInfo = lambda row, *args: getEventInfo(row)
else:
    getInfo = lambda row, zMassVar, *objects: getCandInfo(zMassVar, row, *objects)
        
with root_open(inFile) as fin:
    for channel in channels:
        print "\nChannel %s:"%channel
        ntuple = fin.Get(channel+'/ntuple')
        objects = getObjects(channel)
    
        if not args.printChannel:
            chStr = ''
        elif channel == 'mmmm':
            chStr = '4mu:'
        elif channel == 'eemm':
            chStr = '2e2mu:'
        elif channel == 'eeee':
            chStr = '4e:'

        for n, row in enumerate(ntuple):
            if n % 500 == 0:
                print "Processing row %d"%n
    
            evStr = chStr + getInfo(row, 'MassFSR', *objects)
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







