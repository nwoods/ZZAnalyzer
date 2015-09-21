
'''

Cutter for same-sign control region for the 2015 HZZ4l analysis.
Inherits from the control region base class. The difference is that the second 
Z's leptons must be same sign, and do not need to pass tight ID or isolation.

Author: Nate Woods, U. Wisconsin

'''

from ControlRegion_Base import ControlRegion_Base
from collections import OrderedDict
from ZZHelpers import *


class ControlRegion_SS(ControlRegion_Base):
    def __init__(self, cutset="ControlRegion_SS"):
        super(ControlRegion_SS, self).__init__(cutset)


    def getCutTemplate(self, *args):
        '''
        Add a few cuts we need for the SS CR
        '''
        temp = super(ControlRegion_SS, self).getCutTemplate(self, *args)

        temp['SameSign'] = {
            'cuts' : {
                'SS' : (1, ">="),
            },
            'objects' : 2,
        }

        return temp


    def setupCutFlow(self):
        '''
        As the full spectum cutter, except as above
        '''
        signalFlow = super(ControlRegion_SS, self).setupCutFlow()

        crFlow = OrderedDict()
        for cut, params in signalFlow.iteritems():
            # Only the first two leptons have to be really good. 
            # The others only need to be loose + SIP
            if cut == 'LeptonID':
                parTemp = list(params)
                parTemp[1] = [1,2]
                crFlow['Z1ID'] = tuple(parTemp)
                crFlow['Z2LooseID'] = ('MediocreLeptons', [3,4])
            elif cut == 'Isolation':
                parTemp = list(params)
                parTemp[1] = [1,2]
                crFlow[cut] = tuple(parTemp)
            elif cut == 'GoodZ2':
                crFlow['BadZ2'] = ('SameSign', [3,4])
            else:
                crFlow[cut] = params

        return crFlow


    def orderLeptons(self, row, channel, objects):
        '''
        Put the real Z first. If both or neither are real, we don't really 
        care about order.
        '''
        alternateOrder = objects[2:] + objects[:2]
        if self.analysisCut(row, 'BadZ2', *alternateOrder):
            return alternateOrder
        return objects


    def doSmartCut(self, row, *obj):
        # Doesn't apply to eemm
        if obj[0][0] != obj[2][0]:
            return True

        altObj = [list(obj), list(obj)]

        # Find the proper alternate Z pairings. 
        ssInd = 0 # index of Z1 same-sign lepton
        if nObjVar(row, 'SS', obj[1], obj[2]):
            ssInd += 1
        for i in range(2):
            altObj[i][ssInd] = obj[i+2]
            altObj[i][i+2] = obj[ssInd]

        altZMass = [[nObjVar(row, "Mass"+self.fsrVar, *sorted(obs[:2])), nObjVar(row, "Mass"+self.fsrVar, *sorted(obs[2:]))] for obs in altObj]
        altZCompatibility = [[zMassDist(m) for m in mAlt] for mAlt in altZMass]
        z1Compatibility = zCompatibility(row, obj[0], obj[1], self.fsrVar)

        zACompatibility = []
        zBMass = []
        for i in range(len(altZMass)):
            if altZCompatibility[i][0] < altZCompatibility[i][1]:  # Za is first
                zACompatibility.append(altZCompatibility[i][0])
                zBMass.append(altZMass[i][1])
            else:
                zACompatibility.append(altZCompatibility[i][1])
                zBMass.append(altZMass[i][0])

        return not any((zACompatibility[i] < z1Compatibility and zBMass[i] < 12) for i in range(2))
