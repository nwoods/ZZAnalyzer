from Cutter import Cutter
from ZZHelpers import *


class HZZ2016(Cutter):
    def getCutTemplate(self,*args):
        '''
        Template for all cuts
        '''
        temp = super(HZZ2016, self).getCutTemplate(*args)

        temp['ZMassLoose']['cuts']['Mass%s#lower'%self.fsrVar] = (12., '>=')

        temp['4lMass']['cuts'] = {'Mass%s'%self.fsrVar : (70., ">=")}
        
        return temp


    def setupCutFlow(self):
        '''
        Only flow differences from full spectrum are that HZZ uses smart cut
        and has 4l mass cut.
        '''
        flow = super(HZZ2016, self).setupCutFlow()
        flow['4lMass'] = ('4lMass', [])
        flow['SmartCut'] = ('SmartCut', [1,2,3,4])

        return flow
