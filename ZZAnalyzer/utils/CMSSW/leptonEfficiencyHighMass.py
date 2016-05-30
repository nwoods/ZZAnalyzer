# import ROOT in batch mode
import sys
oldargv = sys.argv[:]
sys.argv = [ '-b-' ]
from rootpy.ROOT import gROOT
gROOT.SetBatch(True)
sys.argv = oldargv

import logging
from rootpy import log as rlog; rlog = rlog["/leptonEfficiencyHighMass"]
logging.basicConfig(level=logging.WARNING)
rlog["/ROOT.TCanvas.Print"].setLevel(rlog.WARNING)
rlog["/ROOT.TUnixSystem.SetDisplay"].setLevel(rlog.ERROR)

# load FWlite python libraries
from DataFormats.FWLite import Handle, Events

from rootpy.plotting import Hist, Hist2D, Graph, Canvas, Legend
from rootpy.plotting.hist import _Hist2D
from rootpy.plotting.utils import draw
from rootpy import asrootpy

from collections import OrderedDict
from multiprocessing import cpu_count, Pool, Manager
import signal
import time
from math import sqrt
from itertools import combinations

from ZZAnalyzer.plotting import PlotStyle
from ZZAnalyzer.utils.helpers import deltaR, Z_MASS

style = PlotStyle()


class Observation(object):
    '''
    Need something pickleable to get results out of threads
    '''
    def __init__(self, hBase, hists, uniform):
        self.uniform = uniform
        self.hBase = hBase
        self.hists = hists

        if not self.uniform:
            for h in self.hists.values():
                for b in h:
                    if b.overflow:
                        continue
                    baseSize = Observation.getBinSize(b)
                    break
                for b in h:
                    if b.overflow:
                        continue
                    factor = Observation.getBinSize(b) / baseSize
                    b.value = b.value / factor
                    b.error = b.error / sqrt(factor)

    @staticmethod
    def getBinSize(bin):
        '''
        Takes a bin proxy, returns width/area/volume
        Works because the "width" in a nonexistent dimension is set to 1
        '''
        return bin.x.width * bin.y.width * bin.z.width
        

    def failingHist(self, cut):
        try: # pickling unrootpys ROOT things
            return self.hists[cut].clone()
        except AttributeError:
            for c in self.hists:
                self.hists[c] = asrootpy(self.hists[c])
            return self.failingHist(cut)

    def passingHist(self, cut):
        try: # pickling unrootpys ROOT things
            h = self.hBase.empty_clone()
        except AttributeError:
            self.hBase = asrootpy(self.hBase)
            h = self.hBase.empty_clone()

        for c in self.hists.keys()[::-1]:
            if c == cut:
                return h
            h.add(self.hists[c])    


class Observable(object):
    def __init__(self, function, binning):
        if len(binning) == 3 or len(binning) == 1:
            self.hBase = Hist(*binning)
            self.uniform = len(binning) == 3
        elif len(binning) == 6 or len(binning) == 4 or len(binning) == 2:
            self.hBase = Hist2D(*binning)
            self.uniform = len(binning) == 6
        else:
            raise ValueError("binning {} is not allowed".format(binning))

        self.binning = binning
            
        self.f = function

        self.hists = OrderedDict()

    def addCut(self, name):
        self.hists[name] = self.hBase.clone()
        self.hists[name].SetDirectory(0)

    def selfDestruct(self, *args):
        raise ValueError("You may not add a cut after the first time"
                         " an observable is filled!")

    def _fill(self, cut, *args):
        '''
        Actual fill function. self.fill is set to this after the first use
        '''
        val = self.f(*args)
        
        self.hists[cut].fill(val)

    def _fillND(self, cut, *args):
        '''
        Fill function for >= 2D histograms
        '''
        vals = self.f(*args)

        self.hists[cut].fill(*vals)
        
    def fill(self, cut, *args):
        '''
        The first time this is done, add a hist to the cut flow for leptons
        that pass everything, and forbid adding new cuts. Then set this
        method to self._fill so these setup things are only done once.
        '''
        self.addCut("pass")

        self.addCut = self.selfDestruct

        if self.hBase.GetDimension() == 1:
            self.fill = self._fill
        else:
            self.fill = self._fillND
        self.fill(cut, *args)

    def getResults(self):
        return Observation(self.hBase, self.hists, self.uniform)


class Classification(object):
    '''
    Need pickleable thing
    '''
    def __init__(self, observables1, observables2, cutFlow, zCutFlow, mass, 
                 color='black', marker=20):
        self.observables = observables2
        self.observables.update(observables1)
        self.cutFlow = cutFlow
        self.zCutFlow = zCutFlow
        self.m = mass
        self.color = color
        self.marker=marker

    def formatHist(self, h, normalize=True):
        if normalize and bool(h.Integral()):
            h.scale(1. / h.Integral())

        if(h.GetDimension() == 1):
            h.color = self.color
            h.drawstyle = 'hist'
            h.SetTitle("m_{{H}} = {}".format(self.m))
        else:
            h.drawstyle = 'colz'
            h.SetTitle('_M-{}'.format(self.m))

        return h
        
    def makeEfficiency(self, cut, var, nMinus1=False):
        obs = self.observables[var]

        num = obs.passingHist(cut)

        if nMinus1:
            denom = num.clone()
            denom.add(obs.failingHist(cut))
        else:
            denom = obs.passingHist('genMatched')

        if num.GetDimension() == 1:
            eff = Graph(type='asymm')
            eff.Divide(num, denom)

            eff.color = self.color
            eff.markerstyle = self.marker
            eff.drawstyle = 'PE'
            eff.SetTitle("m_{{H}} = {}".format(self.m))

            return eff
        else:
            num.Divide(denom)
            num.drawstyle = 'colz'
            num.SetTitle('_M-{}'.format(self.m))
            
            return num

    def passingHist(self, cut, var, normalize=True):
        return self.formatHist(self.observables[var].passingHist(cut),
                               normalize)

    def failingHist(self, cut, var, normalize=True):
        return self.formatHist(self.observables[var].failingHist(cut),
                               normalize)


class LeptonClassifier(object):
    def __init__(self):
        self.cuts = OrderedDict()
        self.observables1 = {}
        self.observables2 = {}
        self.cutFlow = OrderedDict()
        self.zCutFlow = OrderedDict()
        self.addCut('total', lambda *args: True)
        self.addCut('genMatched', self.__class__.goodGen)


    def addObservable1(self, name, function, binning):
        '''
        observables that needs just 1 object (+ maybe the vertext) to calculate
        '''
        obs = Observable(function, binning)
        for cut in self.cuts:
            obs.addCut(cut)
        self.observables1[name] = obs

    def addObservable2(self, name, function, binning):
        '''
        observable that needs 2 objects (and maybe their delta R) to calculate
        '''
        obs = Observable(function, binning)
        for cut in self.cuts:
            obs.addCut(cut)
        self.observables2[name] = obs

    def addCut(self, name, function):
        self.cuts[name] = function
        self.cutFlow[name] = 0
        self.zCutFlow[name] = 0
        for obs in self.observables1.itervalues():
            obs.addCut(name)
        for obs in self.observables2.itervalues():
            obs.addCut(name)

    @classmethod
    def goodGen(cls, lep, *args):
        '''
        Is the associated gen particle one we should choose?
        '''
        if lep.genParticleRef().isNull():
            return False

        return lep.genParticleRef().fromHardProcessFinalState()

    @classmethod
    def preselect(cls, lep, *args):
        return lep.pt() > 4.

    def classify1(self, lep, vtx):
        '''
        classify single object
        returns failed cut (or '' for preselection, or 'pass')
        '''
        if not self.__class__.preselect(lep):
            return ''

        for cut, f in self.cuts.iteritems():
            if not f(lep, vtx):
                for obs in self.observables1.itervalues():
                    obs.fill(cut, lep, vtx)
                return cut
            self.cutFlow[cut] += 1
        else: # if all cuts are passed
            for obs in self.observables1.itervalues():
                obs.fill("pass", lep, vtx)
            return 'pass'

    def classify2(self, obj1, failedCut1, obj2, failedCut2):
        '''
        classify dilepton object given which cuts they failed
        (the earlier failure is used)
        '''
        for cut in self.zCutFlow:
            if cut == failedCut1 or cut == failedCut2:
                break
            self.zCutFlow[cut] += 1
        dR = deltaR(obj1.eta(), obj1.phi(), obj2.eta(), obj2.phi())
        for obs in self.observables2.itervalues():
            obs.fill(failedCut1, obj1, obj2, dR)
            obs.fill(failedCut2, obj2, obj1, dR)

    def firstFailedCut(self, lep, vtx):
        '''
        Returns empty string if object fails preselection or passes
        '''
        if not self.__class__.preselect(lep):
            return ''

        for cut, f in self.cuts.iteritems():
            if not f(lep, vtx):
                return cut
        
        return ''
    
    def getResults(self, mass, color, marker):
        observations1 = {name : obs.getResults() for name, obs in self.observables1.iteritems()}
        observations2 = {name : obs.getResults() for name, obs in self.observables2.iteritems()}
        
        return Classification(observations1, observations2, self.cutFlow, 
                              self.zCutFlow, mass, color, marker)


class MuonClassifier(LeptonClassifier):
    def __init__(self):
        super(MuonClassifier, self).__init__()
    
    @classmethod
    def goodGen(cls, lep, *args):
        '''
        Is the associated gen particle one we should choose?
        '''
        if lep.genParticleRef().isNull():
            return False

        gp = lep.genParticleRef()
        
        return gp.fromHardProcessFinalState() and abs(gp.eta()) < 2.4 and gp.pt() > 5.

    @classmethod
    def preselect(cls, mu):
        if mu.pt() < 4. or not mu.muonBestTrack():
            return False
        return True


class MassPoint(object):
    def __init__(self, m, files, color='black', marker=20, name=''):
        self.m = m
        self.color = color
        self.marker = marker
        self.name = name
        if isinstance(files, str):
            self.files = files.split(',')
        else:
            self.files = files
        self.events = Events(self.files)

        self.classifier = MuonClassifier()

    def addCut(self, name, function):
        self.classifier.addCut(name, function)

    def addObservable1(self, name, function, binning):
        self.classifier.addObservable1(name, function, binning)

    def addObservable2(self, name, function, binning):
        self.classifier.addObservable2(name, function, binning)

    def listFailing(self, cut, nEvents=5):
        nFailed = 0

        lines = []
        lines.append("Finding some events that fail {} cut for m = {} {}".format(cut, self.m, self.name))
        
        muons, muonsLabel = Handle("std::vector<pat::Muon>"), "slimmedMuons"
        vertices, vertexLabel = Handle("std::vector<reco::Vertex>"), "offlineSlimmedPrimaryVertices"
                                       
        for iEv, ev in enumerate(self.events):

            ev.getByLabel(vertexLabel, vertices)
            if len(vertices.product()) == 0:
                continue
            pv = vertices.product()[0]
            if pv.ndof() < 4:
                continue

            ev.getByLabel(muonsLabel, muons)

            for mu in muons.product():
                if self.classifier.firstFailedCut(mu, pv) == cut:
                    break
            else: # if we never hit a break, everything must have passed
                continue

            # we can only get here if there was a bad muon
            lines.append("    {}:{}:{}".format(ev.eventAuxiliary().run(),
                                               ev.eventAuxiliary().luminosityBlock(),
                                               ev.eventAuxiliary().event()))
            nFailed += 1
            if nFailed == nEvents:
                lines.append("Done!\n")
                return '\n'.join(lines)

    def process(self, maxEvents=-1, verbose=True):
        if verbose:
            print "Processing m = {} {}".format(self.m, self.name)
        
        muons, muonsLabel = Handle("std::vector<pat::Muon>"), "slimmedMuons"
        vertices, vertexLabel = Handle("std::vector<reco::Vertex>"), "offlineSlimmedPrimaryVertices"
                                       
        for iEv, ev in enumerate(self.events):
            if iEv == maxEvents:
                break

            if verbose and iEv % 5000 == 0:
                print "m={} Processing event {} {}".format(self.m, iEv, self.name)

            ev.getByLabel(vertexLabel, vertices)
            if len(vertices.product()) == 0:
                continue
            pv = vertices.product()[0]
            if pv.ndof() < 4:
                continue

            ev.getByLabel(muonsLabel, muons)
            
            leps = {}

            for mu in muons.product():
                lastCut = self.classifier.classify1(mu, pv)
                if lastCut:
                    leps[mu] = lastCut

            zs = MassPoint.getZPairs(*leps.keys())
            for z in zs:
                self.classifier.classify2(z[0], leps[z[0]], z[1], leps[z[1]])

        if verbose:
            print "m={} {} Done!".format(self.m, self.name)

        cutFlowStrs = ["Cut flow:"]
        nTot = self.classifier.cutFlow['genMatched']
        nZTot = self.classifier.zCutFlow['genMatched']
        nPrev = nTot
        nZPrev = nZTot
        for cut, n in self.classifier.cutFlow.iteritems():
            nZs = self.classifier.zCutFlow[cut]
            if cut == 'total':
                continue
            cutFlowStrs.append("    {}: {}% removed ({}% of Zs)".format(cut, 
                                                                        100. * (nPrev - n) / nTot,
                                                                        100. * (nZPrev - nZs) / nZTot))
            nPrev = n
            nZPrev = nZs
        cutFlowStrs.append('')

        return '\n'.join(cutFlowStrs)

    @staticmethod
    def zCompatibility(leps):
        if leps[0].pdgId() != -1 * leps[1].pdgId():
            return 999.

        return abs((leps[0].p4() + leps[1].p4()).mass() - Z_MASS)

    @staticmethod
    def getZPairs(*leps):
        out = []

        if len(leps) > 1:
            bestZ = min(combinations(leps, 2), key=MassPoint.zCompatibility)
            if bestZ[0].pdgId() != -1 * bestZ[1].pdgId():
                return []
            mZ = (bestZ[0].p4() + bestZ[1].p4()).mass()
            if mZ < 60. or mZ > 120.:
                return []
            out.append(bestZ)

            otherLeps = [lep for lep in leps if lep not in bestZ]
            out += MassPoint.getZPairs(otherLeps)

        return out

    def getResults(self):
        return self.classifier.getResults(self.m, self.color, self.marker)


def drawThings(outFile, *things, **opts):
    '''
    opts are passed to rootpy.utils.draw, except 'legOpts', which is passed
    to the Legend constructor
    '''
    c = Canvas(1000, 1000)

    legOpts = opts.pop('legOpts', {})

    if 'xtitle' in opts and 'Vs' in opts['xtitle']:
        titles = opts['xtitle'].split('Vs')
        opts['xtitle'] = titles[0]
        opts['ytitle'] = titles[1]

    if not any(isinstance(t, _Hist2D) for t in things):
        draw(things, c, **opts)
        leg = Legend(things, c, **legOpts)
        leg.Draw("SAME")
        # broken for some reason
        # style.setCMSStyle(c, "", True, "Preliminary Simulation", 13, 1000.)
        c.Print(outFile)
        c.Print(outFile.replace('.png', '.C'))
    else:
        for i, t in enumerate(things):
            can = Canvas(1000,1000)

            t.draw("colz")

            # fix temperature plot scale
            zScale = t.GetListOfFunctions().FindObject("palette")
            if zScale:
                can.SetRightMargin(0.105)
                can.Update()
                # print "scale location:", zScale.GetX1(), zScale.GetX2()
                # exit(1)
                # canvases[i].Update()
                zScale.SetX1NDC(.9)
                zScale.SetX2NDC(.925)
                can.Paint() # TODO: figure out why this gets rid of that stupid box
                

            can.Print(outFile.replace('.png', '{}.png'.format(t.GetTitle())))
            can.Print(outFile.replace('.png', '{}.C'.format(t.GetTitle())))
        
### Functions needed for threads
def newMassPoint(m, files, cuts, observables, observables2, binnings, color,
                 name=''):
    mp = MassPoint(m, files, color, name=name)
    for c, f in cuts.iteritems():
        mp.addCut(c, f)
    for obs, f in observables.iteritems():
        mp.addObservable1(obs, f, binnings[obs])
    for obs, f in observables2.iteritems():
        mp.addObservable2(obs, f, binnings[obs])

    return mp
    
def makeAndProcessMassPoint(m, files, whichID,
                            color, maxEvents, errorQueue):
    print "processing m = {} {}".format(m, whichID)
    try:
        if whichID == 'HighPt':
            cuts = getCutsHighPt()
        elif whichID == 'HighPtTracker':
            cuts = getCutsHighPtTracker()
        elif whichID == 'HighPtOr':
            cuts = getCutsHighPtOr()
        else:
            cuts = getCuts()
        observables = getObservables()
        observables2 = getObservables2()
        binnings = getBinning()
        mp = newMassPoint(m, files, cuts, observables, 
                          observables2, binnings, color,
                          name=whichID)
        resultText = mp.process(maxEvents)
        return mp.getResults(), resultText
    # exceptions won't print from threads without help
    except Exception as e:
        print "**********************************************************************"
        print "EXCEPTION"
        print "Caught exception:"
        print e
        print "Killing task"
        print "**********************************************************************"
        errorQueue.put(e)
        return mp.getResults(), "FAILED"

def listFailingFromMassPoint(failingCut, m, files, allCuts, observables, 
                             binnings, nEvents):
    mp = newMassPoint(m, files, allCuts, {}, {}, 'black')
    failText = mp.listFailing(failingCut, nEvents)

    return mp, failText

def printSomeThings(*args):
    for a in args:
        if isinstance(a, str):
            print a


def init_worker():
    '''
    Ignore interrupt signals.
    Tell worker processes to do this so that the parent process handles
    keyboard interrupts.
    '''
    signal.signal(signal.SIGINT, signal.SIG_IGN)



def main(args):
    files = getFiles()
    colors = getColors()
    cuts = getCuts()
    cutsHighPt = getCutsHighPt()
    cutsHighPtTracker = getCutsHighPt()
    cutsHighPtOr = getCutsHighPt()
    observables = getObservables()
    observables2 = getObservables2()
    binning = getBinning()

    masses = [1500, 2500, 125]

    pool = Pool(args.maxThreads, init_worker)
    results = {}
    resultsHighPt = {}
    resultsHighPtTracker = {}
    resultsHighPtOr = {}
    manager = Manager()
    errorQueue = manager.Queue()

    if args.printFailing:
        if args.printFailing in cuts:
            for mH in masses:
                results[mH] = pool.apply_async(listFailingFromMassPoint,
                                               args=(args.printFailing, mH, 
                                                     files[mH], cuts, 
                                                     observables, binning,
                                                     args.maxEvents),
                                               callback=printSomeThings)
        if args.highPtID and args.printFailing in cutsHighPt:
            for mH in masses:
                resultsHighPt[mH] = pool.apply_async(listFailingFromMassPoint,
                                                     args=(args.printFailing, mH, 
                                                           files[mH], cutsHighPt, 
                                                           observables, binning,
                                                           args.maxEvents),
                                                     callback=printSomeThings)
                resultsHighPtTracker[mH] = pool.apply_async(listFailingFromMassPoint,
                                                            args=(args.printFailing, mH, 
                                                                  files[mH], cutsHighPtTracker, 
                                                                  observables, binning,
                                                                  args.maxEvents),
                                                            callback=printSomeThings)
                resultsHighPtOr[mH] = pool.apply_async(listFailingFromMassPoint,
                                                       args=(args.printFailing, mH, 
                                                             files[mH], cutsHighPtOr, 
                                                             observables, binning,
                                                             args.maxEvents),
                                                       callback=printSomeThings)
    else:
        for mH in masses:
            results[mH] = pool.apply_async(makeAndProcessMassPoint,
                                           args=(mH, files[mH], 'Regular',
                                                 colors[mH], args.maxEvents, 
                                                 errorQueue),
                                           callback=printSomeThings)
            if args.highPtID:
                resultsHighPt[mH] = pool.apply_async(makeAndProcessMassPoint,
                                                     args=(mH, files[mH], 'HighPt',
                                                           colors[mH], args.maxEvents,
                                                           errorQueue),
                                                     callback=printSomeThings)
                resultsHighPtTracker[mH] = pool.apply_async(makeAndProcessMassPoint,
                                                            args=(mH, files[mH], 'HighPtTracker',
                                                                  colors[mH], args.maxEvents,
                                                                  errorQueue),
                                                            callback=printSomeThings)
                resultsHighPtOr[mH] = pool.apply_async(makeAndProcessMassPoint,
                                                       args=(mH, files[mH], 'HighPtOr',
                                                             colors[mH], args.maxEvents,
                                                             errorQueue),
                                                       callback=printSomeThings)

    try:
        while not all(result.ready() for result in (results.values()+resultsHighPt.values())):
            time.sleep(3)
            if not errorQueue.empty():
                e = errorQueue.get()
                raise e
    except KeyboardInterrupt:
        pool.terminate()
        pool.join()
        print "\n Killing..."
        exit(1)
    except Exception as e:
        pool.terminate()
        pool.join()
        print "\n Error! Killing everything!"
        raise
    else:
        pool.close()
        pool.join()

    if args.printFailing:
        return

    observations = {mH : res.get()[0] for mH, res in results.iteritems()}
    cutFlows = {mH : res.get()[1] for mH, res in results.iteritems()}
    observationsHighPt = {mH : res.get()[0] for mH, res in resultsHighPt.iteritems()}
    cutFlowsHighPt = {mH : res.get()[1] for mH, res in resultsHighPt.iteritems()}
    observationsHighPtTracker = {mH : res.get()[0] for mH, res in resultsHighPtTracker.iteritems()}
    cutFlowsHighPtTracker = {mH : res.get()[1] for mH, res in resultsHighPtTracker.iteritems()}
    observationsHighPtOr = {mH : res.get()[0] for mH, res in resultsHighPtOr.iteritems()}
    cutFlowsHighPtOr = {mH : res.get()[1] for mH, res in resultsHighPtOr.iteritems()}

    print "\nCut Flows:"
    for mH in sorted(cutFlows.keys()):
        print "m = {}:".format(mH)
        print cutFlows[mH]
    
    if args.highPtID:
        print ''
        print "High Pt ID:"
        for mH in sorted(cutFlowsHighPt.keys()):
            print "m = {}:".format(mH)
            print cutFlowsHighPt[mH]

        print ''
        print "Tracker High Pt ID:"
        for mH in sorted(cutFlowsHighPtTracker.keys()):
            print "m = {}:".format(mH)
            print cutFlowsHighPtTracker[mH]

        print ''
        print "OR of IDs:"
        for mH in sorted(cutFlowsHighPtOr.keys()):
            print "m = {}:".format(mH)
            print cutFlowsHighPtOr[mH]
        print ''
    


    effLegOpts = {
        'leftmargin' : 0.1,
        'rightmargin' : 0.45,
        'topmargin' : 0.5,
        }

    # make plots
    for cut in ['genMatched', 'PF']:
        if cut != 'genMatched':
            for obs in observables.keys() + observables2.keys():
                plots = [mp.makeEfficiency(cut, obs) for mp in observations.values()]
                drawThings(args.outdir+'eff{}_{}.png'.format(obs[0].upper()+obs[1:], cut), 
                           *plots, xtitle=obs, ytitle='efficiency',
                           legOpts=effLegOpts)
        for obs in observables.keys() + observables2.keys():
            plots = [mp.passingHist(cut, obs) for mp in observations.values()]
            drawThings(args.outdir+obs+'_after_{}_Cut.png'.format(cut), *plots,
                       xtitle=obs, ytitle='arb.')
    for obs in observables.keys() + observables2.keys():
        plots = [mp.failingHist('PF', obs) for mp in observations.values()]
        drawThings(args.outdir+obs+'_failing_PF_Cut.png', *plots,
                   xtitle=obs, ytitle='arb.')
    
    if args.highPtID:
        for cut in ['genMatched', 'muonChamberInFit', 'matchedStations']:
            if cut != 'genMatched':
                for obs in observables.keys() + observables2.keys():
                    plots = [mp.makeEfficiency(cut, obs) for mp in observationsHighPt.values()]
                    drawThings(args.outdir+'highPtID/eff{}_{}.png'.format(obs[0]+obs[1:], cut), 
                               *plots, xtitle=obs, ytitle='efficiency',
                               legOpts=effLegOpts)    
            for obs in observables.keys() + observables2.keys():
                plots = [mp.passingHist(cut, obs) for mp in observationsHighPt.values()]
                drawThings(args.outdir+'highPtID/'+obs+'_after_{}_Cut.png'.format(cut), *plots,
                           xtitle=obs, ytitle='arb.')
        for obs in observables.keys() + observables2.keys():
            plots = [mp.failingHist('global', obs) for mp in observationsHighPt.values()]
            drawThings(args.outdir+'highPtID/'+obs+'_failing_global_Cut.png', *plots,
                       xtitle=obs, ytitle='arb.')

        for cut in ['genMatched', 'tracker', 'matchedStations']:
            if cut != 'genMatched':
                for obs in observables.keys() + observables2.keys():
                    plots = [mp.makeEfficiency(cut, obs) for mp in observationsHighPtTracker.values()]
                    drawThings(args.outdir+'highPtIDTracker/eff{}_{}.png'.format(obs[0]+obs[1:], cut), 
                               *plots, xtitle=obs, ytitle='efficiency',
                               legOpts=effLegOpts)    
            for obs in observables.keys() + observables2.keys():
                plots = [mp.passingHist(cut, obs) for mp in observationsHighPtTracker.values()]
                drawThings(args.outdir+'highPtIDTracker/'+obs+'_after_{}_Cut.png'.format(cut), *plots,
                           xtitle=obs, ytitle='arb.')
        for obs in observables.keys() + observables2.keys():
            plots = [mp.failingHist('matchedStations', obs) for mp in observationsHighPtTracker.values()]
            drawThings(args.outdir+'highPtIDTracker/'+obs+'_failing_matchedStations_Cut.png', *plots,
                       xtitle=obs, ytitle='arb.')

        for cut in ['genMatched', 'globalOrTrackerOrPF']:
            if cut != 'genMatched':
                for obs in observables.keys() + observables2.keys():
                    plots = [mp.makeEfficiency(cut, obs) for mp in observationsHighPtOr.values()]
                    drawThings(args.outdir+'highPtIDOr/eff{}_{}.png'.format(obs[0]+obs[1:], cut), 
                               *plots, xtitle=obs, ytitle='efficiency',
                               legOpts=effLegOpts)    
            for obs in observables.keys() + observables2.keys():
                plots = [mp.passingHist(cut, obs) for mp in observationsHighPtOr.values()]
                drawThings(args.outdir+'highPtIDOr/'+obs+'_after_{}_Cut.png'.format(cut), *plots,
                           xtitle=obs, ytitle='arb.')
        for obs in observables.keys() + observables2.keys():
            plots = [mp.failingHist('globalOrTrackerOrPF', obs) for mp in observationsHighPtOr.values()]
            drawThings(args.outdir+'highPtIDOr/'+obs+'_failing_globalOrTrackerOrPF_Cut.png', *plots,
                       xtitle=obs, ytitle='arb.')


        for mp in observationsHighPt.keys():
            for obs in ['dR', 'zPt', 'pt', 'eta']:
                plots = []
                plots.append(observations[mp].makeEfficiency('PF', obs))
                plots[-1].SetTitle("Legacy")
                plots[-1].color = 'black'
                plots.append(observationsHighPt[mp].makeEfficiency('matchedStations', obs))
                plots[-1].SetTitle("High p_{T}")
                plots[-1].color = 'red'
                plots.append(observationsHighPtTracker[mp].makeEfficiency('matchedStations', obs))
                plots[-1].SetTitle("Tracker High p_{T}")
                plots[-1].color = 'blue'
                plots.append(observationsHighPtOr[mp].makeEfficiency('globalOrTrackerOrPF', obs))
                plots[-1].SetTitle("OR")
                plots[-1].color = 'forestgreen'
                
                compLegOpts = effLegOpts.copy()
                compLegOpts['textsize'] = .04
                compLegOpts['rightmargin'] = .37
                if obs == 'dR':
                    xTitle = '\\Delta R'
                elif obs == 'zPt':
                    xTitle = 'p_{T_{\\text{Z}}}'
                elif obs == 'pt':
                    xTitle = 'p_{T_{\\mu}}'
                elif obs == 'eta':
                    xTitle = '\\eta_{\\mu}'
                else:
                    xTitle = obs
                drawThings(args.outdir + "effComp_{}_{}.png".format(obs, mp), *plots,
                           xtitle=xTitle, ytitle='efficiency', legOpts=compLegOpts)
                


_files = {
    2500 : [
        'root://xrootd-cms.infn.it//store/mc/RunIIFall15MiniAODv2/GluGluHToZZTo4L_M2500_13TeV_powheg2_JHUgenV6_pythia8/MINIAODSIM/PU25nsData2015v1_76X_mcRun2_asymptotic_v12-v1/60000/0CBF39E6-F2E4-E511-A775-002590A370B2.root',
        'root://xrootd-cms.infn.it//store/mc/RunIIFall15MiniAODv2/GluGluHToZZTo4L_M2500_13TeV_powheg2_JHUgenV6_pythia8/MINIAODSIM/PU25nsData2015v1_76X_mcRun2_asymptotic_v12-v1/60000/16CD5DE6-F2E4-E511-9F1D-002590200978.root',
        'root://xrootd-cms.infn.it//store/mc/RunIIFall15MiniAODv2/GluGluHToZZTo4L_M2500_13TeV_powheg2_JHUgenV6_pythia8/MINIAODSIM/PU25nsData2015v1_76X_mcRun2_asymptotic_v12-v1/60000/186590E7-F2E4-E511-9665-002590200930.root',
        'root://xrootd-cms.infn.it//store/mc/RunIIFall15MiniAODv2/GluGluHToZZTo4L_M2500_13TeV_powheg2_JHUgenV6_pythia8/MINIAODSIM/PU25nsData2015v1_76X_mcRun2_asymptotic_v12-v1/60000/24CA0B1E-F3E4-E511-832B-AC162DA603B4.root',
        'root://xrootd-cms.infn.it//store/mc/RunIIFall15MiniAODv2/GluGluHToZZTo4L_M2500_13TeV_powheg2_JHUgenV6_pythia8/MINIAODSIM/PU25nsData2015v1_76X_mcRun2_asymptotic_v12-v1/60000/02C0EC1D-F3E4-E511-ADCA-AC162DA603B4.root',
        'root://xrootd-cms.infn.it//store/mc/RunIIFall15MiniAODv2/GluGluHToZZTo4L_M2500_13TeV_powheg2_JHUgenV6_pythia8/MINIAODSIM/PU25nsData2015v1_76X_mcRun2_asymptotic_v12-v1/60000/34B38BD2-F2E4-E511-989E-008CFAF0751E.root',
        'root://xrootd-cms.infn.it//store/mc/RunIIFall15MiniAODv2/GluGluHToZZTo4L_M2500_13TeV_powheg2_JHUgenV6_pythia8/MINIAODSIM/PU25nsData2015v1_76X_mcRun2_asymptotic_v12-v1/60000/3C2101E2-F2E4-E511-843D-001E67E68677.root',
        'root://xrootd-cms.infn.it//store/mc/RunIIFall15MiniAODv2/GluGluHToZZTo4L_M2500_13TeV_powheg2_JHUgenV6_pythia8/MINIAODSIM/PU25nsData2015v1_76X_mcRun2_asymptotic_v12-v1/60000/40DDA4CE-F2E4-E511-9D68-008CFA1113F8.root',
        'root://xrootd-cms.infn.it//store/mc/RunIIFall15MiniAODv2/GluGluHToZZTo4L_M2500_13TeV_powheg2_JHUgenV6_pythia8/MINIAODSIM/PU25nsData2015v1_76X_mcRun2_asymptotic_v12-v1/60000/505ED4E5-F2E4-E511-B831-002590200B78.root',
        'root://xrootd-cms.infn.it//store/mc/RunIIFall15MiniAODv2/GluGluHToZZTo4L_M2500_13TeV_powheg2_JHUgenV6_pythia8/MINIAODSIM/PU25nsData2015v1_76X_mcRun2_asymptotic_v12-v1/60000/52111A27-F3E4-E511-A600-001E67397238.root',
        'root://xrootd-cms.infn.it//store/mc/RunIIFall15MiniAODv2/GluGluHToZZTo4L_M2500_13TeV_powheg2_JHUgenV6_pythia8/MINIAODSIM/PU25nsData2015v1_76X_mcRun2_asymptotic_v12-v1/60000/529B7226-F3E4-E511-8CD4-AC162DA6E2F8.root',
        'root://xrootd-cms.infn.it//store/mc/RunIIFall15MiniAODv2/GluGluHToZZTo4L_M2500_13TeV_powheg2_JHUgenV6_pythia8/MINIAODSIM/PU25nsData2015v1_76X_mcRun2_asymptotic_v12-v1/60000/56478AFA-F2E4-E511-B746-001E67E71CC7.root',
        'root://xrootd-cms.infn.it//store/mc/RunIIFall15MiniAODv2/GluGluHToZZTo4L_M2500_13TeV_powheg2_JHUgenV6_pythia8/MINIAODSIM/PU25nsData2015v1_76X_mcRun2_asymptotic_v12-v1/60000/5889A4D8-F2E4-E511-89BB-00259073E512.root',
        'root://xrootd-cms.infn.it//store/mc/RunIIFall15MiniAODv2/GluGluHToZZTo4L_M2500_13TeV_powheg2_JHUgenV6_pythia8/MINIAODSIM/PU25nsData2015v1_76X_mcRun2_asymptotic_v12-v1/60000/60FEE3CB-F2E4-E511-B050-001E67D5D89A.root',
        'root://xrootd-cms.infn.it//store/mc/RunIIFall15MiniAODv2/GluGluHToZZTo4L_M2500_13TeV_powheg2_JHUgenV6_pythia8/MINIAODSIM/PU25nsData2015v1_76X_mcRun2_asymptotic_v12-v1/60000/689A6C26-F3E4-E511-802A-AC162DA6E2F8.root',
        'root://xrootd-cms.infn.it//store/mc/RunIIFall15MiniAODv2/GluGluHToZZTo4L_M2500_13TeV_powheg2_JHUgenV6_pythia8/MINIAODSIM/PU25nsData2015v1_76X_mcRun2_asymptotic_v12-v1/60000/700DF9EC-F2E4-E511-9273-34E6D7BDDEDB.root',
        'root://xrootd-cms.infn.it//store/mc/RunIIFall15MiniAODv2/GluGluHToZZTo4L_M2500_13TeV_powheg2_JHUgenV6_pythia8/MINIAODSIM/PU25nsData2015v1_76X_mcRun2_asymptotic_v12-v1/60000/7E5132F3-F2E4-E511-BB05-0025905C6448.root',
        'root://xrootd-cms.infn.it//store/mc/RunIIFall15MiniAODv2/GluGluHToZZTo4L_M2500_13TeV_powheg2_JHUgenV6_pythia8/MINIAODSIM/PU25nsData2015v1_76X_mcRun2_asymptotic_v12-v1/60000/96275FCE-F2E4-E511-86A9-001E67A3EA7A.root',
        'root://xrootd-cms.infn.it//store/mc/RunIIFall15MiniAODv2/GluGluHToZZTo4L_M2500_13TeV_powheg2_JHUgenV6_pythia8/MINIAODSIM/PU25nsData2015v1_76X_mcRun2_asymptotic_v12-v1/60000/98B4911B-F3E4-E511-A16F-002590A370DC.root',
        'root://xrootd-cms.infn.it//store/mc/RunIIFall15MiniAODv2/GluGluHToZZTo4L_M2500_13TeV_powheg2_JHUgenV6_pythia8/MINIAODSIM/PU25nsData2015v1_76X_mcRun2_asymptotic_v12-v1/60000/A82948DB-F2E4-E511-B6AA-02163E01457F.root',
        'root://xrootd-cms.infn.it//store/mc/RunIIFall15MiniAODv2/GluGluHToZZTo4L_M2500_13TeV_powheg2_JHUgenV6_pythia8/MINIAODSIM/PU25nsData2015v1_76X_mcRun2_asymptotic_v12-v1/60000/AAC010D9-F2E4-E511-BEA8-02163E01784B.root',
        'root://xrootd-cms.infn.it//store/mc/RunIIFall15MiniAODv2/GluGluHToZZTo4L_M2500_13TeV_powheg2_JHUgenV6_pythia8/MINIAODSIM/PU25nsData2015v1_76X_mcRun2_asymptotic_v12-v1/60000/AAC0EA3B-24E5-E511-9B88-F04DA23BCE4C.root',
        'root://xrootd-cms.infn.it//store/mc/RunIIFall15MiniAODv2/GluGluHToZZTo4L_M2500_13TeV_powheg2_JHUgenV6_pythia8/MINIAODSIM/PU25nsData2015v1_76X_mcRun2_asymptotic_v12-v1/60000/B442EBE5-F2E4-E511-8FAC-001E67398CE1.root',
        'root://xrootd-cms.infn.it//store/mc/RunIIFall15MiniAODv2/GluGluHToZZTo4L_M2500_13TeV_powheg2_JHUgenV6_pythia8/MINIAODSIM/PU25nsData2015v1_76X_mcRun2_asymptotic_v12-v1/60000/BC2F6FCC-F2E4-E511-8247-002590AC5068.root',
        'root://xrootd-cms.infn.it//store/mc/RunIIFall15MiniAODv2/GluGluHToZZTo4L_M2500_13TeV_powheg2_JHUgenV6_pythia8/MINIAODSIM/PU25nsData2015v1_76X_mcRun2_asymptotic_v12-v1/60000/C42422C7-F2E4-E511-8C6A-00266CF97FF4.root',
        'root://xrootd-cms.infn.it//store/mc/RunIIFall15MiniAODv2/GluGluHToZZTo4L_M2500_13TeV_powheg2_JHUgenV6_pythia8/MINIAODSIM/PU25nsData2015v1_76X_mcRun2_asymptotic_v12-v1/60000/CE64C3DB-F2E4-E511-B434-008CFA0A5A10.root',
        'root://xrootd-cms.infn.it//store/mc/RunIIFall15MiniAODv2/GluGluHToZZTo4L_M2500_13TeV_powheg2_JHUgenV6_pythia8/MINIAODSIM/PU25nsData2015v1_76X_mcRun2_asymptotic_v12-v1/60000/D0200FE1-F2E4-E511-8F13-1CC1DE046F78.root',
        'root://xrootd-cms.infn.it//store/mc/RunIIFall15MiniAODv2/GluGluHToZZTo4L_M2500_13TeV_powheg2_JHUgenV6_pythia8/MINIAODSIM/PU25nsData2015v1_76X_mcRun2_asymptotic_v12-v1/60000/D27C82D3-F2E4-E511-9410-0CC47A4DED04.root',
        'root://xrootd-cms.infn.it//store/mc/RunIIFall15MiniAODv2/GluGluHToZZTo4L_M2500_13TeV_powheg2_JHUgenV6_pythia8/MINIAODSIM/PU25nsData2015v1_76X_mcRun2_asymptotic_v12-v1/60000/EE1E4ADF-F2E4-E511-8226-78E7D1E4B874.root',
        'root://xrootd-cms.infn.it//store/mc/RunIIFall15MiniAODv2/GluGluHToZZTo4L_M2500_13TeV_powheg2_JHUgenV6_pythia8/MINIAODSIM/PU25nsData2015v1_76X_mcRun2_asymptotic_v12-v1/60000/F2F63FDB-F2E4-E511-AF81-002590A4C6BE.root',
        'root://xrootd-cms.infn.it//store/mc/RunIIFall15MiniAODv2/GluGluHToZZTo4L_M2500_13TeV_powheg2_JHUgenV6_pythia8/MINIAODSIM/PU25nsData2015v1_76X_mcRun2_asymptotic_v12-v1/60000/FAA336DF-F2E4-E511-B52A-20CF3027A5B6.root',
        ],
    125 : [
        'root://xrootd-cms.infn.it//store/mc/RunIIFall15MiniAODv2/GluGluHToZZTo4L_M125_13TeV_powheg2_JHUgenV6_pythia8/MINIAODSIM/PU25nsData2015v1_76X_mcRun2_asymptotic_v12-v1/50000/024F30C4-96B9-E511-91A0-24BE05C616C1.root', 
        'root://xrootd-cms.infn.it//store/mc/RunIIFall15MiniAODv2/GluGluHToZZTo4L_M125_13TeV_powheg2_JHUgenV6_pythia8/MINIAODSIM/PU25nsData2015v1_76X_mcRun2_asymptotic_v12-v1/50000/06A78A71-97B9-E511-A22A-24BE05C3CBD1.root', 
        'root://xrootd-cms.infn.it//store/mc/RunIIFall15MiniAODv2/GluGluHToZZTo4L_M125_13TeV_powheg2_JHUgenV6_pythia8/MINIAODSIM/PU25nsData2015v1_76X_mcRun2_asymptotic_v12-v1/50000/0AFC3AB4-96B9-E511-AE01-5065F3817221.root', 
        'root://xrootd-cms.infn.it//store/mc/RunIIFall15MiniAODv2/GluGluHToZZTo4L_M125_13TeV_powheg2_JHUgenV6_pythia8/MINIAODSIM/PU25nsData2015v1_76X_mcRun2_asymptotic_v12-v1/50000/1004E816-97B9-E511-82D3-A0000420FE80.root', 
        'root://xrootd-cms.infn.it//store/mc/RunIIFall15MiniAODv2/GluGluHToZZTo4L_M125_13TeV_powheg2_JHUgenV6_pythia8/MINIAODSIM/PU25nsData2015v1_76X_mcRun2_asymptotic_v12-v1/50000/10FB2F05-97B9-E511-A3EA-24BE05C616E1.root', 
        'root://xrootd-cms.infn.it//store/mc/RunIIFall15MiniAODv2/GluGluHToZZTo4L_M125_13TeV_powheg2_JHUgenV6_pythia8/MINIAODSIM/PU25nsData2015v1_76X_mcRun2_asymptotic_v12-v1/50000/14D5233D-97B9-E511-9C2F-A0000420FE80.root', 
        'root://xrootd-cms.infn.it//store/mc/RunIIFall15MiniAODv2/GluGluHToZZTo4L_M125_13TeV_powheg2_JHUgenV6_pythia8/MINIAODSIM/PU25nsData2015v1_76X_mcRun2_asymptotic_v12-v1/50000/24985C45-97B9-E511-8AAB-0002C92A1020.root', 
        'root://xrootd-cms.infn.it//store/mc/RunIIFall15MiniAODv2/GluGluHToZZTo4L_M125_13TeV_powheg2_JHUgenV6_pythia8/MINIAODSIM/PU25nsData2015v1_76X_mcRun2_asymptotic_v12-v1/50000/3299BDB2-96B9-E511-96B6-A0369F310120.root', 
        'root://xrootd-cms.infn.it//store/mc/RunIIFall15MiniAODv2/GluGluHToZZTo4L_M125_13TeV_powheg2_JHUgenV6_pythia8/MINIAODSIM/PU25nsData2015v1_76X_mcRun2_asymptotic_v12-v1/50000/3877AF13-97B9-E511-8282-A0000420FE80.root', 
        'root://xrootd-cms.infn.it//store/mc/RunIIFall15MiniAODv2/GluGluHToZZTo4L_M125_13TeV_powheg2_JHUgenV6_pythia8/MINIAODSIM/PU25nsData2015v1_76X_mcRun2_asymptotic_v12-v1/50000/3AB48FFE-96B9-E511-99E5-24BE05CEFB31.root', 
        'root://xrootd-cms.infn.it//store/mc/RunIIFall15MiniAODv2/GluGluHToZZTo4L_M125_13TeV_powheg2_JHUgenV6_pythia8/MINIAODSIM/PU25nsData2015v1_76X_mcRun2_asymptotic_v12-v1/50000/40B8A9E4-96B9-E511-B4BD-A0000420FE80.root', 
        'root://xrootd-cms.infn.it//store/mc/RunIIFall15MiniAODv2/GluGluHToZZTo4L_M125_13TeV_powheg2_JHUgenV6_pythia8/MINIAODSIM/PU25nsData2015v1_76X_mcRun2_asymptotic_v12-v1/50000/58C2F2E1-97B9-E511-A150-A0000420FE80.root', 
        'root://xrootd-cms.infn.it//store/mc/RunIIFall15MiniAODv2/GluGluHToZZTo4L_M125_13TeV_powheg2_JHUgenV6_pythia8/MINIAODSIM/PU25nsData2015v1_76X_mcRun2_asymptotic_v12-v1/50000/5CDC700A-97B9-E511-8C0F-A0000420FE80.root', 
        'root://xrootd-cms.infn.it//store/mc/RunIIFall15MiniAODv2/GluGluHToZZTo4L_M125_13TeV_powheg2_JHUgenV6_pythia8/MINIAODSIM/PU25nsData2015v1_76X_mcRun2_asymptotic_v12-v1/50000/769C5B1D-97B9-E511-8507-A0000420FE80.root', 
        'root://xrootd-cms.infn.it//store/mc/RunIIFall15MiniAODv2/GluGluHToZZTo4L_M125_13TeV_powheg2_JHUgenV6_pythia8/MINIAODSIM/PU25nsData2015v1_76X_mcRun2_asymptotic_v12-v1/50000/7E90C511-97B9-E511-9D7D-A0000420FE80.root', 
        'root://xrootd-cms.infn.it//store/mc/RunIIFall15MiniAODv2/GluGluHToZZTo4L_M125_13TeV_powheg2_JHUgenV6_pythia8/MINIAODSIM/PU25nsData2015v1_76X_mcRun2_asymptotic_v12-v1/50000/86BCF2E1-97B9-E511-95D1-A0000420FE80.root', 
        'root://xrootd-cms.infn.it//store/mc/RunIIFall15MiniAODv2/GluGluHToZZTo4L_M125_13TeV_powheg2_JHUgenV6_pythia8/MINIAODSIM/PU25nsData2015v1_76X_mcRun2_asymptotic_v12-v1/50000/9E75AF13-97B9-E511-9EA0-A0000420FE80.root', 
        'root://xrootd-cms.infn.it//store/mc/RunIIFall15MiniAODv2/GluGluHToZZTo4L_M125_13TeV_powheg2_JHUgenV6_pythia8/MINIAODSIM/PU25nsData2015v1_76X_mcRun2_asymptotic_v12-v1/50000/A0C0F2E1-97B9-E511-B0AD-A0000420FE80.root', 
        'root://xrootd-cms.infn.it//store/mc/RunIIFall15MiniAODv2/GluGluHToZZTo4L_M125_13TeV_powheg2_JHUgenV6_pythia8/MINIAODSIM/PU25nsData2015v1_76X_mcRun2_asymptotic_v12-v1/50000/AC94C511-97B9-E511-BEA1-A0000420FE80.root', 
        'root://xrootd-cms.infn.it//store/mc/RunIIFall15MiniAODv2/GluGluHToZZTo4L_M125_13TeV_powheg2_JHUgenV6_pythia8/MINIAODSIM/PU25nsData2015v1_76X_mcRun2_asymptotic_v12-v1/50000/C6DB5FDF-96B9-E511-AA87-24BE05C6D711.root', 
        'root://xrootd-cms.infn.it//store/mc/RunIIFall15MiniAODv2/GluGluHToZZTo4L_M125_13TeV_powheg2_JHUgenV6_pythia8/MINIAODSIM/PU25nsData2015v1_76X_mcRun2_asymptotic_v12-v1/50000/D6A05B1D-97B9-E511-8F27-A0000420FE80.root', 
        'root://xrootd-cms.infn.it//store/mc/RunIIFall15MiniAODv2/GluGluHToZZTo4L_M125_13TeV_powheg2_JHUgenV6_pythia8/MINIAODSIM/PU25nsData2015v1_76X_mcRun2_asymptotic_v12-v1/50000/D8BC223D-97B9-E511-84DE-A0000420FE80.root', 
        'root://xrootd-cms.infn.it//store/mc/RunIIFall15MiniAODv2/GluGluHToZZTo4L_M125_13TeV_powheg2_JHUgenV6_pythia8/MINIAODSIM/PU25nsData2015v1_76X_mcRun2_asymptotic_v12-v1/50000/E0BCF2E1-97B9-E511-AE54-A0000420FE80.root', 
        'root://xrootd-cms.infn.it//store/mc/RunIIFall15MiniAODv2/GluGluHToZZTo4L_M125_13TeV_powheg2_JHUgenV6_pythia8/MINIAODSIM/PU25nsData2015v1_76X_mcRun2_asymptotic_v12-v1/50000/F2BEF2E1-97B9-E511-818C-A0000420FE80.root', 
        'root://xrootd-cms.infn.it//store/mc/RunIIFall15MiniAODv2/GluGluHToZZTo4L_M125_13TeV_powheg2_JHUgenV6_pythia8/MINIAODSIM/PU25nsData2015v1_76X_mcRun2_asymptotic_v12-v1/50000/F4A0223D-97B9-E511-A4AC-A0000420FE80.root', 
        ],
    1500 : [
        'root://xrootd-cms.infn.it//store/mc/RunIIFall15MiniAODv2/GluGluHToZZTo4L_M1500_13TeV_powheg2_JHUgenV6_pythia8/MINIAODSIM/PU25nsData2015v1_76X_mcRun2_asymptotic_v12-v1/40000/0CB24220-65E2-E511-ADED-901B0E5427BA.root', 
        'root://xrootd-cms.infn.it//store/mc/RunIIFall15MiniAODv2/GluGluHToZZTo4L_M1500_13TeV_powheg2_JHUgenV6_pythia8/MINIAODSIM/PU25nsData2015v1_76X_mcRun2_asymptotic_v12-v1/40000/248955CE-64E2-E511-A250-44A84224053C.root', 
        'root://xrootd-cms.infn.it//store/mc/RunIIFall15MiniAODv2/GluGluHToZZTo4L_M1500_13TeV_powheg2_JHUgenV6_pythia8/MINIAODSIM/PU25nsData2015v1_76X_mcRun2_asymptotic_v12-v1/40000/28A479C2-64E2-E511-A2E8-008CFA197AF4.root', 
        'root://xrootd-cms.infn.it//store/mc/RunIIFall15MiniAODv2/GluGluHToZZTo4L_M1500_13TeV_powheg2_JHUgenV6_pythia8/MINIAODSIM/PU25nsData2015v1_76X_mcRun2_asymptotic_v12-v1/40000/28CC37C3-64E2-E511-96FF-008CFA5D2758.root', 
        'root://xrootd-cms.infn.it//store/mc/RunIIFall15MiniAODv2/GluGluHToZZTo4L_M1500_13TeV_powheg2_JHUgenV6_pythia8/MINIAODSIM/PU25nsData2015v1_76X_mcRun2_asymptotic_v12-v1/40000/2ACB754C-65E2-E511-85BA-44A84225C851.root', 
        'root://xrootd-cms.infn.it//store/mc/RunIIFall15MiniAODv2/GluGluHToZZTo4L_M1500_13TeV_powheg2_JHUgenV6_pythia8/MINIAODSIM/PU25nsData2015v1_76X_mcRun2_asymptotic_v12-v1/40000/347581AF-65E2-E511-A507-00259021A2AA.root', 
        'root://xrootd-cms.infn.it//store/mc/RunIIFall15MiniAODv2/GluGluHToZZTo4L_M1500_13TeV_powheg2_JHUgenV6_pythia8/MINIAODSIM/PU25nsData2015v1_76X_mcRun2_asymptotic_v12-v1/40000/36F99AC0-64E2-E511-ACC6-A0369F301924.root', 
        'root://xrootd-cms.infn.it//store/mc/RunIIFall15MiniAODv2/GluGluHToZZTo4L_M1500_13TeV_powheg2_JHUgenV6_pythia8/MINIAODSIM/PU25nsData2015v1_76X_mcRun2_asymptotic_v12-v1/40000/40A14AB9-64E2-E511-979F-0CC47A4C8ECE.root', 
        'root://xrootd-cms.infn.it//store/mc/RunIIFall15MiniAODv2/GluGluHToZZTo4L_M1500_13TeV_powheg2_JHUgenV6_pythia8/MINIAODSIM/PU25nsData2015v1_76X_mcRun2_asymptotic_v12-v1/40000/42CAC4C3-64E2-E511-A69D-0025907B500C.root', 
        'root://xrootd-cms.infn.it//store/mc/RunIIFall15MiniAODv2/GluGluHToZZTo4L_M1500_13TeV_powheg2_JHUgenV6_pythia8/MINIAODSIM/PU25nsData2015v1_76X_mcRun2_asymptotic_v12-v1/40000/461D71D4-64E2-E511-AEA5-008CFA1113FC.root', 
        'root://xrootd-cms.infn.it//store/mc/RunIIFall15MiniAODv2/GluGluHToZZTo4L_M1500_13TeV_powheg2_JHUgenV6_pythia8/MINIAODSIM/PU25nsData2015v1_76X_mcRun2_asymptotic_v12-v1/40000/4C343943-66E2-E511-864C-44A84224053C.root', 
        'root://xrootd-cms.infn.it//store/mc/RunIIFall15MiniAODv2/GluGluHToZZTo4L_M1500_13TeV_powheg2_JHUgenV6_pythia8/MINIAODSIM/PU25nsData2015v1_76X_mcRun2_asymptotic_v12-v1/40000/502427C2-64E2-E511-8DA7-008CFA197A04.root', 
        'root://xrootd-cms.infn.it//store/mc/RunIIFall15MiniAODv2/GluGluHToZZTo4L_M1500_13TeV_powheg2_JHUgenV6_pythia8/MINIAODSIM/PU25nsData2015v1_76X_mcRun2_asymptotic_v12-v1/40000/6281D328-65E2-E511-875E-008CFA1113E8.root', 
        'root://xrootd-cms.infn.it//store/mc/RunIIFall15MiniAODv2/GluGluHToZZTo4L_M1500_13TeV_powheg2_JHUgenV6_pythia8/MINIAODSIM/PU25nsData2015v1_76X_mcRun2_asymptotic_v12-v1/40000/721A2CB4-64E2-E511-89F6-0025905A609A.root', 
        'root://xrootd-cms.infn.it//store/mc/RunIIFall15MiniAODv2/GluGluHToZZTo4L_M1500_13TeV_powheg2_JHUgenV6_pythia8/MINIAODSIM/PU25nsData2015v1_76X_mcRun2_asymptotic_v12-v1/40000/766228AD-64E2-E511-920A-002590D0B00C.root', 
        'root://xrootd-cms.infn.it//store/mc/RunIIFall15MiniAODv2/GluGluHToZZTo4L_M1500_13TeV_powheg2_JHUgenV6_pythia8/MINIAODSIM/PU25nsData2015v1_76X_mcRun2_asymptotic_v12-v1/40000/8A4E97CA-64E2-E511-941E-002590D0B02E.root', 
        'root://xrootd-cms.infn.it//store/mc/RunIIFall15MiniAODv2/GluGluHToZZTo4L_M1500_13TeV_powheg2_JHUgenV6_pythia8/MINIAODSIM/PU25nsData2015v1_76X_mcRun2_asymptotic_v12-v1/40000/920649CC-64E2-E511-BFBE-20CF305B04CC.root', 
        'root://xrootd-cms.infn.it//store/mc/RunIIFall15MiniAODv2/GluGluHToZZTo4L_M1500_13TeV_powheg2_JHUgenV6_pythia8/MINIAODSIM/PU25nsData2015v1_76X_mcRun2_asymptotic_v12-v1/40000/9213AFC2-64E2-E511-9C53-001E67A42A71.root', 
        'root://xrootd-cms.infn.it//store/mc/RunIIFall15MiniAODv2/GluGluHToZZTo4L_M1500_13TeV_powheg2_JHUgenV6_pythia8/MINIAODSIM/PU25nsData2015v1_76X_mcRun2_asymptotic_v12-v1/40000/94C91ECD-64E2-E511-A251-003048F5B300.root', 
        'root://xrootd-cms.infn.it//store/mc/RunIIFall15MiniAODv2/GluGluHToZZTo4L_M1500_13TeV_powheg2_JHUgenV6_pythia8/MINIAODSIM/PU25nsData2015v1_76X_mcRun2_asymptotic_v12-v1/40000/9A8487B7-64E2-E511-9B1E-0CC47A4D9A40.root', 
        'root://xrootd-cms.infn.it//store/mc/RunIIFall15MiniAODv2/GluGluHToZZTo4L_M1500_13TeV_powheg2_JHUgenV6_pythia8/MINIAODSIM/PU25nsData2015v1_76X_mcRun2_asymptotic_v12-v1/40000/A41C14B6-64E2-E511-B71B-0CC47A4D75F6.root', 
        'root://xrootd-cms.infn.it//store/mc/RunIIFall15MiniAODv2/GluGluHToZZTo4L_M1500_13TeV_powheg2_JHUgenV6_pythia8/MINIAODSIM/PU25nsData2015v1_76X_mcRun2_asymptotic_v12-v1/40000/A480DDBA-64E2-E511-8996-002590D0AFB4.root', 
        'root://xrootd-cms.infn.it//store/mc/RunIIFall15MiniAODv2/GluGluHToZZTo4L_M1500_13TeV_powheg2_JHUgenV6_pythia8/MINIAODSIM/PU25nsData2015v1_76X_mcRun2_asymptotic_v12-v1/40000/AEA860C4-64E2-E511-8AEF-20CF3027A61B.root', 
        'root://xrootd-cms.infn.it//store/mc/RunIIFall15MiniAODv2/GluGluHToZZTo4L_M1500_13TeV_powheg2_JHUgenV6_pythia8/MINIAODSIM/PU25nsData2015v1_76X_mcRun2_asymptotic_v12-v1/40000/AEBD52B8-64E2-E511-B236-00259073E4F0.root', 
        'root://xrootd-cms.infn.it//store/mc/RunIIFall15MiniAODv2/GluGluHToZZTo4L_M1500_13TeV_powheg2_JHUgenV6_pythia8/MINIAODSIM/PU25nsData2015v1_76X_mcRun2_asymptotic_v12-v1/40000/BE192DB3-64E2-E511-92F5-20CF3027A635.root', 
        'root://xrootd-cms.infn.it//store/mc/RunIIFall15MiniAODv2/GluGluHToZZTo4L_M1500_13TeV_powheg2_JHUgenV6_pythia8/MINIAODSIM/PU25nsData2015v1_76X_mcRun2_asymptotic_v12-v1/40000/CA662206-87E2-E511-B645-001E67504B25.root', 
        'root://xrootd-cms.infn.it//store/mc/RunIIFall15MiniAODv2/GluGluHToZZTo4L_M1500_13TeV_powheg2_JHUgenV6_pythia8/MINIAODSIM/PU25nsData2015v1_76X_mcRun2_asymptotic_v12-v1/40000/D005442A-65E2-E511-A7C3-008CFA111354.root', 
        ],
    }
def getFiles():
    return _files

_colors = {
    125  : 'red',
    1500 : 'forestgreen',
    2500 : 'blue',
    }
def getColors():
    return _colors

_cuts = OrderedDict()
_cuts['globalOrTracker'] = lambda mu, vtx: mu.isGlobalMuon() or (mu.isTrackerMuon() and mu.numberOfMatchedStations() > 0)
_cuts['pt']              = lambda mu, vtx: mu.pt() > 5.
_cuts['eta']             = lambda mu, vtx: abs(mu.eta()) < 2.4
_cuts['notStandalone']   = lambda mu, vtx: mu.muonBestTrackType() != 2
_cuts['PVDXY']           = lambda mu, vtx: abs(mu.muonBestTrack().dxy(vtx.position())) < 0.5
_cuts['PVDZ']            = lambda mu, vtx: abs(mu.muonBestTrack().dz(vtx.position())) < 1.
_cuts['PF']              = lambda mu, vtx: mu.isPFMuon()
def getCuts():
    return _cuts

_cutsHighPt = OrderedDict()
_cutsHighPt['dxy'] = lambda mu, vtx: abs(mu.muonBestTrack().dxy(vtx.position())) < 0.2
_cutsHighPt['dz'] = lambda mu, vtx: abs(mu.muonBestTrack().dz(vtx.position())) < 0.5
_cutsHighPt['ptRelError'] = lambda mu, vtx: mu.muonBestTrack().ptError()/mu.muonBestTrack().pt() < 0.3
_cutsHighPt['global'] = lambda mu, vtx: mu.isGlobalMuon()
_cutsHighPt['muonChamberInFit'] = lambda mu, vtx: mu.globalTrack().hitPattern().numberOfValidMuonHits() > 0
_cutsHighPt['pixelHits'] = lambda mu, vtx: mu.innerTrack().hitPattern().numberOfValidPixelHits() > 0
_cutsHighPt['trackerHits'] = lambda mu, vtx: mu.innerTrack().hitPattern().trackerLayersWithMeasurement() > 5
_cutsHighPt['matchedStations'] = lambda mu, vtx: mu.numberOfMatchedStations() > 1
def getCutsHighPt():
    return _cutsHighPt

_cutsHighPtTracker = OrderedDict()
_cutsHighPtTracker['dxy'] = lambda mu, vtx: abs(mu.muonBestTrack().dxy(vtx.position())) < 0.2
_cutsHighPtTracker['dz'] = lambda mu, vtx: abs(mu.muonBestTrack().dz(vtx.position())) < 0.5
_cutsHighPtTracker['ptRelError'] = lambda mu, vtx: mu.muonBestTrack().ptError()/mu.muonBestTrack().pt() < 0.3
_cutsHighPtTracker['tracker'] = lambda mu, vtx: mu.isTrackerMuon()
_cutsHighPtTracker['pixelHits'] = lambda mu, vtx: mu.innerTrack().hitPattern().numberOfValidPixelHits() > 0
_cutsHighPtTracker['trackerHits'] = lambda mu, vtx: mu.innerTrack().hitPattern().trackerLayersWithMeasurement() > 5
_cutsHighPtTracker['matchedStations'] = lambda mu, vtx: mu.numberOfMatchedStations() > 1
def getCutsHighPtTracker():
    return _cutsHighPtTracker

_cutsHighPtOr = OrderedDict()
_cutsHighPtOr['eta'] = lambda mu, vtx: abs(mu.eta()) < 2.4
_cutsHighPtOr['dxy'] = lambda mu, vtx: abs(mu.muonBestTrack().dxy(vtx.position())) < 0.2
_cutsHighPtOr['dz'] = lambda mu, vtx: abs(mu.muonBestTrack().dz(vtx.position())) < 0.5
_cutsHighPtOr['globalOrTrackerOrPF'] = lambda mu, vtx: ((mu.isTrackerMuon() or (mu.isGlobalMuon() and mu.globalTrack().hitPattern().numberOfValidMuonHits() > 0)) and (mu.numberOfMatchedStations() > 1 and mu.muonBestTrack().ptError()/mu.muonBestTrack().pt() < 0.3 and mu.innerTrack().hitPattern().numberOfValidPixelHits > 0 and mu.innerTrack().hitPattern().trackerLayersWithMeasurement() > 5)) or (mu.isPFMuon() and mu.muonBestTrackType() != 2 and ((mu.isTrackerMuon() and mu.numberOfMatchedStations() > 0) or mu.isGlobalMuon()))
def getCutsHighPtOr():
    return _cutsHighPtOr

def nPixelHits(mu, vtx):
    if mu.innerTrack().isNull():
        return -1
    return mu.innerTrack().hitPattern().numberOfValidPixelHits()

def trackerLayersWithHit(mu, vtx):
    if mu.innerTrack().isNull():
        return -1
    return mu.innerTrack().hitPattern().trackerLayersWithMeasurement()

_observables = {
    #'nHits' : lambda mu, vtx: mu.numberOfValidHits(),
    'normChi2' : lambda mu, vtx: mu.muonBestTrack().normalizedChi2(),
    #'trackKink' : lambda mu, vtx: mu.combinedQuality().trkKink,
    'trackMatch' : lambda mu, vtx: mu.combinedQuality().chi2LocalPosition,
    'segmentCompatibility' : lambda mu, vtx: mu.segmentCompatibility(),
    'nMuonHits' : lambda mu, vtx: mu.muonBestTrack().hitPattern().numberOfValidMuonHits(),
    'nMatchedStations' : lambda mu, vtx: mu.numberOfMatchedStations(),
    'nPixelHits' : nPixelHits,
    'trackerLayersWithHit' : trackerLayersWithHit,
    'pt': lambda lep, vtx: lep.pt(), 
    'eta': lambda lep, vtx: abs(lep.eta()), 
    }
def getObservables():
    return _observables

_observables2 = {
    'dR' : lambda lep1, lep2, dR: dR,
    'zMass' : lambda lep1, lep2, dR: (lep1.p4()+lep2.p4()).mass(),
    'zPt' : lambda lep1, lep2, dR: (lep1.p4()+lep2.p4()).pt(),
    'ptVsDR' : lambda lep1, lep2, dR: (lep1.pt(), dR),
    'zPtVsDR' : lambda lep1, lep2, dR: ((lep1.p4()+lep2.p4()).pt(), dR),
    'segmentCompatibilityVsDR' : lambda lep1, lep2, dR: (lep1.segmentCompatibility(), dR),
    'normChi2VsDR' : lambda lep1, lep2, dR: (lep1.muonBestTrack().normalizedChi2(), dR),
    }
def getObservables2():
    return _observables2

_binning = {
    'nHits' : [12, 5, 17],
    'normChi2' : [16, 0., 8.],
    'trackKink' : [40, 0., 40.],
    'trackMatch' : [20, 0., 20.],
    'segmentCompatibility' : [20, 0., 1.],
    'nMuonHits' : [50,0,50],
    'nMatchedStations' : [9,0,9],
    'nPixelHits' : [7,0,7],
    'trackerLayersWithHit' : [11,0,11],
    'pt' : [[i*40. for i in xrange(20)] + [800.+i*80 for i in xrange(5)] + [1200.+i*160. for i in xrange(6)]], #[50, 0., 2000.],
    'eta' : [24, 0., 2.4],
    'dR' : [20, 0., 2.],
    'zMass' : [60, 60., 120.],
    'zPt' : [45, 0., 1800],
    'ptVsDR' : [[i*40. for i in xrange(20)] + [800.+i*80 for i in xrange(5)] + [1200.+i*160. for i in xrange(6)], 20, 0., 2.],
    'zPtVsDR' : [45, 0., 1800., 20, 0., 2.],
    'segmentCompatibilityVsDR' : [20, 0., 1., 20, 0., 2.],
    'normChi2VsDR' : [16, 0., 8., 20, 0., 2.],
    }
def getBinning():
    return _binning


if __name__ == "__main__":
    from argparse import ArgumentParser
    parser = ArgumentParser(description='Muon efficiency at various Higgs masses.')
    parser.add_argument('--outdir', nargs='?', type=str, 
                        default='/afs/cern.ch/user/n/nawoods/www/highMassEfficiency/',
                        help='Output plot location')
    parser.add_argument('--maxEvents', nargs='?', type=int, default=-1,
                        help='Max number of events to run (or -1 for infinite)')
    parser.add_argument('--printFailing', nargs='?', type=str, default='',
                        help='Instead of making plots, print a few events which fail this cut')
    parser.add_argument('--maxThreads', nargs='?', type=int, default=6,
                        help='Maximum number of threads to use at one time')
    parser.add_argument('--email', action='store_true', 
                        help='Send email when finished')
    parser.add_argument('--highPtID', action='store_true',
                        help='Also analyzer the POG high pt ID')
    args = parser.parse_args()


    if args.email:
        from os import system
        from socket import gethostname

        def sendMail(subject, message):
            mailInfo = [
                'To: nwoods@hep.wisc.edu',
                'From: {}.noreply@mail.cern.ch'.format(gethostname()),
                'Subject: {}'.format(subject),
                message,
                ]

            system('echo "{}" | /usr/lib/sendmail -t'.format('\n'.join(mailInfo)))

    startTime = time.time()

    try:
        main(args)
    except Exception as e:
        if args.email:
            sendMail('High Mass Efficiency Analyzer FAILURE',
                     'Analyzer failed due to exception:\n    {}'.format(e))
        raise
    else:
        elapsedTime = time.time() - startTime
        if args.email:
            sendMail('High Mass Efficiency Analyzer done',
                     'Analyzer finished successfully in {}s'.format(elapsedTime))
        print 'done in {}s!'.format(elapsedTime)
