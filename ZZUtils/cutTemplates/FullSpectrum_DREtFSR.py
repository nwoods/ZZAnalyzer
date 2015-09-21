
'''

Cutter for 2015 HZZ4l analysis with dR/eT^n FSR.

Author: Nate Woods, U. Wisconsin

'''

from FullSpectrum_DREtFSR_Base import FullSpectrum_DREtFSR_Base


fsrTypes = ['DREt', 'DREt15', 'DREt2', 'Et4DR01', 'Et4DR03']
isoTypes = ['', 'Iso']
dmTypes = ['', 'DM']
fsrs = ['%s%s%sFSR'%(fsr, iso, dm) for fsr in fsrTypes \
            for iso in isoTypes \
            for dm in dmTypes]
altFSR_cutters = {'FullSpectrum_'+f : type('FullSpectrum_'+f, (FullSpectrum_DREtFSR_Base,), 
                {'fsrVar' : f.replace('DMFSR','FSRDM')}) for f in fsrs}



