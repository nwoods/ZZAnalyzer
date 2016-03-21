
'''

Cutter for Z+l_tight control region for the 2015 HZZ4l analysis. 
Inherits from the control region base class. 
Assumed to run on the results of the Z+l_loose CR Cutter (which gives the
denominator) to select events where the extra lepton is tight ID'd (to get
the numerator).

Author: Nate Woods, U. Wisconsin

'''

from ZZAnalyzer.cuts.cutTemplates.ControlRegion_Base import ControlRegion_Base

from collections import OrderedDict


class ControlRegion_ZpluslTight(ControlRegion_Base):
    def __init__(self, cutset="ControlRegion_ZpluslTight"):
        super(ControlRegion_ZpluslTight, self).__init__(cutset)


    def setupCutFlow(self):
        '''
        As the full spectum cutter, except as above
        '''
        flow = OrderedDict()
        
        flow['Total'] = ('true', [])
        flow['Lepton3ID'] = ('leptonTightID', [3])
        flow['Lepton3Iso'] = ('LeptonIso', [3])
        
        return flow


    def needReorder(self, channel):
        '''
        3e, 3mu, and eemu are already in the right order. emumu is always in 
        the wrong order (should always be m1, m2, e)
        '''
        return channel == 'emm'


    def orderLeptons(self, row, channel, objects):
        '''
        Should only get called for emumu channel, where we always need 
        to swap the order.
        '''
        return objects[1:]+[objects[0]]
