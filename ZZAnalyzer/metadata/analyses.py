

cleaner = 'HZZ4l2015Cleaner'

zzAnalyses = {
    'channels' : 'zz',
    'fullSpectrum_noclean' : {
        'resultDir' : 'results_full_noclean',
        'cutModifiers' : [],
        },
    'fullSpectrum_blind' : {
        'resultDir' : 'results_full',
        'cutModifiers' : ['Blind',],
        'cleanRows' : cleaner,
        },
    'fullSpectrum' : {
        'resultDir' : 'results_full',
        'cutModifiers' : [],
        'cleanRows' : cleaner,
        },
    'fullSpectrum_2P2F' : {
        'resultDir' : 'results_full_2P2F',
        'cutModifiers' : ['ControlRegion_OS_2P2F'],
        'cleanRows' : cleaner,
        },
    'fullSpectrum_3P1F' : {
        'resultDir' : 'results_full_3P1F',
        'cutModifiers' : ['ControlRegion_OS_3P1F'],
        'cleanRows' : cleaner,
        },
    'fullSpectrum_2P2F_noclean' : {
        'resultDir' : 'results_full_2P2F',
        'cutModifiers' : ['ControlRegion_OS_2P2F'],
        },
    'fullSpectrum_3P1F_noclean' : {
        'resultDir' : 'results_full_3P1F',
        'cutModifiers' : ['ControlRegion_OS_3P1F'],
        },
    'smp' : {
        'baseCuts' : 'AllPass',
        'resultDir' : 'results_smp',
        'cutModifiers' : ['SMPZZ2016'],
        'prereq' : 'fullSpectrum',
        },
    'smp_2P2F' : {        
        'baseCuts' : 'AllPass',
        'resultDir' : 'results_smp_2P2F',
        'cutModifiers' : ['SMPZZ2016'],
        'prereq' : 'fullSpectrum_2P2F',
        },
    'smp_3P1F' : {
        'baseCuts' : 'AllPass',
        'resultDir' : 'results_smp_3P1F',
        'cutModifiers' : ['SMPZZ2016'],
        'prereq' : 'fullSpectrum_3P1F',
        },
    'hzz_blind' : {
        'baseCuts' : 'AllPass',
        'resultDir' : 'results_hzz',
        'cutModifiers' : ['Blind', 'HZZ2016'],
        'prereq' : 'fullSpectrum_noclean',
        'cleanRows' : 'HZZ4l2016Cleaner',
        },
    'hzz' : {
        'baseCuts' : 'AllPass',
        'resultDir' : 'results_hzz',
        'cutModifiers' : ['HZZ2016'],
        'prereq' : 'fullSpectrum_noclean',
        'cleanRows' : 'HZZ4l2016Cleaner',
        },
    'hzz_2P2F' : {
        'baseCuts' : 'AllPass',
        'resultDir' : 'results_hzz_2P2F',
        'cutModifiers' : ['HZZ2016'],
        'prereq' : 'fullSpectrum_2P2F_noclean',
        'cleanRows' : 'HZZ4l2016Cleaner',
        },
    'hzz_3P1F' : {
        'baseCuts' : 'AllPass',
        'resultDir' : 'results_hzz_3P1F',
        'cutModifiers' : ['HZZ2016'],
        'prereq' : 'fullSpectrum_3P1F_noclean',
        'cleanRows' : 'HZZ4l2016Cleaner',
        },
    'z4l' : {
        'baseCuts' : 'AllPass',
        'resultDir' : 'results_z4l',
        'cutModifiers' : ['ZMassWindow'],
        'prereq' : 'fullSpectrum',
        },
    'z4l_2P2F' : {
        'baseCuts' : 'AllPass',
        'resultDir' : 'results_z4l_2P2F',
        'cutModifiers' : ['ZMassWindow'],
        'prereq' : 'fullSpectrum_2P2F',
        },
    'z4l_3P1F' : {
        'baseCuts' : 'AllPass',
        'resultDir' : 'results_z4l_3P1F',
        'cutModifiers' : ['ZMassWindow'],
        'prereq' : 'fullSpectrum_3P1F',
        },
    }

zlAnalyses = {
    'channels' : '3l',
    'zPluslLoose' : {
        'resultDir' : 'resultsLoose',
        'cutModifiers' : ['ControlRegion_Zplusl', 'SMPZZ2016'],
        'cleanRows' : 'ZPlusXCleaner',
        },
    'zPluslTight' : {
        'resultDir' : 'resultsTight',
        'cutModifiers' : ['ControlRegion_ZpluslTight', 'SMPZZ2016'],
        'prereq' : 'zPluslLoose',
        },
    }

zAnalyses = {
    'channels' : 'z',
    'singleZ' : {
        'resultDir' : 'results',
        'cutModifiers' : ['SingleZ','ZPlusAnything','SMPZZ2016'],
        'cleanRows' : 'SingleZCleaner',
        },
    }
