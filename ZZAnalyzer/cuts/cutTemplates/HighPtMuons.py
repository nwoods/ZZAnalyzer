from ZZAnalyzer.cuts import Cutter


class HighPtMuons(Cutter):
    def getCutTemplate(self,*args):
        '''
        Template for all cuts
        '''
        temp = super(HighPtMuons, self).getCutTemplate(*args)

        temp['mLegacyID'] = temp['mTightID'].copy()

        temp['mHighPtID'] = {
            'cuts' : {
                'Pt' : (200., '>='),
                'HighPtID' : (1., '>='),
                },
            'objects' : 1,
            }

        temp['mTightID']['cuts'] = {
            'legacy' : 'mLegacyID',
            'highPt' : 'mHighPtID',
            }
        temp['mTightID']['logic'] = 'or'

        return temp



