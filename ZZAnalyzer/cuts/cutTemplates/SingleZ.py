
'''

Cutter than requires a good Z (leptons and initial state candidate pass 
analysis Z1 cuts)... and nothing else. 

Author: Nate Woods, U. Wisconsin

'''

from ZZAnalyzer.cuts import Cutter
from ZZAnalyzer.utils.helpers import objVar

from collections import OrderedDict


class SingleZ(Cutter):
    def __init__(self, cutset="SingleZ"):
        super(SingleZ, self).__init__(cutset)


    def setupCutFlow(self):
        '''
        Just require 1 good Z
        '''
        superFlow = super(SingleZ, self).setupCutFlow()
        
        flow = OrderedDict()

        flow['Total'] = superFlow['Total']
        flow['LeptonID'] = ('GoodLeptons', [1,2])
        flow['Isolation'] = ('Isolation', [1,2])
        flow['ZMass'] = ('ZMassTight', [])
        flow['GoodZ'] = ('GoodZ', [])
        flow['SIP'] = ('SIP', [1,2])
        flow['Lepton1Pt'] = ('Lepton1Pt', [1])
        flow['Lepton2Pt'] = ('Lepton2Pt', [1,2])
        flow['Vertex'] = ('Vertex', [])
        flow['Trigger'] = ('Trigger', [])
        
        return flow


    def getCutTemplate(self, *args):
        '''
        Cuts that are normally for 2-leptons are now for the initial state
        '''
        temp = super(SingleZ, self).getCutTemplate()

        for cut, info in temp.iteritems():
            if info.get('objects', 0) == 2 and 'obj' not in info.get('logic', ''):
                del info['objects']

        temp['Trigger'] = {
                'cuts' : {
                    'doubleEPass' : (1, ">="),
                    'doubleMuPass' : (1, ">="),
                    'doubleMuDZPass' : (1, ">="),
                },
                'logic' : 'or',
            }

        return temp


    def needReorder(self, channel):
        return False


