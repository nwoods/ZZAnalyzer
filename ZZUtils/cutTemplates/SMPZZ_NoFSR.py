
'''

13 TeV Standard Model ZZ analysis without FSR

Author: Nate Woods, U. Wisconsin

'''

from SMPZZ_FullFSR_Sync import SMPZZ_FullFSR_Sync


class SMPZZ_NoFSR(SMPZZ_FullFSR_Sync):
    fsrVar = ''
