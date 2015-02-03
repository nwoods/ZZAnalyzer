'''

Redundant row cleaner using Simon's algorithm that picks the best candidate
last (then does another cut, not included here).

Author: Nate Woods, U. Wisconsin.

'''

from ZZRowCleanerBase import ZZRowCleanerBase
from ZZHelpers import * # evVar, objVar, nObjVar, Z_MASS


class HZZ4l2012Cleaner(ZZRowCleanerBase):
    def __init__(self, ntuple, channel, cutter, sampleName, maxEvents=float('inf')):
        super(HZZ4l2012Cleaner, self).__init__(ntuple, channel, cutter, sampleName, maxEvents)


    def getRedundantRows(self):
        '''
        Returns a set of row numbers of rows that are the incorrect combinatorial
        version of the relevant event. The correct row is the one with Z1 closest
        to on-shell, with the highest scalar Pt sum of the remaining leptons used as a 
        tiebreaker
        '''
        nRow = 0
        nEvent = 0
        redundantRows = set()

        prevRun = -1
        prevLumi = -1
        prevEvt = -1
        prevDZ = 999.
        prevPtSum = -999.
        prevRow = -1

        # make a copy in case we have to reorder
        objects = self.objectTemplate
        
        for row in self.ntuple:
            if nEvent == self.maxEvents:
                print "%s: Found redundant rows for %d %s events"%(self.sampleName, self.maxEvents, self.channel)
                break

            if nRow % 5000 == 0:
                print "%s: Finding redundant rows %s row %d"%(self.sampleName, self.channel, nRow)
            nRow += 1

            if self.needReorder:
                objects = orderLeptons(row, self.channel, self.objectTemplate)

            # Keep track of events within this function by run, lumi block, and event number
            run =  evVar(row, 'run')
            lumi = evVar(row, 'lumi')
            evt =  evVar(row, 'evt')
            sameEvent = (evt == prevEvt and lumi == prevLumi and run == prevRun)

            if not sameEvent:
                nEvent += 1

            dZ = zCompatibility(row, objects[0], objects[1])
            ptSum = objVar(row, 'Pt', objects[2]) + objVar(row, 'Pt', objects[3])

            # if this doesn't seem to be a duplicate event, we don't need to do anything but store
            # its info in case it's the first of several
            if not sameEvent:
                prevRun = run
                prevLumi = lumi
                prevEvt = evt
                prevDZ = dZ
                prevPtSum = ptSum
                prevRow = nRow
                continue
            else:
                if dZ < prevDZ:
                    redundantRows.add(prevRow)
                    prevRun = run
                    prevLumi = lumi
                    prevEvt = evt
                    prevDZ = dZ
                    prevPtSum = ptSum
                    prevRow = nRow
                elif dZ == prevDZ:
                    if ptSum > prevPtSum:
                        redundantRows.add(prevRow)
                        prevRun = run
                        prevLumi = lumi
                        prevEvt = evt
                        prevDZ = dZ
                        prevPtSum = ptSum
                        prevRow = nRow
                    else:
                        redundantRows.add(nRow)
                else:
                    redundantRows.add(nRow)
        else:
            print "%s: Found redundant rows for %d %s events"%(self.sampleName, nRow, self.channel)
                    
        return redundantRows
       
 
def orderLeptons(row, channel, objects):
    '''
    Put best (closest to nominal mass) Z candidate first. 
    FSA does this automatically for 4e and 4mu cases.
    Assumes 4 leptons, with (l1,l2) and (l3,l4) same-flavor pairs;
    will have to be overloaded for other final states.
    '''
    if channel == 'eeee' or channel == 'mmmm':
        return objects

    dM1 = zCompatibility(row,objects[0],objects[1])
    dM2 = zCompatibility(row,objects[2],objects[3])
    
    if dM1 > dM2:
        return objects[2:] + objects[:2]
    return objects


def zCompatibility(row, ob1, ob2):
    '''
    Absolute distance from Z mass. 1000 if same sign.
    '''
    if nObjVar(row, 'SS', ob1, ob2):
        return 1000
    return abs(nObjVar(row, "MassFSR", ob1, ob2) - Z_MASS)


