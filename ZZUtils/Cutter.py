'''

Class containing all cuts in ZZ analysis

The goal is to have everything in one place, so that when a cut needs 
    to be changed, we're not stuck searching through  the selection  
    software and hard coding the new variables, and if we have two 
    sets of cuts (e.g. one for the HZZ analysis, one for the SMP ZZ
    analysis) we don't have to maintain two versions of the selection
    code or change things back and forth by hand. Instead, just change
    the cut key and all the cuts change automatically

The structure of the dictionary should be:

>>> cuts[cut]['cuts'][variable] = (value, lessThanCut)
>>> cuts[cut]['mode'] = mode

    where variable is the name of the variable stored in the ntuple,  
    lessThanCut is True if var < value passes the cut, false if 
    var >= value does, and mode can be 'and' or 'or' depending
    on whether all conditions must be true, or just one of them,
    'other' if the cut must be specially calculated, or '2obj' if
    the cut is on a composite object (e.g. Z mass). In the case of
    'other', the dictionary structure will change, but it won't matter
    because it must also call a special function to do the cut. A 
    '#' and anything after it in a variable name will be ignored, 
    allowing the same variable to be cut twice (e.g. 60.<Zmass<120.).

Booleans that should be True should be entered as (1, False), booleans
    that should be False should be entered as (1, True). If you enter
    a boolean as (0, False), it will always evaluate to True because
    lessThanCut=False returns true for var >= cut

Optionally, 

>>> cuts[cut]['options'] = option

    may be used to pass in a special operator. The only one currently
    supported is absVARIABLE, which will place the cut on the absolute
    value of VARIABLE. E.G., 'absEta' will cut on absolute value of eta.
    'absVAR1absVAR2' will use absolute values for VAR1 and VAR2.

Once a set of cuts is entered, the user shouldn't need to know anything
    but the name of the analysis, the name of the cut, and the object
    it's being applied to. Instantiate a cutter with

>>> cuts = Cutter.Cutter('AnalysisName')

    and get the result of a cut with 

>>> result = cuts.doCut(row, 'cutName'[, object[, object2]])

Author: Nate Woods, U. Wisconsin

'''

import imp

def getVar(obj, var):
    return obj+var
def getVar2(obj1, obj2, var):
    return obj1+'_'+obj2+'_'+var

class Cutter():
    def __init__(self, cutSet):

        self.cutSet = cutSet

        self.cuts = self.getCutDict(self.cutSet)


    def doCut(self, row, cutName, obj='', obj2=''):
        '''
        Returns true if obj passes cuts[cutName]
        obj2 is ignored unless the cut's mode is '2obj'

        It turns out that we get the desired less/greaterOrEqual behavior with
                variable<cut XNOR lessThanCut
            which is most easily expressed as
                variable<cut == lessThanCut

        If no objects are supplied, it will just give back the global variable with 
            the appropriate name
        '''
        assert cutName in self.cuts, 'Incorrect cut name %s'%cutName

        if 'options' not in self.cuts[cutName]:
            if self.cuts[cutName]['mode'] == '2obj':
                passList = [((getattr(row, getVar2(obj, obj2, var.split('#')[0])) < cut[0]) == cut[1]) for var, cut in \
                            self.cuts[cutName]['cuts'].iteritems()]
            elif self.cuts[cutName]['mode'] == 'other':
                if cutName == 'eID' and self.cutSet == 'HZZ4l2012':
                    return self.eIDTight2012(row, obj)
                raise NameError('Special cut %s is not yet defined for cutSet %s'%(cutName,self.cutSet))
            else:
                passList = [((getattr(row, getVar(obj, var.split('#')[0])) < cut[0]) == cut[1]) for var, cut in \
                            self.cuts[cutName]['cuts'].iteritems()]

            if self.cuts[cutName]['mode'] == 'or':
                return any(passList)
            return all(passList)
        else:
            assert 'abs' in self.cuts[cutName]['options'], "Unknown option %s"%self.cuts[cutName]['options']
            absolutes = self.cuts[cutName]['options'].split('abs')
            passList = []
            for var, cut in self.cuts[cutName]['cuts'].iteritems():
                if var in absolutes:
                    passList.append((abs(getattr(row, getVar(obj, var.split('#')[0]))) < cut[0]) == cut[1])
                else:
                    passList.append((getattr(row, getVar(obj, var.split('#')[0])) < cut[0]) == cut[1])
            if self.cuts[cutName]['mode'] == 'or':
                return any(passList)
            return all(passList)

    def eIDTight2012(self, row, obj):
        BDTName = 'MVANonTrigCSA14'
        pt = getattr(row, getVar(obj, 'Pt'))
        eta = getattr(row, getVar(obj, 'SCEta'))
        bdt = getattr(row, getVar(obj, BDTName))
        if pt > 5. and pt < 10.:
            ptName = '5<pt<10'
        else:
            ptName = 'pt>10'

        if abs(eta) < 0.8:
            etaName = 'eta<0.8'
        elif abs(eta) < 1.479:
            etaName = '0.8<eta<1.479'
        else:
            etaName = 'eta>1.479'

        cut = self.cuts['eID']['cuts'][ptName][etaName][BDTName][0]

#         print ptName + ", " + etaName
#         print "want > " + str(cut)
#         print "got" + str(getattr(row, getVar(obj, BDTName)))

        return getattr(row, getVar(obj, BDTName)) > cut

    
    def getCutDict(self, cutSet, path='./ZZUtils/templates'):
        '''
        Gets a dictionary of cuts from a python template file. 
        Assumes that the file will be named cutSet.py and will contain
        a dictionary called cuts
        '''
        
        f, fName, desc = imp.find_module(cutSet, [path])
        
        assert f, 'Set of cuts %s does not exist in %s'%(cutSet,path)
        
        mod = imp.load_module(cutSet, f, fName, desc)
        
        assert mod.cuts and type(mod.cuts) == dict, 'No valid set of cuts'
        
        return mod.cuts
        
    
    def dumpCutValues(self, row, cutName, obj):
        '''
        Debugging tool to print all values involved in cut
        '''
        for var, cut in self.cuts[cutName]['cuts'].iteritems():
            willPass = (getattr(row, getVar(obj, var)) < cut[0]) == cut[1]
            print var + "(" + str(cut[0]) + "): " + str(getattr(row, getVar(obj, var))) + "(" + str(willPass) + ")"
        if self.doCut(row, cutName, obj):
            print "Passed"
        else:
            print "Failed"
            
        







