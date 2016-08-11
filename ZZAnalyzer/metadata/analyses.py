

cleaner = 'HZZ4l2016Cleaner'

zzAnalyses = {
    'channels' : 'zz',
    'fullSpectrum_noclean' : {
        'resultDir' : 'results_full_noclean',
        'cutModifiers' : ['HighPtMuons',],
        },
    'fullSpectrum_bkg_noclean' : {
        'resultDir' : 'results_full_noclean',
        'cutModifiers' : ['HighPtMuons', 'NoTrigger'],
        },
    'fullSpectrum_blind' : {
        'resultDir' : 'results_full',
        'cutModifiers' : ['Blind', 'HighPtMuons',],
        'cleanRows' : cleaner,
        },
    'fullSpectrum' : {
        'resultDir' : 'results_full',
        'cutModifiers' : ['HighPtMuons',],
        'cleanRows' : cleaner,
        },
    'fullSpectrum_bkg' : {
        'resultDir' : 'results_full',
        'cutModifiers' : ['HighPtMuons', 'NoTrigger'],
        'cleanRows' : cleaner,
        },
    'fullSpectrum_2P2F' : {
        'resultDir' : 'results_full_2P2F',
        'cutModifiers' : ['ControlRegion_OS_2P2F', 'HighPtMuons', 'NoTrigger'],
        'cleanRows' : cleaner,
        },
    'fullSpectrum_3P1F' : {
        'resultDir' : 'results_full_3P1F',
        'cutModifiers' : ['ControlRegion_OS_3P1F', 'HighPtMuons', 'NoTrigger'],
        'cleanRows' : cleaner,
        },
    'smp' : {
        'baseCuts' : 'AllPass',
        'resultDir' : 'results_smp',
        'cutModifiers' : ['SMPZZ2016'],
        'prereq' : 'fullSpectrum_bkg',
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
        'prereq' : 'fullSpectrum',
        },
    'hzz' : {
        'baseCuts' : 'AllPass',
        'resultDir' : 'results_hzz',
        'cutModifiers' : ['HZZ2016'],
        'prereq' : 'fullSpectrum',
        },
    'hzz_bkg' : {
        'baseCuts' : 'AllPass',
        'resultDir' : 'results_hzz',
        'cutModifiers' : ['HZZ2016'],
        'prereq' : 'fullSpectrum_bkg',
        },
    'hzz_2P2F' : {
        'baseCuts' : 'AllPass',
        'resultDir' : 'results_hzz_2P2F',
        'cutModifiers' : ['HZZ2016'],
        'prereq' : 'fullSpectrum_2P2F',
        },
    'hzz_3P1F' : {
        'baseCuts' : 'AllPass',
        'resultDir' : 'results_hzz_3P1F',
        'cutModifiers' : ['HZZ2016'],
        'prereq' : 'fullSpectrum_3P1F',
        },
    'z4l' : {
        'baseCuts' : 'AllPass',
        'resultDir' : 'results_z4l',
        'cutModifiers' : ['ZMassWindow'],
        'prereq' : 'fullSpectrum',
        },
    'z4l_bkg' : {
        'baseCuts' : 'AllPass',
        'resultDir' : 'results_z4l',
        'cutModifiers' : ['ZMassWindow'],
        'prereq' : 'fullSpectrum_bkg',
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
