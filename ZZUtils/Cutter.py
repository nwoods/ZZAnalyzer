'''

Base class to do cuts in ZZ analysis. In practice, analyses will 
    typically use a daughter class of Cutter. Cutter can do most
    of the cuts one wants from a bare template, but most analyses
    will do *something* unusual that requires special methods and
    so forth. Cutter can read cut information in from a bare
    cut dictionary and cutflow collections.OrderedDict, but daughter
    classes are expected to overload the getCutTemplate(*args) and 
    setupCutFlow methods

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

import imp, collections, os, itertools
from ZZHelpers import *


class Cutter(object):
    def __init__(self, cutSet):

        self.cutSet = cutSet

        self.otherCuts = self.setupOtherCuts()

        self.cutFlow = self.setupCutFlow()

        self.cuts = self.setupCuts(self.cutSet)
        
        # Add an always-true cut because it's vaguely useful
        if 'true' not in self.cuts:
            self.cuts['true'] = lambda *args: True


    def setupOtherCuts(self):
        '''
        Virtual; use to add hand-coded cuts to daughter classes of Cutter
        '''
        return {}


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
            if params['logic'] == 'other':
                cuts[cut] = self.otherCuts[cut]
                continue
            
            if params['type'] == 'caller':
                cuts[cut] = self.cutCaller(params)
                continue
            
            if 'objects' not in params:
                nObjects = 0 # event variable
            else:
                try:
                    nObjects = int(params['objects'])
                except ValueError:
                    print "Base cuts must have an integer number of input objects"

            if nObjects == 0:
                cuts[cut] = self.baseEvCut(params)
            elif nObjects == 1:
                cuts[cut] = self.baseObjCut(params)
            else:
                cuts[cut] = self.baseNObjCut(params)
                
        return cuts


    def getCutTemplate(self, *args):
        '''
        Gets cuts from a template file as a dictionary. May be (likely will 
        be) overwritten by daughter classes of Cutter to set up the dictionary
        by hand or in some other way.
        '''
        mod = self.getTemplateFile(*args)

        return mod.cuts


    def setupCutFlow(self, *args):
        '''
        Gets cutFlow  from a template file as a collections.OrderedDict. May 
        be (likely will be) overwritten by daughter classes of Cutter to set 
        up the OrderedDict by hand or in some other way.
        '''
        mod = self.getTemplateFile(*args)
        
        return mod.cutFlow


    def getTemplateFile(self,*args):
        '''
        Find a python file with the templates in it. Crash if it's missing
        the cuts dictionary and/or the cutFlow OrderedDict. 
        Expects *args to be a template name and a path. If no path is 
        specified, will look in $zza/ZZUtils/templates
        '''
        assert len(args), "Need cut set name for template"
        cutSet = args[0]
        if len(args) >= 2:
            path = args[1]
        else: 
            path = "%s/ZZUtils/templates"%os.environ["zza"]

        f, fName, desc = imp.find_module(cutSet, [path])
        
        assert f, 'Set of cuts %s does not exist in %s'%(cutSet,path)
        
        mod = imp.load_module(cutSet, f, fName, desc)
        
        assert mod.cuts and type(mod.cuts) == dict, 'No valid set of cuts in %s'%fName        
        assert mod.cutFlow and type(mod.cutFlow) == collections.OrderedDict, 'No valid cutFlow in %s'%fName
        
        return mod


    def cutCaller(self, cutDict):
        '''
        Return a function that does one or more object cuts. 
        cutDict is template[cut] or at least in the same format
        '''
        requireAll = cutDict['logic'] == 'and'
        if cutDict['objects'] == 'pairs':
            if requireAll:
                return lambda row, *obj: all([self.doCut(row, cut, *sorted(ob)) for foo, cut in cutDict['cuts'].iteritems() for ob in itertools.combinations(obj,2)])
            else:
                return lambda row, *obj: any(
                    [all(self.doCut(row, cut, *sorted(ob)) for foo, cut in cutDict['cuts'].iteritems()) for ob in itertools.combinations(obj,2)])

        if cutDict['objects'] == 'sfpairs':
            if requireAll:
                return lambda row, *obj: all([(self.doCut(row, cut, *sorted(ob)) if ob[0][0] == ob[1][0] else True) for foo, cut in cutDict['cuts'].iteritems() for ob in itertools.combinations(obj,2)])
            else:
                return lambda row, *obj: any([all((self.doCut(row, cut, *sorted(ob)) if ob[0][0] == ob[1][0] else True) for foo, cut in cutDict['cuts'].iteritems()) for ob in itertools.combinations(obj,2)])

        # otherwise, it's just the number of objects used
        try:
            nObjects = int(cutDict['objects'])
        except ValueError:
            print "Number of objects must be an integer"
            raise

        if requireAll:
            return lambda row, *obj: all([self.doCut(row, self.getCutName(cut,ob), ob) for foo, cut in cutDict['cuts'].iteritems() for ob in obj])
        else:
            return lambda row, *obj: any([all(self.doCut(row, self.getCutName(cut,ob), ob) for foo, cut in cutDict['cuts'].iteritems()) for ob in obj])



    def getCutName(self, cut, ob):
        '''
        Replaces 'TYPE' with the object type (e.g. TYPEIso becomes eIso or mIso)
        '''
        return cut.replace("TYPE", ob[0])


    def baseEvCut(self, cutDict):
        '''
        Return a function that does one event-level cut.
        cutDict is template[cut] or at least in the same format
        '''
        requireAll = cutDict['logic'] == 'and'
        if requireAll:
            return lambda row: all([self.cutEvVar(row, var.split("#")[0], val[0], val[1]) for var, val in cutDict['cuts'].iteritems()])
        else:
            return lambda row: any([self.cutEvVar(row, var.split("#")[0], val[0], val[1]) for var, val in cutDict['cuts'].iteritems()])


    def baseObjCut(self, cutDict):
        '''
        Return a function that does one event-level cut.
        cutDict is template[cut] or at least in the same format
        '''
        requireAll = cutDict['logic'] == 'and'
        if requireAll:
            return lambda row, obj: all([self.cutObjVar(row, var.split("#")[0], val[0], val[1], obj) for var, val in cutDict['cuts'].iteritems()])
        else:
            return lambda row, obj: any([self.cutObjVar(row, var.split("#")[0], val[0], val[1], obj) for var, val in cutDict['cuts'].iteritems()])


    def baseNObjCut(self, cutDict):
        '''
        Return a function that does one event-level cut.
        cutDict is template[cut] or at least in the same format
        '''
        requireAll = cutDict['logic'] == 'and'
        if requireAll:
            return lambda row, *obj: all([self.cutNObjVar(row, var.split("#")[0], val[0], val[1], *obj) for var, val in cutDict['cuts'].iteritems()])
        else:
            return lambda row, *obj: any([self.cutNObjVar(row, var.split("#")[0], val[0], val[1], *obj) for var, val in cutDict['cuts'].iteritems()])


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
            
        

#     def doCut(self, row, cutName, obj='', obj2=''):
#         '''
#         Returns true if obj passes cuts[cutName]
#         obj2 is ignored unless the cut's mode is '2obj'
# 
#         It turns out that we get the desired less/greaterOrEqual behavior with
#                 variable<cut XNOR lessThanCut
#             which is most easily expressed as
#                 variable<cut == lessThanCut
# 
#         If no objects are supplied, it will just give back the global variable with 
#             the appropriate name
#         '''
# 
# 
# 
#         assert cutName in self.cuts, 'Incorrect cut name %s'%cutName
# 
#         if 'options' not in self.cuts[cutName]:
#             if self.cuts[cutName]['mode'] == '2obj':
#                 passList = [((getattr(row, getVar2(obj, obj2, var.split('#')[0])) < cut[0]) == cut[1]) for var, cut in \
#                             self.cuts[cutName]['cuts'].iteritems()]
#             elif self.cuts[cutName]['mode'] == 'other':
# #                if cutName == 'eID' and ('2012' in self.cutSet or '8TeV' in self.cutSet):
#                 return self.eIDTight2012(row, obj)
# #                raise NameError('Special cut %s is not yet defined for cutSet %s'%(cutName,self.cutSet))
#             else:
#                 passList = [((getattr(row, getVar(obj, var.split('#')[0])) < cut[0]) == cut[1]) for var, cut in \
#                             self.cuts[cutName]['cuts'].iteritems()]
# 
#             if self.cuts[cutName]['mode'] == 'or':
#                 return any(passList)
#             return all(passList)
#         else:
#             assert 'abs' in self.cuts[cutName]['options'], "Unknown option %s"%self.cuts[cutName]['options']
#             absolutes = self.cuts[cutName]['options'].split('abs')
#             passList = []
#             for var, cut in self.cuts[cutName]['cuts'].iteritems():
#                 if var in absolutes:
#                     passList.append((abs(getattr(row, getVar(obj, var.split('#')[0]))) < cut[0]) == cut[1])
#                 else:
#                     passList.append((getattr(row, getVar(obj, var.split('#')[0])) < cut[0]) == cut[1])
#             if self.cuts[cutName]['mode'] == 'or':
#                 return any(passList)
#             return all(passList)


