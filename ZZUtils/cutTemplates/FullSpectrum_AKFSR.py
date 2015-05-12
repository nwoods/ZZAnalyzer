
'''

Cutter for the 2015 H->ZZ->4l analysis with AKFSR.
Inherits from the full spectrum cutter.

Author: Nate Woods, U. Wisconsin

'''


from collections import OrderedDict
from FullSpectrum_FullFSR_Sync import FullSpectrum_FullFSR_Sync
from ZZHelpers import *


class FullSpectrum_AKFSR(FullSpectrum_FullFSR_Sync):
    def __init__(self, cutset="FullSpectrum_AKFSR"):
        super(FullSpectrum_AKFSR, self).__init__(cutset)


    def getCutTemplate(self, *args):
        '''
        Use AK FSR
        '''
        temp = super(FullSpectrum_AKFSR, self).getCutTemplate()

        del temp['mIso']['cuts']['RelPFIsoDBDefaultFSR']
        temp['mIso']['cuts']['RelPFIsoDBAKFSR'] = (0.4, "<")
        del temp['eIso']['cuts']['RelPFIsoRhoFSR']
        temp['eIso']['cuts']['RelPFIsoRhoAKFSR'] = (0.5, "<")

        del temp['ZMassLoose']['cuts']['MassFSR#lower']
        del temp['ZMassLoose']['cuts']['MassFSR#upper']
        temp['ZMassLoose']['cuts']['MassAKFSR#lower'] = (12., '>=')
        temp['ZMassLoose']['cuts']['MassAKFSR#upper'] = (120., '<')

        del temp['ZMassTight']['cuts']['MassFSR#lower']
        temp['ZMassTight']['cuts']['MassAKFSR#lower'] = (40, ">=")
        del temp['ZMassTight']['cuts']['MassFSR#upper']
        temp['ZMassTight']['cuts']['MassAKFSR#upper'] = (120, "<")

        del temp['4lMass']['cuts']['MassFSR']

        temp['4lMass']['cuts']['MassAKFSR'] = (70, ">=")

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

        altZMass = [nObjVar(row, "MassAKFSR", *sorted(altObj[:2])), nObjVar(row, "MassAKFSR", *sorted(altObj[2:]))]
        altZCompatibility = [zMassDist(m) for m in altZMass]
        z1Compatibility = zCompatibility(row, obj[0], obj[1], fsrType="AKFSR")

        if altZCompatibility[0] < altZCompatibility[1]:  # Za is first
            zACompatibility = altZCompatibility[0]
            zBMass = altZMass[1]
        else:
            zACompatibility = altZCompatibility[1]
            zBMass = altZMass[0]

        return not (zACompatibility < z1Compatibility and zBMass < 12)
