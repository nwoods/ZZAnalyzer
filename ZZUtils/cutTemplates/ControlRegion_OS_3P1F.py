
'''

Cutter for opposite-sign control region for the 2015 HZZ4l analysis, 
where exactly one lepton is fake. Inherits from the control region base class. 
The difference is that exactly one of the second Z's leptons must pass loose
ID and SIP but fail tight ID and isolation

Author: Nate Woods, U. Wisconsin

'''

from ControlRegion_Base import ControlRegion_Base
from collections import OrderedDict


class ControlRegion_OS_3P1F(ControlRegion_Base):
    def __init__(self, cutset="ControlRegion_OS_3P1F"):
        super(ControlRegion_OS_3P1F, self).__init__(cutset)


    def getCutTemplate(self, *args):
        '''
        Add a few cuts we need for the SS CR
        '''
        temp = super(ControlRegion_OS_3P1F, self).getCutTemplate(self, *args)

        # At least one lepton is fake
        temp['OneFakeLepton'] = {
            'cuts' : {
                'loose' : 'leptonLooseID',
                'fake' : 'FailTightOrIso',
            },
            'logic' : 'objor',
        }
        
        # At least one lepton is real
        temp['OnePromptLepton'] = {
            'cuts' : {
                'id' : 'leptonTightID',
                'iso' : 'LeptonIso',
            },
            'logic' : 'objor',
        }

        # We can ensure exactly one fake by requiring at least one of the two 
        # to be real and at least one of the two to be fake
        temp['OnePromptOneFake'] = {
            'cuts' : {
                'oneFake' : 'OneFakeLepton',
                'oneReal' : 'OnePromptLepton',
            },
            'objects' : 2,
        }

        # Make sure this event isn't in the signal region by making sure 
        # there's not a tight lepton of the same type as the fake also
        # in the event
        temp['ExtraLepVeto'] = {
            'cuts' : {
                'veto' : 'TYPEVetoTightIso',
                },
            'objects' : 1,
            }
        temp['eVetoTightIso'] = {
            'cuts' : {
                'eVetoTightIso' : (0.9, "<"),
                },
            'objects' : 'ignore',
            }
        temp['mVetoTightIso'] = {
            'cuts' : {
                'muVetoTightIso' : (0.9, "<"),
                },
            'objects' : 'ignore',
            }

        return temp


    def setupCutFlow(self):
        '''
        As the full spectum cutter, except as above
        '''
        signalFlow = super(ControlRegion_OS_3P1F, self).setupCutFlow()

        crFlow = OrderedDict()
        for cut, params in signalFlow.iteritems():
            # Only the first two leptons have to be really good. 
            # The others only need to be loose + SIP
            if cut == 'LeptonID':
                parTemp = list(params)
                parTemp[1] = [1,2]
                crFlow['Z1ID'] = tuple(parTemp)
                # do isolation now
                isoParams = list(signalFlow.pop('Isolation'))
                isoParams[1] = [1,2]
                crFlow['Z1Iso'] = tuple(isoParams)
                # require 1P1F in the other Z now
                crFlow['PromptPlusFake'] = ('OnePromptOneFake', [3,4])
            elif cut == 'Isolation':
                pass # shouldn't happen, since we popped it
            else:
                crFlow[cut] = params
        crFlow['ExtraLeptonVeto'] = ('ExtraLepVeto', [3])

        return crFlow


    def orderLeptons(self, row, channel, objects):
        '''
        Put the real Z first. If both or neither are real, we don't really 
        care about order.
        '''
        alternateOrder = objects[2:] + objects[:2]
        if self.analysisCut(row, 'PromptPlusFake', *alternateOrder):
            return alternateOrder
        return objects
