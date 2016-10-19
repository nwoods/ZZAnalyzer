'''

Dump candidate information in the approved SMP-ZZ sync format.

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


def getCandInfo(row, *objects):
    numbers = {}
    numbers['run'] = row.run
    numbers['lumi'] = row.lumi
    numbers['event'] = row.evt
    numbers['m4l'] = evVar(row, 'Mass')
    numbers['mZ1'] = nObjVar(row, 'Mass', objects[0], objects[1])
    numbers['mZ2'] = nObjVar(row, 'Mass', objects[2], objects[3])

    # eemm channel may have masses swapped
    if zMassDist(numbers['mZ1']) > zMassDist(numbers['mZ2']):
        temp = numbers['mZ2']
        numbers['mZ2'] = numbers['mZ1']
        numbers['mZ1'] = temp

    numbers['nJets'] = evVar(row, 'nJets')
    numbers['jet1pt'] = max(0,evVar(row, 'jet1Pt'))
    numbers['jet2pt'] = max(0,evVar(row, 'jet2Pt'))
    numbers['mjj'] = max(0,evVar(row, 'mjj'))

    return numbers


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

outStrings = []
outStringsGen = []

outTemp = ('{run}:{lumi}:{event}:{channel}:{m4l:.2f}:{mZ1:.2f}:{mZ2:.2f}:'
           '{nJets}:{jet1pt:.2f}:{jet2pt:.2f}:{mjj:.2f}\n')


with root_open(inFile) as fin:
    for channel in channels:
        objects = getObjects(channel)

        ntuple = fin.Get(channel+'/ntuple')
        for n, row in enumerate(ntuple):
            numbers = getCandInfo(row, *objects)
            outStrings.append(outTemp.format(channel=channel,**numbers))

        ntupleGen = fin.Get(channel+'Gen/ntuple')
        for n, row in enumerate(ntupleGen):
            numbers = getCandInfo(row, *objects)
            outStringsGen.append(outTemp.format(channel=channel,**numbers))


with open(args.output, 'w') as fout:
    for s in sorted(outStrings):
        fout.write(s)

if '.' in args.output:
    outputGen = 'Gen.'.join(args.output.rsplit('.',1))
else:
    outputGen = args.output+'Gen'

with open(outputGen, 'w') as fout:
    for s in sorted(outStringsGen):
        fout.write(s)

