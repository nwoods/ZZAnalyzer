from ZZAnalyzer.cuts import Cutter


class NoTrigger(Cutter):
    '''
    Ignore triggers
    '''
    def getCutTemplate(self, *args):
        temp = super(NoTrigger, self).getCutTemplate()

        temp['Trigger']['cuts'] = {'true' : 'true'}
        
        return temp
    

