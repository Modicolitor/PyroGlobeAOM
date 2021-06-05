import bpy


class AOMGeoNodesHandler:
    def __init__(self, context):
        self.context = context

    def new_geonodes_mod(self, ocean):
        mod = ocean.modifiers.new(name="GeoNode", type="NODES")
        node_group = mod.node_group

        return mod, node_group

    # def make_geonodes(self, ob):

    def move_mod_one_up(self, ocean, mod):
        n = len(ocean.modifiers)
        if n-2 >= 0:
            bpy.ops.object.modifier_move_to_index(modifier=mod.name, index=n-2)
        else:
            bpy.ops.object.modifier_move_to_index(modifier=mod.name, index=0)

    def new_spray(self, context, ocean):
        # make mod and name
        mod, nodegroup = self.new_geonodes_mod(ocean)
        mod.name = "Spray"
        nodegroup.name = "Spray"
        self.move_mod_one_up(ocean, mod)
        self.make_spray_nodes(mod.node_group)

    def make_spray_nodes(self, node_group):
        nodes = node_group.nodes
        links = node_group.links

    def remove_spray(self, context, ocean):
        if "Spray" in ocean.modifiers:
            ocean.modifiers.remove(ocean.modifiers['Spray'])
