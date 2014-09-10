'''

Cut dictionary for the 2012 HZZ4l analysis, to be used by Cutter.py

Author: Nate Woods

'''

cuts = {
    'trigger' : {
        'cuts' : {
            'doubleMuPass' : (1, False),
            'doubleMuTrkPass' : (1, False),
            'doubleEPass' : (1, False), 
            'mu17ele8Pass' : (1, False),
            'mu8ele17Pass' : (1, False),
        },
        'mode' : 'or',
    },
    'overlap' : { 
        'cuts' : { 'DR' : (0.1, False), },
        'mode' : '2obj',
    },
    'mIso' : { 
        'cuts' : { 'RelPFIsoDBDefault' : (0.4, True) },
        'mode' : 'and',
    },
    'mTightIso' : { 
        'cuts' : { 'RelPFIsoDB' : (0.2, True) },
        'mode' : 'and',
    },
    'eIso' : { 
        'cuts' : { 'RelPFIsoRhoFSR' : (0.4, True) },
        'mode' : 'and',
    },
    'eTightIso' : { 
        'cuts' : { 'RelPFIsoRhoFSR' : (0.2, True) },
        'mode' : 'and',
    },
    'eSelection' : {
        'cuts' : {
            'Pt' : (7., False),
            'AbsEta' : (2.5, True),
            'SIP3D' : (4., True),
            'PVDXY' : (0.5, True),
            'PVDZ' : (1., True),
            },
        'mode' : 'and',
        'options' : 'absPVDZabsPVDXY',
    },
    'mSelection' : { 
        'cuts' : {
            'Pt' : (5., False),
            'AbsEta' : (2.5, True),
            'SIP3D' : (4., True),
            'PVDXY' : (0.5, True),
            'PVDZ' : (1., True),
        },
        'mode' : 'and',
        'options' : 'absPVDZabsPVDXY',
    },
    'mID' : { 
        'cuts' : { 
            'IsGlobal' : (1, False) ,  # actually boolean 0s, written as 0.1 to
            'IsTracker' : (1, False),  # because False makes the comparison >=
        },
        'mode' : 'or',
    },
### Old eID not available, use CSA14 ID for now
#     'eID' : { 
#         'cuts' : {
#             '5<pt<10' : {
#                 'eta<0.8' : {
#                     'MVANonTrig' : (0.47, False),
#                 },
#                 '0.8<eta<1.479' : {
#                     'MVANonTrig' : (0.004, False),
#                 },
#                 'eta>1.479' : {
#                     'MVANonTrig' : (0.47, False),
#                 },
#             },
#             'pt>10' : {
#                 'eta<0.8' : {
#                     'MVANonTrig' : (-0.34, False),
#                 },
#                 '0.8<eta<1.479' : {
#                     'MVANonTrig' : (-0.65, False),
#                 },
#                 'eta>1.479' : {
#                     'MVANonTrig' : (0.6, False),
#                 },
#             },
#         },
#         'mode' : 'other',
#     },
    'eID' : {
        'cuts' : {
            'CBIDTight_25ns' : (1, False),
        },
        'mode' : 'and',
    },
    'Z1Mass' : {
        'cuts' : { 
            'Mass#lower' : (40., False),
            'Mass#upper' : (120., True),
        },
        'mode' : '2obj',
    },
    'Z2Mass' : {
        'cuts' : { 
            'Mass#lower' : (12., False),
            'Mass#upper' : (120., True),
        },
        'mode' : '2obj',
    },
    'leptonPairMass' : {
        'cuts' : {
            'Mass' : (4., False),
            'SS' : (1, True), # Must be opposite sign, same flavor not required
        },
        'mode' : '2obj',
    },
    'lepton1Pt' : {
        'cuts' : {
            'Pt' : (20., False),
        },
        'mode' : 'and',
    },                    
    'lepton2Pt' : {
        'cuts' : {
            'Pt' : (10., False),
        },
        'mode' : 'and',
    },
    '4lMass' : {
        'cuts' : { 'Mass' : (100., False), },
        'mode' : 'and',
    },
}
