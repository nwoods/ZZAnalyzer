
'''

Cutter for the 2015 H->ZZ->4l analysis with no FSR.
Inherits from the full spectrum cutter.

Author: Nate Woods, U. Wisconsin

'''


from collections import OrderedDict
from FullSpectrum_FullFSR_Sync import FullSpectrum_FullFSR_Sync
from ZZHelpers import *


class FullSpectrum_NoFSR(FullSpectrum_FullFSR_Sync):
    def __init__(self, cutset="FullSpectrum_NoFSR"):
        super(FullSpectrum_NoFSR, self).__init__(cutset)


    def getCutTemplate(self, *args):
        '''
        Use no FSR
        '''
        temp = super(FullSpectrum_NoFSR, self).getCutTemplate()

        del temp['mIso']['cuts']['RelPFIsoDBDefaultFSR']
        temp['mIso']['cuts']['RelPFIsoDBDefault'] = (0.4, "<")
        del temp['eIso']['cuts']['RelPFIsoRhoFSR']
        temp['eIso']['cuts']['RelPFIsoRho'] = (0.5, "<")

        del temp['ZMassLoose']['cuts']['MassFSR#lower']
        del temp['ZMassLoose']['cuts']['MassFSR#upper']
        temp['ZMassLoose']['cuts']['Mass#lower'] = (12., '>=')
        temp['ZMassLoose']['cuts']['Mass#upper'] = (120., '<')

        del temp['ZMassTight']['cuts']['MassFSR#lower']
        temp['ZMassTight']['cuts']['Mass#lower'] = (40, ">=")
        del temp['ZMassTight']['cuts']['MassFSR#upper']
        temp['ZMassTight']['cuts']['Mass#upper'] = (120, "<")

        del temp['4lMass']['cuts']['MassFSR']

        temp['4lMass']['cuts']['Mass'] = (70, ">=")

        return temp
    

    def doSmartCut(self, row, *obj):
        # Doesn't apply to eemm
        if obj[0][0] != obj[2][0]:
            return True

        # Find the proper alternate Z pairing. We already checked that we have 2 OS pairs
        if nObjVar(row, 'SS', *sorted([obj[0], obj[2]])): # l1 matches l4
            altObj = [obj[0], obj[3], obj[1], obj[2]]
        else: # l1 matches l3
            altObj = [obj[0], obj[2], obj[1], obj[3]]

        altZMass = [nObjVar(row, "Mass", *sorted(altObj[:2])), nObjVar(row, "Mass", *sorted(altObj[2:]))]
        altZCompatibility = [zMassDist(m) for m in altZMass]
        z1Compatibility = zCompatibility(row, obj[0], obj[1], False)

        if altZCompatibility[0] < altZCompatibility[1]:  # Za is first
            zACompatibility = altZCompatibility[0]
            zBMass = altZMass[1]
        else:
            zACompatibility = altZCompatibility[1]
            zBMass = altZMass[0]

        return not (zACompatibility < z1Compatibility and zBMass < 12)
