
'''

Base Cutter for control regions in the 2015 HZZ4l analysis. Defines some loose
ID cuts and other things useful for CRs.

Author: Nate Woods, U. Wisconsin

'''

from FullSpectrum_FullFSR_Sync import FullSpectrum_FullFSR_Sync


class ControlRegion_Base(FullSpectrum_FullFSR_Sync):
    def __init__(self, cutset="ControlRegion_Base"):
        super(ControlRegion_Base, self).__init__(cutset)


    def getCutTemplate(self, *args):
        '''
        Define a few useful cuts for CRs
        '''
        temp = super(ControlRegion_Base, self).getCutTemplate(self, *args)

        temp['leptonLooseID'] = {
            'cuts' : {
                'id' : 'TYPELooseID',
            },
            'objects' : 1,
        }

        temp['MediocreLeptons'] = {
            'cuts' : {
                'id' : 'leptonLooseID',
            },
            'logic' : 'objand',
        }

        return temp


    def needReorder(self, *args):
        '''
        In the control regions, we always need to check to see if things ought
        to be reordered (the real Z is always first).
        '''
        return True



