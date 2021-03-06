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

    def get_mod_index(self, ocean, mod):
        mods = ocean.modifiers
        for a, mid in enumerate(mods):
            if mod == mid:
                return a
        return -1

    def get_DP_mod_index(self, ocean):
        mods = ocean.modifiers
        for a, mod in enumerate(mods):
            # print(a)
            # print(mod.name)
            if "Dynamic Paint" in mod.name:
                return a
        # wenn nicht ACHTUUNG
        print('way out')
        return len(mods)-1

    def move_above_DP(self, ocean, mod):

        m = self.get_mod_index(ocean, mod)
        n = self.get_DP_mod_index(ocean)
        print(f'DP detected {n}')
        if n >= 1:
            print(f'1möp {n}')
            print(mod.name)
            print(f'm {m}')
            print(f'n{n}')
            while m > n:
                print(mod.name)
                bpy.ops.object.modifier_move_up(modifier=mod.name)
                m = self.get_mod_index(ocean, mod)
                n = self.get_DP_mod_index(ocean)
                #bpy.ops.object.modifier_move_to_index(modifier=mod.name, index=n)
                print(f'm {m}')
                print(f'n{n}')
        else:
            print('2möp  1')
            bpy.ops.object.modifier_move_to_index(modifier=mod.name, index=1)

    def move_mod_one_up(self, ocean, mod):
        n = len(ocean.modifiers)
        if n-2 >= 0:
            bpy.ops.object.modifier_move_up(modifier=mod.name)
            #bpy.ops.object.modifier_move_to_index(modifier=mod.name, index=n-2)
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
                        # print("unline ob {ob.name} col {col} ")
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
        # self.move_mod_one_up(ocean, mod)
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

        # it will be only one but more flexible
        for inp in mod.node_group.inputs:
            if inp.bl_socket_idname == 'NodeSocketCollection':
                self.add_collection_to_modinp(collection, mod, inp)

        context.layer_collection.children['Spray'].exclude = True
        dg = bpy.context.evaluated_depsgraph_get()

        context.view_layer.objects.active = ocean
        # collection.exclude = True
        # self.AdvCollection.children[collection.name].exclude = True

    def make_spray_nodes(self, mod, node_group):
        self.remove_nodes(node_group)
        nodes = node_group.nodes
        links = node_group.links

        inp = node_group.inputs.new('NodeSocketFloat', 'Height')
        inp.default_value = 1.0
        inp = node_group.inputs.new('NodeSocketFloat', 'Density Max')
        inp.default_value = 50.0
        inp = node_group.inputs.new('NodeSocketFloat', 'Contrast')
        inp.default_value = 1.2
        inp = node_group.inputs.new('NodeSocketFloat', 'MaxParticleScale')
        inp.default_value = 0.5
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
        node.location = (-1321, 150)

        node = nodes.new("ShaderNodeMath")
        node.name = "Math"
        node.location = (-984, 374)
        node.operation = "ADD"
        node.use_clamp = False
        node.inputs[0].default_value = 0.5
        node.inputs[1].default_value = 1.0
        node.inputs[2].default_value = 0.0
        node.outputs[0].default_value = 0.0

        node = nodes.new("ShaderNodeMath")
        node.name = "Math.001"
        node.location = (-782, 368)
        node.operation = "LOGARITHM"
        node.use_clamp = False
        node.inputs[0].default_value = 0.5
        node.inputs[1].default_value = 51.4
        node.inputs[2].default_value = 0.0
        node.outputs[0].default_value = 0.0

        node = nodes.new("GeometryNodeAttributeMapRange")
        node.name = "Attribute Map Range"
        node.location = (-547, 371)
        node.data_type = "FLOAT"
        node.interpolation_type = "LINEAR"
        node.inputs[1].default_value = "foam"
        node.inputs[2].default_value = "foamLim"
        node.inputs[3].default_value = 0.25
        node.inputs[4].default_value = 1.0
        node.inputs[5].default_value = 0.0
        node.inputs[6].default_value = 1.0
        node.inputs[7].default_value = 4.0
        node.inputs[8].default_value = (0.0, 0.0, 0.0,)
        node.inputs[9].default_value = (1.0, 1.0, 1.0,)
        node.inputs[10].default_value = (0.0, 0.0, 0.0,)
        node.inputs[11].default_value = (1.0, 1.0, 1.0,)
        node.inputs[12].default_value = (4.0, 4.0, 4.0,)
        node.inputs[13].default_value = False

        node = nodes.new("GeometryNodeAttributeMix")
        node.name = "Attribute Mix"
        node.location = (-286, 357)
        node.input_type_a = "ATTRIBUTE"
        node.input_type_b = "ATTRIBUTE"
        node.input_type_factor = "FLOAT"
        node.blend_type = "ADD"
        node.inputs[1].default_value = ""
        node.inputs[2].default_value = 0.5
        node.inputs[3].default_value = "foamLim"
        node.inputs[4].default_value = 0.0
        node.inputs[5].default_value = (0.0, 0.0, 0.0,)
        node.inputs[6].default_value = (0.5, 0.5, 0.5, 1.0,)
        node.inputs[7].default_value = "dp_wetmap"
        node.inputs[8].default_value = 0.0
        node.inputs[9].default_value = (0.0, 0.0, 0.0,)
        node.inputs[10].default_value = (0.5, 0.5, 0.5, 1.0,)
        node.inputs[11].default_value = "foamLim"

        node = nodes.new("NodeReroute")
        node.name = "Reroute.005"
        node.location = (-7, 29)
        node.inputs[0].default_value = 0.0
        node.outputs[0].default_value = 0.0

        node = nodes.new("NodeReroute")
        node.name = "Reroute.006"
        node.location = (-4, 139)
        node.inputs[0].default_value = 0.0
        node.outputs[0].default_value = 0.0

        node = nodes.new("GeometryNodePointDistribute")
        node.name = "Point Distribute"
        node.location = (64, 348)
        node.distribute_method = "RANDOM"
        node.inputs[1].default_value = 0.0
        node.inputs[2].default_value = 30.0
        node.inputs[3].default_value = "foamLim"
        node.inputs[4].default_value = 0

        node = nodes.new("GeometryNodeAttributeVectorMath")
        node.name = "Attribute Vector Math.001"
        node.location = (289, 331)
        node.operation = "SCALE"
        node.input_type_a = "ATTRIBUTE"
        node.input_type_b = "FLOAT"
        node.inputs[1].default_value = "spray"
        node.inputs[2].default_value = (0.0, 0.0, 0.0,)
        node.inputs[3].default_value = ""
        node.inputs[4].default_value = (0.0, 0.0, 0.0,)
        node.inputs[5].default_value = 0.0
        node.inputs[6].default_value = ""
        node.inputs[7].default_value = (0.0, 0.0, 0.0,)
        node.inputs[8].default_value = 0.0
        node.inputs[9].default_value = "spray"

        node = nodes.new("GeometryNodeAttributeVectorMath")
        node.name = "Attribute Vector Math"
        node.location = (520, 341)
        node.operation = "ADD"
        node.input_type_a = "ATTRIBUTE"
        node.input_type_b = "ATTRIBUTE"
        node.inputs[1].default_value = "position"
        node.inputs[2].default_value = (0.0, 0.0, 0.0,)
        node.inputs[3].default_value = "spray"
        node.inputs[4].default_value = (0.0, 0.0, 0.0,)
        node.inputs[5].default_value = 0.0
        node.inputs[6].default_value = ""
        node.inputs[7].default_value = (0.0, 0.0, 0.0,)
        node.inputs[8].default_value = 0.0
        node.inputs[9].default_value = "position"

        node = nodes.new("GeometryNodeAttributeRandomize")
        node.name = "Attribute Randomize"
        node.location = (673, 87)
        node.data_type = "FLOAT"
        node.operation = "REPLACE_CREATE"
        node.inputs[1].default_value = "scale"
        node.inputs[2].default_value = (0.0, 0.0, 0.0,)
        node.inputs[3].default_value = (1.0, 1.0, 1.0,)
        node.inputs[4].default_value = 0.01
        node.inputs[5].default_value = 0.8
        node.inputs[6].default_value = 0
        node.inputs[7].default_value = 100
        node.inputs[8].default_value = 0

        node = nodes.new("GeometryNodePointScale")
        node.name = "Point Scale"
        node.location = (893, 230)
        node.input_type = "FLOAT"
        node.inputs[1].default_value = "scale"
        node.inputs[2].default_value = (
            0.029999999329447746, 0.029999999329447746, 0.029999999329447746,)
        node.inputs[3].default_value = 1.0

        node = nodes.new("GeometryNodePointInstance")
        node.name = "Point Instance"
        node.location = (1090, 179)
        node.instance_type = "COLLECTION"
        node.use_whole_collection = False
        node.inputs[1].default_value = None
        node.inputs[2].default_value = None
        node.inputs[3].default_value = 0

        node = nodes.new("GeometryNodeJoinGeometry")
        node.name = "Join Geometry"
        node.location = (1306, 173)

        node = nodes.new("NodeGroupOutput")
        node.name = "Group Output"
        node.location = (1491, 176)
        links.new(nodes['Group Input'].outputs[0],
                  nodes['Join Geometry'].inputs[0])
        links.new(nodes['Group Input'].outputs[0],
                  nodes['Attribute Map Range'].inputs[0])

        links.new(nodes['Group Input'].outputs[2],
                  nodes['Reroute.005'].inputs[0])

        links.new(nodes['Group Input'].outputs[8],
                  nodes['Point Instance'].inputs[2])
        links.new(nodes['Point Instance'].outputs['Geometry'],
                  nodes['Join Geometry'].inputs['Geometry'])
        links.new(nodes['Attribute Vector Math'].outputs['Geometry'],
                  nodes['Attribute Randomize'].inputs['Geometry'])
        links.new(nodes['Point Distribute'].outputs['Geometry'],
                  nodes['Attribute Vector Math.001'].inputs['Geometry'])
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
        links.new(nodes['Attribute Vector Math.001'].outputs['Geometry'],
                  nodes['Attribute Vector Math'].inputs['Geometry'])

        #############################################

        links.new(nodes['Group Input'].outputs[4],
                  nodes['Attribute Randomize'].inputs[5])
        links.new(nodes['Group Input'].outputs[5],
                  nodes['Attribute Randomize'].inputs[4])
        links.new(nodes['Group Input'].outputs[6],
                  nodes['Point Scale'].inputs[3])
        links.new(nodes['Group Input'].outputs[7],
                  nodes['Attribute Mix'].inputs[2])
        links.new(nodes['Group Input'].outputs[1],
                  nodes['Attribute Vector Math.001'].inputs[5])
        links.new(nodes['Group Input'].outputs[3],  nodes['Math'].inputs[1])

        node_group.inputs[7].min_value = 0
        node_group.inputs[7].max_value = 1

        # for inp in node_group.inputs:
        #    if inp.bl_socket_idname != 'NodeSocketGeometry':
        #        mod[inp.identifier] = inp.default_value

    def remove_spray(self, context, ocean):
        if "Spray" in ocean.modifiers:
            ocean.modifiers.remove(ocean.modifiers['Spray'])

    def new_ripples(self, context, ocean, ob):
        context.view_layer.objects.active = ocean
        if ocean == None:
            return None
        # make mod and name
        mod, nodegroup = self.new_geonodes_mod(ocean)
        mod.name = "Ripples"
        nodegroup.name = "Ripples"
        #self.move_mod_one_up(ocean, mod)

        self.make_rippels_nodes(mod, mod.node_group)
        if ob != None:
            mod['Input_15'] = ob
            ob.aom_data.ripple_parent = ocean

        ocean.modifiers.active = mod

        self.move_above_DP(ocean, mod)

        # driver

    def make_rippels_nodes(self, mod, node_group):
        self.remove_nodes(node_group)
        nodes = node_group.nodes
        links = node_group.links

        inp = node_group.inputs.new('NodeSocketFloat', 'Wavelength')
        inp.default_value = 0.25
        inp = node_group.inputs.new('NodeSocketFloat', 'Amplitude')
        inp.default_value = 1.0
        inp = node_group.inputs.new('NodeSocketFloat', 'OuterFalloff')
        inp.default_value = 20.0
        inp = node_group.inputs.new('NodeSocketFloat', 'InnerCut')
        inp.default_value = 25.0
        inp = node_group.inputs.new('NodeSocketFloat', 'Speed')
        inp.default_value = 10.0
        inp = node_group.inputs.new('NodeSocketObject', 'Object')

        node = nodes.new("NodeGroupInput")
        node.name = "Group Input"
        node.location = (-1865, 256)

        node = nodes.new("GeometryNodeObjectInfo")
        node.name = "Object Info"
        node.location = (-1655, 373)
        node.transform_space = "RELATIVE"
        node.inputs[0].default_value = None
        node.outputs[0].default_value = (0.0, 0.0, 0.0,)
        node.outputs[1].default_value = (0.0, 0.0, 0.0,)
        node.outputs[2].default_value = (0.0, 0.0, 0.0,)

        node = nodes.new("NodeReroute")
        node.name = "Reroute.003"
        node.location = (-1268, 493)

        node = nodes.new("GeometryNodeAttributeProximity")
        node.name = "Attribute Proximity"
        node.location = (-1262, 375)
        node.inputs[2].default_value = "dst"
        node.inputs[3].default_value = ""

        node = nodes.new("GeometryNodeAttributeMath")
        node.name = "Scaledistance.004"
        node.location = (-1097, 659)
        node.operation = "SUBTRACT"
        node.input_type_a = "FLOAT"
        node.input_type_b = "ATTRIBUTE"
        node.inputs[1].default_value = "dst"
        node.inputs[2].default_value = 20.0
        node.inputs[3].default_value = "dst"
        node.inputs[4].default_value = 0.5
        node.inputs[5].default_value = ""
        node.inputs[6].default_value = 0.0
        node.inputs[7].default_value = "Falloffinner"

        node = nodes.new("GeometryNodeAttributeMath")
        node.name = "Scaledistance.001"
        node.location = (-1084, 400)
        node.operation = "SUBTRACT"
        node.input_type_a = "FLOAT"
        node.input_type_b = "ATTRIBUTE"
        node.inputs[1].default_value = "dst"
        node.inputs[2].default_value = 20.5
        node.inputs[3].default_value = "dst"
        node.inputs[4].default_value = 0.5
        node.inputs[5].default_value = ""
        node.inputs[6].default_value = 0.0
        node.inputs[7].default_value = "Falloff"

        node = nodes.new("ShaderNodeValue")
        node.name = "Value"
        node.location = (-1011, -248)
        node.outputs[0].default_value = -125.0

        node = nodes.new("GeometryNodeAttributeMath")
        node.name = "Scaledistance.003"
        node.location = (-930, 661)
        node.operation = "GREATER_THAN"
        node.input_type_a = "FLOAT"
        node.input_type_b = "ATTRIBUTE"
        node.inputs[1].default_value = "dst"
        node.inputs[2].default_value = 20.0
        node.inputs[3].default_value = "Falloffinner"
        node.inputs[4].default_value = 0.5
        node.inputs[5].default_value = ""
        node.inputs[6].default_value = 0.0
        node.inputs[7].default_value = "InnerFalloffMIx"

        node = nodes.new("GeometryNodeAttributeMath")
        node.name = "Scaledistance.002"
        node.location = (-928, 395)
        node.operation = "GREATER_THAN"
        node.input_type_a = "FLOAT"
        node.input_type_b = "ATTRIBUTE"
        node.inputs[1].default_value = "dst"
        node.inputs[2].default_value = 0.0
        node.inputs[3].default_value = "Falloff"
        node.inputs[4].default_value = 0.5
        node.inputs[5].default_value = ""
        node.inputs[6].default_value = 0.0
        node.inputs[7].default_value = "FalloffMIx"

        node = nodes.new("GeometryNodeAttributeMix")
        node.name = "Attribute Mix.002"
        node.location = (-775, 410)
        node.input_type_a = "ATTRIBUTE"
        node.input_type_b = "FLOAT"
        node.input_type_factor = "ATTRIBUTE"
        node.blend_type = "MIX"
        node.inputs[1].default_value = "FalloffMIx"
        node.inputs[2].default_value = 0.5
        node.inputs[3].default_value = "Falloff"
        node.inputs[4].default_value = 0.0
        node.inputs[5].default_value = (0.0, 0.0, 0.0,)
        node.inputs[6].default_value = (0.5, 0.5, 0.5, 1.0,)
        node.inputs[7].default_value = ""
        node.inputs[8].default_value = 0.0
        node.inputs[9].default_value = (0.0, 0.0, 0.0,)
        node.inputs[10].default_value = (0.5, 0.5, 0.5, 1.0,)
        node.inputs[11].default_value = "Falloff"

        node = nodes.new("GeometryNodeAttributeMix")
        node.name = "Attribute Mix.003"
        node.location = (-773, 682)
        node.input_type_a = "FLOAT"
        node.input_type_b = "ATTRIBUTE"
        node.input_type_factor = "ATTRIBUTE"
        node.blend_type = "MIX"
        node.inputs[1].default_value = "InnerFalloffMIx"
        node.inputs[2].default_value = 0.5
        node.inputs[3].default_value = "Falloff"
        node.inputs[4].default_value = 0.0
        node.inputs[5].default_value = (0.0, 0.0, 0.0,)
        node.inputs[6].default_value = (0.5, 0.5, 0.5, 1.0,)
        node.inputs[7].default_value = "Falloff"
        node.inputs[8].default_value = 0.0
        node.inputs[9].default_value = (0.0, 0.0, 0.0,)
        node.inputs[10].default_value = (0.5, 0.5, 0.5, 1.0,)
        node.inputs[11].default_value = "Falloff"

        node = nodes.new("ShaderNodeMath")
        node.name = "Math"
        node.location = (-672, -191)
        node.operation = "DIVIDE"
        node.use_clamp = False
        node.inputs[0].default_value = 0.5
        node.inputs[1].default_value = 0.5
        node.inputs[2].default_value = 0.0
        node.outputs[0].default_value = 0.0

        node = nodes.new("NodeReroute")
        node.name = "Reroute"
        node.location = (-533, -60)
        node.inputs[0].default_value = 0.0
        node.outputs[0].default_value = 0.0

        node = nodes.new("NodeReroute")
        node.name = "Reroute.001"
        node.location = (-425, -234)
        node.inputs[0].default_value = 0.0
        node.outputs[0].default_value = 0.0

        node = nodes.new("GeometryNodeAttributeMath")
        node.name = "Scaledistance"
        node.location = (-164, 300)
        node.operation = "DIVIDE"
        node.input_type_a = "ATTRIBUTE"
        node.input_type_b = "FLOAT"
        node.inputs[1].default_value = "dst"
        node.inputs[2].default_value = 0.0
        node.inputs[3].default_value = ""
        node.inputs[4].default_value = 0.5
        node.inputs[5].default_value = ""
        node.inputs[6].default_value = 0.0
        node.inputs[7].default_value = "dst"

        node = nodes.new("NodeReroute")
        node.name = "Reroute.002"
        node.location = (-105, -51)
        node.inputs[0].default_value = 0.0
        node.outputs[0].default_value = 0.0

        node = nodes.new("GeometryNodeAttributeMath")
        node.name = "Offset"
        node.location = (-4, 300)
        node.operation = "ADD"
        node.input_type_a = "ATTRIBUTE"
        node.input_type_b = "FLOAT"
        node.inputs[1].default_value = "dst"
        node.inputs[2].default_value = 0.0
        node.inputs[3].default_value = ""
        node.inputs[4].default_value = 80.3
        node.inputs[5].default_value = ""
        node.inputs[6].default_value = 0.0
        node.inputs[7].default_value = "dst"

        node = nodes.new("ShaderNodeMapRange")
        node.name = "Map Range"
        node.location = (61, 3)
        node.interpolation_type = "LINEAR"
        node.clamp = False
        node.inputs[0].default_value = 29.3
        node.inputs[1].default_value = 0.0
        node.inputs[2].default_value = 1.0
        node.inputs[3].default_value = 0.0
        node.inputs[4].default_value = 0.01
        node.inputs[5].default_value = 4.0
        node.outputs[0].default_value = 0.0

        node = nodes.new("GeometryNodeAttributeMath")
        node.name = "Attribute Math.001"
        node.location = (154, 300)
        node.operation = "SINE"
        node.input_type_a = "ATTRIBUTE"
        node.input_type_b = "ATTRIBUTE"
        node.inputs[1].default_value = "dst"
        node.inputs[2].default_value = 0.0
        node.inputs[3].default_value = ""
        node.inputs[4].default_value = 0.0
        node.inputs[5].default_value = ""
        node.inputs[6].default_value = 0.0
        node.inputs[7].default_value = "dst"

        node = nodes.new("GeometryNodeAttributeMix")
        node.name = "Attribute Mix.001"
        node.location = (314, 300)
        node.input_type_a = "ATTRIBUTE"
        node.input_type_b = "ATTRIBUTE"
        node.input_type_factor = "FLOAT"
        node.blend_type = "MULTIPLY"
        node.inputs[1].default_value = ""
        node.inputs[2].default_value = 1.0
        node.inputs[3].default_value = "dst"
        node.inputs[4].default_value = 0.0
        node.inputs[5].default_value = (0.0, 0.0, 0.0,)
        node.inputs[6].default_value = (0.5, 0.5, 0.5, 1.0,)
        node.inputs[7].default_value = "Falloff"
        node.inputs[8].default_value = 0.0
        node.inputs[9].default_value = (0.0, 0.0, 0.0,)
        node.inputs[10].default_value = (0.5, 0.5, 0.5, 1.0,)
        node.inputs[11].default_value = "dst"

        node = nodes.new("GeometryNodeAttributeMath")
        node.name = "Attribute Math"
        node.location = (494, 300)
        node.operation = "MULTIPLY"
        node.input_type_a = "ATTRIBUTE"
        node.input_type_b = "FLOAT"
        node.inputs[1].default_value = "dst"
        node.inputs[2].default_value = 0.0
        node.inputs[3].default_value = ""
        node.inputs[4].default_value = 0.4
        node.inputs[5].default_value = ""
        node.inputs[6].default_value = 0.0
        node.inputs[7].default_value = "dst"

        node = nodes.new("GeometryNodeAttributeCombineXYZ")
        node.name = "Attribute Combine XYZ"
        node.location = (674, 300)
        node.input_type_x = "FLOAT"
        node.input_type_y = "FLOAT"
        node.input_type_z = "ATTRIBUTE"
        node.inputs[1].default_value = "position"
        node.inputs[2].default_value = 0.0
        node.inputs[3].default_value = "position"
        node.inputs[4].default_value = 0.0
        node.inputs[5].default_value = "dst"
        node.inputs[6].default_value = 1.0
        node.inputs[7].default_value = "height"

        node = nodes.new("GeometryNodeAttributeMix")
        node.name = "Attribute Mix"
        node.location = (834, 300)
        node.input_type_a = "ATTRIBUTE"
        node.input_type_b = "ATTRIBUTE"
        node.input_type_factor = "FLOAT"
        node.blend_type = "ADD"
        node.inputs[1].default_value = ""
        node.inputs[2].default_value = 1.0
        node.inputs[3].default_value = "position"
        node.inputs[4].default_value = 0.0
        node.inputs[5].default_value = (0.0, 0.0, 0.0,)
        node.inputs[6].default_value = (0.5, 0.5, 0.5, 1.0,)
        node.inputs[7].default_value = "height"
        node.inputs[8].default_value = 0.0
        node.inputs[9].default_value = (0.0, 0.0, 0.0,)
        node.inputs[10].default_value = (0.5, 0.5, 0.5, 1.0,)
        node.inputs[11].default_value = "position"

        node = nodes.new("NodeGroupOutput")
        node.name = "Group Output"
        node.location = (1267, 299)
        links.new(nodes['Group Input'].outputs[0],
                  nodes['Attribute Proximity'].inputs[0])
        links.new(nodes['Group Input'].outputs[1],  nodes['Reroute'].inputs[0])
        links.new(nodes['Group Input'].outputs[2],
                  nodes['Reroute.002'].inputs[0])
        links.new(nodes['Group Input'].outputs[3],
                  nodes['Scaledistance.001'].inputs[1])

        links.new(nodes['Group Input'].outputs[6],
                  nodes['Object Info'].inputs[0])
        links.new(nodes['Object Info'].outputs['Geometry'],
                  nodes['Attribute Proximity'].inputs['Target'])
        links.new(nodes['Attribute Mix'].outputs['Geometry'],
                  nodes['Group Output'].inputs['Geometry'])
        links.new(nodes['Attribute Proximity'].outputs['Geometry'],
                  nodes['Scaledistance.001'].inputs['Geometry'])
        links.new(nodes['Scaledistance.001'].outputs['Geometry'],
                  nodes['Scaledistance.002'].inputs['Geometry'])
        links.new(nodes['Offset'].outputs['Geometry'],
                  nodes['Attribute Math.001'].inputs['Geometry'])
        links.new(nodes['Attribute Combine XYZ'].outputs['Geometry'],
                  nodes['Attribute Mix'].inputs['Geometry'])
        links.new(nodes['Attribute Mix.001'].outputs['Geometry'],
                  nodes['Attribute Math'].inputs['Geometry'])
        links.new(nodes['Attribute Math.001'].outputs['Geometry'],
                  nodes['Attribute Mix.001'].inputs['Geometry'])
        links.new(nodes['Attribute Math'].outputs['Geometry'],
                  nodes['Attribute Combine XYZ'].inputs['Geometry'])
        links.new(nodes['Scaledistance'].outputs['Geometry'],
                  nodes['Offset'].inputs['Geometry'])
        links.new(nodes['Map Range'].outputs['Result'],
                  nodes['Attribute Math'].inputs['B'])
        links.new(nodes['Reroute.002'].outputs['Output'],
                  nodes['Map Range'].inputs['Value'])
        links.new(nodes['Value'].outputs['Value'],
                  nodes['Math'].inputs['Value'])
        links.new(nodes['Math'].outputs['Value'],
                  nodes['Reroute.001'].inputs['Input'])
        links.new(nodes['Scaledistance.002'].outputs['Geometry'],
                  nodes['Attribute Mix.002'].inputs['Geometry'])
        links.new(nodes['Reroute.001'].outputs['Output'],
                  nodes['Offset'].inputs['B'])
        links.new(nodes['Reroute'].outputs['Output'],
                  nodes['Scaledistance'].inputs['B'])
        links.new(nodes['Map Range'].outputs['Result'],
                  nodes['Attribute Math'].inputs['B'])
        links.new(nodes['Reroute.003'].outputs['Output'],
                  nodes['Scaledistance.004'].inputs['Geometry'])
        links.new(nodes['Scaledistance.003'].outputs['Geometry'],
                  nodes['Attribute Mix.003'].inputs['Geometry'])
        links.new(nodes['Attribute Mix.003'].outputs['Geometry'],
                  nodes['Scaledistance'].inputs['Geometry'])
        links.new(nodes['Attribute Mix.002'].outputs['Geometry'],
                  nodes['Reroute.003'].inputs['Input'])
        links.new(nodes['Scaledistance.004'].outputs['Geometry'],
                  nodes['Scaledistance.003'].inputs['Geometry'])
        mod['Input_5'] = 0.31
        mod['Input_7'] = 3.0
        mod['Input_9'] = 20.0
        mod['Input_15'] = 20.0
        mod['Input_11'] = 25.0

        ###########correcting script #

        links.new(nodes['Reroute.001'].outputs['Output'],
                  nodes['Offset'].inputs[4])
        links.new(nodes['Reroute'].outputs['Output'],
                  nodes['Scaledistance'].inputs[4])

        links.new(nodes['Map Range'].outputs['Result'],
                  nodes['Attribute Math'].inputs[4])
        links.new(nodes['Group Input'].outputs[3],
                  nodes['Scaledistance.001'].inputs[2])

        links.new(nodes['Group Input'].outputs[5],
                  nodes['Math'].inputs[1])  # 4 is inner, 5 is speed
        links.new(nodes['Group Input'].outputs[4],
                  nodes['Scaledistance.003'].inputs[2])

        source = nodes['Value'].outputs[0]
        target = bpy.context.scene
        prop = 'default_value'
        data_path = "frame_current"
        id_type = 'SCENE'
        driver = self.add_driver(source, target, prop,
                                 data_path, -1, func="-", id_type=id_type)

    def remove_ripples(self, context, ocean, ob):
        # object selected
        if ob != None:
            for mod in ocean.modifiers[:]:
                if 'Ripples' in mod.name:
                    if ob == mod['Input_15']:
                        ocean.modifiers.remove(mod)
                        ob.aom_data.ripple_parent = None
                    else:
                        print(
                            f"{mod.name} is called Ripples but doesn't have the right object.")
        # ocean selected
        else:
            for mod in reversed(ocean.modifiers[:]):
                if 'Ripples' in mod.name:
                    ob = mod['Input_15']
                    if ob != None:
                        ob.aom_data.ripple_parent = None

                    ocean.modifiers.remove(mod)
                    break

    def add_driver(
        self, source, target, prop, dataPath,
        index=-1, negative=False, func='', id_type=''
    ):
        ''' Add driver to source prop (at index), driven by target dataPath '''

        if index != -1:
            d = source.driver_add(prop, index).driver
        else:
            d = source.driver_add(prop).driver

        v = d.variables.new()
        v.name = prop
        v.targets[0].id_type = id_type
        v.targets[0].id = target
        v.targets[0].data_path = dataPath

        d.expression = func + "(" + v.name + ")" if func else v.name
        d.expression = d.expression if not negative else "-1 * " + d.expression

        return d
