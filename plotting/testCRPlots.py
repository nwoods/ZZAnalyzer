from NtuplePlotter import NtuplePlotter
from ZZHelpers import Z_MASS

plotters = {}
crs = ['SS', '3P1F', '2P2F']

for cr in crs:

    plotters[cr] = NtuplePlotter('zz', './plots/mcPlots25ns_anDraft/CR_%s'%cr,
                                 '/data/nawoods/ntuples/zzNtuples25ns_anDraft_0/results_CR_%s/*.root'%cr, 
                                 '/data/nawoods/ntuples/zzNtuples25ns_anDraft_0/results_CR_%s/data*.root'%cr, 1000.)

    for channel in ['zz', 'eeee', 'eemm', 'mmmm']:

        chdir = "_%s"%channel
        if channel == 'zz':
            chdir = ''

        plotters[cr].fullPlot('4lMassFSR_total', channel, 'MassFSR', '', 40, 0., 800, 
                              canvasX=1000, logy=False, xTitle="m_{4\\ell}", 
                              outFile='m4l%s.png'%chdir, )
        plotters[cr].fullPlot('nJets_total', channel, 'nJets', '', 8, -0.5, 7.5, canvasX=1000, 
                              logy=False, xTitle="\\text{#Jets}", xUnits="",
                              outFile='nJets%s.png'%chdir,
                              # legParams={'leftmargin':0.6,'rightmargin':0.03,'textsize':0.023,
                              #            'entryheight':0.023,'entrysep':0.006} 
                              )

# zPlotChannels = ['eeee', 'eemm', 'eemm', 'mmmm']
# z1PlotVariables = ['e1_e2_MassFSR', 'e1_e2_MassFSR', 
#                    'm1_m2_MassFSR', 'm1_m2_MassFSR']
# z2PlotVariables = ['e3_e4_MassFSR', 'm1_m2_MassFSR', 
#                    'e1_e2_MassFSR', 'm3_m4_MassFSR']
# zPlotSelections = ['', 'abs(e1_e2_MassFSR-%f) < abs(m1_m2_MassFSR-%f)'%(Z_MASS, Z_MASS), 
#                    'abs(m1_m2_MassFSR-%f) < abs(e1_e2_MassFSR-%f)'%(Z_MASS, Z_MASS), '']
# 
# plotter.fullPlot('mZ1_total', zPlotChannels, z1PlotVariables, zPlotSelections, 
#                  30, 60., 120, logy=False, xTitle="m_{Z_{1}}", outFile='mZ1.png', )
# plotter.fullPlot('mZ2_total', zPlotChannels, z2PlotVariables, zPlotSelections, 
#                  30, 60., 120, logy=False, xTitle="m_{Z_{2}}", outFile='mZ2.png', )
