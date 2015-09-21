'''

Template for saving ntuple of ZZ analyzer results (mass and whatnot)
Inherits from ZZNtupleSaver, which inherits from ZZResultSaverBase

Author: Nate Woods, U. Wisconsin

'''


from ZZNtupleSaver import ZZNtupleSaver
from ZZHelpers import * # evVar, objVar, nObjVar, deltaR, Z_MASS
from rootpy.vector import LorentzVector
from itertools import combinations
from collections import OrderedDict


class ZZNtupleDREtFSR(ZZNtupleSaver):
    def __init__(self, fileName, channels, inputNtuples, *args, **kwargs):
        self.copyVars = [[],[],[]] # 0, 1, and 2- lepton variables
        self.calcVars = [{},{},{}] # dictionary of function-makers for 0, 1 and 2-lepton calculated variables
        self.flavoredCopyVars = {'e':[],'m':[]}
        self.flavoredCalcVars = {'e':{},'m':{}}
        self.inputs = inputNtuples
        super(ZZNtupleDREtFSR, self).__init__(fileName, channels, *args, **kwargs)

        
    def setupTemplate(self):
        fsrTypesDREt = ['DREt', 'DREt15', 'DREt2',]
        fsrTypesSquare = ['Et4DR01', 'Et4DR03']
        isoStrings = ['', 'Iso']
        dmStrings = ['', 'DM']

        dREtCuts = {
            'DREtIso' : .0372,
            'DREt2Iso' : .0110,
            'DREt15IsoDM' : .0450,
            'DREt15DM' : .0048,
            'DREt2IsoDM' : 0.03,
            'DREt2' : .0031,
            'DREt15' : .0031,
            'DREt' : .0152,
            'DREtIsoDM' : 0.05,
            'DREtDM' : .02,
            'DREt2DM' : .00476,
            'DREt15Iso' : .011,
            }

        self.copyVars[0] = [
            'Mass',
            'Pt',
            'Eta',
            'Phi',
            'Mt',
            'MassFSR',
            'PtFSR',
            'EtaFSR',
            'PhiFSR',
            'MtFSR',
            'evt',
            'lumi',
            'run',
            'singleEPass',
            'doubleMuPass',
            'doubleEPass',
            'singleESingleMuPass',
            'singleMuSingleEPass',
            'doubleESingleMuPass',
            'doubleMuSingleEPass',
            'tripleEPass',
            'tripleMuPass',
            'pvZ',
            'pvndof',
            'pvRho',
            'pvIsFake',
            'vbfNJets',
            'vbfj1pt',
            'vbfj2pt',
            'jet1Pt',
            'jet2Pt',
            'jet3Pt',
            'jet4Pt',
            'jet1Eta',
            'jet2Eta',
            'jet3Eta',
            'jet4Eta',
            'nJets',
            'D_bkg',
            'D_bkg_kin',
            'D_gg',
            'D_g4',
            'Djet_VAJHU',
            'HZZCategory',
            'GenWeight',
            'nvtx',
            'nTruePU',
        ]
        self.copyVars[0] += ["%s%s%sFSR%s"%(var, fsrType, maybeIso, maybeDM) \
                                 for var in ['Pt', 'Eta', 'Phi', 'Mass'] \
                                 for fsrType in fsrTypesSquare \
                                 for maybeIso in isoStrings \
                                 for maybeDM in dmStrings
                             ]

        self.copyVars[1] = [
            '%sAbsEta',
            '%sCharge',
            '%sEta',
            '%sGenCharge',
            '%sGenEnergy',
            '%sGenPdgId',
            '%sGenPhi',
            '%sMass',
            '%sPVDXY',
            '%sPVDZ',
            '%sPhi',
            '%sPt',
            '%sSIP3D',
            '%sPFChargedIso',
            '%sPFNeutralIso',
            '%sPFPhotonIso',
            '%sRho',
            '%sHasGenFSR',
            '%sGenFSRPt',
            '%sGenFSRDR',
            '%sHasFSR',
            '%sGenFSRMassChange',
            ]
        self.copyVars[1] += ["%%s%s%sFSR%s"%(fsrType, maybeIso, var) \
                                 for var in ['Pt', 'Eta', 'Phi'] \
                                 for fsrType in fsrTypesSquare \
                                 for maybeIso in isoStrings
                             ]
        self.copyVars[1] += ["%%s%s%sFSRImprovesZ"%(fsrType, maybeIso) \
                                 for fsrType in fsrTypesSquare+fsrTypesDREt \
                                 for maybeIso in isoStrings
                             ]
        self.copyVars[1] += ["%%s%s%sFSRGenMatch"%(fsrType, maybeIso) \
                                 for fsrType in fsrTypesSquare \
                                 for maybeIso in isoStrings
                             ]
        self.copyVars[1] += ["%%s%s%sFSRMassChange"%(fsrType, maybeIso) \
                                 for fsrType in fsrTypesSquare \
                                 for maybeIso in isoStrings
                             ]
        self.copyVars[1] += ["%%s%s%sFSRDR"%(fsrType, maybeIso) \
                                 for fsrType in fsrTypesSquare \
                                 for maybeIso in isoStrings
                             ]
        self.copyVars[1] += ['%%s%s%sFSRDREt'%(fsrType, maybeIso) \
                                 for fsrType in fsrTypesDREt \
                                 for maybeIso in isoStrings
                             ]

        self.flavoredCopyVars['e'] = [ 
            '%sMVANonTrigID',
            '%sRelPFIsoRho',
            '%sSCEnergy',
            '%sSCEta',
            '%sSCPhi',
            '%sMissingHits',
            '%sNearestMuonDR',
            '%sRelPFIsoRhoFSR',
        ]
        self.flavoredCopyVars['e'] += ["%%sRelPFIsoRho%s%sFSR%s"%(fsrType, maybeIso, maybeDM) \
                                           for fsrType in fsrTypesSquare \
                                           for maybeIso in isoStrings \
                                           for maybeDM in dmStrings
                                       ]

        self.flavoredCopyVars['m'] = [
            '%sIsGlobal',
            '%sIsTracker',
            '%sRelPFIsoDBDefault',
            '%sIsPFMuon',
            '%sMatchedStations',
            '%sPFPUChargedIso',
            '%sBestTrackType',
            '%sRelPFIsoDBFSR',
            ]
        self.flavoredCopyVars['m'] += ["%%sRelPFIsoDB%s%sFSR%s"%(fsrType, maybeIso, maybeDM) \
                                           for fsrType in fsrTypesSquare \
                                           for maybeIso in isoStrings \
                                           for maybeDM in dmStrings
                                       ]

        self.copyVars[2] = [
            '%s_%s_Mass',
            '%s_%s_MassFSR',
            '%s_%s_Pt',
            '%s_%s_PtFSR',
            '%s_%s_Eta',
            '%s_%s_EtaFSR',
            '%s_%s_Phi',
            '%s_%s_PhiFSR',
            '%s_%s_Mt',
            '%s_%s_MtFSR',
            '%s_%s_FSRPt',
            '%s_%s_FSREta',
            '%s_%s_FSRPhi',
            '%s_%s_SS',
            '%s_%s_DR',
            '%s_%s_MassFSR',
            '%s_%s_FSRGenMatch',
            '%s_%s_FSRGenPt',
            '%s_%s_FSRGenDR',
            '%s_%s_FSRDR',
        ]
        self.copyVars[2] += ["%%s_%%s_%s%s%sFSR%s"%(var, fsrType, maybeIso, maybeDM) \
                                 for var in ['Pt', 'Eta', 'Phi', 'Mass'] \
                                 for fsrType in fsrTypesSquare \
                                 for maybeIso in isoStrings \
                                 for maybeDM in dmStrings
                             ]
        
        self.calcVars[0] = {}
        # self.calcVars[0].update(
        #     {
        #         "%s%s%sFSR%s"%(var, fsrType, maybeIso, maybeDM) : \
        #             self.makeLambdaizer(self.nObjVarDREtCut, 4, 
        #                                 var, fsrType, dREtCuts[fsrType+maybeIso+maybeDM],
        #                                 maybeDM == 'DM') \
        #             for var in ['Pt', 'Eta', 'Phi'] \
        #             for fsrType in fsrTypesDREt \
        #             for maybeIso in isoStrings \
        #             for maybeDM in dmStrings
        #         }
        #     )
        self.calcVars[0].update(
            {
                "Mass%s%sFSR%s"%(fsrType, maybeIso, maybeDM) : \
                    self.makeLambdaizer(self.nObjMassDREtCut, 4,
                                        fsrType,
                                        dREtCuts[fsrType+maybeIso+maybeDM],
                                        maybeDM == 'DM') \
                    for fsrType in fsrTypesDREt \
                    for maybeIso in isoStrings \
                    for maybeDM in dmStrings
                }
            )
        
        self.calcVars[1] = {}
        self.calcVars[1].update(
            {
                '%%s%s%sFSR%s%s'%(fsrType, maybeIso, maybeDM, var) : \
                    self.makeLambdaizer(self.varOrValDREtCut, 1,
                                        '%s%sFSR%s'%(fsrType, maybeIso, var),
                                        -999., '%s%s'%(fsrType, maybeIso),
                                        dREtCuts[fsrType+maybeIso+maybeDM],
                                        maybeDM == 'DM') \
                    for var in ['Pt', 'DR'] \
                    for fsrType in fsrTypesDREt \
                    for maybeIso in isoStrings \
                    for maybeDM in dmStrings
                }
            )
        self.calcVars[1].update(
            {
                '%%s%s%sFSRDM%s'%(fsrType, maybeIso, var) : \
                    self.makeLambdaizer(self.varOrValDMCut, 1,
                                        '%s%sFSR%s'%(fsrType, maybeIso, var),
                                        -999., '%s%s'%(fsrType, maybeIso)) \
                    for var in ['Pt', 'DR'] \
                    for fsrType in fsrTypesSquare \
                    for maybeIso in isoStrings \
                }
            )

        self.calcVars[1].update(
            {
                '%%s%s%sFSR%sGenMatch'%(fsrType, maybeIso, maybeDM) : \
                    self.makeLambdaizer(self.varOrValDREtCut, 1,
                                        '%s%sFSRGenMatch'%(fsrType, maybeIso),
                                        0., '%s%s'%(fsrType, maybeIso),
                                        dREtCuts[fsrType+maybeIso+maybeDM],
                                        maybeDM == 'DM') \
                    for fsrType in fsrTypesDREt \
                    for maybeIso in isoStrings \
                    for maybeDM in dmStrings
                }
            )
        self.calcVars[1].update(
            {
                '%%s%s%sFSRDMGenMatch'%(fsrType, maybeIso) : \
                    self.makeLambdaizer(self.varOrValDMCut, 1,
                                        '%s%sFSRGenMatch'%(fsrType, maybeIso),
                                        0., '%s%s'%(fsrType, maybeIso)) \
                    for fsrType in fsrTypesSquare \
                    for maybeIso in isoStrings \
                }
            )

        self.calcVars[1].update(
            {
                '%%s%s%sFSR%sMassChange'%(fsrType, maybeIso, maybeDM) : \
                    self.makeLambdaizer(self.varOrValDREtCut, 1,
                                        '%s%sFSRMassChange'%(fsrType, maybeIso),
                                        0., '%s%s'%(fsrType, maybeIso),
                                        dREtCuts[fsrType+maybeIso+maybeDM],
                                        maybeDM == 'DM') \
                    for fsrType in fsrTypesDREt \
                    for maybeIso in isoStrings \
                    for maybeDM in dmStrings
                }
            )
        self.calcVars[1].update(
            {
                '%%s%s%sFSRDMMassChange'%(fsrType, maybeIso) : \
                    self.makeLambdaizer(self.varOrValDMCut, 1,
                                        '%s%sFSRMassChange'%(fsrType, maybeIso),
                                        0., '%s%s'%(fsrType, maybeIso)) \
                    for fsrType in fsrTypesSquare \
                    for maybeIso in isoStrings \
                }
            )
                
            
        self.calcVars[2] = {}
        # self.calcVars[2].update(
        #     {
        #         "%%s_%%s_%s%s%sFSR%s"%(var, fsrType, maybeIso, maybeDM) :\
        #             self.makeLambdaizer(self.nObjVarDREtCut, 2,
        #                                 var, fsrType, dREtCuts[fsrType+maybeIso+maybeDM],
        #                                 maybeDM == 'DM') \
        #             for var in ['Pt', 'Eta', 'Phi'] \
        #             for fsrType in fsrTypesDREt \
        #             for maybeIso in isoStrings \
        #             for maybeDM in dmStrings
        #         }
        #     )
        self.calcVars[2].update(
            {
                "%%s_%%s_Mass%s%sFSR%s"%(fsrType, maybeIso, maybeDM) :\
                    self.makeLambdaizer(self.nObjMassDREtCut, 2,
                                        fsrType, dREtCuts[fsrType+maybeIso+maybeDM],
                                        maybeDM == 'DM') \
                    for fsrType in fsrTypesDREt \
                    for maybeIso in isoStrings \
                    for maybeDM in dmStrings
                }
            )
        self.calcVars[2].update(
            {
                "%s_%s_FSRMassChange" : self.makeLambdaizer(self.legacyFSRMassChange, 2),
                }
            )

        self.flavoredCalcVars['m'] = {}
        self.flavoredCalcVars['m'].update( 
                    {
                        "%%sRelPFIsoDB%s%sFSR%s"%(fsrType, maybeIso, maybeDM) : \
                            self.makeLambdaizer(self.varSubstitutionDREtCut, 1, 
                                                "RelPFIsoDB", "RelPFIsoDBDefault", fsrType,
                                                dREtCuts[fsrType+maybeIso+maybeDM],
                                                maybeDM == 'DM') \
                            for fsrType in fsrTypesDREt \
                            for maybeIso in isoStrings \
                            for maybeDM in dmStrings
                        }
                    )

        self.flavoredCalcVars['e'] = {}
        self.flavoredCalcVars['e'].update( 
                    {
                        "%%sRelPFIsoRho%s%sFSR%s"%(fsrType, maybeIso, maybeDM) : \
                            self.makeLambdaizer(self.varDREtCut, 1, 
                                                "RelPFIsoRho", fsrType,
                                                dREtCuts[fsrType+maybeIso+maybeDM],
                                                maybeDM == 'DM') \
                            for fsrType in fsrTypesDREt \
                            for maybeIso in isoStrings \
                            for maybeDM in dmStrings
                        }
                    )                  


        obj4M = ['m' + str(i+1) for i in range(4)]
        obj4E = ['e' + str(i+1) for i in range(4)]
        obj2E2M = ['e' + str(i+1) for i in range(2)] + ['m' + str(i+1) for i in range(2)]


        template = {
            'mmmm' : {
                'final' : {
                    'vars' : self.templateForObjects('mmmm', obj4M),
                    },
                },
            'eemm' : {
                'final' : {
                    'vars' : self.templateForObjects('eemm', obj2E2M),
                    },
                },
            'eeee' : {
                'final' : {
                    'vars' : self.templateForObjects('eeee', obj4E),
                    },
                },
            }
    
        return template


    def templateForObjects(self, channel, objects):
        '''
        Takes a channel and list of objects, returns a variable template for it.
        For variables that must be calculated, if None is found instead of a
        lambda or other calculator function, the variable is copied instead of
        calculated (or allow the functions that generate the calculators to
        decide intelligently if a variable already exists).
        '''
        temp = {'copy' : {'ntuple' : self.inputs[channel], 'only' : []}}

        for n, varList in enumerate(self.copyVars):
            for objs in combinations(objects, n):
                for var in varList:
                    temp['copy']['only'].append(var%objs)

        for obj in objects:
            if obj[0] not in self.flavoredCopyVars:
                continue
            for var in self.flavoredCopyVars[obj[0]]:
                temp['copy']['only'].append(var%obj)

        for n, funcs in enumerate(self.calcVars):
            for var, func in funcs.iteritems():
                for objs in combinations(objects, n):
                    allObj = list(objs)+objects
                    f = func(*allObj)
                    if f is None:
                        temp['copy']['only'].append(var%objs)
                    else:
                        temp[var%objs] = {'f':f}

        for obj in objects:
            if obj[0] not in self.flavoredCalcVars:
                continue
            for var, func in self.flavoredCalcVars[obj[0]].iteritems():
                f = func(obj, objects)
                if f is None:
                    temp['copy']['only'].append(var%obj)
                else:
                    temp[var%obj] = {'f':f}

        return temp


    def photonP4(self, row, obj, fsrType):
        '''
        4-momentum of FSR photon of appropriate type if is exists. Otherwise
        returns vector with p=0.
        '''
        pt = objVar(row, fsrType+"FSRPt", obj)
        if pt <= 0.:
            return LorentzVector(0.,0.,0.,0.)
        v = LorentzVector()
        v.SetPtEtaPhiM(pt, objVar(row, fsrType+"FSREta", obj),
                       objVar(row, fsrType+"FSRPhi", obj), 0.)
        return v


    def photonP4DREtCut(self, row, obj, fsrType, dREtCut, requireDM):
        '''
        4-momentum of FSR photon of appropriate type if is exists and passes
        a deltaR/eT^n cut. If requireDM evaluates to true, also requires the
        photon to improve Z mass. Otherwise returns vector with p=0.
        '''
        dret = objVar(row, fsrType+"FSRDREt", obj)
        if dret < 0. or dret >= dREtCut:
            return LorentzVector(0.,0.,0.,0.)
        if requireDM:
            return self.photonP4DMCut(row, obj, fsrType)
        return self.photonP4(row, obj, fsrType)

        
    def photonP4DMCut(self, row, obj, fsrType):
        '''
        4-momentum of FSR photon of appropriate type if improves the candidate
        Z mass. Otherwise returns vector with p=0.
        '''
        if objVar(row, fsrType+"FSRImprovesZ", obj) < 0.5:
            return LorentzVector(0.,0.,0.,0.)
        return self.photonP4(row, obj, fsrType)

        
    def lepP4(self, row, obj):
        '''
        4-momentum of this lepton. No FSR.
        '''
        v = LorentzVector()
        v.SetPtEtaPhiM(objVar(row, "Pt", obj),
                       objVar(row, "Eta", obj),
                       objVar(row, "Phi", obj),
                       0.105658 if obj[0] == 'm' else 0.000511)
        return v


    def nObjP4DREtCut(self, row, objs, fsrType, dREtCut, requireDM):
        '''
        Total 4-momentum of a list of objects, with each including any FSR
        photons that pass the dREtCut (and the Z mass requirement if 
        requireDM evaluates to True). 
        '''
        return sum(self.lepP4(row, obj)+self.photonP4DREtCut(row, obj, fsrType, dREtCut, requireDM) for obj in objs)


    def nObjP4DMCut(self, row, objs, fsrType):
        '''
        Total 4-momentum of a list of objects, with each including any FSR
        photons of the relevant type that improve the Z mass.
        '''
        return sum(lepP4(row, obj)+self.photonP4DMCut(row, obj, fsrType) for obj in objs)


    def nObjMassDREtCut(self, row, objs, fsrType, dREtCut, requireDM):
        return self.nObjP4DREtCut(row, objs, fsrType, dREtCut, requireDM).M()


    def nObjVarDREtCut(self, row, objs, var, fsrType, dREtCut, requireDM):
        '''
        Works for Pt, Eta, Phi, maybe others
        '''
        return getattr(self.nObjP4DREtCut(row, objs, fsrType, dREtCut, requireDM), var)()


    def nObjMassDMCut(self, row, objs, var, fsrType):
        return self.nObjP4DMCut(row, objs, fsrType).M()


    def nObjVarDMCut(self, row, objs, var, fsrType):
        '''
        Works for Pt, Eta, Phi, maybe others
        '''
        return getattr(nObjP4DMCut(row, objs, fsrType), var)()


    def varDREtCut(self, row, obj, var, fsrType, dREtCut, requireDM):
        '''
        Returns var with FSR correction if there is a passing deltaR/eT^n
        photon, without if there isn't.
        '''
        dret = objVar(row, fsrType+"FSRDREt", obj)
        if dret < 0. or dret >= dREtCut:
            return objVar(row, var, obj)
        if requireDM:
            return self.varDMCut(row, obj, var, fsrType)
        return objVar(row, var+fsrType+"FSR", obj)


    def varDMCut(self, row, obj, var, fsrType):
        '''
        Returns var modified by the relevant type of FSR if the FSR improves
        the Z candidate, or unmodified if it doesn't.
        '''
        if objVar(row, fsrType+"FSRImprovesZ", obj) < 0.5:
            return objVar(row, obj, var)
        return objVar(row, var+fsrType+"FSR", obj)


    def varSubstitutionDREtCut(self, row, obj, varFSR, varNoFSR, fsrType, dREtCut, requireDM):
        '''
        Returns varFSR with FSR correction if there is a passing deltaR/eT^n
        photon, returns varNoFSR if there isn't.
        '''
        dret = objVar(row, fsrType+"FSRDREt", obj)
        if dret < 0. or dret >= dREtCut:
            return objVar(row, varNoFSR, obj)
        if requireDM:
            return self.varSubstitutionDMCut(row, obj, varFSR, varNoFSR, fsrType)
        return objVar(row, varFSR+fsrType+"FSR", obj)


    def varSubstitutionDMCut(self, row, obj, varFSR, varNoFSR, fsrType):
        '''
        Returns varFSR modified by the relevant type of FSR if the FSR improves
        the Z candidate, or varNoFSR unmodified if it doesn't.
        '''
        if objVar(row, fsrType+"FSRImprovesZ", obj) < 0.5:
            return objVar(row, varNoFSR, obj)
        return objVar(row, varFSR+fsrType+"FSR", obj)


    def varOrValDMCut(self, row, obj, var, val, fsrType):
        '''
        Returns var if this object's FSR improves the Z mass, or val
        if it does not.
        '''
        if objVar(row, fsrType+"FSRImprovesZ", obj) < 0.5:
            return val
        return objVar(row, var, obj)


    def varOrValDREtCut(self, row, obj, var, val, fsrType, dREtCut, requireDM):
        '''
        Returns var if there is a passing deltaR/eT^n photon, val if there is not.
        If requireDM evaluates to True, the photon is also required to improve 
        the Z mass.
        '''
        dret = objVar(row, fsrType+"FSRDREt", obj)
        if dret < 0. or dret >= dREtCut:
            return val
        if requireDM:
            return self.varOrValDMCut(row, obj, var, val, fsrType)
        return objVar(row, var, obj)

        
    def legacyFSRMassChange(self, row, (obj1, obj2)):
        '''
        Returns the amount the legacy FSR photon for objects 1 and 2 changes
        the 4l mass.
        '''
        fsrPt = nObjVar(row, "FSRPt", obj1, obj2)
        if fsrPt <= 0.:
            return 0.
        fsrEta = nObjVar(row, "FSREta", obj1, obj2)
        fsrPhi = nObjVar(row, "FSRPhi", obj1, obj2)

        pt4l = evVar(row, "Pt")
        eta4l = evVar(row, "Eta")
        phi4l = evVar(row, "Phi")
        m4l = evVar(row, "Mass")

        fsrP4 = LorentzVector()
        fsrP4.SetPtEtaPhiM(fsrPt, fsrEta, fsrPhi, 0.)
        p44l = LorentzVector()
        p44l.SetPtEtaPhiM(pt4l, eta4l, phi4l, m4l)

        return ((fsrP4 + p44l).M() - m4l)


    def makeLambdaizer(self, fun, nObj, *args):
        '''
        Returns a lambda function that takes nObj objects, 
        and returns another lambda function that takes a row 
        and calls fun with row as the first argument, the
        object or a list of the objects as the second argument, and args as the
        rest of the arguments.
        '''
        if not nObj:
            return lambda *x: self.lambdaize(fun, *args)
        if nObj == 1:
            return lambda *obj: self.lambdaize(fun, obj[0], *args)
        return lambda *obj: self.lambdaize(fun, obj[:nObj], *args)


    def lambdaize(self, fun, obj, *args):
        '''
        Returns a lambda function that takes a row and returns fun with row
        as the first argument, obj as the second, and args as other arguments.
        '''
        return lambda row: fun(row, obj, *args)
