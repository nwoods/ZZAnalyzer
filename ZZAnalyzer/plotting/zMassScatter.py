'''

Make a scatter plot of m_Z2 vs m_Z1.

Author: Nate Woods, U. Wisconsin

'''

from NtuplePlotter import NtuplePlotter
from ZZAnalyzer.utils.helpers import Z_MASS

from rootpy.plotting import Graph, Canvas, Legend
from rootpy.plotting.utils import draw



plotter = NtuplePlotter('zz', '',
                        {}, 
                        {'data':'/data/nawoods/ntuples/zzNtuples_data_2015silver_26jan2016_0/results_full/data*.root'}, 
                        intLumi=2619.,)


colors = {'eeee':'b','eemm':'r','mmmm':'forestgreen'}
markers = {'eeee':20,'eemm':21,'mmmm':22}
titles = {'eeee':'4\\text{e}','eemm':'2\\text{e}2\\mu','mmmm':'4\\mu'}

massVar = 'MassDREtFSR'

def getMZ1_2e2m(row):
    if abs(getattr(row, 'e1_e2_%s'%massVar) - Z_MASS) < abs(getattr(row, 'm1_m2_%s'%massVar) - Z_MASS):
        return getattr(row, 'e1_e2_%s'%massVar)
    return getattr(row, 'm1_m2_%s'%massVar)
def getMZ2_2e2m(row):
    if abs(getattr(row, 'e1_e2_%s'%massVar) - Z_MASS) < abs(getattr(row, 'm1_m2_%s'%massVar) - Z_MASS):
        return getattr(row, 'm1_m2_%s'%massVar)
    return getattr(row, 'e1_e2_%s'%massVar)

getMZ1 = {
    'eeee' : lambda row: getattr(row, 'e1_e2_%s'%massVar),
    'eemm' : getMZ1_2e2m,
    'mmmm' : lambda row: getattr(row, 'm1_m2_%s'%massVar),
}
getMZ2 = {
    'eeee' : lambda row: getattr(row, 'e3_e4_%s'%massVar),
    'eemm' : getMZ2_2e2m,
    'mmmm' : lambda row: getattr(row, 'm3_m4_%s'%massVar),
}

def selectLowMass(row):
    return row.MassDREtFSR < 110.

for ana in ['full', 'z4l']:
    
    if ana == 'z4l':
        selector = selectLowMass
    else:
        selector = lambda *args: True

    g = {}
    for ch in plotter.channels:
        g[ch] = Graph(plotter.ntuples['data']['data'][ch].GetEntries(), title=titles[ch])
        g[ch].color = colors[ch]
        g[ch].markerstyle = markers[ch]
        g[ch].drawstyle = 'P'
        g[ch].SetMarkerSize(g[ch].GetMarkerSize()*1.5)
        if ch == 'mmmm':
            g[ch].SetMarkerSize(g[ch].GetMarkerSize()*1.18)
    
    for ch in plotter.channels:
        #nWithFSR = 0
        for i, row in enumerate(plotter.ntuples['data']['data'][ch]):
            if selector(row):
                g[ch].SetPoint(i, getMZ1[ch](row), getMZ2[ch](row))
            #if row.Mass != row.MassDREtFSR:
            #    nWithFSR += 1
        #print "%s: %d / %d"%(ch, nWithFSR, int(plotter.ntuples['data']['data'][ch].GetEntries()))
    
    #for gr in g.values():
    #    gr.yaxis.SetTitleOffset(gr.yaxis.GetTitleOffset()*0.8)
    #    gr.yaxis.SetTitleSize(gr.yaxis.GetTitleSize()*0.9)
    #c.Update()

    if ana == 'z4l':
        xlimits=(40.,90.)
        ylimits=(0.,60.)
    else:
        xlimits=(40.,120.)
        ylimits=(0.,120.)


    c = Canvas(1000,1000)
    (xaxis,yaxis), things = draw(g.values(), c, xtitle='m_{Z_1} [\\text{GeV}]', 
                                 ytitle='m_{Z_2} [\\text{GeV}]',
                                 xlimits=xlimits, ylimits=ylimits)
    yaxis.SetTitleSize(yaxis.GetTitleSize()*0.9)
    c.Update()
    leg = Legend(g.values(), c, leftmargin=0.6, textsize=0.04, 
                 header='\\text{     Data}', entrysep=0.01,
                 entryheight=0.04)
    leg.Draw("same")
    plotter.style.setCMSStyle(c, "", True, "", 13, plotter.intLumi)
    
    c.Print('~/www/ZZPlots/mZ2VsmZ1_{}.png'.format(ana))
    
