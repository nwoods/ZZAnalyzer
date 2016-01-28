


from Cutter import Cutter

class Blind(Cutter):
    '''
    Applies HZZ mass blinding
    '''
    def getCutTemplate(self, *args):
        temp = super(Blind, self).getCutTemplate(*args)

        temp['applyBlinding'] = {
            'cuts' : {
                "Mass%s#LOW"%self.fsrVar : (110., "<"),
                "Mass%s#HIGH"%self.fsrVar : (150., ">="),
                },
            'logic' : 'or',
            }

        return temp

    def setupCutFlow(self, *args):
        flow = super(Blind, self).setupCutFlow(*args)

        flow['Total'] = ('applyBlinding', [])

        return flow


