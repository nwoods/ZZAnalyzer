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
    def __init__(self, cutter, initChannel='eeee'):
        '''
        Set up most data needed by all cleaners (basic previous event info, 
        channels, etc.).
        '''
        self.cleanAtEnd = True # Daughter class should overwrite!
        
        self.bestRows = {}

        self.cuts = cutter
        
        self.setChannel(initChannel)

        self.prevRun = -1
        self.prevLumi = -1
        self.prevEvt = -1
        self.prevInfo = None
        
        
    def setChannel(self, channel):
        '''
        Set the cutter's channel for future rows. 
        '''
        self.channel = channel
        self.objectTemplate = mapObjects(channel)
        self.needReorder = self.cuts.needReorder(self.channel)
                       
                       
    def betterRow(self, a, b):
        '''
        Virtual.

        Given two RowInfos a and b, returns the better one.
        '''
        return a # daughter class should override
                       

    def cleanAfter(self):
        '''
        Returns True if cleaning should be done after other cuts are performed,
        or False if cleaning should be done first thing.
        '''
        return self.cleanAtEnd


    def finalize(self):
        '''
        Save the correct row for the last event, so we don't forget it.
        '''
        self.bestRows[(self.prevRun, self.prevLumi, self.prevEvt)] = self.prevInfo
        

    def bookRow(self, row, idx):
        '''
        If this row is from the same event as the previous, check 
        which is better and hang onto its info. If it's from a different event,
        enshrine the best row of the previous event, then check to make sure we
        didn't have the new event previously in another channel. If we 
        did, compare this new row with the info from the other channel. If we 
        didn't, hang onto this info so we can compare it to the next row.
        '''
        run = row.run
        lumi = row.lumi
        evt = row.evt
        newEvent = (evt != self.prevEvt or lumi != self.prevLumi or run != self.prevRun)

        if self.needReorder:
            objects = self.cuts.orderLeptons(row, self.channel, self.objectTemplate)
        else:
            objects = self.objectTemplate

        info = self.__class__.RowInfo(row, self.channel, idx, objects, self.cuts)

        if newEvent:
            self.bestRows[(self.prevRun, self.prevLumi, self.prevEvt)] = self.prevInfo
            
            self.prevRun = run
            self.prevLumi = lumi
            self.prevEvt = evt

            if (run, lumi, evt) in self.bestRows:
                # this event existed in another channel
                self.prevInfo = self.bestRows[(run, lumi, evt)]
                newEvent = False
            else:
                self.prevInfo = info
                
        if not newEvent:
            self.prevInfo = self.betterRow(info, self.prevInfo)


    def isRedundant(self, row, channel, idx):
        '''
        Return True if the row with this index is not the best version
        of its event.
        '''
        return not self.isBestCand(row, channel, idx)


    def isBestCand(self, row, channel, idx):
        '''
        Return True if the row with this index is the best version of its event
        '''
        info = self.bestRows.get((row.run, row.lumi, row.evt), None)
        if info is None:
            return False
        
        ch = info.channel
        ind = info.idx
        return (ind == idx and ch == channel)


    class RowInfo(object):
        '''
        Base class for a simple container for variables needed to compare rows.
        Row cleaner classes should define an inheriting RowInfo class that 
        knows the right variables and how to calculate them.
        '''
        def __init__(self, row, channel, idx, objects, cuts):
            '''
            Objects should already be sorted
            '''
            self.channel = channel
            self.idx = idx
            self.storeVars(row, objects, cuts)

        def storeVars(self, row, objects, cuts):
            '''
            Virtual.
            Inheriting classes should calculate needed variables here.
            '''
            self.one = 1 # don't do this


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


