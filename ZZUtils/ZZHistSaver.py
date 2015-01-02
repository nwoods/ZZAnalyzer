
'''

Base class for module to save histograms in a file. 

By default, just makes a directory for each channel and dumps all relevant
histograms into it, but of course this can be overridden by daughters. 

Daughter classes should override the relevant functions to create a dictionary
mapping a variable name to the histogram it should fill.

Author: Nate Woods, U. Wisconsin

'''

from rootpy.plotting import Hist
from ZZResultSaverBase import ZZResultSaverBase
from ZZHelpers import * # evVar, objVar, nObjVar



class ZZHistSaver(ZZResultSaverBase):
    def __init__(self, fileName, channels, *args, **kwargs):
        '''
        More stuff may be set up in daughter class __init__ methods.
        '''
        super(ZZHistSaver, self).__init__(fileName, channels, *args, **kwargs)


    def saveNumber(self, hist, num, var=''):
        '''
        Fill hist with num
        '''
        hist.Fill(num)
#         print histDict[var].GetName()
#         print var
#         print histDict[var].GetEntries()
#         print "\n"


    def setupResultObjects(self, resultArgs, *args, **kwargs):
        '''
        Dictionary of histograms
        '''
        hists = {}
        for var, params in resultArgs.iteritems():
            if len(params) == 3:
                hists[var] = Hist(*params,name=var)
            else:
                hists[var] = Hist(params, name=var) # uneven bins passed as list

        return hists
        
                     
    def getResultObject(self, resultDict, var):
        '''
        Get correct histogram from dictionary
        '''
        return resultDict[var]
