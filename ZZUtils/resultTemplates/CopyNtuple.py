'''

Copy any passing row exactly.
Inherits from ZZNtupleSaver, which inherits from ZZResultSaverBase

Author: Nate Woods, U. Wisconsin

'''


from ZZNtupleSaver import ZZNtupleSaver


class CopyNtuple(ZZNtupleSaver):
    def __init__(self, fileName, channels, inputNtuples, *args, **kwargs):
        self.inputs = inputNtuples
        self.channels = channels
        super(CopyNtuple, self).__init__(fileName, channels, *args, **kwargs)


    def setupTemplate(self):
        template = {}

        for channel in self.channels:
            template[channel] = {'final':{'vars':{'copy':{'ntuple':self.inputs[channel]}}}}
    
        return template


