from Cutter import Cutter
from ZZHelpers import *


class HZZ2016(Cutter):
    def getCutTemplate(self,*args):
        '''
        Template for all cuts
        '''
        temp = super(HZZ2016, self).getCutTemplate(*args)

        temp['ZMassLoose']['cuts']['Mass%s#lower'%self.fsrVar] = (12., '>=')

        return temp
