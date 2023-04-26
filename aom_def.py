def is_ocean(context, ob):
    if hasattr(ob, "aom_data"):
        return ob.aom_data.is_ocean
    return False


def is_floatcage(context, ob):
    # if "FloatAnimCage" in ob.name:
    #    return True
    return ob.aom_data.is_floatcage


def is_collision(context, ob):
  
    return ob.aom_data.is_collision

def is_collision_in_name(context, ob):
    
    if 'collision' in ob.name or 'COLLISION' in ob.name  or 'Collision' in ob.name :
        return True
    return False

def is_ocean_material(context, mat):

    if 'AdvOceanMat' in mat.name:
        return True
    return False


def is_loop(context, ocean):
    return ocean.aom_data.is_loop
