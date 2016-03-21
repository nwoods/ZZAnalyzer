from ResultSaverBase import ResultSaverBase
from NtupleSaver import NtupleSaver
from HistSaver import HistSaver


from ZZAnalyzer.utils.helpers import importClass
def getResultClass(result):
    '''
    Get a result saver class.
    '''
    return importClass(result, 'result')
