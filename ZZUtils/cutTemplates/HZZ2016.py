from Cutter import Cutter
from ZZHelpers import *


class HZZ2016(Cutter):
    def getCutTemplate(self,*args):
        '''
        Template for all cuts
        '''
        temp = super(HZZ2016, self).getCutTemplate(*args)

        if 'ZMassLoose' in temp:
            temp['ZMassLoose']['cuts']['Mass%s#lower'%self.fsrVar] = (12., ">=")
        else:
            temp['ZMassLoose'] = {
                'cuts' : { 
                    'Mass%s#lower'%self.fsrVar : (12., '>='),
                    'Mass%s#upper'%self.fsrVar : (120., '<'),
                    },
                'objects' : 2,
                }
        
        return temp


    def setupCutFlow(self):
        '''
        Only flow differences from full spectrum are Z mass cuts
        '''
        flow = super(HZZ2016, self).setupCutFlow()

        flow['Z2MassLoose'] = ('ZMassLoose', [3,4])

        return flow
