from ZZAnalyzer.cuts import Cutter

from collections import OrderedDict


class LooseSIP(Cutter):
    '''
    Loosens SIP cut to 10
    '''
    def getCutTemplate(self,*args):
        '''
        Template for all cuts
        '''
        temp = super(LooseSIP, self).getCutTemplate(*args)

        if 'SIP' in temp:
            temp['SIP']['cuts']['SIP3D'] = (10., '<')
        else:
            temp['SIP'] = {
                'cuts' : {
                    'SIP3D' : (10., "<"),
                    },
                'logic' : 'objand',
                }

        return temp


