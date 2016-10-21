'''

A greatly simplified way to copy the passing rows of ntuples, because that's
all we ever do anyway.

Nate Woods, U. Wisconsin

'''


from rootpy.io import root_open, Directory
from rootpy.tree import Tree


class NtupleCopier(object):
    def __init__(self, fileName, *args, **ntuples):
        self.channels = ntuples.keys()

        self.file = root_open(fileName, 'recreate')
        # assume all ntuples from same file
        self.ntupleFile = ntuples.values()[0].GetDirectory().GetFile()

        self.ntuples = self.makeNtuples(self.file, *args, **ntuples)


    def makeNtuples(self, outFile, *args, **ntuplesIn):
        out = {}

        for channel, nIn in ntuplesIn.iteritems():
            outFile.cd()
            d = self.file.mkdir(nIn.GetDirectory().GetPath().split(':/')[-1],
                                recurse=True)
            d.cd()

            out[channel] = Tree(nIn.GetName())

            if not nIn._buffer:
                nIn.create_buffer()
            out[channel].set_buffer(nIn._buffer, create_branches=True, visible=True)

        return out


    def saveRow(self, row, channel, *args, **kwargs):
        self.ntuples[channel].fill()


    def save(self, *exclude, **kwargs):
        self.writeNtuples(**kwargs)

        self.copyEverythingElse(*exclude, **kwargs)

        self.file.close()


    def writeNtuples(self, **kwargs):
        for n in self.ntuples.values():
            n.write()


    def copyEverythingElse(self, *exclude, **kwargs):
        '''
        Copies everything in the input file except those containing input
        ntuples and those listed in exclude.
        TODO: make this copy non-ntuple things in ntuple directories too.
        TODO: right now, this only works for directories, TTrees, or other
        objects with a copytree method.
        '''
        exclude = set(list(exclude) + [k.GetName() for k in self.file.keys()])

        for key in self.ntupleFile.keys(True):
            k = key.GetName()
            if k not in exclude:
                getattr(self.ntupleFile, k).copytree(self.file)

