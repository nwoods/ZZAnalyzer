
'''

Cutter than requires a good Z (leptons and Z candidate pass analysis Z1
cuts)... and nothing else.

Author: Nate Woods, U. Wisconsin

'''

from SMPZZ_FullFSR_Sync import SMPZZ_FullFSR_Sync
from collections import OrderedDict
from ZZHelpers import Z_MASS, evVar, objVar, nObjVar
from rootpy.vector import LorentzVector


class ZPlusAnything(SMPZZ_FullFSR_Sync):
    def __init__(self, cutset="ZPlusAnything"):
        super(ZPlusAnything, self).__init__(cutset)


    def setupCutFlow(self):
        '''
        As the full spectum cutter, except as above
        '''
        flow = OrderedDict()
        
        flow['Total'] = ('true', [])
        flow['Trigger'] = ('Trigger', [])
        flow['ZLeptonID'] = ('GoodLeptons', [1,2])
        flow['ZLeptonIso'] = ('Isolation', [1,2])
        flow['CrossCleaning'] = ('CrossCleaning', [1,2])
        flow['SIP'] = ('SIP', [1,2])
        flow['GoodZ'] = ('GoodZ', [1,2])
        flow['ZMass'] = ('ZMassTight', [1,2])
        flow['Overlap'] = ('Overlap', [1,2])
        flow['Lepton1Pt'] = ('Lepton1Pt', [1])
        flow['Lepton2Pt'] = ('Lepton2Pt', [1,2])
        flow['Vertex'] = ('Vertex', [])
        
        return flow


    def needReorder(self, channel):
        '''
        In order to make this work for 3 or 4l, we have to be slightly tricky.
        '''
        if channel == 'emm':
            self.orderLeptons = self.orderLeptonsEMM
            return True

        if len(channel) == 4:
            self.orderLeptons = self.realZFirst
            return True

        return False


    def orderLeptonsEMM(self, row, channel, objects):
        '''
        In 1e2mu channel, muons always go first
        '''
        return ['m1', 'm2', 'e']


    def realZFirst(self, row, channel, objects):
        '''
        For use with 4l final states only. If the second Z is made out of
        tight + isolated leptons and the first isn't, swap them.
        '''
        if (objVar(row, 'HZZTightID', objects[2]) < 0.5 or
            objVar(row, 'HZZTightID', objects[3]) < 0.5 or
            objVar(row, 'HZZIsoPass', objects[2]) < 0.5 or
            objVar(row, 'HZZIsoPass', objects[3]) < 0.5 or
            nObjVar(row, 'SS', objects[2], objects[3])):
            return objects
        
        if (objVar(row, 'HZZTightID', objects[0]) < 0.5 or
            objVar(row, 'HZZTightID', objects[1]) < 0.5 or
            objVar(row, 'HZZIsoPass', objects[0]) < 0.5 or
            objVar(row, 'HZZIsoPass', objects[1]) < 0.5):
            return objects[2:]+objects[:2] # Z2 good, Z1 not (Z1 guaranteed OSSF if Z2 is)

        # if both are good, order however the base class would
        if super(ZPlusAnything, self).needReorder(channel):
            return super(ZPlusAnything, self).orderLeptons(row, channel, objects)
        return objects

