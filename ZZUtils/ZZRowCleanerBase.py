'''

Base class for utilities to clean redundant rows out of ntuples.

Analyzer passes in rows and corresponding indices with bookRow(row, iRow). 
Row Cleaner keeps track of what event it saw last, and the best row for that
event. When it sees a new row for that same event, it picks which is better. 
Each time it sees a new event, it places the index of the best row from
the previous event into a set of good rows. This means that all rows for an 
event must be booked consecutively! The analyzer can then query the Row Cleaner
to see if a row is in the set with isRedundant(iRow) or isBestCand(iRow).

Daughter classes must define:
    - isNewBest(row, newEvent) to determine if this row is better than the last
      and, if so, to store necessary information about it. newEvent is a boolean
      that, if True, means this is definitely the new best (presumably because
      it's the first row from the new event)
    - Enough data about the previous best row to know
    - self.cleanAtEnd, which should be True if cleaning is to be performed
      after all other cuts, and False if it should be done before.


Author: Nate Woods, U. Wisconsin

'''



class ZZRowCleanerBase(object):
    '''
    Virtual class with methods that will always be needed for a row cleaner.
    '''

    def __init__(self, channel, cutter):
        '''
        Set up data needed by all cleaners (basic previous event info, 
        '''
        self.cleanAtEnd = True # Daughter class should overwrite!

        self.bestRows = set()

        self.channel = channel
        self.objectTemplate = mapObjects(self.channel)
        # Sometimes need to check that best Z is listed first
        self.needReorder = self.objectTemplate[0][0] != self.objectTemplate[-1][0]
        self.cuts = cutter

        # Set up information about the previous best row for this event
        self.prevIdx = -1
        self.prevRun = -1
        self.prevLumi = -1
        self.prevEvt = -1
        ### daughter classes should define variables needed to compare rows



    def isNewBest(self, row, newEvent):
        '''
        Virtual.
        Check if this row is better than the previous best for its event, and,
        if this row is better, store its information. newEvent is a boolean
        indicating that the new event is definitely the new best and can be 
        stored without checking (probably because it's the first of an event).
        '''
        return newEvent # Takes the first unless overwritten (it should be)


    def cleanAfter(self):
        '''
        Returns True if cleaning should be done after other cuts are performed,
        or False if cleaning should be done first thing.
        '''
        return self.cleanAtEnd


    def bookRow(self, row, idx):
        '''
        If this row is from the same event as the previous, check 
        which is better and store its info. If it's from a different event,
        enshrine the previous best row and make this the new one.
        '''
        run = row.run
        lumi = row.lumi
        evt = row.evt
        newEvent = (evt != self.prevEvt or lumi != self.prevLumi or run != self.prevRun)

        if newEvent: # store the best from the last event
            self.bestRows.add(self.prevIdx)
            self.prevRun = run
            self.prevLumi = lumi
            self.prevEvt = evt

        # isNewBest automatically stores other info if this is the new best
        if self.isNewBest(row, newEvent):
            self.prevIdx = idx


    def isRedundant(self, idx):
        '''
        Return True if the row with this index is not the best version
        of its event.
        '''
        return not self.isBestCand(idx)


    def isBestCand(self, idx):
        '''
        Return True if the row with this index is the best version of its event
        '''
        return idx in self.bestRows


def mapObjects(channel):
    '''
    Return a list of objects of the form ['e1','e2','m1','m2'] or ['e1','e2','m']
    Objects are in alphabetical/numerical order order
    '''
    nObjects = {}
    objects = []

    for obj in channel:
        if obj not in nObjects:
            nObjects[obj] = 1
        else:
            nObjects[obj] += 1

    for obj, num in nObjects.iteritems():
        if num == 1:
            objects.append(obj)
        else:
            for i in range(num):
                objects.append(obj+str(i+1))
    
    objects.sort()

    return objects


