def is_ocean(ob):
    if "AdvOcean" in ob.name:
        return True
    return False


def is_floatcage(context, ob):
    if "floatcage" in ob.name:
        return True
    return False
