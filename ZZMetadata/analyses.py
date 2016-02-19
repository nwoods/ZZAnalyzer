

cleaner = 'HZZ4l2015Cleaner'

zzAnalyses = {
    'channels' : 'zz',
    'fullSpectrum_noclean' : {
        'resultDir' : 'results_full_noclean',
        },
    'fullSpectrum_blind' : {
        'baseCuts' : 'AllPass',
        'resultDir' : 'results_full',
        'cutModifiers' : ['Blind'],
        'cleanRows' : cleaner,
        'prereq' : 'fullSpectrum_noclean',
        },
    'fullSpectrum' : {
        'baseCuts' : 'AllPass',
        'resultDir' : 'results_full',
        'cleanRows' : cleaner,
        'prereq' : 'fullSpectrum_noclean',
        },
    'fullSpectrum_2P2F_noclean' : {
        'resultDir' : 'results_full_2P2F_noclean',
        'cutModifiers' : ['ControlRegion_OS_2P2F'],
        },
    'fullSpectrum_2P2F' : {
        'resultDir' : 'results_full_2P2F',
        'baseCuts' : 'AllPass',
        'cleanRows' : cleaner,
        'prereq' : 'fullSpectrum_2P2F_noclean',
        },
    'fullSpectrum_3P1F_noclean' : {
        'resultDir' : 'results_full_3P1F_noclean',
        'cutModifiers' : ['ControlRegion_OS_3P1F'],
        'cleanRows' : cleaner,
        },
    'fullSpectrum_3P1F' : {
        'baseCuts' : 'AllPass',
        'resultDir' : 'results_full_3P1F',
        'cleanRows' : cleaner,
        'prereq' : 'fullSpectrum_3P1F_noclean'
        },
    'smp' : {
        'resultDir' : 'results_smp',
        'cutModifiers' : ['SMPZZ2016'],
        'cleanRows' : cleaner,
        'prereq' : 'fullSpectrum_noclean',
        },
    'smp_2P2F' : {
        'resultDir' : 'results_smp_2P2F',
        'cutModifiers' : ['SMPZZ2016', 'ControlRegion_OS_2P2F'],
        'cleanRows' : cleaner,
        'prereq' : 'fullSpectrum_2P2F_noclean',
        },
    'smp_3P1F' : {
        'resultDir' : 'results_smp_3P1F',
        'cutModifiers' : ['SMPZZ2016', 'ControlRegion_OS_3P1F'],
        'cleanRows' : cleaner,
        'prereq' : 'fullSpectrum_3P1F_noclean',
        },
    'hzz_blind' : {
        'resultDir' : 'results_hzz',
        'cutModifiers' : ['Blind', 'HZZ2016'],
        'cleanRows' : cleaner,
        'prereq' : 'fullSpectrum_noclean',
        },
    'hzz' : {
        'resultDir' : 'results_hzz',
        'cutModifiers' : ['HZZ2016'],
        'cleanRows' : cleaner,
        'prereq' : 'fullSpectrum_noclean',
        },
    'hzz_2P2F' : {
        'resultDir' : 'results_hzz_2P2F',
        'cutModifiers' : ['HZZ2016', 'ControlRegion_OS_2P2F'],
        'cleanRows' : cleaner,
        'prereq' : 'fullSpectrum_2P2F_noclean',
        },
    'hzz_3P1F' : {
        'resultDir' : 'results_hzz_3P1F',
        'cutModifiers' : ['HZZ2016', 'ControlRegion_OS_3P1F'],
        'cleanRows' : cleaner,
        'prereq' : 'fullSpectrum_3P1F_noclean',
        },
    'z4l' : {
        'resultDir' : 'results_z4l',
        'cutModifiers' : ['ZMassWindow'],
        'cleanRows' : cleaner,
        'prereq' : 'fullSpectrum_noclean',
        },
    'z4l_2P2F' : {
        'resultDir' : 'results_z4l_2P2F',
        'cutModifiers' : ['ZMassWindow', 'ControlRegion_OS_2P2F'],
        'cleanRows' : cleaner,
        'prereq' : 'fullSpectrum_2P2F_noclean',
        },
    'z4l_3P1F' : {
        'resultDir' : 'results_z4l_3P1F',
        'cutModifiers' : ['ZMassWindow', 'ControlRegion_OS_3P1F'],
        'cleanRows' : cleaner,
        'prereq' : 'fullSpectrum_3P1F_noclean',
        },
    }

zlAnalyses = {
    'channels' : '3l',
    'zPluslLoose' : {
        'resultDir' : 'resultsLoose',
        'cutModifiers' : ['ControlRegion_Zplusl'],
        },
    'zPluslTight' : {
        'resultDir' : 'resultsTight',
        'cutModifiers' : ['ControlRegion_ZpluslTight'],
        'prereq' : 'zPluslLoose',
        },
    'zPluslTightID' : {
        'resultDir' : 'resultsTightID',
        'cutModifiers' : ['ControlRegion_ZpluslTightID'],
        'prereq' : 'zPluslLoose',
        },
    'zPluslIso' : {
        'resultDir' : 'resultsTightIDIso',
        'cutModifiers' : ['ControlRegion_ZpluslIso'],
        'prereq' : 'zPluslTightID',
        },
    }

zAnalyses = {
    'channels' : 'z',
    'singleZ' : {
        'resultDir' : 'results',
        'cutModifiers' : ['ZPlusAnything','SMPZZ2016'],
        'cleanRows' : 'SingleZCleaner',
        },
    }
