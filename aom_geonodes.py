import bpy


class AOMGeoNodesHandler:
    def __init__(self, context, advcol):
        self.context = context
        self.AdvCollection = advcol

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

    # links ob to target col and removes from original col
    def ob_to_collection(self, context, col, ob):
        # find ori col
        allcol = bpy.data.collections
        oricols = []
        for cole in allcol:
            for cob in cole.objects:
                if ob.name == cob.name:
                    oricols.append(cole)

        print(f"{col.name}")
        col.objects.link(ob)

        for cole in oricols:
            print(cole)
            if cole.name != col.name:

                for cob in cole.objects:
                    if ob.name == cob.name:
                        #print("unline ob {ob.name} col {col} ")
                        cole.objects.unlink(ob)

    def add_collection_to_modinp(self, col, mod, modinput):

        mod[modinput.identifier] = col

    def new_spray(self, context, ocean):
        ocean.modifiers["Ocean"].use_spray = True
        ocean.modifiers["Ocean"].spray_layer_name = "spray"

        # make mod and name
        mod, nodegroup = self.new_geonodes_mod(ocean)
        mod.name = "Spray"
        nodegroup.name = "Spray"
        #self.move_mod_one_up(ocean, mod)
        self.make_spray_nodes(mod, mod.node_group)

        # collection
        # gibts schon den Brushordner
        if bpy.data.collections.find('Spray') < 0:
            collection = bpy.data.collections.new(
                name='Spray')  # makes collection
            self.AdvCollection.children.link(
                collection)
        else:
            collection = bpy.data.collections['Spray']

        bpy.ops.mesh.primitive_ico_sphere_add(
            subdivisions=1, radius=1, enter_editmode=False, align='WORLD', location=(0, 0, 0), scale=(1, 1, 1))

        self.ob_to_collection(context, collection, context.object)

        #context.layer_collection.children['Spray'].exclude = True

        # it will be only one but more flexible
        for inp in mod.node_group.inputs:
            if inp.bl_socket_idname == 'NodeSocketCollection':
                self.add_collection_to_modinp(collection, mod, inp)

        #context.view_layer.active_layer_collection = collection
        #collection.exclude = True
        #self.AdvCollection.children[collection.name].exclude = True

    def make_spray_nodes(self, mod, node_group):
        self.remove_nodes(node_group)
        nodes = node_group.nodes
        links = node_group.links

        inp = node_group.inputs.new('NodeSocketFloat', 'Density Max')
        inp = node_group.inputs.new('NodeSocketFloat', 'Density Max')
        inp.default_value = 30.0
        inp = node_group.inputs.new('NodeSocketFloat', 'Contrast')
        inp.default_value = 0.25
        inp = node_group.inputs.new('NodeSocketFloat', 'MaxParticleScale')
        inp.default_value = 0.8
        inp = node_group.inputs.new('NodeSocketFloat', 'MinParticleScale')
        inp.default_value = 0.01
        inp = node_group.inputs.new('NodeSocketFloat', 'OverallParticleScale')
        inp.default_value = 0.06
        inp = node_group.inputs.new('NodeSocketFloatFactor', 'ObjectSpray')
        inp.default_value = 0.0
        inp = node_group.inputs.new(
            'NodeSocketCollection', 'SprayPartikleCollection')

        node = nodes.new("NodeGroupInput")
        node.name = "Group Input"
        node.location = (-1160, 129)

        node = nodes.new("ShaderNodeMath")
        node.name = "Math"
        node.location = (-984, 374)
        node.inputs[0].default_value = 0.5
        node.operation = "ADD"
        node.inputs[1].default_value = 1.0
        node.operation = "ADD"
        node.inputs[2].default_value = 0.0
        node.operation = "ADD"
        node.outputs[0].default_value = 0.0

        node = nodes.new("ShaderNodeMath")
        node.name = "Math.001"
        node.location = (-782, 368)
        node.inputs[0].default_value = 0.5
        node.operation = "LOGARITHM"
        node.inputs[1].default_value = 51.4
        node.operation = "LOGARITHM"
        node.inputs[2].default_value = 0.0
        node.operation = "LOGARITHM"
        node.outputs[0].default_value = 0.0

        node = nodes.new("GeometryNodeAttributeMapRange")
        node.name = "Attribute Map Range"
        node.location = (-547, 371)
        node.data_type = "FLOAT"
        node.inputs[1].default_value = "foam"
        node.data_type = "FLOAT"
        node.inputs[2].default_value = "foamLim"
        node.data_type = "FLOAT"
        node.inputs[3].default_value = 0.25
        node.data_type = "FLOAT"
        node.inputs[4].default_value = 1.0
        node.data_type = "FLOAT"
        node.inputs[5].default_value = 0.0
        node.data_type = "FLOAT"
        node.inputs[6].default_value = 1.0
        node.data_type = "FLOAT"
        node.inputs[7].default_value = 4.0
        node.data_type = "FLOAT"
        node.inputs[8].default_value = (0.0, 0.0, 0.0,)
        node.data_type = "FLOAT"
        node.inputs[9].default_value = (1.0, 1.0, 1.0,)
        node.data_type = "FLOAT"
        node.inputs[10].default_value = (0.0, 0.0, 0.0,)
        node.data_type = "FLOAT"
        node.inputs[11].default_value = (1.0, 1.0, 1.0,)
        node.data_type = "FLOAT"
        node.inputs[12].default_value = (4.0, 4.0, 4.0,)
        node.data_type = "FLOAT"
        node.inputs[13].default_value = False
        node.data_type = "FLOAT"

        node = nodes.new("GeometryNodeAttributeMix")
        node.name = "Attribute Mix"
        node.location = (-286, 357)
        node.input_type_a = "ATTRIBUTE"
        node.inputs[1].default_value = ""
        node.input_type_a = "ATTRIBUTE"
        node.inputs[2].default_value = 0.5
        node.input_type_a = "ATTRIBUTE"
        node.inputs[3].default_value = "foamLim"
        node.input_type_a = "ATTRIBUTE"
        node.inputs[4].default_value = 0.0
        node.input_type_a = "ATTRIBUTE"
        node.inputs[5].default_value = (0.0, 0.0, 0.0,)
        node.input_type_a = "ATTRIBUTE"
        node.inputs[6].default_value = (0.5, 0.5, 0.5, 1.0,)
        node.input_type_a = "ATTRIBUTE"
        node.inputs[7].default_value = "dp_wetmap"
        node.input_type_a = "ATTRIBUTE"
        node.inputs[8].default_value = 0.0
        node.input_type_a = "ATTRIBUTE"
        node.inputs[9].default_value = (0.0, 0.0, 0.0,)
        node.input_type_a = "ATTRIBUTE"
        node.inputs[10].default_value = (0.5, 0.5, 0.5, 1.0,)
        node.input_type_a = "ATTRIBUTE"
        node.inputs[11].default_value = "foamLim"
        node.input_type_a = "ATTRIBUTE"

        node = nodes.new("NodeReroute")
        node.name = "Reroute.005"
        node.location = (-7, 29)
        node.inputs[0].default_value = 0.0
        node.outputs[0].default_value = 0.0

        node = nodes.new("NodeReroute")
        node.name = "Reroute.006"
        node.location = (4, 97)
        node.inputs[0].default_value = 0.0
        node.outputs[0].default_value = 0.0

        node = nodes.new("GeometryNodePointDistribute")
        node.name = "Point Distribute"
        node.location = (76, 264)
        node.distribute_method = "RANDOM"
        node.inputs[1].default_value = 0.0
        node.distribute_method = "RANDOM"
        node.inputs[2].default_value = 30.0
        node.distribute_method = "RANDOM"
        node.inputs[3].default_value = "foamLim"
        node.distribute_method = "RANDOM"
        node.inputs[4].default_value = 0
        node.distribute_method = "RANDOM"

        node = nodes.new("GeometryNodeAttributeVectorMath")
        node.name = "Attribute Vector Math"
        node.location = (297, 307)
        node.operation = "ADD"
        node.inputs[1].default_value = "position"
        node.operation = "ADD"
        node.inputs[2].default_value = (0.0, 0.0, 0.0,)
        node.operation = "ADD"
        node.inputs[3].default_value = "spray"
        node.operation = "ADD"
        node.inputs[4].default_value = (0.0, 0.0, 0.0,)
        node.operation = "ADD"
        node.inputs[5].default_value = 0.0
        node.operation = "ADD"
        node.inputs[6].default_value = ""
        node.operation = "ADD"
        node.inputs[7].default_value = (0.0, 0.0, 0.0,)
        node.operation = "ADD"
        node.inputs[8].default_value = 0.0
        node.operation = "ADD"
        node.inputs[9].default_value = "position"
        node.operation = "ADD"

        node = nodes.new("GeometryNodeAttributeRandomize")
        node.name = "Attribute Randomize"
        node.location = (502, 272)
        node.data_type = "FLOAT"
        node.inputs[1].default_value = "scale"
        node.data_type = "FLOAT"
        node.inputs[2].default_value = (0.0, 0.0, 0.0,)
        node.data_type = "FLOAT"
        node.inputs[3].default_value = (1.0, 1.0, 1.0,)
        node.data_type = "FLOAT"
        node.inputs[4].default_value = 0.01
        node.data_type = "FLOAT"
        node.inputs[5].default_value = 0.8
        node.data_type = "FLOAT"
        node.inputs[6].default_value = 0
        node.data_type = "FLOAT"
        node.inputs[7].default_value = 100
        node.data_type = "FLOAT"
        node.inputs[8].default_value = 0
        node.data_type = "FLOAT"

        node = nodes.new("GeometryNodePointScale")
        node.name = "Point Scale"
        node.location = (726, 230)
        node.input_type = "FLOAT"
        node.inputs[1].default_value = "scale"
        node.input_type = "FLOAT"
        node.inputs[2].default_value = (
            0.029999999329447746, 0.029999999329447746, 0.029999999329447746,)
        node.input_type = "FLOAT"
        node.inputs[3].default_value = 1.0
        node.input_type = "FLOAT"

        node = nodes.new("GeometryNodePointInstance")
        node.name = "Point Instance"
        node.location = (923, 179)
        node.instance_type = "COLLECTION"
        node.inputs[1].default_value = None
        node.instance_type = "COLLECTION"
        node.inputs[2].default_value = None
        node.instance_type = "COLLECTION"
        node.inputs[3].default_value = 0
        node.instance_type = "COLLECTION"

        node = nodes.new("GeometryNodeJoinGeometry")
        node.name = "Join Geometry"
        node.location = (1139, 173)

        node = nodes.new("NodeGroupOutput")
        node.name = "Group Output"
        node.location = (1324, 176)
        links.new(nodes['Group Input'].outputs[0],
                  nodes['Join Geometry'].inputs[0])
        links.new(nodes['Group Input'].outputs[0],
                  nodes['Attribute Map Range'].inputs[0])
        links.new(nodes['Group Input'].outputs[1],
                  nodes['Reroute.005'].inputs[0])
        links.new(nodes['Group Input'].outputs[2],  nodes['Math'].inputs[0])
        links.new(nodes['Group Input'].outputs[3],
                  nodes['Attribute Randomize'].inputs[3])
        links.new(nodes['Group Input'].outputs[4],
                  nodes['Attribute Randomize'].inputs[2])
        links.new(nodes['Group Input'].outputs[5],
                  nodes['Point Scale'].inputs[1])
        links.new(nodes['Group Input'].outputs[6],
                  nodes['Attribute Mix'].inputs[1])
        links.new(nodes['Group Input'].outputs[7],
                  nodes['Point Instance'].inputs[2])
        links.new(nodes['Point Instance'].outputs['Geometry'],
                  nodes['Join Geometry'].inputs['Geometry'])
        links.new(nodes['Attribute Vector Math'].outputs['Geometry'],
                  nodes['Attribute Randomize'].inputs['Geometry'])
        links.new(nodes['Point Distribute'].outputs['Geometry'],
                  nodes['Attribute Vector Math'].inputs['Geometry'])
        links.new(nodes['Join Geometry'].outputs['Geometry'],
                  nodes['Group Output'].inputs['Geometry'])
        links.new(nodes['Point Scale'].outputs['Geometry'],
                  nodes['Point Instance'].inputs['Geometry'])
        links.new(nodes['Attribute Randomize'].outputs['Geometry'],
                  nodes['Point Scale'].inputs['Geometry'])
        links.new(nodes['Reroute.006'].outputs['Output'],
                  nodes['Point Distribute'].inputs['Density Max'])
        links.new(nodes['Reroute.005'].outputs['Output'],
                  nodes['Reroute.006'].inputs['Input'])
        links.new(nodes['Attribute Map Range'].outputs['Geometry'],
                  nodes['Attribute Mix'].inputs['Geometry'])
        links.new(nodes['Math'].outputs['Value'],
                  nodes['Math.001'].inputs['Value'])
        links.new(nodes['Math.001'].outputs['Value'],
                  nodes['Attribute Map Range'].inputs['From Min'])
        links.new(nodes['Attribute Mix'].outputs['Geometry'],
                  nodes['Point Distribute'].inputs['Geometry'])
        mod['Input_5'] = 17.0
        mod['Input_17'] = 1.17
        mod['Input_7'] = 1.56
        mod['Input_9'] = 0.17
        mod['Input_13'] = 0.06
        mod['Input_19'] = 0.5

    def remove_spray(self, context, ocean):
        if "Spray" in ocean.modifiers:
            ocean.modifiers.remove(ocean.modifiers['Spray'])
