'''

Cut dictionary for the 2012 SMP ZZ->4l analysis, to be used by Cutter.py

Author: Nate Woods, U. Wisconsin

'''

cuts = {
    'Trigger' : {
        'cuts' : {
            'doubleMuPass' : (1, False),
            'doubleMuTrkPass' : (1, False),
            'doubleEPass' : (1, False), 
            'mu17ele8Pass' : (1, False),
            'mu8ele17Pass' : (1, False),
        },
        'mode' : 'or',
    },
    'Overlap' : { 
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
            'IsGlobal' : (1, False),
            'IsTracker' : (1, False),
        },
        'mode' : 'or',
    },
    'eID' : { 
        'cuts' : {
            '5<pt<10' : {
                'eta<0.8' : {
                    'MVANonTrigCSA14' : (0.47, False),
                },
                '0.8<eta<1.479' : {
                    'MVANonTrigCSA14' : (0.004, False),
                },
                'eta>1.479' : {
                    'MVANonTrigCSA14' : (0.295, False),
                },
            },
            'pt>10' : {
                'eta<0.8' : {
                    'MVANonTrigCSA14' : (-0.34, False),
                },
                '0.8<eta<1.479' : {
                    'MVANonTrigCSA14' : (-0.65, False),
                },
                'eta>1.479' : {
                    'MVANonTrigCSA14' : (0.6, False),
                },
            },
        },
        'mode' : 'other',
    },
    'Z1Mass' : {
        'cuts' : { 
            'Mass#lower' : (60., False),
            'Mass#upper' : (120., True),
        },
        'mode' : '2obj',
    },
    'Z2Mass' : {
        'cuts' : { 
            'Mass#lower' : (60., False),
            'Mass#upper' : (120., True),
        },
        'mode' : '2obj',
    },
    'LeptonPairMass' : {
        'cuts' : {
            'Mass' : (4., False),
            'SS' : (1, True), # Must be opposite sign, same flavor not required
        },
        'mode' : '2obj',
    },
    'Lepton1Pt' : {
        'cuts' : {
            'Pt' : (20., False),
        },
        'mode' : 'and',
    },                    
    'Lepton2Pt' : {
        'cuts' : {
            'Pt' : (10., False),
        },
        'mode' : 'and',
    },
    '4lMass' : {
        'cuts' : { 'Mass' : (0., False), },
        'mode' : 'and',
    },
}
