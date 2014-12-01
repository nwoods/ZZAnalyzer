
'''

Base class for a module to save events that pass all cuts (or whatever). 
Mostly virtual, because there's a lot of things one might want to do with
passing events; put them in a new ntuple to make a skim, make an ntuple 
with some of the variables (maybe combined into new variables) to make
a different analysis ntuple, fill histograms with some of the variables,
make plots, etc. This contains machinery for setting up a new file, saving
it, and other things that one always wants to do in an output module.

Author: Nate Woods, U. Wisconsin.

'''

from rootpy.io import root_open, Directory
from rootpy.tree import Tree, Ntuple
from ZZHelpers import * # evVar, objVar, nObjVar


class ZZResultSaverBase(object):
    '''
    Virtual class with methods that will always be needed by a module 
    for saving output, including pure virtual methods that must always be
    defined by a subclass.
    '''
    def __init__(self, fileName, channels, *args, **kwargs):
        '''
        Superclass setup. fileName is a string with the full (including path)
        name of the output file, channels is a list of strings with the names
        of the channels. 
        If kwargs["keepTotal'] == True, every stored result is stored for both 
        its own channel and for channel 'Total'.
        '''
        self.fileName = fileName
        self.channels = channels
        self.keepTotal = kwargs.get('keepTotal',False) or 'Total' in channels
        self.template = self.setupTemplate(*args, **kwargs)
        self.results, self.variables = self.setupResults(*args, **kwargs)


    def saveNumber(self, num, resultObject):
        '''
        Virtual.
        Used to store num in resultObject
        '''
        pass


    def setupResultObjects(self, resultArgs, *args, **kwargs):
        '''
        Virtual.
        Returns a dictionary containing result objects (histograms or Trees
        or whatever), takes a dictionary of arguments needed to build these.
        '''
        return {}


    def getDictItem(self, theDict, *args):
        '''
        Cute little function to get theDict[args[0]][args[1]][...]
        '''
        return reduce(dict.__getitem__, args, theDict) 


    def setupResults(self, *args, **kwargs):
        '''
        Virtual.
        Inherited classes should use this to set two dictionaries mapping 
        channels (or whatever) to trees (or histograms or ntuples or whatever)
        that will be stored in the  output file, and to functions that can be
        used to calculate the numbers to put into the stored objects.
        The dictionary structure is assumed to be the desired directory 
        structure of the resulting output file. That is, at the end we'll
        traverse through this dictionary, and anytime we find a dictionary
        we'll make a new directory, go into it, and set up everything in it
        (recursively). The key pointing to a dictionary will be the name of the
        resulting subdirectory.
        Several keywords are exceptions:
            'all' is the key for objects that are shared by all other 
                subdirectories of the current directory, used (e.g.) for
                variables that are shared by all channels
            'vars' is the key for the dictionary of variables we will actually
                save. Its keys are the names of the variables, the values they
                point to are dictionaries with entries:
                    'f' - function to compute the variable
                        If 'f' is missing, the variable is assumed to be in the
                        input ntuple and directly copiable
                    'params' - The parameters needed to construct the result
                        objects. It 'params' is missing, None will be passed
                        to the function that generates result objects.
        '''
#         self.stopnow = False
        results, variables = self.setupResultDirectory(self.template, *args, **kwargs)

        return results, variables


    def setupResultDirectory(self, temp, *args, **kwargs):
        '''
        Recursive helper function for self.setupResults.
        Takes a dictionary that acts as a template for two dictionaries, one
        of result objects to be saved eventually, one of functions to compute
        the numbers to go in them.
        '''
        variables = {} # functions for these variables, returned

#         print temp
        varTemp = temp.pop('vars', {})
#         print temp
#         print varTemp
        resultArgs = {}
        for var, varDef in varTemp.iteritems():
            if 'f' in varDef:
                variables[var] = varDef.get('f')
            else:
                variables[var] = self.copyFunc(var, *args, **kwargs)
            resultArgs[var] = varDef.get('params', None)

        results = self.setupResultObjects(resultArgs, *args, **kwargs)

        allItems = temp.pop('all', {})

#         print "\n"
#         for k in temp:
#             print k
#             print "\n"

        for k, v in temp.iteritems():
#             print temp
#             print k
#             print v
            subTemp = {}
            if k in allItems:
                subTemp = allItems[k].copy()
                subTemp.update(v) # specific items overwrite items in 'all'
 #               print "Hi!"
            else:
                subTemp = v.copy()
#                print subTemp
#                if self.stopnow:
#                    exit(0)
#                else:
#                    print "\n\n Second time:"
#                    self.stopnow = True
#
#            print "\n\n"
            subResults, subVariables = self.setupResultDirectory(subTemp, 
                                                                 *args, 
                                                                 **kwargs)
            variables[k] = subVariables
            results[k] = subResults

        return results, variables            


    def saveRow(self, row, *args, **kwargs):
        '''
        Save everything we want from the row. args specified the directory we
        care about (i.e. the channel).
        The directory is specified by args; all variables in 
        self.variables[args[0]][args[1]][...] will be stored. 
        The keyword argument "nested" causes saveRow to recurse down 
        the directory structure and do the same in all subdirectories
        '''
        nested = kwargs.get("nested", False)
        outputs = self.getDictItem(self.results, *args)
        calculators = self.getDictItem(self.variables, *args)
        for var in outputs:
            if not isinstance(outputs[var], dict): # Not nested by default
                self.saveNumber(calculators[var](row), outputs[var])
            elif nested: # if we do want to recurse down
                self.saveRow(row, *(list(args)+[var]), nested=True)


    def copyFunc(self, var):
        '''
        Return a function that returns the value of var from a row.
        '''
        return lambda row: evVar(row, var)


    def save(self, *args):
        '''
        Save everything, by calling self.saveResult, which saves everything in 
        a directory structure matching the dictionary structure of self.results
        (see header comment on self.setupResults)
        '''
        with root_open(self.fileName,"recreate") as f:
            self.saveResult(self.results, *args)


    def saveResult(self, result, *args):
        '''
        Recursively saves objects in a directory structure matching the 
        dictionary structure of result. See header comment on self.setupResults
        for details.
        '''
        for name, obj in result.iteritems():
            if isinstance(obj, dict):
                subdir = Directory(name)
                subdir.cd()
                self.saveResult(obj)
                subdir.Write()
                subdir.GetMotherDir().cd()
            else:
                obj.Write()




#     def commonSimpleBranches(self):
#         '''
#         Virtual.
#         See self.setupVariables header comment for use.
#         '''
#         return []
# 
# 
#     def specificSimpleBranches(self):
#         '''
#         Virtual.
#         See self.setupVariables header comment for use.
#         '''
#         return {chan : [] for chan in self.channels}
# 
# 
#     def commonComputedBranches(self):
#         '''
#         Virtual.
#         See self.setupVariables header comment for use.
#         '''
#         return {}
# 
# 
#     def specificComputedBranches(self):
#         '''
#         Virtual.
#         See self.setupVariables header comment for use.
#         '''
#         return {chan : {} for chan in self.channels}
# 
# 
#     def setupVariables(self, *args, **kwargs):
#         '''
#         Figures out from vitual methods how to make a dictionary of functions
#         to get variables we want to save, and returns this dictionary.
#         Wants daughter classes to define the following methods:
#             self.commonSimpleBranches() - names of branches that should be 
#                                           copied directly for all trees
#             self.specificSimpleBranches() - dictionary mapping specific trees 
#                                             to branches that they should copy
#             self.commonComputedBranches() - dictionary mapping branch names to
#                                             a method for computing them for 
#                                             branches in all trees
#             self.specificComputedBranches() - dictionary mapping trees to 
#                                               dictionaries mapping branch names
#                                               to methods for computing them for
#                                               tree-specific branches
#         '''
#         # Base dictionary for common branches
#         commonVars = {}        
# 
#         # Make a simple function to get the variable for all the common 
#         # simple branches
#         for var in self.commonSimpleBranches():
#             commonVars[var] = lambda row: evVar(row, var)
# 
#         # Add common branches for which functions are specially defined
#         for var, fun in self.commonComputedBranches().iteritems():
#             commonVars[var] = fun
# 
#         out = {}
# 
#         # Make a copy for every channel
#         # Shallow copy should be good enough because commonVars doesn't 
#         # hold containers
#         for chan in self.channels:
#             out[chan] = commonVars.copy()
# 
#         # Add channel-specific functions to the relevant dictionary
#         for chan, varList in self.specificSimpleBranches():
#             for var in varList:
#                 out[chan][var] = lambda row: evVar(row, var)
#         for chan, funDict in self.specificComputedBranches().iteritems():
#             for var, fun in funDict.iteritems():
#                 out[chan][var] = fun
#         
#         return out
