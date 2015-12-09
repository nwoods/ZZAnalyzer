
'''

Base class for module to save ntuples in a file. 

Daughter classes should override the relevant functions to create a dictionary
mapping a variable name to the ntuple and variable it should fill. All 
variables in a directory are assumed to go in the same ntuple there.

Implemented with rootpy Tree and TreeModel, because rootpy ntuples aren't
sufficiently flexible.

Author: Nate Woods, U. Wisconsin

'''

from rootpy.io import DoesNotExist
from rootpy.tree import Tree, TreeModel, FloatCol, IntCol
from rootpy import lookup_by_name

from ZZResultSaverBase import ZZResultSaverBase
from ZZHelpers import * # evVar, objVar, nObjVar
from collections import OrderedDict



class ZZNtupleSaver(ZZResultSaverBase):
    def __init__(self, fileName, channels, *args, **kwargs):
        '''
        More stuff may be set up in daughter class __init__ methods.
        '''
        self.specialVarList = ['copy']

        super(ZZNtupleSaver, self).__init__(fileName, channels, *args, **kwargs)

        self.copyMetaData(channels)
        

    def copyMetaData(self, channels):
        '''
        Copy over metadata for each channel if it exists. If metaInfo tree
        doesn't exist, print a warning but don't crash.
        '''
        for ch in channels:
            chDir = self.inputs[ch].GetDirectory().GetMotherDir()
            try:
                chDir.copytree(self.outFile.Get(ch), "metaInfo")
            except DoesNotExist:
                print "WARNING: %s/metaInfo not found. Metadata will not be copied!"%ch


    def saveNumber(self, tree, num, var=''):
        '''
        Place num in tree buffer as var for later filling
        '''
        setattr(tree, var, num)

        
    def specialVars(self):
        '''
        The "variable" copy is special (giving the ntuple and branches to copy)
        and should be passed right through to the object builder.
        '''
        return self.specialVarList


    _columnTypes_ = {
        lookup_by_name("Float_t") : FloatCol,
        lookup_by_name("Int_t") : IntCol,
        }

    @classmethod
    def getColumnType(cls, dataType):
        '''
        Get the type of the column to use for this object in a TreeModel.
        '''
        try:
            return cls._columnTypes_[dataType]
        except KeyError:
            # inherits from rootpy.tree.treetypes.Column
            class NewColumn(FloatCol.__bases__[0]): 
                type = dataType
            cls._columnTypes_[dataType] = NewColumn
            return NewColumn


    def setupResultObjects(self, resultArgs, *args, **kwargs):
        '''
        Dict with an Ntuple keyed to 'Ntuple'
        '''
        if not resultArgs:
            return {}

        cols = {} # cols[branchName] = BranchType (FloatCol is default)
        # default values of copy variables
        copyFrom = False # will be an ntuple if copying
        copyOnly = None # will be a list of branches to copy if needed
        copyExcept = None # will be a list of branches *not* to copy if needed

        if 'copy' in resultArgs:
            copyCols = []
            copyVars = resultArgs.pop('copy')
            copyFrom = copyVars.pop('ntuple')
            if 'only' in copyVars:
                assert 'except' not in copyVars, \
                    "Can't have both an only list and an except list for ntuple %s!"%copyFrom.GetName()
                copyCols = copyVars['only']
            elif 'except' in copyVars:
                copyExcept = copyVars['except']
                for b in copyFrom.iterbranchnames():
                    if b not in copyExcept:
                        copyCols.append(b)
            else: # otherwise, just copy everything
                copyCols = copyFrom.branchnames
            
            for col in copyCols:
                typeName = Tree.branch_type(copyFrom.GetBranch(col))
                cols[col] = ZZNtupleSaver.getColumnType(lookup_by_name(typeName))

        # Everything else in resultArgs should be new branches
        cols.update({c:FloatCol for c in resultArgs.keys()})

        modelCols = {}
        # Sort so entries are in alphabetical order in TBrowser
        for col in sorted(cols):
            modelCols[col] = cols[col]()
    
        ntupleModel = type("aModel", (TreeModel,), modelCols)
        ntuple = Tree("Ntuple", model=ntupleModel)
        
        if bool(copyFrom):
            # This seems to be required to initialize the buffer. No idea why.
            for row in copyFrom:
                break

            # Set copying branches to point to the input ntuple's buffer
            ntuple.set_buffer(copyFrom._buffer, copyOnly, copyExcept)

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
        ntuple.Fill()
