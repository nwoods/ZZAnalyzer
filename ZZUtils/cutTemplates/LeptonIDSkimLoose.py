
'''

Cutter for loosely skimming on lepton ID for the 2015 HZZ4l analysis.
Inherits from the SMP ZZ->4l Cutter.

Requires tight ID and isolation on the better Z candidate's leptons, loose ID 
on the other two leptons, and other basic cuts like trigger, vertex, etc. 
Z1 must be an OSSF pair in the tight mass window, Z2 must be in the loose
mass window. The idea is to skim events that can be used for signal or 
control regions.

Author: Nate Woods, U. Wisconsin

'''

from SMPZZ_FullFSR_Sync import SMPZZ_FullFSR_Sync

from collections import OrderedDict

class LeptonIDSkimLoose(SMPZZ_FullFSR_Sync):
    def __init__(self, cutset="LeptonIDSkimLoose"):
        super(LeptonIDSkimLoose, self).__init__(cutset)


    def setupCutFlow(self):
        '''
        As the full spectum cutter, but don't do anything afterlepton ID
        '''
        flow = OrderedDict()
        flow['Total'] = ('true', [])
        flow['Vertex'] = ('Vertex', [])
        flow['Trigger'] = ('Trigger', [])
        flow['Z1LeptonTightID'] = ('GoodLeptons', [1,2])
        flow['Z1Isolation'] = ('Isolation', [1,2])
        flow['Z2LeptonLooseID'] = ('OKLeptons', [3,4])
        flow['CrossCleaning'] = ('CrossCleaning', [1,2,3,4])
        flow['GoodZ1'] = ('GoodZ', [1,2])
        flow['Z1Mass'] = ('ZMassTight', [1,2])
        flow['Z2MassLoose'] = ('ZMassLoose', [3,4])
        flow['Overlap'] = ('Overlap', [1,2,3,4])
        
        return flow


