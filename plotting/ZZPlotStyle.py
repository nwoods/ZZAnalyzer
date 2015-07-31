'''

Make plots not look like crap without messing around with rootlogon.C or similar.

Author: Nate Woods, U. Wisconsin

'''

from ROOT import gROOT, gStyle, EColor, kTRUE, TGaxis, TH1, TPad, THStack, TLatex
import tdrstyle, CMS_lumi
from ZZHelpers import makeNumberPretty


gROOT.SetBatch(kTRUE)


class ZZPlotStyle(object):
    '''
    A class for making plots look decent. Sets up gStyle, adds garnishes like text boxes.
    '''
    def __init__(self):
        '''
        Set up ZZPlotStyle, set gStyle for things we always want no matter what.
        '''
        # CMS-approved everything
        tdrstyle.setTDRStyle()

        ### Differences from TDR standard:

        # Big canvas (can always shrink later)
        gStyle.SetCanvasDefH(1200)
        gStyle.SetCanvasDefW(1200)

        # Tick marks on all sides
        gStyle.SetPadTickX(1)
        gStyle.SetPadTickY(1)
    
        # Everything has white backgrounds
        gStyle.SetLegendFillColor(0)

        # Colors that don't suck
        gStyle.SetPalette(1)

        # Make axis title and labels just a little smaller and (for Y) closer to the axis
        gStyle.SetTitleSize(0.04, "XYZ")
        gStyle.SetLabelSize(0.03, "XYZ")
        gStyle.SetTitleYOffset(1.25)
#        gStyle.SetTitleXOffset(0.85)
        gStyle.SetPadLeftMargin(0.1)
        gStyle.SetPadRightMargin(0.025)
        gStyle.SetPadBottomMargin(0.082)
        gStyle.SetTitleAlign(12)

        # Apply changes
        gROOT.ForceStyle()

        # Force exponentials when axes are over 3 digits
        TGaxis.SetMaxDigits(3)
        TGaxis.SetExponentOffset(-0.060, 0.008, "y")
        TGaxis.SetExponentOffset(-0.055, -0.062, "x") # will overlap with title unless title is centered


    def setCMSStyle(self, canvas, author='N. Woods', textRight=True, dataType='Preliminary Simulation', energy=13, intLumi=19710.):
        '''
        Set plotting defaults to something appropriate for CMS Analysis Notes
        intLumi is given in pb^-1 and converted to fb^-1, unless it is less than 1 fb^-1
        '''
        # Make sure that if there's an exponent on the X axis, it's visible but not on top of the axis title
        self.fixXExponent(canvas)
        
        # Put "Preliminary" or similar on the plots
        if dataType:
            CMS_lumi.relPosX = 0.12
            CMS_lumi.extraText = dataType
        else:
            CMS_lumi.writeExtraText = False

        # Put sqrt(s) on plots
        if type(energy) == int:
            energy = [energy]
        assert type(energy) == list, "Energy must be an integer or list of integers"
        if type(intLumi) == float:
            intLumi = [intLumi]
        assert type(intLumi) == list, "Integrated Luminosity must be a float  or list of floats"
        assert len(intLumi) == len(energy), "Must have exactly one integrated luminosity per energy"

        iPeriod = 0
        for i, e in enumerate(energy):
            iL = intLumi[i]
            if iL >= 1000:
                iL /= 1000 # convert to fb^-1
                unit = "fb"
            else:
                unit = "pb"
            iLStr = makeNumberPretty(iL, 2)

            if e == 13:
                iPeriod += 4
                CMS_lumi.lumi_13TeV = CMS_lumi.lumi_13TeV.replace("20.1","%s"%iLStr).replace("fb", unit)
            elif energy == 8:
                iPeriod += 2
                CMS_lumi.lumi_8TeV = CMS_lumi.lumi_8TeV.replace("19.7","%.1f"%iLStr).replace("fb", unit)
            if energy == 7:
                iPeriod += 1
                CMS_lumi.lumi_7TeV = CMS_lumi.lumi_7TeV.replace("5.1","%.1f"%iLStr).replace("fb", unit)
                
        # Put "CMS preliminary simulation" or whatever above the left side of the plot
        iPos = 0

        # Draw all that stuff
        CMS_lumi.CMS_lumi(canvas, iPeriod, iPos)

        # Put author name and "Preliminary Exam" and a box in the top right corner of the frame
        latex = TLatex()
        latex.SetNDC()
        latex.SetTextAngle(0)
        latex.SetTextColor(EColor.kBlack)
        latex.SetTextFont(61)
        latex.SetTextSize(0.03)
        latex.SetTextAlign(12)
        latex.DrawLatex(0.01, 0.05, author)
#        latex.DrawLatex(0.01, 0.02, "U. Wisconsin Preliminary Exam")
        
#         # Make frame and tick marks thicker
#         gStyle.SetFrameLineWidth(3)
#         gStyle.SetLineWidth(3)


    def fixXExponent(self,canvas):
        '''
        If there's an exponent on the Y axis, it will either be in a weird 
        place or it will overlap with the axis title. We fix the placement in
        __init__(), but we still have to move the title if need be.        
        Recursive, so we find histograms in pads in pads.
        '''
        for obj in canvas.GetListOfPrimitives():
            if obj.InheritsFrom(TH1.Class()) or obj.InheritsFrom(THStack.Class()):
                axis = obj.GetXaxis()
                if axis.GetXmax() >= 10**TGaxis.GetMaxDigits():
                    # has exponent
                    axis.CenterTitle()
            if obj.InheritsFrom(TPad.Class()):
                self.fixXExponent(obj)



















