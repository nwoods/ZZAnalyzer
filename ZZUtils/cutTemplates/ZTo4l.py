
'''

Cutter for the 2015 H->ZZ group's Z->4l analysis.

Author: Nate Woods, U. Wisconsin

'''


from collections import OrderedDict
from FullSpectrum_FullFSR_Sync import FullSpectrum_FullFSR_Sync


class ZTo4l(FullSpectrum_FullFSR_Sync):
    def __init__(self, cutset="ZTo4l"):
        super(ZTo4l, self).__init__(cutset)


    def getCutTemplate(self, *args):
        '''
        Full spectrum analysis, but require low 4l invariant mass
        '''
        temp = super(ZTo4l, self).getCutTemplate()

        temp['4lMass']['cuts']['Mass'+self.fsrVar] = (110, "<")
        
        return temp
                

