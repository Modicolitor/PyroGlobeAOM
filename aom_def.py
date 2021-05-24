def is_ocean(context, ob):
    if "AdvOcean" in ob.name:
        return True
    return False


def is_floatcage(context, ob):
    if "floatcage" in ob.name:
        return True
    return False


def is_ocean_material(context, mat):

    if 'AdvOceanMat' in mat.name:
        return True
    return False
