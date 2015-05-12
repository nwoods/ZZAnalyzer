
'''

Cutter for the 2015 H->ZZ->4l analysis with non-isolated AKFSR.
Inherits from the full spectrum cutter.

Author: Nate Woods, U. Wisconsin

'''


from collections import OrderedDict
from FullSpectrum_FullFSR_Sync import FullSpectrum_FullFSR_Sync
from ZZHelpers import *


class FullSpectrum_AKFSRNIso(FullSpectrum_FullFSR_Sync):
    def __init__(self, cutset="FullSpectrum_AKFSRNIso"):
        super(FullSpectrum_AKFSRNIso, self).__init__(cutset)


    def getCutTemplate(self, *args):
        '''
        Use AK FSR
        '''
        temp = super(FullSpectrum_AKFSRNIso, self).getCutTemplate()

        del temp['mIso']['cuts']['RelPFIsoDBDefaultFSR']
        temp['mIso']['cuts']['RelPFIsoDBAKFSRNIso'] = (0.4, "<")
        del temp['eIso']['cuts']['RelPFIsoRhoFSR']
        temp['eIso']['cuts']['RelPFIsoRhoAKFSRNIso'] = (0.5, "<")

        del temp['ZMassLoose']['cuts']['MassFSR#lower']
        del temp['ZMassLoose']['cuts']['MassFSR#upper']
        temp['ZMassLoose']['cuts']['MassAKFSRNIso#lower'] = (12., '>=')
        temp['ZMassLoose']['cuts']['MassAKFSRNIso#upper'] = (120., '<')

        del temp['ZMassTight']['cuts']['MassFSR#lower']
        temp['ZMassTight']['cuts']['MassAKFSRNIso#lower'] = (40, ">=")
        del temp['ZMassTight']['cuts']['MassFSR#upper']
        temp['ZMassTight']['cuts']['MassAKFSRNIso#upper'] = (120, "<")

        del temp['4lMass']['cuts']['MassFSR']

        temp['4lMass']['cuts']['MassAKFSRNIso'] = (70, ">=")

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

        altZMass = [nObjVar(row, "MassAKFSRNIso", *sorted(altObj[:2])), nObjVar(row, "MassAKFSRNIso", *sorted(altObj[2:]))]
        altZCompatibility = [zMassDist(m) for m in altZMass]
        z1Compatibility = zCompatibility(row, obj[0], obj[1], fsrType="AKFSRNIso")

        if altZCompatibility[0] < altZCompatibility[1]:  # Za is first
            zACompatibility = altZCompatibility[0]
            zBMass = altZMass[1]
        else:
            zACompatibility = altZCompatibility[1]
            zBMass = altZMass[0]

        return not (zACompatibility < z1Compatibility and zBMass < 12)
