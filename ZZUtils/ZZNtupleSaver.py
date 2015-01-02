
'''

Base class for module to save ntuples in a file. 

Daughter classes should override the relevant functions to create a dictionary
mapping a variable name to the ntuple and variable it should fill. All 
variables in a directory are assumed to go in the same ntuple there.

Implemented with rootpy Tree and TreeModel, because rootpy ntuples aren't
sufficiently flexible.

Author: Nate Woods, U. Wisconsin

'''

from rootpy.tree import Tree, TreeModel, FloatCol
from ZZResultSaverBase import ZZResultSaverBase
from ZZHelpers import * # evVar, objVar, nObjVar



class ZZNtupleSaver(ZZResultSaverBase):
    def __init__(self, fileName, channels, *args, **kwargs):
        '''
        More stuff may be set up in daughter class __init__ methods.
        '''
        super(ZZNtupleSaver, self).__init__(fileName, channels, *args, **kwargs)


    def saveNumber(self, tree, num, var=''):
        '''
        Place num in tree buffer as var for later filling
        '''
        setattr(tree, var, num)



    def setupResultObjects(self, resultArgs, *args, **kwargs):
        '''
        Dict with an Ntuple keyed to 'Ntuple'
        '''
        modelCols = {}
        for result in resultArgs:
            modelCols[result] = FloatCol()
        
        ntupleModel = type("aModel", (TreeModel,), modelCols)
        ntuple = Tree("Ntuple", model=ntupleModel)
        
        return {'Ntuple' : ntuple}

                     
    def getResultObject(self, resultDict, var):
        '''
        Get correct histogram from dictionary
        '''
        return resultDict['Ntuple']

    
    def finalizeResultObject(self, ntuple):
        '''
        Fill the ntuple after the buffer is already filled.
        '''
        print "Filling " + ntuple.GetName()
        try:
            print "e1_e2_Mass = " + str(ntuple["e1_e2_Mass"])
        except:
            pass
        try:
            print "m1_m2_Mass = " + str(ntuple["m1_m2_Mass"])
        except:
            pass
        ntuple.Fill()
