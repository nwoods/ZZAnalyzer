
'''

Cutter for opposite-sign control region for the 2015 HZZ4l analysis, where 
exactly two leptons are fake. Inherits from the control region base class.
The difference is that the second Z's leptons must pass loose
ID and SIP but fail tight ID and isolation

Author: Nate Woods, U. Wisconsin

'''

from ZZAnalyzer.cuts.cutTemplates.ControlRegion_Base import ControlRegion_Base

from collections import OrderedDict


class ControlRegion_OS_2P2F(ControlRegion_Base):
    def __init__(self, cutset="ControlRegion_OS_2P2F"):
        super(ControlRegion_OS_2P2F, self).__init__(cutset)


    def getCutTemplate(self, *args):
        '''
        Add a few cuts we need for the 2P2F OS CR
        '''
        temp = super(ControlRegion_OS_2P2F, self).getCutTemplate(self, *args)

        # Leptons are fake (pass loose ID, fail tight ID or isolation)
        temp['FakeID'] = {
            'cuts' : {
                'loose' : 'leptonLooseID',
                'areFake' : 'FailTightOrIso',
            },
            'logic' : 'objand',
        }

        # Make sure this event isn't in the 3P1F region by making sure 
        # there's not a tight lepton of the same type as the fakes also
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
        signalFlow = super(ControlRegion_OS_2P2F, self).setupCutFlow()

        crFlow = OrderedDict()
        for cut, params in signalFlow.iteritems():
            # Only the first two leptons have to be really good. 
            # The others must be fake
            if cut == 'LeptonID':
                parTemp = list(params)
                parTemp[1] = [1,2]
                crFlow['Z1ID'] = tuple(parTemp)
            elif cut == 'Isolation':
                parTemp = list(params)
                parTemp[1] = [1,2]
                crFlow['Z1Iso'] = tuple(parTemp)
                # Require the other two to be fake
                crFlow['Z2FakeID'] = ('FakeID', [3,4])
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
        if self.analysisCut(row, 'Z1ID', *alternateOrder) and self.analysisCut(row, 'Z1Iso', *alternateOrder):
            return alternateOrder
        return objects

