'''

Copy any passing row exactly.
Inherits from NtupleSaver, which inherits from ResultSaverBase

Author: Nate Woods, U. Wisconsin

'''


from ZZAnalyzer.results import NtupleSaver


class CopyNtuple(NtupleSaver):
    def __init__(self, fileName, channels, inputNtuples, *args, **kwargs):
        self.inputs = inputNtuples
        self.channels = channels
        super(CopyNtuple, self).__init__(fileName, channels, *args, **kwargs)


    def setupTemplate(self):
        template = {}

        for channel in self.channels:
            template[channel] = {'final':{'vars':{'copy':{'ntuple':self.inputs[channel]}}}}
    
        return template


