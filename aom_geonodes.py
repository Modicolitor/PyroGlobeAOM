import bpy


class AOMGeoNodesHandler:
    def __init__(self, context):
        self.context = context

    def new_geonodes_mod(self, ocean):
        mod = ocean.modifiers.new(name="GeoNode", type="NODES")
        node_group = mod.node_group

        return mod, node_group

    def remove_nodes(self, node_group):
        nodes = node_group.nodes
        for n in nodes:
            nodes.remove(n)

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
        self.remove_nodes(node_group)
        nodes = node_group.nodes
        links = node_group.links

        node = nodes.new("NodeGroupInput")

        node.name = "Group Input"
        node.location = (-710, 65)
        node.outputs.new("NodeSocketGeometry", "Geometry")
        node.outputs.new("NodeSocketFloat", "Density Max")
        node.outputs.new("NodeSocketFloat", "MaxParticleScale")
        node.outputs.new("NodeSocketFloat", "MinParticleScale")
        node.outputs.new("NodeSocketFloat", "OverallParticleScale")

        node = nodes.new("GeometryNodeAttributeMapRange")
        node.name = "Attribute Map Range"
        node.location = (-227, 350)
        node.inputs[1].default_value = "foam"
        node.inputs[2].default_value = "foamLim"
        node.inputs[3].default_value = 0
        node.inputs[4].default_value = 1
        node.inputs[5].default_value = 0
        node.inputs[6].default_value = 1
        node.inputs[7].default_value = 4
        node.inputs[8].default_value = (0.0, 0.0, 0.0,)
        node.inputs[9].default_value = (1.0, 1.0, 1.0,)
        node.inputs[10].default_value = (0.0, 0.0, 0.0,)
        node.inputs[11].default_value = (1.0, 1.0, 1.0,)
        node.inputs[12].default_value = (4.0, 4.0, 4.0,)
        node.inputs[13].default_value = False

        node = nodes.new("NodeReroute")
        node.name = "Reroute.001"
        node.location = (-120, -139)

        node = nodes.new("NodeReroute")
        node.name = "Reroute.005"
        node.location = (-7, 29)
        node.inputs[0].default_value = 0
        node.outputs[0].default_value = 0

        node = nodes.new("NodeReroute")
        node.name = "Reroute.006"
        node.location = (4, 97)
        node.inputs[0].default_value = 0
        node.outputs[0].default_value = 0

        node = nodes.new("GeometryNodePointDistribute")
        node.name = "Point Distribute"
        node.location = (88, 221)
        node.inputs[1].default_value = 0
        node.inputs[2].default_value = 30
        node.inputs[3].default_value = "foamLim"
        node.inputs[4].default_value = 0

        node = nodes.new("GeometryNodeAttributeVectorMath")
        node.name = "Attribute Vector Math"
        node.location = (297, 307)
        node.inputs[1].default_value = "position"
        node.inputs[2].default_value = (0.0, 0.0, 0.0,)
        node.inputs[3].default_value = "spray"
        node.inputs[4].default_value = (0.0, 0.0, 0.0,)
        node.inputs[5].default_value = 0
        node.inputs[6].default_value = ""
        node.inputs[7].default_value = (0.0, 0.0, 0.0,)
        node.inputs[8].default_value = 0
        node.inputs[9].default_value = "position"

        node = nodes.new("NodeReroute")
        node.name = "Reroute.004"
        node.location = (301, 6)
        node.inputs[0].default_value = 0
        node.outputs[0].default_value = 0

        node = nodes.new("NodeReroute")
        node.name = "Reroute.003"
        node.location = (321, -8)
        node.inputs[0].default_value = 0
        node.outputs[0].default_value = 0

        node = nodes.new("NodeReroute")
        node.name = "Reroute.002"
        node.location = (475, -71)
        node.inputs[0].default_value = 0
        node.outputs[0].default_value = 0

        node = nodes.new("ShaderNodeCombineXYZ")
        node.name = "Combine XYZ"
        node.location = (497, 3)
        node.inputs[0].default_value = 0
        node.inputs[1].default_value = 0
        node.inputs[2].default_value = 0
        node.outputs[0].default_value = (0.0, 0.0, 0.0,)

        node = nodes.new("GeometryNodeAttributeRandomize")
        node.name = "Attribute Randomize"
        node.location = (502, 272)
        node.inputs[1].default_value = "scale"
        node.inputs[2].default_value = (0.0, 0.0, 0.0,)
        node.inputs[3].default_value = (1.0, 1.0, 1.0,)
        node.inputs[4].default_value = 0
        node.inputs[5].default_value = 0
        node.inputs[6].default_value = 0
        node.inputs[7].default_value = 100
        node.inputs[8].default_value = 0

        node = nodes.new("GeometryNodePointScale")
        node.name = "Point Scale"
        node.location = (726, 230)
        node.inputs[1].default_value = "scale"
        node.inputs[2].default_value = (
            0.029999999329447746, 0.029999999329447746, 0.029999999329447746,)
        node.inputs[3].default_value = 1

        node = nodes.new("NodeReroute")
        node.name = "Reroute"
        node.location = (908, -131)

        node = nodes.new("GeometryNodePointInstance")
        node.name = "Point Instance"
        node.location = (919, 235)
        node.inputs[1].default_value = None
        node.inputs[2].default_value = None
        node.inputs[3].default_value = 0

        node = nodes.new("GeometryNodeJoinGeometry")
        node.name = "Join Geometry"
        node.location = (1139, 173)

        node = nodes.new("NodeGroupOutput")
        node.name = "Group Output"
        node.location = (1324, 176)
        node.inputs.new("NodeSocketGeometry", "Geometry")
        links.new(nodes['Point Instance'].outputs['Geometry'],
                  nodes['Join Geometry'].inputs['Geometry'])
        links.new(nodes['Attribute Vector Math'].outputs['Geometry'],
                  nodes['Attribute Randomize'].inputs['Geometry'])
        links.new(nodes['Point Distribute'].outputs['Geometry'],
                  nodes['Attribute Vector Math'].inputs['Geometry'])
        links.new(nodes['Join Geometry'].outputs['Geometry'],
                  nodes['Group Output'].inputs['Geometry'])
        links.new(nodes['Reroute'].outputs['Output'],
                  nodes['Join Geometry'].inputs['Geometry'])
        links.new(nodes['Reroute.001'].outputs['Output'],
                  nodes['Reroute'].inputs['Input'])
        links.new(nodes['Group Input'].outputs['Geometry'],
                  nodes['Reroute.001'].inputs['Input'])
        links.new(nodes['Point Scale'].outputs['Geometry'],
                  nodes['Point Instance'].inputs['Geometry'])
        links.new(nodes['Attribute Randomize'].outputs['Geometry'],
                  nodes['Point Scale'].inputs['Geometry'])
        links.new(nodes['Reroute.006'].outputs['Output'],
                  nodes['Point Distribute'].inputs['Density Max'])
        links.new(nodes['Reroute.004'].outputs['Output'],
                  nodes['Attribute Randomize'].inputs['Max'])
        links.new(nodes['Reroute.003'].outputs['Output'],
                  nodes['Attribute Randomize'].inputs['Min'])
        links.new(nodes['Reroute.002'].outputs['Output'],
                  nodes['Combine XYZ'].inputs['X'])
        links.new(nodes['Group Input'].outputs['OverallParticleScale'],
                  nodes['Reroute.002'].inputs['Input'])
        links.new(nodes['Reroute.002'].outputs['Output'],
                  nodes['Combine XYZ'].inputs['Y'])
        links.new(nodes['Reroute.002'].outputs['Output'],
                  nodes['Combine XYZ'].inputs['Z'])
        links.new(nodes['Combine XYZ'].outputs['Vector'],
                  nodes['Point Scale'].inputs['Factor'])
        links.new(nodes['Group Input'].outputs['MinParticleScale'],
                  nodes['Reroute.003'].inputs['Input'])
        links.new(nodes['Group Input'].outputs['MaxParticleScale'],
                  nodes['Reroute.004'].inputs['Input'])
        links.new(nodes['Group Input'].outputs['Density Max'],
                  nodes['Reroute.005'].inputs['Input'])
        links.new(nodes['Reroute.005'].outputs['Output'],
                  nodes['Reroute.006'].inputs['Input'])
        links.new(nodes['Group Input'].outputs['Geometry'],
                  nodes['Attribute Map Range'].inputs['Geometry'])
        links.new(nodes['Attribute Map Range'].outputs['Geometry'],
                  nodes['Point Distribute'].inputs['Geometry'])

    def remove_spray(self, context, ocean):
        if "Spray" in ocean.modifiers:
            ocean.modifiers.remove(ocean.modifiers['Spray'])
