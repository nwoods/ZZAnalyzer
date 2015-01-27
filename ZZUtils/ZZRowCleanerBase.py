'''

Base class for utilities to clean redundant rows out of ntuples.

Author: Nate Woods, U. Wisconsin

'''



class ZZRowCleanerBase(object):
    '''
    Virtual class with methods that will always be needed for a row cleaner.
    '''

    def __init__(self, ntuple, channel, cutter, sampleName, maxEvents=float('inf')):
        '''
        Redundant rows are found immediately on initialization and stored as a
        set.
        '''
        self.ntuple = ntuple
        self.channel = channel
        self.objectTemplate = mapObjects(self.channel)
        # Sometimes need to check that best Z is listed first
        self.needReorder = self.objectTemplate[0][0] != self.objectTemplate[-1][0]
        self.cuts = cutter
        self.sampleName = sampleName
        self.maxEvents = maxEvents

        self.redundantRows = self.getRedundantRows()


    def getRedundantRows(self):
        '''
        Virtual.
        Used by daughter classes to loop through all rows in an ntuple and 
        return a set containing the entry numbers of the ones that can be
        ignored.
        '''
        pass


    def isRedundant(self, nRow):
        '''
        Return True if the row with this entry number is not the best version
        of its event.
        '''
        return nRow in self.redundantRows


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


