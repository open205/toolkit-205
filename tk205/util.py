from numbers import Number
from math import isclose


def objects_near_equal(object1, object2, rel_tol=1e-9, abs_tol=0.0):
    if type(object1) != type(object2):
        if not isinstance(object1, Number) or not isinstance(object2, Number):
            return False
    if isinstance(object1, dict):
        if len(object1) != len(object2):
            return False
        for key in object1:
            if key not in object2:
                return False
            if not objects_near_equal(object1[key], object2[key], rel_tol=rel_tol, abs_tol=abs_tol):
                return False
    elif isinstance(object1, list):
        if len(object1) != len(object2):
            return False
        for index_item in enumerate(object1):
            if not objects_near_equal(object1[index_item[0]], object2[index_item[0]], rel_tol=rel_tol, abs_tol=abs_tol):
                return False
    elif isinstance(object1, Number):
        if not isclose(object1, object2, rel_tol=rel_tol, abs_tol=abs_tol):
            return False
    else:
        if not (object1 == object2):
            return False
    return True


def iterdict(d, dict_as_list, level=0):
    for key in d:
        preamble = 'Level ' + str(level) + ' ' + '  '*level + ' ' + key
        if isinstance(d[key], dict):
            dict_as_list.append(preamble + ': [dict]')
            iterdict(d[key], dict_as_list, level+1)
        else:
            dict_as_list.append(preamble + ': ' + str(d[key]))

