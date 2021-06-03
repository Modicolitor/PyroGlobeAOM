def is_ocean(context, ob):
    # if "AdvOcean" in ob.name:
    #    return True
    return ob.aom_data.is_ocean


def is_floatcage(context, ob):
    # if "FloatAnimCage" in ob.name:
    #    return True
    return ob.aom_data.is_floatcage


def is_ocean_material(context, mat):

    if 'AdvOceanMat' in mat.name:
        return True
    return False


def is_loop(context, ocean):
    return ocean.aom_data.is_loop
