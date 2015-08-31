from NtuplePlotter import NtuplePlotter
from ZZHelpers import Z_MASS

plotter = NtuplePlotter('zz', './plots/mcPlots25ns_anDraft', 
                        '/data/nawoods/ntuples/zzNtuples25ns_anDraft_0/results/*.root', 
                        '/data/nawoods/ntuples/zzNtuples25ns_anDraft_0/results/data*.root', intLumi=1000)

for channel in ['eeee', 'zz', 'eemm', 'mmmm']:

    chEnding = ''
    if channel != 'zz':
        chEnding = '_%s'%channel
    if channel == 'zz':
        particles = '4\\ell'
    elif channel == 'eeee':
        particles = '4e'
    elif channel == 'eemm':
        particles = '2e2\\mu'
    elif channel == 'mmmm':
        particles = '4\\mu'

    plotter.fullPlot('4lMassFSR%s'%chEnding, channel, 'MassFSR', '', 40, 0., 800, 
                     canvasX=1000, logy=False, xTitle="m_{%s}"%particles, 
                     outFile='m4l%s.png'%chEnding, )

plotter.fullPlot('nJets_total', 'zz', 'nJets', '', 6, -0.5, 5.5, 
                 canvasX=1000, logy=False, xTitle="\\text{#Jets}", xUnits="",
                 outFile='nJets.png')

zPlotChannels = ['eeee', 'eemm', 'eemm', 'mmmm']
z1PlotVariables = ['e1_e2_MassFSR', 'e1_e2_MassFSR', 
                   'm1_m2_MassFSR', 'm1_m2_MassFSR']
z2PlotVariables = ['e3_e4_MassFSR', 'm1_m2_MassFSR', 
                   'e1_e2_MassFSR', 'm3_m4_MassFSR']
zPlotSelections = ['', 'abs(e1_e2_MassFSR-%f) < abs(m1_m2_MassFSR-%f)'%(Z_MASS, Z_MASS), 
                   'abs(m1_m2_MassFSR-%f) < abs(e1_e2_MassFSR-%f)'%(Z_MASS, Z_MASS), '']

plotter.fullPlot('mZ1_total', zPlotChannels, z1PlotVariables, zPlotSelections, 
                 30, 60., 120, canvasX=1000, logy=False, xTitle="m_{Z_{1}}", 
                 outFile='mZ1.png', )
plotter.fullPlot('mZ2_total', zPlotChannels, z2PlotVariables, zPlotSelections, 
                 30, 60., 120, canvasX=1000, logy=False, xTitle="m_{Z_{2}}", 
                 outFile='mZ2.png', )
