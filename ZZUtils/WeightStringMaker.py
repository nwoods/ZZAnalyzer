'''

WeightStringMaker.py

Some functions to make strings to do binned event weighting.

Author: Nate Woods, U. Wisconsin

'''


from rootpy.plotting import Hist, Hist2D, Hist3D
import rootpy.compiled as ROOTComp
from rootpy.ROOT import gROOT


_WeightStringMaker_counter_ = 0
_WeightStringMaker_histCopies_ = []
def makeWeightStringFromHist(h, *variables, **kwargs):
    '''
    Return a string that weights an event by the value of histogram h in 
    the bin that would be filled by variables.
    '''
    global _WeightStringMaker_counter_
    global _WeightStringMaker_histCopies_

    # make a copy so we can change directory, save it in global scope
    hCopy = h.clone()
    hCopy.SetDirectory(gROOT)
    _WeightStringMaker_histCopies_.append(hCopy)

    ROOTComp.register_code('''
    #include "TH1.h"
    #include "TROOT.h"
    double weightFun{0}({1})
    {{
      TH1* h = (TH1*)gROOT->Get("{2}");
      return h->GetBinContent(h->FindBin({3}));
    }}'''.format(_WeightStringMaker_counter_,
                ', '.join('double x%d'%i for i in range(len(variables))),
                hCopy.GetName(),
                ', '.join("x%d"%i for i in range(len(variables)))),
                  ["weightFun%d"%_WeightStringMaker_counter_,])
    out = 'weightFun%d(%s)'%(_WeightStringMaker_counter_, ', '.join(variables))

    # force system to compile code now
    arglebargle = getattr(ROOTComp, "weightFun%d"%_WeightStringMaker_counter_)

    _WeightStringMaker_counter_ += 1

    return out


_WeightStringMaker_histTypes_ = {
    1 : Hist,
    2 : Hist2D,
    3 : Hist3D,
}

def makeWeightHistFromJSONDict(jd, weightVar, *binVars, **kwargs): 
    '''
    Take a dictionary jd built from a json, return a histogram in bins of
    binVars, with the bin edges given in the json by binVars[i] postpended 
    with a suffix taken from kwargs['loSuffix'] and kwargs['hiSuffix']. 
    The error on the weight is taken to be weightVar+kwargs['errSuffix'] 
    (there is taken to be no error if kwargs['errSuffix'] evaluates to False).
    If kwargs['scale'] is 'up' ('down') the histogram has its error
    added to (subtracted from) the mean value.
    '''
    loSuffix=kwargs.get('loSuffix', '_lo')
    hiSuffix=kwargs.get('hiSuffix', '_hi')
    errSuffix=kwargs.get('errSuffix', '_err')
    scale = kwargs.get('scale', '')

    binEdges = {v:set() for v in binVars}
    varsLo = [v+loSuffix for v in binVars]
    varsHi = [v+hiSuffix for v in binVars]
    weights = {}
    errVar = weightVar+errSuffix if errSuffix else False
    errs = {}

    for bin in jd:
        binLo = tuple(bin[v] for v in varsLo)
        binHi = tuple(bin[v] for v in varsHi)
        centerTuple = tuple((binLo[i]+binHi[i])/2 for i in range(len(binVars)))
        weights[centerTuple] = bin[weightVar]
        if errVar:
            errs[centerTuple] = bin[errVar]
        for i, v in enumerate(binVars):
            binEdges[v].add(binHi[i])
            binEdges[v].add(binLo[i])

    edgeArgs = [sorted(list(binEdges[v])) for v in binVars]
    h = _WeightStringMaker_histTypes_[len(binVars)](*edgeArgs)

    for center, w in weights.iteritems():
        binInd = h.FindBin(*center)
        h.SetBinContent(binInd, w)
        if errVar:
            h.SetBinError(binInd, errs[center])
            
            if scale == 'up':
                h.SetBinContent(binInd, w+errs[center])
            elif scale == 'down':
                h.SetBinContent(binInd, w-errs[center])

    return h





