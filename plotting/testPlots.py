from NtuplePlotter import NtuplePlotter
from ZZHelpers import Z_MASS

plotter = NtuplePlotter('zz', './plots/dataPlots50ns', 
                        '/data/nawoods/ntuples/zzNtuples50nsFinal/results/[ZDGW]*.root', 
                        '/data/nawoods/ntuples/zzNtuples50nsFinal/results/data*.root', 40.03)

fnames = plotter.getFileNamesFromStr('/data/nawoods/data*.root')

plotter.fullPlot('4lMassFSR_total', 'zz', 'MassFSR', '', 30, 0., 600, 
                 logy=False, xTitle="m_{4\\ell}", outFile='m4l.png', )
plotter.fullPlot('nJets_total', 'zz', 'nJets', '', 6, -0.5, 5.5, logy=False, 
                 xTitle="\\sharp \\text{Jets}", xUnits="",outFile='nJets.png', )

zPlotChannels = ['eeee', 'eemm', 'eemm', 'mmmm']
z1PlotVariables = ['e1_e2_MassFSR', 'e1_e2_MassFSR', 
                   'm1_m2_MassFSR', 'm1_m2_MassFSR']
z2PlotVariables = ['e3_e4_MassFSR', 'm1_m2_MassFSR', 
                   'e1_e2_MassFSR', 'm3_m4_MassFSR']
zPlotSelections = ['', 'abs(e1_e2_MassFSR-%f) < abs(m1_m2_MassFSR-%f)'%(Z_MASS, Z_MASS), 
                   'abs(m1_m2_MassFSR-%f) < abs(e1_e2_MassFSR-%f)'%(Z_MASS, Z_MASS), '']

plotter.fullPlot('mZ1_total', zPlotChannels, z1PlotVariables, zPlotSelections, 
                 30, 60., 120, logy=False, xTitle="m_{Z_{1}}", outFile='mZ1.png', )
plotter.fullPlot('mZ2_total', zPlotChannels, z2PlotVariables, zPlotSelections, 
                 30, 60., 120, logy=False, xTitle="m_{Z_{2}}", outFile='mZ2.png', )
