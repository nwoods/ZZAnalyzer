from ZZAnalyzer.cuts import Cutter


class TightenVtx(Cutter):
    '''
    Add stricter IP cuts than HZZ uses
    '''
    def getCutTemplate(self,*args):
        '''
        Template for all cuts
        '''
        temp = super(TightenVtx, self).getCutTemplate(*args)

        temp['eInBarrel'] = {
            'cuts' : {
                'SCEta#POS' : (1.479, '<'),
                'SCEta#NEG' : (-1.479, '>='),
                },
            'objects' : 1,
            }

        temp['eBarrelVtx'] = {
            'cuts' : {
                'inBarrel' : 'eInBarrel',
                'PVDXY#POS' : (0.05, '<'),
                'PVDZ#POS' : (0.1, '<'),
                'PVDXY#NEG' : (-0.05, '>='),
                'PVDZ#NEG' : (-0.1, '>='),
                },
            'objects' : 1,
            }

        temp['eEndcapVtx'] = {
            'cuts' : {
                'inEndcap' : '!eInBarrel',
                'PVDXY#POS' : (0.1, '<'),
                'PVDZ#POS' : (0.2, '<'),
                'PVDXY#NEG' : (-0.1, '>='),
                'PVDZ#NEG' : (-0.2, '>='),
                },
            'objects' : 1,
            }

        temp['eVtx'] = {
            'cuts' : {
                'barrel' : 'eBarrelVtx',
                'endcap' : 'eEndcapVtx',
                },
            'logic' : 'or',
            'objects' : 1,
            }

        temp['mVtx'] = {
            'cuts' : {
                'PVDXY#POS' : (0.05, '<'),
                'PVDZ#POS' : (0.1, '<'),
                'PVDXY#NEG' : (-0.05, '>='),
                'PVDZ#NEG' : (-0.1, '>='),
                },
            'objects' : 1,
            }

        temp['LeptonVtx'] = {
            'cuts' : {
                'vtx' : 'TYPEVtx',
                },
            'logic' : 'objand',
            }

        return temp


    def setupCutFlow(self):
        baseFlow = super(TightenVtx, self).setupCutFlow()

        flow = OrderedDict()
        flow['LeptonVtx'] = ('LeptonVtx', baseFlow[n][1])

        return flow

