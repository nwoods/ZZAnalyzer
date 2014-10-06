'''

Fast hack to make a muon isolation efficincy plot.

Nate Woods, U. Wisconsin

'''

import ROOT
import array

ROOT.gROOT.SetBatch(ROOT.kTRUE)
ROOT.gStyle.SetOptStat(0)
ROOT.gROOT.ForceStyle()

f = ROOT.TFile("/home/nwoods/UWCMS/ZZ/ntuples/8TeV/ZZTo4mu_8TeV-powheg-pythia6.root") #ZZTo4L_Tune4C_13TeV-powheg-pythia8_Spring14miniaod_PU20bx25.root") #GluGluToHToZZTo4L_M-125_13TeV-powheg-pythia6_Spring14miniaod_PU20bx25.root")
t = f.Get("mmmm/final/Ntuple")

objects = ['m%d'%(i+1) for i in range(4)]

nums = []
denoms = []

for ob in objects:
    if ob[1] == '1' or ob[1] == '2':
        zmassStr = "&&m1_m2_SS==0&&m1_m2_Mass<120&&m1_m2_Mass>60"
    if ob[1] == '3' or ob[1] == '4':
        zmassStr = "&&m3_m4_SS==0&&m3_m4_Mass<120&&m3_m4_Mass>60"
    t.Draw("nvtx>>h%sDenom(20, 0., 40.)"%(ob), "%sPt>5.&&fabs(%sEta)<2.4&&(%sIsGlobal||%sIsTracker)&&abs(%sGenPdgId)==13%s&&%sComesFromHiggs==0"%(ob,ob,ob,ob,ob,zmassStr,ob), "goff")
    t.Draw("nvtx>>h%sNum(20, 0., 40.)"%(ob), "%sPt>5.&&fabs(%sEta)<2.4&&(%sIsGlobal||%sIsTracker)&&abs(%sGenPdgId)==13%s&&%sComesFromHiggs==0&&%sRelPFIsoDBDefault<0.4"%(ob,ob,ob,ob,ob,zmassStr,ob,ob), "goff")
    #%sSIP3D<4.&&
    nums.append(ROOT.gDirectory.Get("h%sNum"%ob))
    denoms.append(ROOT.gDirectory.Get("h%sDenom"%ob))

num = nums[0].Clone("numerator")
for h in nums[1:]:
    num.Add(h) 
denom = denoms[0].Clone("denominator")
for h in denoms[1:]:
    denom.Add(h) 

saveFile = ROOT.TFile("/home/nwoods/UWCMS/ZZ/ZZAnalyzer/plots/SMPCombo_summary/isoEffNVtx_8TeV.root","RECREATE")

newbins = array.array('d', [i for i in range(0,28,3)]+[33, 40])

num.Sumw2()
denom.Sumw2()

num = num.Rebin(len(newbins)-1, '', newbins)
denom = denom.Rebin(len(newbins)-1, '', newbins)

num.Sumw2()
denom.Sumw2()

eff = ROOT.TGraphAsymmErrors(num, denom)

eff.SetMarkerStyle(20)
eff.SetLineColor(ROOT.EColor.kBlack)
eff.SetMarkerColor(ROOT.EColor.kBlack)
c = ROOT.TCanvas("foo","foo",1000,1000)

#c.SetLogx()

frame = ROOT.TH1F("frame", "frame", len(newbins)-1, newbins)
frame.SetTitle("ZZ->4#mu Isolation efficiency")
frame.GetXaxis().SetTitle("No. Primary Vertices")
frame.GetYaxis().SetTitle("Iso < 0.4 Efficiency")

frame.Draw()
eff.Draw("PE1")

c.Print("/home/nwoods/UWCMS/ZZ/ZZAnalyzer/plots/4muIsoEff_nvtx_8TeV.png")

saveFile.Write()












