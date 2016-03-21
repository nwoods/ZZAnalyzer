'''

Base class to do cuts in ZZ analysis. In practice, analyses will
    typically use a daughter class of Cutter. Cutter can do most
    of the cuts one wants from a bare template, but has the ability to
    do cuts that are simply programmed as functions.
    Cutter can read cut information in from a bare
    cut dictionary and cutflow collections.OrderedDict, but daughter
    classes are expected to overload the getCutTemplate(*args) and
    setupCutFlow methods

The goal is to have everything in one place, so that when a cut needs
    to be changed, we're not stuck searching through the selection
    software and hard coding the new variables, and if we have two
    sets of cuts (e.g. one for the HZZ analysis, one for the SMP ZZ
    analysis) we don't have to maintain two versions of the selection
    code or change things back and forth by hand. Instead, just change
    the cut key and all the cuts change automatically

The structure of the dictionary should be:

>>> cuts[cut]['cuts'][variable] = (value, lessThanCut) # if type is 'base'
>>> cuts[cut]['cuts'][variable] = 'NameOfSomeOtherCut' # type is 'caller'
>>> cuts[cut]['logic'] = 'and'/'or'/'other'/'objand'/'objor'
>>> cuts[cut]['objects'] = nObjects/'pairs'/'ignore'
>>> cuts[cut]['type'] = 'base/caller'

    where variable is the name of the variable stored in the ntuple,
    lessThanCut is True if var < value passes the cut, False if
    var >= value does. A '#' and anything after it in a variable
    name will be ignored, allowing the same variable to be cut
    twice (e.g. 60.<Zmass<120.). The string TYPE will be replaced by
    the name of a particle ('e1', etc.) Logic can be 'and' or 'or' depending
    on whether all conditions must be true, or just one of them, or
    'other' if the cut must be specially calculated by a function.
    If 'obj' is prepended to the logic, each object (pairs may be objecs,
    see the end of this paragraph) undergoes the and of all cuts, and
    the cut result is the (and/or) of all the results for all the objects.
    In the case of 'other', the rest of the dictionary structure may
    change, but it won't matter because it must also call a special
    function to do the cut. 'objects' points the
    number of objects cut on. 'pairs' is a special
    value that will apply the cut on all possible pairs of objects.
    If 'objects' is 'ignore', the cut will accept any number of
    objects as input, but ignore them and do an event-level cut.

The type of a cut may be 'base', for cuts that just take a value
    from the ntuple and cut on it, or 'caller' for cuts that call other
    cuts.

Booleans that should be True should be entered as (1, False), booleans
    that should be False should be entered as (1, True). If you enter
    a boolean as (0, False), it will always evaluate to True because
    lessThanCut=False returns true for var >= cut

Cuts whose logic is 'other' must be defined in the function
    setupOtherCuts(self). It should return a dictionary containing
    functions that perform the cuts on a row and the specified number
    of objects, e.g., for a cut on second lepton pt:

>>> def setupOtherCuts(self):
>>>     template = self.getCutTemplate()
>>>     others = {}
>>>     others['L2Pt'] = lambda row, *obj: self.ptCutTwoObjects(template['L2Pt;], row, *obj)
>>>     return others

with the necessary functions defined somewhere.

The last necessary thing is the order of the cuts, which must be placed
    in an ordered dict returned by self.setupCutFlow(), e.g.

>>> def setupCutFlow(self):
>>>     flow = collections.OrderedDict()
>>>     flow['Total'] = ('nameOfCut', [*objectNumbers])
>>>     return flow

    where 'nameOfCut' is a cut (base or caller) from the template and
    objectNumbers are the indices of the objects to cut on, e.g. [1,2]
    if the cut should be performed on the two leptons from the better Z.

Once a set of cuts is entered, the user shouldn't need to know anything.
    Use Cutter.doCut(row, 'cutName'[, object[, object2...]]) to do a
    particular cut where the needed objects are known, or (more often)
    just loop through the result of Cutter.setupCutFlow()
    and do Cutter.analysisCut(row, cut, *allObjects) for all cuts. The
    results of these are booleans for whether the cut was passed or not.

A few simple, common cuts are provided by default. 'true' always returns
    True, 'SameFlavor' returns whether the objects are the same type 
    (electron, muon etc.). 'DifferentFlavor' does the opposite.
    'IsElectron' and 'IsMuon' tell you if the 
    object is an electron or a muon, respectively.


Author: Nate Woods, U. Wisconsin

'''

import itertools
from collections import OrderedDict
from ZZAnalyzer.utils.helpers import *


class Cutter(object):
    '''
    Base class for anything setting, modifying, or executing analysis cuts.
    Cutters may be combined via multiple inheritance as long as everything
    derives from this base class and calls super() from the first three 
    methods here, to ensure an appropriate MRO.
    '''
    def setupCutFlow(self):
        '''
        This OrderedDict should be filled with cuts by daughter classes,
        in the format flow[cut] = (cutName, objects), where cutName is 
        the name of the cut in the cut template, and objects is a list
        of (one-indexed) integers specifying the objects to pass to the cut.
        '''
        assert not hasattr(super(Cutter, self), 'setupCutFlow'),\
            "Cutter class %s does not derive from Cutter!"%super(Cutter,self).__class__.__name__
        flow = OrderedDict()
        flow['Total'] = ('true', [])
        return flow

    def setupOtherCuts(self):
        '''
        This dict should be filled with functions that perform complicated
        cuts, in the format otherCuts[cut] = f(row, *objects)
        '''
        assert not hasattr(super(Cutter, self), 'setupOtherCuts'),\
            "Cutter class %s does not derive from Cutter!"%super(Cutter,self).__class__.__name__
        return {}

    def getCutTemplate(self, *args):
        '''
        This dict should be filled with cuts in the format specified in the 
        header comments to this file.
        '''
        assert not hasattr(super(Cutter, self), 'getCutTemplate'),\
            "Cutter class %s does not derive from Cutter!"%super(Cutter,self).__class__.__name__
        return {}



    def __init__(self, cutSet):
        self.cutSet = cutSet

        self.otherCuts = self.setupOtherCuts()

        self.cutFlow = self.setupCutFlow()

        self.cuts = self.setupCuts(self.cutSet)
        
        # Add a few always-useful cuts
        if 'true' not in self.cuts:
            self.cuts['true'] = lambda *args: True
        self.cuts['SameFlavor'] = lambda row, obj1, obj2: obj1[0]==obj2[0]
        self.cuts['DifferentFlavor'] = lambda row, obj1, obj2: obj1[0]!=obj2[0]
        self.cuts['IsElectron'] = lambda row, obj: obj[0]=='e'
        self.cuts['IsMuon'] = lambda row, obj: obj[0]=='m'


    def getCutList(self):
        '''
        Get an ordered list of the cuts to be performed
        '''
        return [c for c in self.cutFlow]


    def analysisCut(self, row, cut, *objects):
        '''
        Takes cut name and all leptons, uses self.cutFlow to figure out 
        which cut and objects to use, returns the result
        '''
        return self.cuts[self.cutFlow[cut][0]](row, *[objects[i-1] for i in self.cutFlow[cut][1]])


    def doCut(self, row, cut, *objects):
        '''
        Do a cut on exactly the objects passed (as opposed to passing all 
        objects and letting self.cutFlow tell us which to use as in self.doCut).
        '''
        return self.cuts[cut](row, *objects)


    def negateCut(self, row, cut, *objects):
        '''
        The logical opposite of whatever doCut would return here.
        '''
        return not self.cuts[cut](row, *objects)


    def setupCuts(self, *args):
        '''
        Gets a dictionary of cut parameters from a template file or 
        daughter-class-specific dictionary data member and turns it
        into an dictionary of functions that perform the cuts.
        self.getCutTemplate(*args) should be changed by any daughter
        class of Cutter to create the template if you don't want
        to get it from a template file.
        A cut with mode 'other' is one that requires a special function,
        assumed to be defined already in dictionary self.otherCuts
        '''
        temp = self.getCutTemplate(*args)
        cuts = {}
        
        for cut, params in temp.iteritems():
            if 'logic' not in params:
                params['logic'] = 'and'
            elif params['logic'] == 'other':
                cuts[cut] = self.otherCuts[cut]
                continue
            
            cuts[cut] = self.getCutFunction(params)
                
        return cuts


    def getCutFunction(self, cutDict):
        '''
        Return a function that does one or more object cuts. 
        cutDict is template[cut] or at least in the same format
        '''
        objLogic = 'obj' in cutDict['logic']
        requireAll = 'and' in cutDict['logic']
        
        pairwise = False
        ignoreObjects = False
        if 'objects' in cutDict:
            if isinstance(cutDict['objects'], str) and 'pairs' in cutDict['objects']:
                pairwise = True
                nObjects = 2
            elif isinstance(cutDict['objects'], str) and 'ignore' in cutDict['objects']:
                # to allow us to pass objects to a cut that doesn't use any
                ignoreObjects = True
                nObjects = -1 # just set to junk
            else:
                try:
                    nObjects = int(cutDict['objects'])
                except ValueError:
                    print "Number of objects must be an integer"
                    raise
        else:
            nObjects = 0

        if objLogic and not pairwise:
            nObjects = 1

        # it will be faster to make a list of functions now and loop over it with a generator expression later
        cutFuns = [self.getCutLegFunction(leg, legParams, nObjects, ignoreObjects) for leg, legParams in cutDict['cuts'].iteritems()]
        # the any function or the all fuction, depending on what we need
        logicFun = all if requireAll else any

        if objLogic:
            if pairwise:
                return lambda row, *obj: logicFun(all(cut(row, *sorted(ob)) for cut in cutFuns) for ob in itertools.combinations(obj,2))
            else:
                return lambda row, *obj: logicFun(all(cut(row, ob) for cut in cutFuns) for ob in obj)
        else:
            if nObjects == 0:
                if len(cutFuns) == 1:
                    return lambda row: cutFuns[0](row)
                return lambda row: logicFun(cut(row) for cut in cutFuns)
            elif nObjects == 1:
                if len(cutFuns) == 1:
                    return lambda row, obj: cutFuns[0](row, obj)
                return lambda row, obj: logicFun(cut(row, obj) for cut in cutFuns)
            else:
                if len(cutFuns) == 1:
                    return lambda row, *obj: cutFuns[0](row, *obj)
                return lambda row, *obj: logicFun(cut(row, *obj) for cut in cutFuns)

    
    def getCutLegFunction(self, cutName, cutParams, nObjects, ignoreObjects=False):
        '''
        Get the function to do a single leg of a single cut. If cutName is the
        name of a variable, the function will cut on that, and will look for 
        parameters of the form (cutValue, wantLessThan), where cutValue is the
        threshold at which to cut and wantLessThan is a bool or string. If 
        wantLessThan is True, the cut passes if the value is less than the 
        threshold; if it is False, the cut passes if the value is greater than
        or equal to the threshold. If wantLessThan is a string, we try to 
        figure out whether the user wants var < threshold or var >= threshold
        (those are the only options). If the cut parameter is
        a string, the name doesn't matter and the paramter indicates which 
        other cut to call. 
        '''
        
        if isinstance(cutParams, str):
            # If we just want to do the cut, use doCut(row, cut).
            # If we want to negate the cut, use negateCut(row, cut)
            if cutParams[0] == '!':
                cutDoer = self.negateCut
                cutParams = cutParams[1:]
            else:
                cutDoer = self.doCut
            if ignoreObjects:
                return lambda row, *obj: cutDoer(row, cutParams)
            elif nObjects == 0:
                return lambda row: cutDoer(row, cutParams)
            elif nObjects == 1:
                if len(cutParams) > 4 and cutParams[:4] == "TYPE":
                    strippedName = cutParams.replace("TYPE","")
                    return lambda row, obj: cutDoer(row, obj[0]+strippedName, obj)
                else:
                    return lambda row, obj: cutDoer(row, cutParams, obj)
            else:
                return lambda row, *obj: cutDoer(row, cutParams, *obj)

        # Otherwise, create the cut
        try:
            assert len(cutParams) == 2, "Parameters for cut %s must be of the form (threshold, wantLessThan)."%cutName
        except TypeError:
            print "Parameters for cut %s must be an iterable of the form (threshold, wantLessThan)."%cutName
            raise
        if isinstance(cutParams[1], bool):
            wantLessThan = cutParams[1]
        else:
            assert isinstance(cutParams[1], str), "The second cut parameter for %s must be a boolean or string indicating whether or not the cut passes if val < threshold."%cutName
            if cutParams[1].lower() in ['less', 'l', '<', "lessthan", 'ls']:
                wantLessThan = True
            elif cutParams[1].lower() in ['greater', 'greaterthan', 'greaterthanorequal', 'greaterthanorequalto', 'gr', 'greq', '>', '>=']:
                wantLessThan = False
            else:
                print "I don't know what to do with parameter %s for %s."
                print "Your options are 'less', 'l', '<', 'lessthan', and 'ls' if you want val < threshold to pass the cut, or"
                print "'greater', 'greaterthan', 'greaterthanorequal', 'greaterthanorequalto', 'gr', 'greq', '>', or '>=' if you want val >= threshold."
                print "Note that it's always >=, whether your string indicates that or not."
                raise ValueError

        thisCut = cutName.split("#")[0]

        if ignoreObjects:
            return lambda row, *obj: self.cutEvVar(row, thisCut, cutParams[0], wantLessThan)
        elif nObjects == 0:
            return lambda row: self.cutEvVar(row, thisCut, cutParams[0], wantLessThan)
        elif nObjects == 1:
            return lambda row, obj: self.cutObjVar(row, thisCut, cutParams[0], wantLessThan, obj)
        else:
            return lambda row, *obj: self.cutNObjVar(row, thisCut, cutParams[0], wantLessThan, *obj)


    def cutEvVar(self, row, var, val, wantLessThan):
        '''
        Do one cut on one final state variable. Checks to see if row.var < val if 
        wantLessThan is True, row.var >= val if False
        '''
        return ((evVar(row, var) < val) == wantLessThan)


    def cutObjVar(self, row, var, val, wantLessThan, obj):
        '''
        Do one cut on one object-associated variable. Checks to see if row.objvar < val if 
        wantLessThan is True, row.objvar >= val if False
        '''
        return ((objVar(row, var, obj) < val) == wantLessThan)


    def cutNObjVar(self, row, var, val, wantLessThan, *obj):
        '''
        Do one cut on one N-object composite variable. Checks to see if row.[obj1_obj2_...]_var < val if 
        wantLessThan is True, row.[obj1_obj2...]_var >= val if False
        '''
        return ((nObjVar(row, var, *obj) < val) == wantLessThan)


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
            
        
    def needReorder(self, channel):
        '''
        Return whether or not this channel should have its leptons reordered 
        with each new row (because FSA put them in the wrong order for some 
        reason).
        By default, does this for 2e2mu channel and nothing else. Daughter 
        classes may override if needed for a control region or whatever.
        '''
        return channel[0][0] != channel[-1][0]


    def orderLeptons(self, row, channel, objects):
        '''
        Put best (closest to nominal mass) Z candidate first. 
        FSA does this automatically for 4e and 4mu cases.
        Assumes 4 leptons, with (l1,l2) and (l3,l4) same-flavor pairs;
        will have to be overloaded for other circumstances (CRs, etc.)
        '''
        dM1 = zCompatibility_checkSign(row,objects[0],objects[1], self.fsrVar)
        dM2 = zCompatibility_checkSign(row,objects[2],objects[3], self.fsrVar)
        
        if dM1 > dM2:
            return objects[2:] + objects[:2]
        return objects


    
