
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
from rootpy.tree import Tree
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
        self.outFile = root_open(self.fileName, "recreate")
        self.channels = channels
        self.directories = []
        self.keepTotal = kwargs.get('keepTotal',False) or 'Total' in channels
        self.template = self.setupTemplate(*args, **kwargs)
        self.results, self.functions = self.setupResults(*args, **kwargs)


    def saveNumber(self, result, number, var=''):
        '''
        Virtual.
        Used to store num in result
        '''
        pass


    def getResultObject(self, resultDir, var):
        '''
        Virtual
        Given a directory of result objects and a variable, pick the one 
        variable should be saved into.
        '''
        pass


    def setupResultObjects(self, resultArgs, *args, **kwargs):
        '''
        Virtual.
        Returns a dictionary containing result objects (histograms or Trees
        or whatever), takes a dictionary of arguments needed to build these.
        '''
        return {}


    def finalizeResultObject(self, outputs):
        '''
        Virtual.
        "close" this result object for this event after values have been
        placed. I.e., fill a tree after the buffers are set.
        Not always needed (e.g., histograms are all set after being filled).
        '''
        pass


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
        results, calculators = self.setupResultDirectory(self.template, *args, **kwargs)

        functions = self.setupFunctions(results, calculators)

        return results, functions


    def setupFunctions(self, results, calculators):
        '''
        Given nested dictionaries of result objects and functions (of the
        same structure!), return a nested dictionary of functions that
        calculate numbers (with the calculators) and place them in the
        correct result objects.
        '''
        funs = {}
        for name, calc in calculators.iteritems():
            if isinstance(calc, dict):
                funs[name] = self.setupFunctions(results[name], calc)
            else:
                funs[name] = self.getSaveFunction(results, name, calc)

        return funs


    def getSaveFunction(self, results, var, calculator):
        '''
        Returns a function that saves the result of caclulator in the correct
        item in results for variable var.
        This is a separate function to deal with obnoxious Python scoping
        issues.
        '''
        result = self.getResultObject(results, var)
        return lambda row: self.saveNumber(result, calculator(row), var)


    def setupResultDirectory(self, temp, *args, **kwargs):
        '''
        Recursive helper function for self.setupResults.
        Takes a dictionary that acts as a template for two dictionaries, one
        of result objects to be saved eventually, one of functions to compute
        the numbers to go in them.
        '''
        variables = {} # functions for these variables, returned

        varTemp = temp.pop('vars', {})

        resultArgs = {}
        for var, varDef in varTemp.iteritems():
            if 'f' in varDef:
                variables[var] = varDef.get('f')
            else:
                variables[var] = self.copyFunc(var, *args, **kwargs)
            resultArgs[var] = varDef.get('params', None)

        results = self.setupResultObjects(resultArgs, *args, **kwargs)

        allItems = temp.pop('all', {})

        for k, v in temp.iteritems():
            # Anything in 'all' gets included, plus everything unique to this directory
            subTemp = {}
            for sub in allItems:
                subTemp[sub] = allItems[sub].copy()
            for subSub in v:
                if subSub in subTemp:
                    subTemp[subSub].update(v[subSub].copy()) # specific items overwrite items in 'all'
                else:
                    subTemp[subSub] = v[subSub].copy()

            subdir = Directory(k)
            subdir.cd()
            subResults, subVariables = self.setupResultDirectory(subTemp, 
                                                                 *args, 
                                                                 **kwargs)
#            subdir.Write()
            subdir.GetMotherDir().cd()
            self.directories.append(subdir)

            variables[k] = subVariables
            results[k] = subResults

        return results, variables            


    def saveVar(self, row, *varPath):
        '''
        Saves a variable from row.
        varPath should be the path to the variable, including the variable name
        itself last, in the same format as saveRow's *args.
        '''
        func = self.getDictItem(self.functions, *varPath)
        func(row)


    def saveRow(self, row, *pathToVars, **kwargs):
        '''
        Save everything we want from the row. args specified the directory we
        care about (i.e. the channel).
        The directory is specified by args; all variables in 
        self.variables[args[0]][args[1]][...] will be stored. 
        The keyword argument "nested" causes saveRow to recurse down 
        the directory structure and do the same in all subdirectories
        '''
        nested = kwargs.get("nested", False)
        funs = self.getDictItem(self.functions, *pathToVars)
        for var, fun in funs.iteritems():
            if not isinstance(fun, dict): # Not nested by default
#                print var
                fun(row)
            elif nested: # if we do want to recurse down
                self.saveRow(row, *(list(pathToVars)+[var]), nested=True)
                
        # recursed down here, don't nest the finalize function
        self.finalizeEvent(self.getDictItem(self.results, *pathToVars), False)


    def finalizeEvent(self, resultDict, nested=False):
        '''
        Finalize result objects (filling the tree or whatever). 
        Recurses down result dicts if nested is True.
        '''
        for var, result in resultDict.iteritems():
            if not isinstance(result, dict):
                self.finalizeResultObject(result)
            elif nested:
                self.finalizeEvent(result)


    def copyFunc(self, var):
        '''
        Return a function that returns the value of var from a row.
        '''
        return lambda row: evVar(row, var)


    def save(self, *args):
        '''
        Save output file
        '''
        self.outFile.close()




