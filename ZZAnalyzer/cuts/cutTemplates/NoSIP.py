from ZZAnalyzer.cuts import Cutter

from collections import OrderedDict


class NoSIP(Cutter):
    '''
    Removes SIP cuts
    '''
    def getCutTemplate(self,*args):
        '''
        Template for all cuts
        '''
        temp = super(NoSIP, self).getCutTemplate(*args)

        if 'SIP' in temp:
            temp['SIP'] = {'cuts':{'doNotDo':'true'},'logic':'objor'}

        return temp


    def setupCutFlow(self):
        baseFlow = super(NoSIP, self).setupCutFlow()

        flow = OrderedDict()
        for n, c in baseFlow.iteritems():
            if n.lower() == 'sip':
                pass
            else:
                flow[n] = c

        return flow

