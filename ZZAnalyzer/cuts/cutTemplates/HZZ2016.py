from ZZAnalyzer.cuts import Cutter

from ZZAnalyzer.utils.helpers import nObjVar, zMassDist, zCompatibility

class HZZ2016(Cutter):
    def getCutTemplate(self,*args):
        '''
        Template for all cuts
        '''
        temp = super(HZZ2016, self).getCutTemplate(*args)

        if 'ZMassLoose' in temp:
            temp['ZMassLoose']['cuts']['Mass%s#lower'%self.fsrVar] = (12., ">=")
        else:
            temp['ZMassLoose'] = {
                'cuts' : { 
                    'Mass%s#lower'%self.fsrVar : (12., '>='),
                    'Mass%s#upper'%self.fsrVar : (120., '<'),
                    },
                'objects' : 2,
                }
        
        temp['m4l'] = {
            'cuts' : {
                'Mass%s'%self.fsrVar : (70., ">="),
                },
            }

        # Smart Cut
        temp['SmartCut'] = {
                'logic' : 'other',
                'branches' : ['[em]?_[em]?_SS','[em]?_[em]?_Mass'+self.fsrVar],
            }

        return temp


    def setupCutFlow(self):
        '''
        Only flow differences from full spectrum are Z mass cuts
        '''
        flow = super(HZZ2016, self).setupCutFlow()

        flow['Z2MassLoose'] = ('ZMassLoose', [3,4])
        flow['SmartCut'] = ('SmartCut', [1,2,3,4])
        flow['4lMass'] = ('m4l', [])

        return flow


    def setupOtherCuts(self):
        '''
        Define functions that don't fit the template nicely
        '''
        temp = self.getCutTemplate()
        others = super(HZZ2016, self).setupOtherCuts()
        others['SmartCut'] = lambda row, *obj: self.doSmartCut(row, *obj)

        return others


    def doSmartCut(self, row, *obj):
        # Doesn't apply to eemm
        if obj[0][0] != obj[2][0]:
            return True

        # Find the proper alternate Z pairing. We already checked that we have 2 OS pairs
        if nObjVar(row, 'SS', *sorted([obj[0], obj[2]])): # l1 matches l4
            altObj = [obj[0], obj[3], obj[1], obj[2]]
        else: # l1 matches l3
            altObj = [obj[0], obj[2], obj[1], obj[3]]

        altZMass = [nObjVar(row, "Mass"+self.fsrVar, *sorted(altObj[:2])), nObjVar(row, "Mass"+self.fsrVar, *sorted(altObj[2:]))]
        altZCompatibility = [zMassDist(m) for m in altZMass]
        z1Compatibility = zCompatibility(row, obj[0], obj[1], self.fsrVar)

        if altZCompatibility[0] < altZCompatibility[1]:  # Za is first
            zACompatibility = altZCompatibility[0]
            zBMass = altZMass[1]
        else:
            zACompatibility = altZCompatibility[1]
            zBMass = altZMass[0]

        return not (zACompatibility < z1Compatibility and zBMass < 12)
