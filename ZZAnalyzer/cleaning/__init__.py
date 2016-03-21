from RowCleanerBase import RowCleanerBase


from ZZAnalyzer.utils.helpers import importClass
def getCleanerClass(name):
    return importClass(name, 'clean')
