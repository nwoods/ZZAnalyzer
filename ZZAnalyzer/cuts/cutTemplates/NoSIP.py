from ZZAnalyzer.cuts import Cutter

from collections import OrderedDict


class NoSIP(Cutter):
    '''
    Replace SIP cuts with stricter IP cuts.
    '''
    def getCutTemplate(self,*args):
        '''
        Template for all cuts
        '''
        temp = super(NoSIP, self).getCutTemplate(*args)

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
                'PVDXY' : (0.05, '<'),
                'PVDZ' : (0.1, '<'),
                },
            'objects' : 1,
            }

        temp['eEndcapVtx'] = {
            'cuts' : {
                'inEndcap' : '!eInBarrel',
                'PVDXY' : (0.1, '<'),
                'PVDZ' : (0.2, '<'),
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
                'PVDXY' : (0.05, '<'),
                'PVDZ' : (0.1, '<'),
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
        baseFlow = super(NoSIP, self).setupCutFlow()

        flow = OrderedDict()
        addedVtxCuts = False
        for n, c in baseFlow.iteritems():
            if n.lower() == 'sip':
                flow['LeptonVtx'] = ('LeptonVtx', baseFlow[n][1])
                addedVtxCuts = True
            else:
                flow[n] = c

        if not addedVtxCuts:
            try:
                objectsToUse = flow['LeptonID'][1]
            except KeyError:
                print "Unable to figure out how many leptons there are... guessing 4"
                objectsToUse = [1,2,3,4]

            flow['LeptonVtx'] = ('LeptonVtx', objectsToUse)

        return flow

