from NtuplePlotter import NtuplePlotter
from ZZHelpers import Z_MASS

plotter = NtuplePlotter('zz', './plots/dataMC2015D_8oct2015', 
                        {'mc':'/data/nawoods/ntuples/zzNtuples_mc_5oct2015_0/results/*.root'}, 
                        {'data':'/data/nawoods/ntuples/zzNtuples_data_2015d_5oct2015_test_0/results/data*.root'}, 
                        intLumi=180)

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

    plotter.fullPlot('4lMassFSR%s'%chEnding, channel, 'MassFSR', '', [40, 0., 800], 
                     'mc', 'data', canvasX=1000, logy=False, xTitle="m_{%s}"%particles, 
                     outFile='m4l%s.png'%chEnding, )

plotter.fullPlot('nJets_total', 'zz', 'nJets', '', [6, -0.5, 5.5], 'mc', 'data', 
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
                 [30, 60., 120], 'mc', 'data', canvasX=1000, logy=False, xTitle="m_{Z_{1}}", 
                 outFile='mZ1.png', )
plotter.fullPlot('mZ2_total', zPlotChannels, z2PlotVariables, zPlotSelections, 
                 [30, 60., 120], 'mc', 'data', canvasX=1000, logy=False, xTitle="m_{Z_{2}}", 
                 outFile='mZ2.png', )

# ratioSample = plotter.ntuples['mc'].keys()[0]
# ratioPlot = plotter.Drawing("ratioPlot", plotter.style, 800, 1000)
# num = plotter.makeHist("mc", ratioSample, 'zz', 
#                        'MassFSR', "", [40, 0., 800.], -1., "", perUnitWidth=False)
# num.color = 'b'
# num.drawstyle = 'ep'
# ratioPlot.addObject(num, legendStyle="LPE")
# denom = plotter.makeHist("mc", ratioSample, 'zz', 
#                          'Mass', "", [40, 0., 800.], -1., "", perUnitWidth=False)
# denom.color = 'r'
# denom.drawstyle = 'ep'
# ratioPlot.addObject(denom, legendStyle="LPE")
# ratioPlot.addRatio(num, denom, 0.23)
# ratioPlot.draw(outFile="./plots/ratioTest.png", xTitle="m_{4\\ell}", 
#                xUnits="GeV", yTitle="Events", stackErr=False,
#                intLumi=-1., simOnly=True)

