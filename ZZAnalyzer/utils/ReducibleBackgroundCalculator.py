#############################################################################
#                                                                           #
#    ReducibleBackgroundCalculator.py                                       #
#                                                                           #
#    Some tools for finding ZZ reducible backgrounds                        #
#                                                                           #
#    Author: Nate Woods, U. Wisconsin                                       #
#                                                                           #
#############################################################################



# include logging stuff first so other imports don't babble at us
import logging
from rootpy import log as rlog; rlog = rlog["/ReducibleBackgroundCalculator"]
# don't show most silly ROOT messages
logging.basicConfig(level=logging.WARNING)
rlog["/ROOT.TH1F.Add"].setLevel(rlog.ERROR)
rlog["/rootpy.compiled"].setLevel(rlog.WARNING)

from WeightStringMaker import WeightStringMaker

from rootpy.io import root_open
import rootpy.compiled as ROOTComp

import os

assert os.environ['zza'], "Please run setup.sh before doing anything."



class BkgManager(object):
    def __init__(self, fakeRateVersion):
        '''
        fakeRateVersion is the identifier (date, etc.) for the desired fake
        rates. Fake rates will be taken from 
        data/leptonFakeRate/fakeRate_2015gold_[fakeRateVersion].py
        '''
        self.version = fakeRateVersion
        self.frFileName = os.path.join(os.environ['zza'], 'ZZAnalyzer',
                                       'data', 'leptonFakeRate',
                                       'fakeRate_2015gold_{0}.root'
                                       ).format(self.version)
        self.frFile = root_open(self.frFileName)
        self.fakeRates = {
            'e' : self.frFile.e_FakeRate.clone(),
            'm' : self.frFile.m_FakeRate.clone(),
            }
        wts = WeightStringMaker('bkgWeight')
        self.fakeRateStrs = {
            lep : wts.makeWeightStringFromHist(h,
                                               '{0}Pt', 'abs({0}Eta)'
                                               ) for lep, h in self.fakeRates.iteritems()
            }

        self.compile()


    def compile(self):
        ROOTComp.register_code(___FRCodeToCompile___, 
                               ['lepFakeFactor',
                                'lepFakeFactorAdditive'])
        
        # force system to compile code now
        arglebargle = getattr(ROOTComp, 'lepFakeFactor')

        self.singleLepWeightTemp = ('(lepFakeFactor({f}, '
                                    '{{0}}ZZTightID, '
                                    '{{0}}ZZIsoPass))')

        self.zTemps = {
            lep : '*'.join([
                    self.singleLepWeightTemp.format(f=self.fakeRateStrs[lep]),
                    self.singleLepWeightTemp.format(
                        f=self.fakeRateStrs[lep]).format('{1}'),
                    ]) for lep in ['e','m']
            }

        self.corCondition = (
            '((({{0}}ZZTightID + {{0}}ZZIsoPass + '
            '   {{1}}ZZTightID + {{1}}ZZIsoPass) < 4.) && '
            ' {{0}}_{{1}}_DR < 0.6 ? {0} : 1.)'
            )
        self.corStrTemp3P1F = self.corCondition.format(0.)
        self.corStrTemp2P2F = self.corCondition.format(-1.)

        # To find 2P2F contribution to 3P1F region, we need F1+F2 instead of 
        # F1*F2, so the 'identity' (for tight leptons) needs to be 0
        self.singleLepWeightTempAdditive = ('(lepFakeFactorAdditive({f}, '
                                            '{{0}}ZZTightID, '
                                            '{{0}}ZZIsoPass))')

        self.zTempsAdditive = {
            lep : '(' + ('+'.join([
                        self.singleLepWeightTempAdditive.format(
                            f=self.fakeRateStrs[lep]
                            ),
                        self.singleLepWeightTempAdditive.format(
                            f=self.fakeRateStrs[lep]
                            ).format('{1}'),
                        ])) + ')' for lep in ['e','m']
            }


    def z1String3P1F(self, lep, correct=True):
        out = self.zTemps[lep]
        if correct:
            out = '*'.join([out, self.corStrTemp3P1F])
        return out.format(lep+'1', lep+'2')

    def z2String3P1F(self, lep, correct=True):
        out = self.zTemps[lep]
        if correct:
            out = '*'.join([out, self.corStrTemp3P1F])
        return out.format(lep+'3', lep+'4')

    def z1String2P2F(self, lep, correct=True):
        out = self.zTemps[lep]
        if correct:
            out = '*'.join([out, self.corStrTemp2P2F])
        return out.format(lep+'1', lep+'2')

    def z2String2P2F(self, lep, correct=True):
        out = self.zTemps[lep]
        if correct:
            out = '*'.join([out, self.corStrTemp2P2F])
        return out.format(lep+'3', lep+'4')

    def fullString3P1F(self, channel, correct=True):
        if channel == 'zz':
            return [self.fullString3P1F(c, correct) for c in ['eeee',
                                                              'eemm',
                                                              'mmmm']
                    ]
            
        if isinstance(channel, list):
            return [self.fullString3P1F(c, correct) for c in channel]            

        if channel == 'eeee':
            return '*'.join([self.z1String3P1F('e', correct),
                             self.z2String3P1F('e', correct)])
            
        if channel == 'eemm':
            return '*'.join([self.z1String3P1F('e', correct),
                             self.z1String3P1F('m', correct)])
            
        return '*'.join([self.z1String3P1F('m', correct),
                         self.z2String3P1F('m', correct)])
            
    def fullString2P2F(self, channel, correct=True):
        if channel == 'zz':
            return [self.fullString2P2F(c, correct) for c in ['eeee',
                                                              'eemm',
                                                              'mmmm']
                    ]
            
        if isinstance(channel, list):
            return [self.fullString2P2F(c, correct) for c in channel]            

        if channel == 'eeee':
            return '*'.join([self.z1String2P2F('e', correct),
                             self.z2String2P2F('e', correct)])
            
        if channel == 'eemm':
            return '*'.join([self.z1String2P2F('e', correct),
                             self.z1String2P2F('m', correct)])
            
        return '*'.join([self.z1String2P2F('m', correct),
                         self.z2String2P2F('m', correct)])

    def z1String2P2FMigration(self, lep, correct=True):
        '''
        To find 2P2F contribution to 3P1F instead of SR.
        '''
        out = self.zTempsAdditive[lep]
        # collinear correction as 3P1F
        if correct:
            out = '*'.join([out, self.corStrTemp3P1F])
        return out.format(lep+'1', lep+'2')

    def z2String2P2FMigration(self, lep, correct=True):
        '''
        To find 2P2F contribution to 3P1F instead of SR.
        '''
        out = self.zTempsAdditive[lep]
        # collinear correction as 3P1F
        if correct:
            out = '*'.join([out, self.corStrTemp3P1F])
        return out.format(lep+'3', lep+'4')

    def fullString2P2FMigration(self, channel, correct=True):
        '''
        To find 2P2F contribution to 3P1F instead of SR.
        '''
        if channel == 'zz':
            return [self.fullString2P2FMigration(c, correct) for c in ['eeee',
                                                                       'eemm',
                                                                       'mmmm']
                    ]
            
        if isinstance(channel, list):
            return [self.fullString2P2FMigration(c, correct) for c in channel]

        if channel == 'eeee':
            return '(' + ('+'.join([self.z1String2P2FMigration('e', correct),
                                    self.z2String2P2FMigration('e', correct)])
                          ) + ')'
            
        if channel == 'eemm':
            return '(' + ('+'.join([self.z1String2P2FMigration('e', correct),
                                    self.z1String2P2FMigration('m', correct)])
                          ) + ')'
            
        return '(' + ('*'.join([self.z1String2P2FMigration('m', correct),
                                self.z2String2P2FMigration('m', correct)])
                      ) + ')'



___FRCodeToCompile___ = '''
double lepFakeFactor(double f, double passID, double passIso)
{
  if((passID + passIso) > 1.5) 
    return 1.;

  double out = f / (1. - f);
  return out;
}

// To find the 2P2F contribution to the 3P1F region, we want (F1+F2)
// instead of (F1*F2), so the "identity" (for passing leptons) becomes 0
double lepFakeFactorAdditive(double f, double passID, double passIso)
{
  if((passID + passIso) > 1.5) 
    return 0.;

  double out = f / (1. - f);
  return out;
}
'''


class BkgManagerFactorized(object):
    def __init__(self, fakeRateVersion):
        '''
        fakeRateVersion is the identifier (date, etc.) for the desired fake
        rates. Fake rates will be taken from 
        data/leptonFakeRate/fakeRate_2015gold_[fakeRateVersion]_[ID/Iso].py
        '''
        self.version = fakeRateVersion
        fileBase = os.path.join(os.environ['zza'], 'ZZAnalyzer',
                                'data', 'leptonFakeRate',
                                'fakeRate_2015gold_{0}_{{0}}.root'
                                ).format(self.version)
        self.fileNames = { t : fileBase.format(t) for t in ['ID', 'Iso'] }
        self.saved = [] # objects we need to persistify somehow
        self.fakeRates = { 
            t : self.makeFakeRates(f) for t,f in self.fileNames.iteritems()
            }

        wts = WeightStringMaker('bkgWeight')
        self.fakeRateStrs = {
            t : { 
                lep : wts.makeWeightStringFromHist(fr, 
                                                   '{0}Pt', 'abs({0}Eta)'
                                                   ) for lep, fr in frs.iteritems()
                } for t, frs in self.fakeRates.iteritems()
            }

        self.compile()

    def makeFakeRates(self, f):
        '''
        Take the name of a fake rate file, return a dict with 'e' and 'm' 
        fake rates.
        '''
        fi = root_open(f)
        self.saved.append(fi)
        out = {}
        for lep in ['e','m']:
            self.saved.append(fi.Get('{}_FakeRate'.format(lep)).clone())
            out[lep] = self.saved[-1]

        return out

    def compile(self):
        '''
        Compile the ROOT C macros needed for applying fake rates,
        put together the strings to apply them.
        '''
        ROOTComp.register_code(___FRCodeToCompileFactorized___, 
                               ['overlapArea', 'isoNoOverlap', 
                                'lepFakeFactor', 'zFakeFactorGeom'])
        
        # force system to compile code now
        arglebargle = getattr(ROOTComp, 'lepFakeFactor')

        self.singleLepWeightTemp = ('lepFakeFactor({fID}, '
                                    '{{0}}ZZTightID > 0.5, '
                                    '{fIso}, {{0}}ZZIsoPass > 0.5)')

        self.zTemps = {
            lep : '*'.join([
                    self.singleLepWeightTemp.format(
                        fID=self.fakeRateStrs['ID'][lep],
                        fIso=self.fakeRateStrs['Iso'][lep]),
                    self.singleLepWeightTemp.format(
                        fID=self.fakeRateStrs['ID'][lep],
                        fIso=self.fakeRateStrs['Iso'][lep]).format('{1}')
                    ]) for lep in ['e','m']
            }

        self.zWeightTempCor = (
            'zFakeFactorGeom({fID0}, {{0}}ZZTightID > 0.5, '
            '{fIso0}, {{0}}ZZIsoFSR, {{0}}Pt, '
            '{fID1}, {{1}}ZZTightID > 0.5, {fIso1}, '
            '{{1}}ZZIsoFSR, {{1}}Pt, {{0}}_{{1}}_DR)'
            )

        self.zTempsCor = {
            lep : self.zWeightTempCor.format(
                fID0=self.fakeRateStrs['ID'][lep],
                fIso0=self.fakeRateStrs['Iso'][lep],
                fID1=self.fakeRateStrs['ID'][lep].format('{1}'),
                fIso1=self.fakeRateStrs['Iso'][lep].format('{1}')
                ) for lep in ['e','m']
            }

    def z1String3P1F(self, lep, *args):
        return self.zTemps[lep].format(lep+'1', lep+'2')

    def z2String3P1F(self, lep, *args):
        return self.zTemps[lep].format(lep+'3', lep+'4')

    def z1String2P2F(self, lep, correct=True):
        if correct:
            return self.zTempsCor[lep].format(lep+'1', lep+'2')
        return self.zTemps[lep].format(lep+'1', lep+'2')

    def z2String2P2F(self, lep, correct=True):
        if correct:
            return self.zTempsCor[lep].format(lep+'3', lep+'4')
        return self.zTemps[lep].format(lep+'3', lep+'4')

    def fullString3P1F(self, channel, *args):
        if channel == 'zz':
            return '*'.join(
                self.fullString3P1F(c, *args) for c in ['eeee','eemm','mmmm'])

        if channel == 'eeee':
            return '*'.join([self.z1String3P1F('e', *args),
                             self.z2String3P1F('e', *args)])
            
        if channel == 'eemm':
            return '*'.join([self.z1String3P1F('e', *args),
                             self.z1String3P1F('m', *args)])
            
        return '*'.join([self.z1String3P1F('m', *args),
                         self.z2String3P1F('m', *args)])
            
    def fullString2P2F(self, channel, correct=True):
        if channel == 'zz':
            return [self.fullString2P2F(c, correct) for c in ['eeee',
                                                              'eemm',
                                                              'mmmm']
                    ]
            
        if isinstance(channel, list):
            return [self.fullString2P2F(c, correct) for c in channel]            

        if channel == 'eeee':
            return '*'.join([self.z1String2P2F('e', correct),
                             self.z2String2P2F('e', correct)])
            
        if channel == 'eemm':
            return '*'.join([self.z1String2P2F('e', correct),
                             self.z1String2P2F('m', correct)])
            
        return '*'.join([self.z1String2P2F('m', correct),
                         self.z2String2P2F('m', correct)])



___FRCodeToCompileFactorized___ = '''
#include "TMath.h"

double lepFakeFactor(double fID, bool passID, double fIso, bool passIso)
{
  if(passID)
    {
      if(passIso)
        return 1.;
      fID = 1.;
    }
  if(passIso)
    fIso = 1.;

  double f = fID * fIso;

  return f / (1. - f);
}

double overlapArea(double dR, double R=0.3)
{
  double t1 = 2. * R * R * TMath::ACos(dR / (2 * R));
  double t2 = 0.5 * dR * TMath::Sqrt(4 * R * R - dR * dR);

  return t1 - t2;
}

double isoNoOverlap(double iso1, double iso2, double dR, double R=0.3)
{
  double overlap = overlapArea(dR, R);
  double area = TMath::Pi() * R * R;
  
  double num = iso1 - iso2 * overlap / area;
  double denom = 1. - overlap * overlap / area / area;

  return num / denom;
}

double zFakeFactorGeom(double fID1, bool passID1, 
                       double fIso1, double relIso1, double pt1,
                       double fID2, bool passID2, 
                       double fIso2, double relIso2, double pt2,
                       double dR,
                       double relIsoCut=0.35, double R=0.3)
{
  bool passIso1 = relIso1 < relIsoCut;
  bool passIso2 = relIso2 < relIsoCut;

  if(passID1 && passIso1 && passID2 && passIso2)
    return 1.;

  if(dR > 2. * R || (passIso1 && passIso2))
    return (lepFakeFactor(fID1, passID1, fIso1, passIso1) *
            lepFakeFactor(fID2, passID2, fIso2, passIso2));

  double iso1 = relIso1 * pt1;
  double iso2 = relIso2 * pt2;

  double ownIso1 = isoNoOverlap(iso1, iso2, dR, R);
  double ownIso2 = iso1 + iso2 - ownIso1;
  
  bool passOwnIso1 = (ownIso1 / pt1) < relIsoCut;
  bool passOwnIso2 = (ownIso2 / pt2) < relIsoCut;

  double fFact = (lepFakeFactor(fID1, passID1, fIso1, passOwnIso1) *
                  lepFakeFactor(fID2, passID2, fIso2, passOwnIso2));

  if((passID1 && (passOwnIso1 && (!passIso1))) != 
     (passID2 && (passOwnIso2 && (!passIso2)))) // xor
    fFact *= -1.;

  return fFact;
}
                       

'''


















