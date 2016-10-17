##############################################################################
#                                                                            #
#    AnalysisManager.py                                                      #
#                                                                            #
#    A class that handles related analyses, creating analyzers and           #
#    making threads out of them, making sure they happen in the right        #
#    order and so forth.                                                     #
#                                                                            #
#    Nate Woods, U. Wisconsin                                                #
#                                                                            #
##############################################################################

import os, glob

from Analyzer import Analyzer


# temporary hack: samples with one of these in the name will not have trigger
# requirements applied
_samplesWithoutTrigger = [
    'ZZTo4L',
    'GluGluZZ',
    'Contin',
    'WZTo3LNu',
    ]

def parseInputs(inputs):
    infiles = []
    for path in inputs.split(','):
        if path.endswith('.root'):
            if glob.glob(path):
                infiles += glob.glob(path)
        else:
            if glob.glob(path+'*.root'):
                infiles += glob.glob(path+'*.root')

    # Remove duplicates from input files, just in case
    infiles = list(set(infiles))

    return infiles


def runAnAnalyzer(channels, baseCuts, infile, outdir, resultType,
                  maxEvents, intLumi, cleanRows, cutModifiers):
    '''
    Run an Analyzer.
    Intended for use in threads, such that several processes all do this once.
    '''
    outfile = outdir+'/'+(infile.split('/')[-1])
    try:
        analyzer = Analyzer(channels, baseCuts, infile, outfile,
                            resultType, maxEvents, intLumi,
                            cleanRows, cutModifiers=cutModifiers)
    # Exceptions won't print from threads without help
    except Exception as e:
        print "**********************************************************************"
        print "EXCEPTION"
        print "Caught exception:"
        print e
        print "While initializing analyzer for {} with base cuts {} and modifiers [{}]".format(infile, baseCuts, ', '.join(m for m in cutModifiers))
        print "Killing task"
        print "**********************************************************************"
        return

    try:
        analyzer.analyze()
    except Exception as e:
        print "**********************************************************************"
        print "EXCEPTION"
        print "Caught exception:"
        print e
        print "While running analyzer for {} with base cuts {} and modifiers [{}]".format(infile, baseCuts, ', '.join(m for m in cutModifiers))
        print "Killing task"
        print "**********************************************************************"
        return


class AnalysisManager(object):
    def __init__(self, allAnalyses, inputDir, pool, channels, assumeInputExists=False):
        self.all = allAnalyses
        self.channels = channels
        self.inputDir = inputDir
        self.files = parseInputs(os.path.join(inputDir, '*.root'))
        self.samples = [f.split('/')[-1].replace('.root','') for f in self.files]

        self.analyses = {s:{} for s in self.samples}
        self.pool = pool

        self.assumeInputExists = assumeInputExists
        self.endResults = set()

    class FakeResult(object):
        '''
        A class that is always ready.
        '''
        @staticmethod
        def ready():
            return True

    def addAnalyses(self, *analyses):
        '''
        Puts necessary info in self.analyses for all samples
        '''
        for s in self.samples:
            for ana in analyses:
                self.addAnalysisForSample(ana, s)
                self.endResults.add(ana)
            self.analyses[s]['result'] = self.FakeResult()

    def addAnalysisForSample(self, ana, sample):
        '''
        Puts necessary info in self.analyses[sample], returns that entry
        '''
        info = self.all[ana]
        prereq = info.get('prereq', '')
        if prereq:
            above = self.addAnalysisForSample(prereq, sample)
        else:
            above = self.analyses[sample]

        if ana not in above:
            above[ana] = {'params' : info.copy()}
            if 'params' in above:
                resultDir = above['params']['resultDir']
            else:
                resultDir = ''
            above[ana]['params']['inFile'] = os.path.join(self.inputDir, resultDir, sample+'.root')

        return above[ana]

    def runReady(self):
        '''
        Adds any analyzers that are ready to go to the worker pool.
        Returns False if everything is finished.
        '''
        samplesDone = []
        for s in self.samples:
            done = self.tryToRunAnalyses(self.analyses[s], True)
            samplesDone.append(done)
        return not all(samplesDone)
        #return not all(self.tryToRunAnalyses(self.analyses[s]) for s in self.samples)

    def tryToRunAnalyses(self, info, inPrereqChain):
        '''
        Takes a dict with a result and some info for the previous analysis,
        and similar dicts about the next analyses, and runs the next analyses
        if we're ready to do that.
        inPrereqChain should be True if no previous steps were desired final
        results, so they can be skipped if we're assuming inputs exist
        '''
        if 'result' not in info:
            info['result'] = self.submitAnalysis(info.pop('params'))
            return False
        if not info['result'].ready():
            return False

        subresults = [True]
        for ana in info:
            if ana == 'result' or ana == 'params':
                continue
            if self.assumeInputExists and inPrereqChain:
                if ana not in self.endResults:
                    #print ana
                    #print info[ana]
                    #exit(1)
                    info[ana]['result'] = self.FakeResult()
                else:
                    inPrereqChain = False

            subresults.append(self.tryToRunAnalyses(info[ana], inPrereqChain))

        return all(subresults)

    defaultParams = {
        'baseCuts' : 'BaseCuts2016',
        'maxEvents' : float('inf'),
        'intLumi' : 9200.,
        'cleanRows' : '',
        'cutModifiers' : [],
        'resultType' : 'CopyNtuple',
        }
    argVars = ['channels', 'baseCuts', 'inFile', 'outDir', 'resultType',
               'maxEvents', 'intLumi', 'cleanRows', 'cutModifiers']

    def submitAnalysis(self, params):
        '''
        Given some parameters, submit a job running an
        analyzer with those parameters and return a thread result object.
        '''
        argDict = self.defaultParams.copy()
        argDict['channels'] = self.channels
        argDict['outDir'] = os.path.join(self.inputDir, params['resultDir'])
        argDict.update(params)

        if any(s in argDict['inFile'] for s in _samplesWithoutTrigger):
            print 'Not applying trigger requirements for {}'.format(argDict['inFile'])
            argDict['cutModifiers'] = ['NoTrigger'] + argDict['cutModifiers'][:]

        if not os.path.isdir(argDict['outDir']):
            os.makedirs(argDict['outDir'])

        args = tuple(argDict[v] for v in self.argVars)

        result = self.pool.apply_async(runAnAnalyzer, args=args)

        return result






