'''

Useful helper functions used everywhere in this analyzer.

Author: N. Woods, U. Wisconsin

'''


def evVar(row, var):
    '''
    Get variable from final state
    '''
    return getattr(row,var)


def objVar(row, var, obj):
    '''
    Get variable associated with single object
    '''
    return getattr(row, obj+var)


def nObjVar(row, var, *obj):
    '''
    Get an n object composite variable
    Works for 0 or 1 object too, but the other Var functions are faster for those
    '''
    return getattr(row, '_'.join([o for o in obj]+[var]))


