''' ShadowHunterRUS 2015-2016 '''



#####################################################################
# imports

from mathutils import Vector



#####################################################################
# functions

def AsVector(vector_str):
    return Vector(tuple(map(float, vector_str.strip().split())))



def AsBool(bool_str):
    if 'true' in bool_str.lower():
        return True
    return False



def AsInt(int_str):
    int_str = int_str.strip()
    if int_str.isdigit():
        return int(int_str)
    raise Exception('[AsInt]: %s' % int_str)



def AsFloat(float_str):
    return float(float_str.strip())
