import bpy
#from mathutils import Vector


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

    def get_ocean_mod(self, ocean):
        for mod in ocean.modifiers:
            if mod.type == 'OCEAN':
                return mod
        return None

    def get_dynpaint_mod(self, ocean):
        for mod in ocean.modifiers:
            if mod.type == 'DYNAMIC_PAINT':
                return mod
        return None

    def new_spray(self, context, ocean):
        oceanmod = self.get_ocean_mod(ocean)
        oceanmod.use_spray = True
        oceanmod.spray_layer_name = "spray"

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
        inp.default_value = 0.0
        inp.min_value = 0

        inp = node_group.inputs.new('NodeSocketFloat', 'Density Max')
        inp.default_value = 0.0
        inp.min_value = 0
        inp = node_group.inputs.new('NodeSocketFloat', 'Contrast')
        inp.default_value = 0.0
        inp.min_value = 0
        inp = node_group.inputs.new('NodeSocketFloat', 'MaxParticleScale')
        inp.default_value = 0.0
        inp.min_value = 0
        inp = node_group.inputs.new('NodeSocketFloat', 'MinParticleScale')
        inp.default_value = 0.0
        inp.min_value = 0
        inp = node_group.inputs.new(
            'NodeSocketFloat', 'OverallParticleScale')
        inp.default_value = 0.0
        inp.min_value = 0
        inp = node_group.inputs.new('NodeSocketFloatFactor', 'ObjectSpray')
        inp.default_value = 0.0
        inp.min_value = 0
        inp.max_value = 1
        inp = node_group.inputs.new(
            'NodeSocketCollection', 'SprayPartikleCollection')
        inp = node_group.inputs.new('NodeSocketFloat', 'foam')
        inp.default_value = 0.0
        inp = node_group.inputs.new('NodeSocketFloat', 'spray')
        #inp.default_value = (0, 0, 0)
        inp = node_group.inputs.new('NodeSocketFloat', 'wetmap')
        inp.default_value = 0.0

        node = nodes.new("NodeGroupInput")
        node.name = "Group Input"
        node.location = (-1677, 364)

        node = nodes.new("ShaderNodeMath")
        node.name = "Math"
        node.location = (-1367, 364)
        node.operation = "ADD"
        node.use_clamp = False
        node.inputs[0].default_value = 0.5
        node.inputs[1].default_value = 0.5
        node.inputs[2].default_value = 0.5
        node.outputs[0].default_value = 0.0

        node = nodes.new("ShaderNodeMath")
        node.name = "Math.001"
        node.location = (-1057, 364)
        node.operation = "LOGARITHM"
        node.use_clamp = False
        node.inputs[0].default_value = 0.5
        node.inputs[1].default_value = 51.4
        node.inputs[2].default_value = 0.5
        node.outputs[0].default_value = 0.0

        node = nodes.new("ShaderNodeMapRange")
        node.name = "Map Range"
        node.location = (-747, 364)
        node.interpolation_type = "LINEAR"
        node.clamp = False
        node.inputs[0].default_value = 1.0
        node.inputs[1].default_value = 0.0
        node.inputs[2].default_value = 1.0
        node.inputs[3].default_value = 0.0
        node.inputs[4].default_value = 1.0
        node.inputs[5].default_value = 4.0
        node.outputs[0].default_value = 0.0

        node = nodes.new("ShaderNodeMixRGB")
        node.name = "Mix"
        node.location = (-437, 364)
        node.blend_type = "ADD"
        node.use_clamp = False
        node.inputs[0].default_value = 0.5
        node.inputs[1].default_value = (0.5, 0.5, 0.5, 1.0,)
        node.inputs[2].default_value = (0.5, 0.5, 0.5, 1.0,)
        node.outputs[0].default_value = (0.0, 0.0, 0.0, 0.0,)

        node = nodes.new("NodeReroute")
        node.name = "Reroute"
        node.location = (-127, -187)
        #node.outputs[0].default_value = None

        node = nodes.new("GeometryNodeDistributePointsOnFaces")
        node.name = "Distribute Points on Faces"
        node.location = (-127, 364)
        node.distribute_method = "RANDOM"
        node.inputs[1].default_value = True
        node.inputs[2].default_value = 0.0
        node.inputs[3].default_value = 10.0
        node.inputs[4].default_value = 10.0
        node.inputs[5].default_value = 1.0
        node.inputs[6].default_value = 0
        node.outputs[1].default_value = (0.0, 0.0, 0.0,)
        node.outputs[2].default_value = (0.0, 0.0, 0.0,)

        node = nodes.new("ShaderNodeVectorMath")
        node.name = "Vector Math"
        node.location = (-127, 24)
        node.operation = "SCALE"
        node.inputs[0].default_value = (0.0, 0.0, 0.0,)
        node.inputs[1].default_value = (0.0, 0.0, 0.0,)
        node.inputs[2].default_value = (0.0, 0.0, 0.0,)
        node.inputs[3].default_value = 1.0
        node.outputs[0].default_value = (0.0, 0.0, 0.0,)
        node.outputs[1].default_value = 0.0

        node = nodes.new("NodeReroute")
        node.name = "Reroute"
        node.location = (-127, -187)
        #node.outputs[0].default_value = None

        node = nodes.new("GeometryNodeSetPosition")
        node.name = "Set Position"
        node.location = (227, 364)
        node.inputs[1].default_value = True
        node.inputs[2].default_value = (0.0, 0.0, 0.0,)
        node.inputs[3].default_value = (0.0, 0.0, 0.0,)

        node = nodes.new("FunctionNodeRandomValue")
        node.name = "Random Value"
        node.location = (227, -107)
        node.data_type = "FLOAT"  # "FLOAT_VECTOR"
        node.inputs[0].default_value = (0.0, 0.0, 0.0,)
        node.inputs[1].default_value = (1.0, 1.0, 1.0,)
        node.inputs[2].default_value = 0.0
        node.inputs[3].default_value = 1.0
        node.inputs[4].default_value = 0
        node.inputs[5].default_value = 100
        node.inputs[6].default_value = 0.5
        node.inputs[7].default_value = 0
        node.inputs[8].default_value = 0
        node.outputs[0].default_value = (0.0, 0.0, 0.0,)
        node.outputs[1].default_value = 0.0
        node.outputs[2].default_value = 0
        node.outputs[3].default_value = False

        node = nodes.new("ShaderNodeCombineXYZ")
        node.name = "CombHeight"
        node.location = (-127, 300)

        node = nodes.new("GeometryNodeCollectionInfo")
        node.name = "Collection Info"
        node.location = (227, 134)
        node.transform_space = "ORIGINAL"
        node.inputs[1].default_value = True
        node.inputs[2].default_value = True

        node = nodes.new("GeometryNodeInstanceOnPoints")
        node.name = "Instance on Points"
        node.location = (537, 328)
        node.inputs[1].default_value = True
        node.inputs[3].default_value = True
        node.inputs[4].default_value = 0
        node.inputs[5].default_value = (0.0, 0.0, 0.0,)
        node.inputs[6].default_value = (1.0, 1.0, 1.0,)

        node = nodes.new("GeometryNodeScaleInstances")
        node.name = "Scale Instances"
        node.location = (822, 290)
        node.inputs[1].default_value = True
        node.inputs[2].default_value = (1.0, 1.0, 1.0,)
        node.inputs[3].default_value = (0.0, 0.0, 0.0,)
        node.inputs[4].default_value = True

        node = nodes.new("GeometryNodeJoinGeometry")
        node.name = "Join Geometry"
        node.location = (1157, 364)

        node = nodes.new("NodeGroupOutput")
        node.name = "Group Output"
        node.location = (1467, 364)
        links.new(nodes['Group Input'].outputs[0],
                  nodes['Distribute Points on Faces'].inputs[0])
        links.new(nodes['Group Input'].outputs[0],
                  nodes['Reroute.001'].inputs[0])
        links.new(nodes['Group Input'].outputs[1],
                  nodes['Vector Math'].inputs[3])
        links.new(nodes['Group Input'].outputs[2],
                  nodes['Distribute Points on Faces'].inputs[4])
        links.new(nodes['Group Input'].outputs[2],
                  nodes['Distribute Points on Faces'].inputs[3])
        links.new(nodes['Group Input'].outputs[3],  nodes['Math'].inputs[0])
        links.new(nodes['Group Input'].outputs[4],
                  nodes['Random Value'].inputs[3])
        links.new(nodes['Group Input'].outputs[5],
                  nodes['Random Value'].inputs[2])
        links.new(nodes['Group Input'].outputs[6],
                  nodes['Scale Instances'].inputs[2])
        links.new(nodes['Group Input'].outputs[7],  nodes['Mix'].inputs[0])
        links.new(nodes['Group Input'].outputs[8],  nodes['Reroute'].inputs[0])
        links.new(nodes['Group Input'].outputs[9],
                  nodes['Map Range'].inputs[0])
        links.new(nodes['Group Input'].outputs[10],
                  nodes['Vector Math'].inputs[0])
        links.new(nodes['Group Input'].outputs[11],  nodes['Mix'].inputs[2])
        links.new(nodes['Math'].outputs['Value'],
                  nodes['Math.001'].inputs['Value'])

        links.new(nodes['Math.001'].outputs['Value'],
                  nodes['Map Range'].inputs['From Min'])
        links.new(nodes['Map Range'].outputs['Result'],
                  nodes['Mix'].inputs['Color1'])
        links.new(nodes['Join Geometry'].outputs['Geometry'],
                  nodes['Group Output'].inputs['Geometry'])
        links.new(nodes['Mix'].outputs['Color'],
                  nodes['Distribute Points on Faces'].inputs['Selection'])
        links.new(nodes['Distribute Points on Faces'].outputs['Points'],
                  nodes['Set Position'].inputs['Geometry'])
        links.new(nodes['Set Position'].outputs['Geometry'],
                  nodes['Instance on Points'].inputs['Points'])
        links.new(nodes['Instance on Points'].outputs['Instances'],
                  nodes['Scale Instances'].inputs['Instances'])
        links.new(nodes['Collection Info'].outputs['Geometry'],
                  nodes['Instance on Points'].inputs['Instance'])
        links.new(nodes['Reroute'].outputs['Output'],
                  nodes['Collection Info'].inputs['Collection'])
        # links.new(nodes['Random Value'].outputs[1],
        #          nodes['CombRandom'].inputs['X'])
        # links.new(nodes['Random Value'].outputs[1],
        #          nodes['CombRandom'].inputs['Y'])
        links.new(nodes['Vector Math'].outputs[0],
                  nodes['CombHeight'].inputs['Z'])
        links.new(nodes['CombHeight'].outputs[0],
                  nodes['Set Position'].inputs['Offset'])
        links.new(nodes['Random Value'].outputs[1],
                  nodes['Instance on Points'].inputs['Scale'])
        links.new(nodes['Scale Instances'].outputs['Instances'],
                  nodes['Join Geometry'].inputs['Geometry'])

        links.new(nodes['Reroute.001'].outputs['Output'],
                  nodes['Join Geometry'].inputs['Geometry'])

        mod['Input_2'] = 2.42
        mod['Input_2_use_attribute'] = False
        mod['Input_3'] = 50.0
        mod['Input_3_use_attribute'] = False
        mod['Input_4'] = 1.0
        mod['Input_4_use_attribute'] = False
        mod['Input_5'] = 0.5
        mod['Input_5_use_attribute'] = False
        mod['Input_6'] = 0.01
        mod['Input_6_use_attribute'] = False
        mod['Input_7'] = 0.06
        mod['Input_7_use_attribute'] = False
        mod['Input_8'] = 0.00
        mod['Input_8_use_attribute'] = False
        mod['Input_9'] = None
        mod['Input_9_use_attribute'] = False
        mod['Input_10'] = 0.06
        mod['Input_10_use_attribute'] = True
        mod['Input_10_attribute_name'] = 'foam'
        mod['Input_12'] = 0.06
        mod['Input_12_use_attribute'] = True
        mod['Input_12_attribute_name'] = 'dp_wetmap'

        mod['Input_11'] = 0.06
        mod['Input_11_use_attribute'] = True
        mod['Input_11_attribute_name'] = 'spray'

        nodes['Reroute.001'].location = (-85.0324, 503)
        nodes['CombHeight'].location = (55, 174)

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
            mod['Input_7'] = ob
            ob.aom_data.ripple_parent = ocean

        ocean.modifiers.active = mod

        self.move_above_DP(ocean, mod)

        # driver

    def make_rippels_nodes(self, mod, node_group):
        self.remove_nodes(node_group)
        nodes = node_group.nodes
        links = node_group.links

        inp = node_group.inputs.new('NodeSocketFloat', 'Wavelength')
        inp.default_value = 0.31
        inp = node_group.inputs.new('NodeSocketFloat', 'Amplitude')
        inp.default_value = 2.0
        inp = node_group.inputs.new('NodeSocketFloat', 'OuterFalloff')
        inp.default_value = 20.0
        inp = node_group.inputs.new('NodeSocketFloat', 'Innercut')
        inp.default_value = 25.0
        inp = node_group.inputs.new('NodeSocketFloat', 'Speed')
        inp.default_value = 10.0
        inp = node_group.inputs.new('NodeSocketObject', 'Object')

        node = nodes.new("NodeGroupInput")
        node.name = "Group Input"
        node.location = (-1488, 413)

        node = nodes.new("GeometryNodeObjectInfo")
        node.name = "Object Info"
        node.location = (-1208, 338)
        node.transform_space = "ORIGINAL"
        node.inputs[1].default_value = False
        node.outputs[0].default_value = (0.0, 0.0, 0.0,)
        node.outputs[1].default_value = (0.0, 0.0, 0.0,)
        node.outputs[2].default_value = (0.0, 0.0, 0.0,)
        node.transform_space = 'RELATIVE'

        node = nodes.new("GeometryNodeProximity")
        node.name = "Geometry Proximity.001"
        node.location = (-968, 338)
        node.inputs[1].default_value = (0.0, 0.0, 0.0,)
        node.outputs[0].default_value = (0.0, 0.0, 0.0,)
        node.outputs[1].default_value = 0.0

        node = nodes.new("NodeReroute")
        node.name = "Reroute.002"
        node.location = (-728, 338)
        #node.inputs[0].default_value = 0.0
        #node.outputs[0].default_value = 0.0

        node = nodes.new("ShaderNodeValue")
        node.name = "Time"
        node.location = (-612, 338)
        node.outputs[0].default_value = -147.0

        node = nodes.new("ShaderNodeMath")
        node.name = "Math.005"
        node.location = (-612, 238)
        node.operation = "SUBTRACT"
        node.use_clamp = False
        node.inputs[0].default_value = 0.5
        node.inputs[1].default_value = 0.5
        node.inputs[2].default_value = 0.5
        node.outputs[0].default_value = 0.0

        node = nodes.new("ShaderNodeMath")
        node.name = "Math.009"
        node.location = (-372, 338)
        node.operation = "DIVIDE"
        node.use_clamp = False
        node.inputs[0].default_value = 0.5
        node.inputs[1].default_value = 0.0
        node.inputs[2].default_value = 0.5
        node.outputs[0].default_value = 0.0

        node = nodes.new("ShaderNodeMath")
        node.name = "Math.011"
        node.location = (-372, 164)
        node.operation = "DIVIDE"
        node.use_clamp = False
        node.inputs[0].default_value = 0.5
        node.inputs[1].default_value = 0.0
        node.inputs[2].default_value = 0.5
        node.outputs[0].default_value = 0.0

        node = nodes.new("ShaderNodeMath")
        node.name = "Math.007"
        node.location = (-372, -10)
        node.operation = "SUBTRACT"
        node.use_clamp = False
        node.inputs[0].default_value = 20.0
        node.inputs[1].default_value = 0.5
        node.inputs[2].default_value = 0.5
        node.outputs[0].default_value = 0.0

        node = nodes.new("ShaderNodeMath")
        node.name = "Math.006"
        node.location = (-372, -184)
        node.operation = "GREATER_THAN"
        node.use_clamp = False
        node.inputs[0].default_value = 0.0
        node.inputs[1].default_value = 0.0
        node.inputs[2].default_value = 0.5
        node.outputs[0].default_value = 0.0

        node = nodes.new("ShaderNodeMath")
        node.name = "Math.010"
        node.location = (-132, 338)
        node.operation = "ADD"
        node.use_clamp = False
        node.inputs[0].default_value = 0.5
        node.inputs[1].default_value = 0.0
        node.inputs[2].default_value = 0.5
        node.outputs[0].default_value = 0.0

        node = nodes.new("ShaderNodeMath")
        node.name = "Math.008"
        node.location = (-132, 164)
        node.operation = "GREATER_THAN"
        node.use_clamp = False
        node.inputs[0].default_value = 0.5
        node.inputs[1].default_value = 0.0
        node.inputs[2].default_value = 0.5
        node.outputs[0].default_value = 0.0

        node = nodes.new("ShaderNodeMixRGB")
        node.name = "Mix"
        node.location = (-132, -10)
        node.blend_type = "MIX"
        node.use_clamp = False
        node.inputs[0].default_value = 0.5
        node.inputs[1].default_value = (0.5, 0.5, 0.5, 1.0,)
        node.inputs[2].default_value = (0.0, 0.0, 0.0, 1.0,)
        node.outputs[0].default_value = (0.0, 0.0, 0.0, 0.0,)

        node = nodes.new("ShaderNodeMixRGB")
        node.name = "Mix.001"
        node.location = (108, 186)
        node.blend_type = "MIX"
        node.use_clamp = False
        node.inputs[0].default_value = 0.5
        node.inputs[1].default_value = (0.0, 0.0, 0.0, 1.0,)
        node.inputs[2].default_value = (0.0, 0.0, 0.0, 1.0,)
        node.outputs[0].default_value = (0.0, 0.0, 0.0, 0.0,)

        node = nodes.new("ShaderNodeMath")
        node.name = "Math.012"
        node.location = (108, 338)
        node.operation = "SINE"
        node.use_clamp = False
        node.inputs[0].default_value = 0.5
        node.inputs[1].default_value = 0.0
        node.inputs[2].default_value = 0.5
        node.outputs[0].default_value = 0.0

        node = nodes.new("ShaderNodeMath")
        node.name = "Math.013"
        node.location = (348, 338)
        node.operation = "MULTIPLY"
        node.use_clamp = False
        node.inputs[0].default_value = 0.5
        node.inputs[1].default_value = 0.0
        node.inputs[2].default_value = 0.5
        node.outputs[0].default_value = 0.0

        node = nodes.new("ShaderNodeMapRange")
        node.name = "Map Range"
        node.location = (348, 164)
        node.interpolation_type = "LINEAR"
        node.clamp = False
        node.inputs[0].default_value = 1.0
        node.inputs[1].default_value = 0.0
        node.inputs[2].default_value = 1.0
        node.inputs[3].default_value = 0.0
        node.inputs[4].default_value = 0.01
        node.inputs[5].default_value = 4.0
        node.outputs[0].default_value = 0.0

        node = nodes.new("ShaderNodeMath")
        node.name = "Math.014"
        node.location = (588, 338)
        node.operation = "MULTIPLY"
        node.use_clamp = False
        node.inputs[0].default_value = 0.5
        node.inputs[1].default_value = 0.0
        node.inputs[2].default_value = 0.5
        node.outputs[0].default_value = 0.0

        node = nodes.new("ShaderNodeCombineXYZ")
        node.name = "Combine XYZ"
        node.location = (828, 338)
        node.inputs[0].default_value = 0.0
        node.inputs[1].default_value = 0.0
        node.inputs[2].default_value = 0.0
        node.outputs[0].default_value = (0.0, 0.0, 0.0,)

        node = nodes.new("GeometryNodeSetPosition")
        node.name = "Set Position"
        node.location = (1068, 338)
        node.inputs[1].default_value = True
        node.inputs[2].default_value = (0.0, 0.0, 0.0,)
        node.inputs[3].default_value = (0.0, 0.0, 0.0,)

        node = nodes.new("NodeGroupOutput")
        node.name = "Group Output.001"
        node.location = (1308, 338)
        links.new(nodes['Group Input'].outputs[0],
                  nodes['Set Position'].inputs[0])
        links.new(nodes['Group Input'].outputs[1],
                  nodes['Math.009'].inputs[1])
        links.new(nodes['Group Input'].outputs[2],
                  nodes['Map Range'].inputs[0])
        links.new(nodes['Group Input'].outputs[3],
                  nodes['Math.005'].inputs[0])
        links.new(nodes['Group Input'].outputs[4],
                  nodes['Math.008'].inputs[0])
        links.new(nodes['Group Input'].outputs[5],
                  nodes['Math.011'].inputs[1])
        links.new(nodes['Group Input'].outputs[6],
                  nodes['Object Info'].inputs[0])
        links.new(nodes['Object Info'].outputs['Geometry'],
                  nodes['Geometry Proximity.001'].inputs['Target'])
        links.new(nodes['Reroute.002'].outputs['Output'],
                  nodes['Math.005'].inputs[1])
        links.new(nodes['Math.006'].outputs['Value'],
                  nodes['Mix'].inputs['Fac'])
        links.new(nodes['Math.005'].outputs['Value'],
                  nodes['Mix'].inputs['Color1'])
        links.new(nodes['Reroute.002'].outputs['Output'],
                  nodes['Math.007'].inputs[1])
        links.new(nodes['Mix'].outputs['Color'],
                  nodes['Mix.001'].inputs['Color2'])
        links.new(nodes['Math.008'].outputs['Value'],
                  nodes['Mix.001'].inputs['Fac'])
        links.new(nodes['Reroute.002'].outputs['Output'],
                  nodes['Math.009'].inputs['Value'])
        links.new(nodes['Geometry Proximity.001'].outputs['Distance'],
                  nodes['Reroute.002'].inputs['Input'])
        links.new(nodes['Math.009'].outputs['Value'],
                  nodes['Math.010'].inputs['Value'])
        links.new(nodes['Time'].outputs['Value'],
                  nodes['Math.011'].inputs['Value'])
        links.new(nodes['Math.011'].outputs[0],
                  nodes['Math.010'].inputs[1])
        links.new(nodes['Math.010'].outputs['Value'],
                  nodes['Math.012'].inputs['Value'])
        links.new(nodes['Mix.001'].outputs['Color'],
                  nodes['Math.013'].inputs[1])
        links.new(nodes['Math.012'].outputs['Value'],
                  nodes['Math.013'].inputs['Value'])
        links.new(nodes['Math.013'].outputs[0],
                  nodes['Math.014'].inputs[0])
        links.new(nodes['Map Range'].outputs['Result'],
                  nodes['Math.014'].inputs[1])
        links.new(nodes['Set Position'].outputs['Geometry'],
                  nodes['Group Output.001'].inputs['Geometry'])
        links.new(nodes['Math.014'].outputs['Value'],
                  nodes['Combine XYZ'].inputs['Z'])
        links.new(nodes['Combine XYZ'].outputs['Vector'],
                  nodes['Set Position'].inputs['Offset'])
        links.new(nodes['Math.007'].outputs['Value'],
                  nodes['Math.008'].inputs[1])
        links.new(nodes['Math.005'].outputs['Value'],
                  nodes['Math.006'].inputs[1])

        mod['Input_2'] = 0.31
        mod['Input_2_use_attribute'] = False
        mod['Input_3'] = 1.0
        mod['Input_3_use_attribute'] = False
        mod['Input_4'] = 17.35
        mod['Input_4_use_attribute'] = False
        mod['Input_5'] = 20.0
        mod['Input_5_use_attribute'] = False
        mod['Input_6'] = 10.0
        mod['Input_6_use_attribute'] = False
        mod['Input_7'] = None
        mod['Input_7_use_attribute'] = False

        source = nodes['Time'].outputs[0]
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
                    if ob == mod['Input_7']:
                        ocean.modifiers.remove(mod)
                        ob.aom_data.ripple_parent = None
                    else:
                        print(
                            f"{mod.name} is called Ripples but doesn't have the right object.")
        # ocean selected
        else:
            for mod in reversed(ocean.modifiers[:]):
                if 'Ripples' in mod.name:
                    ob = mod['Input_7']
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
