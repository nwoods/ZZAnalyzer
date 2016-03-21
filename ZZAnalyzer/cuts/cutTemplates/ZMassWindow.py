from ZZAnalyzer.cuts import Cutter


class ZMassWindow(Cutter):
    '''
    Require candidate mass near Z peak
    '''
    def getCutTemplate(self, *args):
        temp = super(ZMassWindow, self).getCutTemplate()

        temp['4lMass'] = {
            'cuts' : {
                'Mass%s#lower'%self.fsrVar : (80., ">="),
                'Mass%s#upper'%self.fsrVar : (100., "<"),
                },
            }
        
        return temp
    

    def setupCutFlow(self):
        flow = super(ZMassWindow, self).setupCutFlow()

        flow['4lMass'] = ('4lMass', [])

        return flow
