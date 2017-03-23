'''

Dump candidate information in the approved SMP-ZZ sync format.

It's often useful to get a list of run:lumi:evt only, with something like

$ cut -d ':' -f -3

The events are sorted by run, then lumi, then event, the same as processing
the same-but-unsorted output with the Unix command

$ sort -t : -k 1n -k 2n -k 3n

Author: N. Woods, U. Wisconsin

'''

import logging
from rootpy import log as rlog; rlog = rlog['/smpSync']
logging.basicConfig(level=logging.WARNING)
rlog["/ROOT.TUnixSystem.SetDisplay"].setLevel(rlog.ERROR)
rlog["/rootpy.tree.chain"].setLevel(rlog.WARNING)

from ZZAnalyzer.utils.helpers import evVar, objVar, nObjVar, parseChannels, zMassDist

from rootpy import asrootpy
from rootpy.io import root_open
from rootpy.tree import TreeChain
import argparse
from glob import glob
from os import environ
from os.path import join


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
    return sorted(out)


def getEventInfo(row, *args):
    return {
        'run' : evVar(row, 'run'),
        'event' : evVar(row, 'evt'),
        'lumi' : evVar(row, 'lumi'),
        }


def getCandInfo(row, hPUWt, *objects):
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

    jetPts = evVar(row, 'jetPt')
    numbers['nJets'] = jetPts.size()
    if jetPts.size():
        numbers['jet1pt'] = jetPts.at(0)
        if jetPts.size() > 1:
            numbers['jet2pt'] = jetPts.at(1)
        else:
            numbers['jet2pt'] = -1.
    else:
        numbers['jet1pt'] = -1.
        numbers['jet2pt'] = -1.

    numbers['puWt'] = hPUWt.GetBinContent(hPUWt.FindBin(evVar(row, 'nTruePU')))
    recoSF = 1.
    selSF = 1.
    for ob in objects:
        if ob[0] == 'm':
            selSF *= objVar(row, 'EffScaleFactor', ob)
        else:
            recoSF *= objVar(row, 'TrkRecoEffScaleFactor', ob)
            selSF *= objVar(row, 'IDIsoEffScaleFactor', ob)

    numbers['recoSF'] = recoSF
    numbers['selSF'] = selSF

    numbers['nPU'] = evVar(row, 'nTruePU')

    numbers['mjj'] = max(-1.,evVar(row, 'mjj'))

    return numbers


def getGenCandInfo(row, hPUWt, *objects):
    numbers = {}
    numbers['mZ1'] = nObjVar(row, 'Mass', objects[0], objects[1])
    if numbers['mZ1'] < 60.:
        return None
    numbers['mZ2'] = nObjVar(row, 'Mass', objects[2], objects[3])
    if numbers['mZ2'] < 60.:
        return None

    # eemm channel may have masses swapped
    if zMassDist(numbers['mZ1']) > zMassDist(numbers['mZ2']):
        temp = numbers['mZ2']
        numbers['mZ2'] = numbers['mZ1']
        numbers['mZ1'] = temp

    numbers['run'] = row.run
    numbers['lumi'] = row.lumi
    numbers['event'] = row.evt
    numbers['m4l'] = evVar(row, 'Mass')

    jetPts = evVar(row, 'jetPt')
    numbers['nJets'] = jetPts.size()
    if jetPts.size():
        numbers['jet1pt'] = jetPts.at(0)
        if jetPts.size() > 1:
            numbers['jet2pt'] = jetPts.at(1)
        else:
            numbers['jet2pt'] = -1.
    else:
        numbers['jet1pt'] = -1.
        numbers['jet2pt'] = -1.

    numbers['mjj'] = max(-1.,evVar(row, 'mjj'))

    return numbers


def getCandInfo3l(row, hPUWt, *objects):
    numbers = {}
    numbers['run'] = row.run
    numbers['lumi'] = row.lumi
    numbers['event'] = row.evt
    numbers['m3l'] = evVar(row, 'Mass')
    numbers['mZ'] = nObjVar(row, 'Mass', objects[0], objects[1])
    numbers['ptL3'] = objVar(row, 'Pt', objects[2])
    numbers['l3Tight'] = 1 if objVar(row, 'ZZTightID', objects[2]) and objVar(row, 'ZZIsoPass', objects[2]) else 0

    return numbers


def getAllInfo(channel, ntuple, fInfo, hPUWt):
    found = set()
    objects = getObjects(channel)
    if channel == 'emm':
        objects = objects[1:]+objects[:1]

    for row in ntuple:
        numbers = fInfo(row, hPUWt, *objects)
        if numbers is None:
            continue
        evtID = (numbers['run'],numbers['lumi'],numbers['event'])
        if evtID in found:
            continue
        found.add(evtID)
        yield numbers


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Dump information about the 4l candidates in an ntuple to a text file, for synchronization.')
    parser.add_argument('input', type=str, nargs=1, help='Input root file or glob to several')
    parser.add_argument('output', type=str, nargs='?', default='candSync.txt',
                        help='Name of the text file to output.')
    parser.add_argument('channels', nargs='?', type=str, default='zz',
                        help='Comma separated (no spaces) list of channels, or keyword indicated multiple channels')
    parser.add_argument('--listOnly', action='store_true',
                        help='Print only run:lumi:event with no further info')
    parser.add_argument('--zPlusL', '--zPlusl', action='store_true',
                        help='Use the Z+l control region format instead of the 4l format')
    parser.add_argument('--doGen', action='store_true',
                        help='Also make a file for the gen-level information')
    parser.add_argument('--puWeightFile', nargs='?', type=str,
                        default='puWeight_69200_24jan2017.root',
                        help='Name of pileup weight file, possibly relative to $zza/ZZAnalyzer/data/pileupReweighting/')


    args = parser.parse_args()

    with root_open(join(environ['zza'], 'ZZAnalyzer', 'data',
                        'pileupReweighting', args.puWeightFile)) as fPU:
        hPUWt = asrootpy(fPU.puScaleFactor)
        hPUWt.SetDirectory(0)

    if args.zPlusL and args.channels == 'zz':
        args.channels = 'zl'
    channels = parseChannels(args.channels)

    inFiles = glob(args.input[0])

    outStrings = []
    outStringsGen = []

    if args.listOnly:
        outTemp = '{run}:{lumi}:{event}:{channel}\n'
        infoGetter = getEventInfo
    elif args.zPlusL:
        outTemp = ('{run}:{lumi}:{event}:{channel}:{m3l:.2f}:{mZ:.2f}:{ptL3:.2f}:'
                   '{l3Tight}\n')
        infoGetter = getCandInfo3l
        args.doGen = False

    else:
        outTemp = ('{run}:{lumi}:{event}:{channel}:{m4l:.2f}:{mZ1:.2f}:{mZ2:.2f}:'
                   '{nJets}:{jet1pt:.2f}:{jet2pt:.2f}:{mjj:.2f}:{puWt:.4f}:{recoSF:.4f}:{selSF:.4f}:{nPU:.2f}\n')
        infoGetter = getCandInfo

    outTempGen = ('{run}:{lumi}:{event}:{channel}:{m4l:.2f}:{mZ1:.2f}:{mZ2:.2f}:'
                  '{nJets}:{jet1pt:.2f}:{jet2pt:.2f}:{mjj:.2f}\n')

    for channel in channels:
        if channel == 'emm':
            channelForStr = 'mme' # for sync with Torino
        else:
            channelForStr = channel

        if len(inFiles) == 1:
            with root_open(inFiles[0]) as fin:
                n = fin.Get(channel+'/ntuple')
                for numbers in getAllInfo(channel, n, infoGetter, hPUWt):
                    outStrings.append(outTemp.format(channel=channelForStr,
                                                     **numbers))
                if args.doGen:
                    n = fin.Get(channel+'Gen/ntuple')
                    for numbers in getAllInfo(channel, n, getGenCandInfo, hPUWt):
                        outStringsGen.append(outTempGen.format(channel=channelForStr,
                                                               **numbers))

        else:
            n = TreeChain(channel+'/ntuple', inFiles)
            for numbers in getAllInfo(channel, n, infoGetter, hPUWt):
                outStrings.append(outTemp.format(channel=channelForStr,
                                                     **numbers))
            if args.doGen:
                n = TreeChain(channel+'Gen/ntuple', inFiles)
                for numbers in getAllInfo(channel, n, getGenCandInfo, hPUWt):
                    outStringsGen.append(outTempGen.format(channel=channelForStr,
                                                           **numbers))

    with open(args.output, 'w') as fout:
        for s in sorted(outStrings, key=lambda x: [int(y) for y in x.split(':')[:3]]):
            fout.write(s)

    if args.doGen:
        if '.' in args.output:
            outputGen = 'Gen.'.join(args.output.rsplit('.',1))
        else:
            outputGen = args.output+'Gen'

        with open(outputGen, 'w') as fout:
            for s in sorted(outStringsGen, key=lambda x: [int(y) for y in x.split(':')[:3]]):
                fout.write(s)

