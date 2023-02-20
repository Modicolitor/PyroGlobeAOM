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
        #make spray nodegroup 
        nodegroup = self.make_spray_nodes(mod, mod.node_group)
        
        # self.move_mod_one_up(ocean, mod)
        
        
        #nodegroup.name = "Spray"
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
        nh = False
        for ng in bpy.data.node_groups:
            if ng.name == 'Spray':
                nh= True
                node_group = ng

        if not nh:
            node_group = bpy.data.node_groups.new(name="Spray", type='GeometryNodeTree')
        
        mod.node_group = node_group
        
        self.remove_nodes(node_group)
        nodes = node_group.nodes
        links = node_group.links

        if not nh:
            inp = node_group.inputs.new('NodeSocketGeometry', 'Geometry')

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
                  nodes['Group Output'].inputs[0])
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

        mod['Input_1'] = 2.42
        mod['Input_1_use_attribute'] = False
        mod['Input_2'] = 50.0
        mod['Input_2_use_attribute'] = False
        mod['Input_3'] = 1.0
        mod['Input_3_use_attribute'] = False
        mod['Input_4'] = 0.5
        mod['Input_4_use_attribute'] = False
        mod['Input_5'] = 0.01
        mod['Input_5_use_attribute'] = False
        mod['Input_6'] = 0.06
        mod['Input_6_use_attribute'] = False
        mod['Input_7'] = 0.00
        mod['Input_7_use_attribute'] = False
        mod['Input_8'] = None
        mod['Input_8_use_attribute'] = False
        mod['Input_9'] = 0.06
        mod['Input_9_use_attribute'] = True
        mod['Input_9_attribute_name'] = 'foam'
        mod['Input_10'] = 0.06
        mod['Input_11_use_attribute'] = True
        mod['Input_11_attribute_name'] = 'dp_wetmap'

        mod['Input_10'] = 0.06
        mod['Input_10_use_attribute'] = True
        mod['Input_10_attribute_name'] = 'spray'

        nodes['Reroute.001'].location = (-85.0324, 503)
        nodes['CombHeight'].location = (55, 174)
        
        return node_group

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
        #make node group
        nodegroup = self.make_rippels_nodes(mod, mod.node_group)
        
        #nodegroup.name = "Ripples"
        #self.move_mod_one_up(ocean, mod)

        self.make_rippels_nodes(mod, mod.node_group)
        #print(f'ob.name {ob.name}')
        if ob != None:
            mod['Input_6'] = ob
            ob.aom_data.ripple_parent = ocean

        ocean.modifiers.active = mod

        self.move_above_DP(ocean, mod)

        # driver

    def label_nodes(self, node_tree):

        nodes = node_tree.nodes

        for node in nodes:
            node.label = node.name

    def make_rippels_nodes(self, mod, node_group):
        nh = False
        for ng in bpy.data.node_groups:
            if ng.name == 'Ripples':
                nh= True
                node_group = ng

        if not nh:
            node_group = bpy.data.node_groups.new(name ='Ripples', type='GeometryNodeTree')
        
        mod.node_group = node_group
        
        self.remove_nodes(node_group)
        nodes = node_group.nodes
        links = node_group.links

        if not nh:
            inp = node_group.inputs.new('NodeSocketGeometry', 'Geometry')
            
            inp = node_group.inputs.new('NodeSocketFloat', 'Wavelength')
            inp.default_value = 0.31
            wlid= inp.identifier 
            inp = node_group.inputs.new('NodeSocketFloat', 'Amplitude')
            inp.default_value = 2.0
            ampid= inp.identifier 
            inp = node_group.inputs.new('NodeSocketFloat', 'OuterFalloff')
            outerid= inp.identifier 
            inp.default_value = 20.0
            inp = node_group.inputs.new('NodeSocketFloat', 'Innercut')
            inp.default_value = 25.0
            innerid = inp.identifier 
            inp = node_group.inputs.new('NodeSocketFloat', 'Speed')
            inp.default_value = 10.0
            speedid = inp.identifier
            inp = node_group.inputs.new('NodeSocketObject', 'Object') #NodeSocketObject
            obsockid = inp.identifier 
        
      
        #######################
        
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
        node.name = "Group Output"
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
                  nodes['Group Output'].inputs[0])
        links.new(nodes['Math.014'].outputs['Value'],
                  nodes['Combine XYZ'].inputs['Z'])
        links.new(nodes['Combine XYZ'].outputs['Vector'],
                  nodes['Set Position'].inputs['Offset'])
        links.new(nodes['Math.007'].outputs['Value'],
                  nodes['Math.008'].inputs[1])
        links.new(nodes['Math.005'].outputs['Value'],
                  nodes['Math.006'].inputs[1])

        mod['Input_1'] = 0.31
        mod['Input_1_use_attribute'] = False
        mod['Input_2'] = 1.0
        mod['Input_2_use_attribute'] = False
        mod['Input_3'] = 17.35
        mod['Input_3_use_attribute'] = False
        mod['Input_4'] = 20.0
        mod['Input_4_use_attribute'] = False
        mod['Input_5'] = 10.0
        mod['Input_5_use_attribute'] = False
        mod['Input_6'] = None
        

        source = nodes['Time'].outputs[0]
        target = bpy.context.scene
        prop = 'default_value'
        data_path = "frame_current"
        id_type = 'SCENE'
        driver = self.add_driver(source, target, prop,
                                 data_path, -1, func="-", id_type=id_type)
        return node_group 

    def remove_ripples(self, context, ocean, ob):
        # object selected
        if ob != None:
            for mod in ocean.modifiers[:]:
                if 'Ripples' in mod.name:
                    if ob == mod['Input_6']:
                        ocean.modifiers.remove(mod)
                        ob.aom_data.ripple_parent = None
                    else:
                        print(
                            f"{mod.name} is called Ripples but doesn't have the right object.")
        # ocean selected
        else:
            for mod in reversed(ocean.modifiers[:]):
                if 'Ripples' in mod.name:
                    ob = mod['Input_6']
                    if ob != None:
                        ob.aom_data.ripple_parent = None

                    ocean.modifiers.remove(mod)
                    break

    def make_FloatRotMove_nodegroup(self):
        ngname = 'AOMFloatRotMove'
        if ngname in bpy.data.node_groups:
            return bpy.data.node_groups[ngname]

        node_group = bpy.data.node_groups.new(ngname, 'GeometryNodeTree')
        # self.remove_nodes(node_group)
        nodes = node_group.nodes
        links = node_group.links

        inp = node_group.inputs.new('NodeSocketGeometry', 'Target Geometry')
        #inp.type = 'GEOMETRY'
        inp = node_group.inputs.new('NodeSocketFloat', 'X')
        inp.default_value = 1.0
        inp = node_group.inputs.new('NodeSocketFloat', 'Y')
        inp.default_value = 0.0
        inp = node_group.inputs.new('NodeSocketFloat', 'Z')
        inp.default_value = 18.3
        inp = node_group.inputs.new('NodeSocketFloat', 'XDistance')
        inp.default_value = 1.0
        inp = node_group.inputs.new('NodeSocketFloat', 'YDistance')
        inp.default_value = 0.0
        inp = node_group.inputs.new('NodeSocketFloat', 'ZDistance')
        inp.default_value = 0.0
        inp = node_group.inputs.new('NodeSocketFloat', 'RotSensitivity')
        inp.default_value = 1.0
        inp = node_group.inputs.new('NodeSocketFloat', 'MoveSensitivity')
        inp.default_value = 1.0

        node = nodes.new("NodeGroupInput")
        node.name = "Group Input"
        node.location = (-2697, 0)

        node = nodes.new("NodeReroute")
        node.name = "Reroute.005"
        node.location = (-2460, -436)

        node = nodes.new("NodeReroute")
        node.name = "Reroute"
        node.location = (-2395, -316)

        node = nodes.new("NodeReroute")
        node.name = "Reroute.006"
        node.location = (-2387, -469)

        node = nodes.new("NodeReroute")
        node.name = "Reroute.003"
        node.location = (-2358, -136)

        frameCoords = nodes.new("NodeFrame")
        frameCoords.name = "Coordinates"
        frameCoords.location = (-2303, -306)

        frameDetect = nodes.new("NodeFrame")
        frameDetect.name = "Detection"
        frameDetect.location = (-1240, -700)

        frameDisplay = nodes.new("NodeFrame")
        frameDisplay.name = "Display Detectionline"
        frameDisplay.location = (480, 1140)

        frameMove = nodes.new("NodeFrame")
        frameMove.name = "Move"
        frameMove.location = (1180, -20)

        frameRot = nodes.new("NodeFrame")
        frameRot.name = "Rotate"
        frameRot.location = (1180, -200)

        node = nodes.new("ShaderNodeMath")
        node.name = "RotMath1"
        node.parent = frameRot
        node.location = (-2181, -398)
        node.operation = "SUBTRACT"
        node.use_clamp = False
        node.inputs[0].default_value = 0.5
        node.inputs[1].default_value = 0.5
        node.inputs[2].default_value = 0.5
        node.outputs[0].default_value = 0.0

        node = nodes.new("ShaderNodeMath")
        node.name = "MoveMath1"
        node.parent = frameMove
        node.location = (-1978, -140)
        node.operation = "MULTIPLY"
        node.use_clamp = False
        node.inputs[0].default_value = 0.5
        node.inputs[1].default_value = -1.0
        node.inputs[2].default_value = 0.5
        node.outputs[0].default_value = 0.0

        node = nodes.new("ShaderNodeMath")
        node.name = "RotMath2"
        node.parent = frameRot
        node.location = (-1945, -392)
        node.operation = "MULTIPLY"
        node.use_clamp = False
        node.inputs[0].default_value = 0.5
        node.inputs[1].default_value = 0.32
        node.inputs[2].default_value = 0.5
        node.outputs[0].default_value = 0.0

        node = nodes.new("GeometryNodeInputIndex")
        node.name = "DispayIndex"
        node.parent = frameDisplay
        node.location = (-1850, -924)
        node.outputs[0].default_value = 0

        node = nodes.new("NodeReroute")
        node.name = "Reroute.010"
        node.parent = frameMove
        node.location = (-1775, -320)

        node = nodes.new("NodeReroute")
        node.name = "Reroute.004"
        node.location = (-1651, -94)

        node = nodes.new("ShaderNodeMath")
        node.name = "RotMath3"
        node.parent = frameRot
        node.location = (-1635, -218)
        node.operation = "MULTIPLY"
        node.use_clamp = False
        node.inputs[0].default_value = 0.5
        node.inputs[1].default_value = 1.0
        node.inputs[2].default_value = 0.5
        node.outputs[0].default_value = 0.0

        node = nodes.new("ShaderNodeMath")
        node.name = "MoveMath2"
        node.parent = frameMove
        node.location = (-1630, -156)
        node.operation = "MULTIPLY"
        node.use_clamp = False
        node.inputs[0].default_value = 0.5
        node.inputs[1].default_value = 1.0
        node.inputs[2].default_value = 0.5
        node.outputs[0].default_value = 0.0

        node = nodes.new("GeometryNodeMeshLine")
        node.name = "DisplayLine"
        node.parent = frameDisplay
        node.location = (-1625, -395)
        node.inputs[0].default_value = 2
        node.inputs[1].default_value = 1.0
        node.inputs[2].default_value = (0.0, 0.0, 0.0,)
        node.inputs[3].default_value = (1.0, 0.0, 0.0,)

        node = nodes.new("FunctionNodeCompare")
        node.name = "DisplayFind0"
        node.parent = frameDisplay
        node.location = (-1481, -681)
        node.data_type = "FLOAT"
        node.operation = "EQUAL"
        node.inputs[0].default_value = 0.0
        node.inputs[1].default_value = 0.0
        node.inputs[2].default_value = 0
        node.inputs[3].default_value = 0
        node.inputs[4].default_value = (0.0, 0.0, 0.0,)
        node.inputs[5].default_value = (0.0, 0.0, 0.0,)
        node.inputs[6].default_value = (0.0, 0.0, 0.0, 0.0,)
        node.inputs[7].default_value = (0.0, 0.0, 0.0, 0.0,)
        node.inputs[8].default_value = ""
        node.inputs[9].default_value = ""
        node.inputs[10].default_value = 0.9
        node.inputs[11].default_value = 0.09
        node.inputs[12].default_value = 0.0
        node.outputs[0].default_value = False

        node = nodes.new("FunctionNodeCompare")
        node.name = "DisplayFind1"
        node.parent = frameDisplay
        node.location = (-1480, -860)
        node.data_type = "FLOAT"
        node.operation = "EQUAL"
        node.inputs[0].default_value = 1.0
        node.inputs[1].default_value = 0.0
        node.inputs[2].default_value = 0
        node.inputs[3].default_value = 0
        node.inputs[4].default_value = (0.0, 0.0, 0.0,)
        node.inputs[5].default_value = (0.0, 0.0, 0.0,)
        node.inputs[6].default_value = (0.0, 0.0, 0.0, 0.0,)
        node.inputs[7].default_value = (0.0, 0.0, 0.0, 0.0,)
        node.inputs[8].default_value = ""
        node.inputs[9].default_value = ""
        node.inputs[10].default_value = 0.9
        node.inputs[11].default_value = 0.09
        node.inputs[12].default_value = 0.0
        node.outputs[0].default_value = False

        node = nodes.new("GeometryNodeSetPosition")
        node.name = "DisplaySetP1"
        node.parent = frameDisplay
        node.location = (-1300, -395)
        node.inputs[1].default_value = True
        node.inputs[2].default_value = (0.0, 0.0, 0.0,)
        node.inputs[3].default_value = (0.0, 0.0, 0.0,)

        node = nodes.new("ShaderNodeMath")
        node.name = "Math"
        node.parent = frameDisplay
        node.location = (-1191, -926)
        node.operation = "MULTIPLY"
        node.use_clamp = False
        node.inputs[0].default_value = 0.5
        node.inputs[1].default_value = -1.0
        node.inputs[2].default_value = 0.5
        node.outputs[0].default_value = 0.0

        node = nodes.new("GeometryNodeSetPosition")
        node.name = "DisplaySetP2"
        node.parent = frameDisplay
        node.location = (-990, -395)
        node.inputs[1].default_value = True
        node.inputs[2].default_value = (0.0, 0.0, 0.0,)
        node.inputs[3].default_value = (0.0, 0.0, 0.0,)

        node = nodes.new("ShaderNodeCombineXYZ")
        node.name = "DisplayExtrudeCombine"
        node.parent = frameDisplay
        node.location = (-977, -652)
        node.inputs[0].default_value = 0.0
        node.inputs[1].default_value = 0.0
        node.inputs[2].default_value = 0.0
        node.outputs[0].default_value = (0.0, 0.0, 0.0,)

        node = nodes.new("GeometryNodeExtrudeMesh")
        node.name = "DisplayExtrude"
        node.parent = frameDisplay
        node.location = (-760, -400)
        node.mode = 'VERTICES'
        node.inputs[1].default_value = True
        node.inputs[2].default_value = (0.0, 0.0, 0.0,)
        node.inputs[3].default_value = 1.0
        node.inputs[4].default_value = True
        node.outputs[1].default_value = False
        node.outputs[2].default_value = False

        node = nodes.new("GeometryNodeRaycast")
        node.name = "RayP1"
        node.parent = frameDetect
        node.location = (-66, 480)
        node.data_type = "FLOAT"
        node.inputs[1].default_value = (0.0, 0.0, 0.0,)
        node.inputs[2].default_value = 0.0
        node.inputs[3].default_value = (0.0, 0.0, 0.0, 0.0,)
        node.inputs[4].default_value = False
        node.inputs[5].default_value = 0
        node.inputs[6].default_value = (0.0, 0.0, 0.0,)
        node.inputs[7].default_value = (0.0, 0.0, -1.0,)
        node.inputs[8].default_value = 100.0
        node.outputs[0].default_value = False
        node.outputs[1].default_value = (0.0, 0.0, 0.0,)
        node.outputs[2].default_value = (0.0, 0.0, 0.0,)
        node.outputs[3].default_value = 0.0
        node.outputs[4].default_value = (0.0, 0.0, 0.0,)
        node.outputs[5].default_value = 0.0
        node.outputs[6].default_value = (0.0, 0.0, 0.0, 0.0,)
        node.outputs[7].default_value = False
        node.outputs[8].default_value = 0

        node = nodes.new("GeometryNodeRaycast")
        node.name = "RayP2"
        node.parent = frameDetect
        node.location = (-61, 71)
        node.data_type = "FLOAT"
        node.inputs[1].default_value = (0.0, 0.0, 0.0,)
        node.inputs[2].default_value = 0.0
        node.inputs[3].default_value = (0.0, 0.0, 0.0, 0.0,)
        node.inputs[4].default_value = False
        node.inputs[5].default_value = 0
        node.inputs[6].default_value = (0.0, 0.0, 0.0,)
        node.inputs[7].default_value = (0.0, 0.0, -1.0,)
        node.inputs[8].default_value = 100.0
        node.outputs[0].default_value = False
        node.outputs[1].default_value = (0.0, 0.0, 0.0,)
        node.outputs[2].default_value = (0.0, 0.0, 0.0,)
        node.outputs[3].default_value = 0.0
        node.outputs[4].default_value = (0.0, 0.0, 0.0,)
        node.outputs[5].default_value = 0.0
        node.outputs[6].default_value = (0.0, 0.0, 0.0, 0.0,)
        node.outputs[7].default_value = False
        node.outputs[8].default_value = 0

        node = nodes.new("ShaderNodeMath")
        node.name = "Math.004"
        node.parent = frameCoords
        node.location = (31, 270)
        node.operation = "MULTIPLY"
        node.use_clamp = False
        node.inputs[0].default_value = 0.5
        node.inputs[1].default_value = 0.5
        node.inputs[2].default_value = 0.5
        node.outputs[0].default_value = 0.0

        node = nodes.new("ShaderNodeMath")
        node.name = "Math.005"
        node.parent = frameCoords
        node.location = (31, -13)
        node.operation = "MULTIPLY"
        node.use_clamp = False
        node.inputs[0].default_value = 0.5
        node.inputs[1].default_value = 0.5
        node.inputs[2].default_value = 0.5
        node.outputs[0].default_value = 0.0

        node = nodes.new("ShaderNodeMath")
        node.name = "Math.007"
        node.parent = frameCoords
        node.location = (31, -297)
        node.operation = "MULTIPLY"
        node.use_clamp = False
        node.inputs[0].default_value = 0.5
        node.inputs[1].default_value = 0.5
        node.inputs[2].default_value = 0.5
        node.outputs[0].default_value = 0.0

        node = nodes.new("NodeReroute")
        node.name = "Reroute.001"
        node.parent = frameCoords
        node.location = (31, 22)

        node = nodes.new("NodeReroute")
        node.name = "Reroute.002"
        node.parent = frameCoords
        node.location = (31, -261)

        node = nodes.new("ShaderNodeMath")
        node.name = "Math.013"
        node.parent = frameCoords
        node.location = (341, -933)
        node.operation = "SUBTRACT"
        node.use_clamp = False
        node.inputs[0].default_value = 0.5
        node.inputs[1].default_value = 0.5
        node.inputs[2].default_value = 0.5
        node.outputs[0].default_value = 0.0

        node = nodes.new("ShaderNodeMath")
        node.name = "Math.008"
        node.parent = frameCoords
        node.location = (341, 306)
        node.operation = "ADD"
        node.use_clamp = False
        node.inputs[0].default_value = 0.5
        node.inputs[1].default_value = 0.5
        node.inputs[2].default_value = 0.5
        node.outputs[0].default_value = 0.0

        node = nodes.new("ShaderNodeMath")
        node.name = "Math.010"
        node.parent = frameCoords
        node.location = (341, 58)
        node.operation = "ADD"
        node.use_clamp = False
        node.inputs[0].default_value = 0.5
        node.inputs[1].default_value = 0.5
        node.inputs[2].default_value = 0.5
        node.outputs[0].default_value = 0.0

        node = nodes.new("ShaderNodeMath")
        node.name = "Math.009"
        node.parent = frameCoords
        node.location = (341, -437)
        node.operation = "SUBTRACT"
        node.use_clamp = False
        node.inputs[0].default_value = 0.5
        node.inputs[1].default_value = 0.5
        node.inputs[2].default_value = 0.5
        node.outputs[0].default_value = 0.0

        node = nodes.new("ShaderNodeMath")
        node.name = "Math.011"
        node.parent = frameCoords
        node.location = (341, -685)
        node.operation = "SUBTRACT"
        node.use_clamp = False
        node.inputs[0].default_value = 0.5
        node.inputs[1].default_value = 0.5
        node.inputs[2].default_value = 0.5
        node.outputs[0].default_value = 0.0

        node = nodes.new("ShaderNodeMath")
        node.name = "Math.012"
        node.parent = frameCoords
        node.location = (341, -189)
        node.operation = "ADD"
        node.use_clamp = False
        node.inputs[0].default_value = 0.5
        node.inputs[1].default_value = 0.5
        node.inputs[2].default_value = 0.5
        node.outputs[0].default_value = 0.0

        node = nodes.new("ShaderNodeCombineXYZ")
        node.name = "Combine XYZ.008"
        node.parent = frameCoords
        node.location = (651, 176)
        node.inputs[0].default_value = 1.0
        node.inputs[1].default_value = 0.0
        node.inputs[2].default_value = 0.0
        node.outputs[0].default_value = (0.0, 0.0, 0.0,)

        node = nodes.new("ShaderNodeCombineXYZ")
        node.name = "Combine XYZ.009"
        node.parent = frameCoords
        node.location = (651, -20)
        node.inputs[0].default_value = 1.0
        node.inputs[1].default_value = 0.0
        node.inputs[2].default_value = 0.0
        node.outputs[0].default_value = (0.0, 0.0, 0.0,)

        node = nodes.new("NodeGroupOutput")
        node.name = "Group Output"
        node.location = (813, -59)

        links.new(nodes['Group Input'].outputs[0],
                  nodes['Reroute.004'].inputs[0])
        links.new(nodes['Group Input'].outputs[1],  nodes['Reroute'].inputs[0])
        links.new(nodes['Group Input'].outputs[2],
                  nodes['Reroute.001'].inputs[0])
        links.new(nodes['Group Input'].outputs[3],
                  nodes['Reroute.002'].inputs[0])
        links.new(nodes['Group Input'].outputs[3],  nodes['Math'].inputs[0])
        links.new(nodes['Group Input'].outputs[4],
                  nodes['Reroute.003'].inputs[0])
        links.new(nodes['Group Input'].outputs[5],
                  nodes['Reroute.005'].inputs[0])
        links.new(nodes['Group Input'].outputs[6],
                  nodes['Reroute.006'].inputs[0])
        links.new(nodes['Group Input'].outputs[7],
                  nodes['RotMath3'].inputs[0])
        links.new(nodes['Group Input'].outputs[8],
                  nodes['Reroute.010'].inputs[0])
        links.new(nodes['Reroute.004'].outputs['Output'],
                  nodes['RayP1'].inputs['Target Geometry'])
        links.new(nodes['Reroute.004'].outputs['Output'],
                  nodes['RayP2'].inputs['Target Geometry'])
        links.new(nodes['RotMath1'].outputs['Value'],
                  nodes['RotMath2'].inputs['Value'])
        links.new(nodes['Reroute.003'].outputs['Output'],
                  nodes['Math.004'].inputs['Value'])
        links.new(nodes['Reroute.005'].outputs['Output'],
                  nodes['Math.005'].inputs['Value'])
        links.new(nodes['Reroute.006'].outputs['Output'],
                  nodes['Math.007'].inputs['Value'])
        links.new(nodes['Reroute'].outputs['Output'],
                  nodes['Math.008'].inputs[0])
        links.new(nodes['Reroute'].outputs['Output'],
                  nodes['Math.009'].inputs[0])
        links.new(nodes['Math.004'].outputs['Value'],
                  nodes['Math.008'].inputs[1])
        links.new(nodes['Math.004'].outputs['Value'],
                  nodes['Math.009'].inputs[1])
        links.new(nodes['Math.005'].outputs['Value'],
                  nodes['Math.010'].inputs[1])
        links.new(nodes['Math.005'].outputs['Value'],
                  nodes['Math.011'].inputs[1])
        links.new(nodes['Reroute.001'].outputs['Output'],
                  nodes['Math.010'].inputs[0])
        links.new(nodes['Reroute.001'].outputs['Output'],
                  nodes['Math.011'].inputs[0])
        links.new(nodes['Math.007'].outputs['Value'],
                  nodes['Math.012'].inputs[1])
        links.new(nodes['Math.007'].outputs['Value'],
                  nodes['Math.013'].inputs[1])
        links.new(nodes['Math.008'].outputs['Value'],
                  nodes['Combine XYZ.008'].inputs['X'])
        links.new(nodes['Reroute.002'].outputs['Output'],
                  nodes['Math.012'].inputs[0])
        links.new(nodes['Reroute.002'].outputs['Output'],
                  nodes['Math.013'].inputs[0])
        links.new(nodes['Math.010'].outputs['Value'],
                  nodes['Combine XYZ.008'].inputs['Y'])
        links.new(nodes['Math.012'].outputs['Value'],
                  nodes['Combine XYZ.008'].inputs['Z'])
        links.new(nodes['Math.009'].outputs['Value'],
                  nodes['Combine XYZ.009'].inputs['X'])
        links.new(nodes['Math.011'].outputs['Value'],
                  nodes['Combine XYZ.009'].inputs['Y'])
        links.new(nodes['Math.013'].outputs['Value'],
                  nodes['Combine XYZ.009'].inputs['Z'])
        links.new(nodes['DisplayLine'].outputs['Mesh'],
                  nodes['DisplaySetP1'].inputs['Geometry'])
        links.new(nodes['DispayIndex'].outputs['Index'],
                  nodes['DisplayFind0'].inputs['B'])
        links.new(nodes['DisplayFind0'].outputs['Result'],
                  nodes['DisplaySetP1'].inputs['Selection'])
        links.new(nodes['Combine XYZ.008'].outputs['Vector'],
                  nodes['DisplaySetP1'].inputs['Position'])
        links.new(nodes['DisplayFind1'].outputs['Result'],
                  nodes['DisplaySetP2'].inputs['Selection'])
        links.new(nodes['DisplaySetP1'].outputs['Geometry'],
                  nodes['DisplaySetP2'].inputs['Geometry'])
        links.new(nodes['Combine XYZ.009'].outputs['Vector'],
                  nodes['DisplaySetP2'].inputs['Position'])
        links.new(nodes['Combine XYZ.008'].outputs['Vector'],
                  nodes['RayP1'].inputs['Source Position'])
        links.new(nodes['Combine XYZ.009'].outputs['Vector'],
                  nodes['RayP2'].inputs['Source Position'])
        links.new(nodes['Reroute.010'].outputs['Output'],
                  nodes['MoveMath2'].inputs[1])
        links.new(nodes['DisplayExtrude'].outputs['Mesh'],
                  nodes['Group Output'].inputs[0])
        links.new(nodes['RotMath3'].outputs['Value'],
                  nodes['Group Output'].inputs[1])
        links.new(nodes['MoveMath2'].outputs['Value'],
                  nodes['Group Output'].inputs[2])
        links.new(nodes['RotMath2'].outputs['Value'],
                  nodes['RotMath3'].inputs[1])
        links.new(nodes['RayP2'].outputs['Hit Distance'],
                  nodes['RotMath1'].inputs[1])
        links.new(nodes['MoveMath1'].outputs['Value'],
                  nodes['MoveMath2'].inputs[0])
        links.new(nodes['RayP1'].outputs['Hit Distance'],
                  nodes['RotMath1'].inputs[0])
        links.new(nodes['RotMath1'].outputs['Value'],
                  nodes['MoveMath1'].inputs[0])
        links.new(nodes['DisplaySetP2'].outputs['Geometry'],
                  nodes['DisplayExtrude'].inputs['Mesh'])
        links.new(nodes['DisplayExtrudeCombine'].outputs['Vector'],
                  nodes['DisplayExtrude'].inputs['Offset'])
        links.new(nodes['Math'].outputs['Value'],
                  nodes['DisplayExtrudeCombine'].inputs['Z'])
        links.new(nodes['DispayIndex'].outputs['Index'],
                  nodes['DisplayFind1'].inputs['B'])

        self.label_nodes(node_group)
        return node_group

    def make_geofloat(self, context, goal, obj, ocean):
        mod, node_group = self.new_geonodes_mod(goal)
        aom_props = context.scene.aom_props
        is_GeoFloat_Smooth = aom_props.is_GeoFloat_Smooth
        instanceFloatobj = aom_props.instanceFloatobj
        if is_GeoFloat_Smooth:
            mod.name = "GeoFloat_hash"
            node_group = self.make_GeoFloat_hash  # !!!
        else:
            mod.name = "GeoFloat_plus"
            node_group = self.make_GeoFloat_plus(mod)
            #nodegroup.name = "Geoflat_plus"
        #self.move_mod_one_up(ocean, mod)

        if instanceFloatobj:
            self.set_FloatInstanced(node_group)
        else:
            self.set_FloatNotInstanced(node_group)

        if obj != None:
            mod['Input_1'] = obj
            # float_parent_id
            #obj.aom_data.ripple_parent = ocean
        if ocean != None:
            mod['Input_2'] = ocean
            #obj.aom_data.ripple_parent = ocean
        #obj.modifiers.active = mod

        #self.move_above_DP(obj, mod)

    def make_GeoFloat_plus(self, mod):
        # does it exist
        ngname = 'AOMGeoFloat_plus'
        if ngname in bpy.data.node_groups:
            mod.node_group = bpy.data.node_groups[ngname]
            return bpy.data.node_groups[ngname]

        node_group = bpy.data.node_groups.new(ngname, 'GeometryNodeTree')
        # self.remove_nodes(node_group)

        mod.node_group = node_group
        nodes = node_group.nodes
        links = node_group.links
        inp = node_group.inputs.new('NodeSocketGeometry', 'Geometry')
        inp = node_group.inputs.new('NodeSocketObject', 'FloatObject')
        #inp.hide_value = True
        inp = node_group.inputs.new('NodeSocketObject', 'Ocean')
        inp = node_group.inputs.new('NodeSocketFloat', 'DetectionHeight')
        inp.default_value = 10.0
        inp = node_group.inputs.new('NodeSocketFloat', 'XRotSensitivity')
        inp.default_value = 1.0
        inp = node_group.inputs.new('NodeSocketFloat', 'YRotSensitivity')
        inp.default_value = 1.0
        inp = node_group.inputs.new('NodeSocketFloat', 'HeightSensitivity')
        inp.default_value = 1.0
        inp = node_group.inputs.new('NodeSocketFloat', 'XDetectionDistance')
        inp.default_value = 2.0
        inp = node_group.inputs.new('NodeSocketFloat', 'YDetectionDistance')
        inp.default_value = 3.0
        inp = node_group.inputs.new('NodeSocketFloat', 'MoveSensitivityX')
        inp.default_value = 0.2
        inp = node_group.inputs.new('NodeSocketFloat', 'MoveSensitivityY')
        inp.default_value = 0.2
        inp = node_group.inputs.new('NodeSocketFloat', 'XOffset')
        inp.default_value = 0.0
        inp = node_group.inputs.new('NodeSocketFloat', 'YOffset')
        inp.default_value = 0.0
        inp = node_group.inputs.new('NodeSocketBool', 'ShowFloatCage')
        inp.default_value = True

        #node.inputs[0].default_value = 0.0
        #node.outputs[0].default_value = 0.0

        frameDetect = nodes.new("NodeFrame")
        frameDetect.name = "OceanSurfaceDetection"
        frameDetect.location = (-1185, -865)

        frameDisplay = nodes.new("NodeFrame")
        frameDisplay.name = "DisplayToggle"
        frameDisplay.location = (-70, -666)

        frameSurface = nodes.new("NodeFrame")
        frameSurface.name = "ShipFollowsurface"
        frameSurface.location = (174, 2486)

        frameInstance = nodes.new("NodeFrame")
        frameInstance.name = "ShipInstancing"
        frameInstance.location = (1123, 2870)

        node = nodes.new("GeometryNodeObjectInfo")
        node.name = "Ocean"
        node.location = (-2180, -780)
        node.transform_space = "RELATIVE"
        node.inputs[1].default_value = False
        node.outputs[0].default_value = (0.0, 0.0, 0.0,)
        node.outputs[1].default_value = (0.0, 0.0, 0.0,)
        node.outputs[2].default_value = (0.0, 0.0, 0.0,)

        node = nodes.new("NodeGroupInput")
        node.name = "Group Input"
        node.location = (-2469, -341)

        node = nodes.new("NodeReroute")
        node.name = "Reroute.001"

        node.location = (-2227, -1146)

        node = nodes.new("NodeReroute")
        node.name = "Reroute.011"
        node.location = (-1959, -887)

        node = nodes.new("NodeReroute")
        node.name = "Reroute.009"
        node.location = (-1933, -513)
        #node.inputs[0].default_value = 0.0
        #node.outputs[0].default_value = 0.0

        node = nodes.new("GeometryNodeMeshLine")
        node.name = "InstancePoint"
        node.parent = frameInstance
        node.location = (-1887, -1954)
        node.inputs[0].default_value = 1
        node.inputs[1].default_value = 1.0
        node.inputs[2].default_value = (0.0, 0.0, 0.0,)
        node.inputs[3].default_value = (0.0, 0.0, 0.0,)

        node = nodes.new("GeometryNodeObjectInfo")
        node.name = "FloatObj"
        node.parent = frameInstance
        node.location = (-1881, -2241)
        node.transform_space = "ORIGINAL"
        node.inputs[1].default_value = False
        node.outputs[0].default_value = (0.0, 0.0, 0.0,)
        node.outputs[1].default_value = (0.0, 0.0, 0.0,)
        node.outputs[2].default_value = (0.0, 0.0, 0.0,)

        node = nodes.new("NodeReroute")
        node.name = "Reroute.005"
        node.location = (-1854, -571)
        #node.inputs[0].default_value = 0.0
        #node.outputs[0].default_value = 0.0

        node = nodes.new("NodeReroute")
        node.name = "Reroute.006"
        node.location = (-1854, -535)
        #node.inputs[0].default_value = 0.0
        #node.outputs[0].default_value = 0.0

        node = nodes.new("NodeReroute")
        node.name = "Reroute"
        node.location = (-1849, -377)
        #node.inputs[0].default_value = 0.0
        #node.outputs[0].default_value = 0.0

        node = nodes.new("ShaderNodeCombineXYZ")
        node.name = "PToHeight"
        node.parent = frameSurface
        node.location = (-1838, -2396)
        node.inputs[0].default_value = 0.0
        node.inputs[1].default_value = 0.0
        node.inputs[2].default_value = 0.0
        node.outputs[0].default_value = (0.0, 0.0, 0.0,)

        node = nodes.new("GeometryNodeInstanceOnPoints")
        node.name = "InstanceOnPoint"
        node.parent = frameInstance
        node.location = (-1649, -2096)
        node.inputs[1].default_value = True
        node.inputs[3].default_value = False
        node.inputs[4].default_value = 0
        node.inputs[5].default_value = (0.0, 0.0, 0.0,)
        node.inputs[6].default_value = (1.0, 1.0, 1.0,)

        node = nodes.new("GeometryNodeRaycast")
        node.name = "RayHeight"
        node.parent = frameSurface
        node.location = (-1561, -2174)
        node.data_type = "FLOAT"
        node.inputs[1].default_value = (0.0, 0.0, 0.0,)
        node.inputs[2].default_value = 0.0
        node.inputs[3].default_value = (0.0, 0.0, 0.0, 0.0,)
        node.inputs[4].default_value = False
        node.inputs[5].default_value = 0
        node.inputs[6].default_value = (0.0, 0.0, 0.0,)
        node.inputs[7].default_value = (0.0, 0.0, -1.0,)
        node.inputs[8].default_value = 100.0
        node.outputs[0].default_value = False
        node.outputs[1].default_value = (0.0, 0.0, 0.0,)
        node.outputs[2].default_value = (0.0, 0.0, 0.0,)
        node.outputs[3].default_value = 0.0
        node.outputs[4].default_value = (0.0, 0.0, 0.0,)
        node.outputs[5].default_value = 0.0
        node.outputs[6].default_value = (0.0, 0.0, 0.0, 0.0,)
        node.outputs[7].default_value = False
        node.outputs[8].default_value = 0

        node = nodes.new("ShaderNodeSeparateXYZ")
        node.name = "HeightSep"
        node.parent = frameSurface
        node.location = (-1294, -2146)
        node.inputs[0].default_value = (0.0, 0.0, 0.0,)
        node.outputs[0].default_value = 0.0
        node.outputs[1].default_value = 0.0
        node.outputs[2].default_value = 0.0

        node = nodes.new("NodeReroute")
        node.name = "Reroute.002"
        node.location = (-1197, -185)
        #node.inputs[0].default_value = 0.0
        #node.outputs[0].default_value = 0.0

        node = nodes.new("ShaderNodeMath")
        node.name = "SetHeightSensitivity"
        node.parent = frameSurface
        node.location = (-996, -2262)
        node.operation = "MULTIPLY"
        node.use_clamp = False
        node.inputs[0].default_value = 0.5
        node.inputs[1].default_value = 1.0
        node.inputs[2].default_value = 0.5
        node.outputs[0].default_value = 0.0

        node = nodes.new("ShaderNodeCombineXYZ")
        node.name = "HeightComb"
        node.parent = frameSurface
        node.location = (-694, -2126)
        node.inputs[0].default_value = 0.0
        node.inputs[1].default_value = 0.0
        node.inputs[2].default_value = 0.0
        node.outputs[0].default_value = (0.0, 0.0, 0.0,)

        floatrotmoveNG = self.make_FloatRotMove_nodegroup()

        node = nodes.new("GeometryNodeGroup")
        node.node_tree = floatrotmoveNG
        node.parent = frameDetect
        node.name = "RotationX"
        node.location = (-354, 445)
        node.inputs[1].default_value = 0.8
        node.inputs[2].default_value = 0.0
        node.inputs[3].default_value = 3.4
        node.inputs[4].default_value = 0.0
        node.inputs[5].default_value = 2.3
        node.inputs[6].default_value = 0.0
        node.inputs[7].default_value = 1.0
        #node.inputs[8].default_value = 1.0
        #node.outputs[1].default_value = 0.0
        #node.outputs[2].default_value = 0.0

        node = nodes.new("GeometryNodeGroup")
        node.node_tree = floatrotmoveNG
        node.name = "RotationY"
        node.parent = frameDetect
        node.location = (-354, 19)
        node.inputs[1].default_value = 0.8
        node.inputs[2].default_value = 0.0
        node.inputs[3].default_value = 3.4
        node.inputs[4].default_value = 1.6
        node.inputs[5].default_value = 0.0
        node.inputs[6].default_value = 0.0
        node.inputs[7].default_value = 1.0
        #node.inputs[8].default_value = 1.0
        #node.outputs[1].default_value = 0.0
        #node.outputs[2].default_value = 0.0

        node = nodes.new("GeometryNodeJoinGeometry")
        node.name = "JoinDisplay"
        node.parent = frameDisplay
        node.location = (-249, 246)

        node = nodes.new("ShaderNodeCombineXYZ")
        node.name = "NewCoordinatesAfterMove"
        node.location = (-119, 347)
        node.inputs[0].default_value = 0.0
        node.inputs[1].default_value = 0.0
        node.inputs[2].default_value = 0.0
        node.outputs[0].default_value = (0.0, 0.0, 0.0,)

        node = nodes.new("GeometryNodeSwitch")
        node.name = "DisplaySwitch"
        node.parent = frameDisplay
        node.location = (70, 246)
        node.input_type = "GEOMETRY"
        node.inputs[0].default_value = False
        node.inputs[1].default_value = False
        node.inputs[2].default_value = 0.0
        node.inputs[3].default_value = 0.0
        node.inputs[4].default_value = 0
        node.inputs[5].default_value = 0
        node.inputs[6].default_value = False
        node.inputs[7].default_value = True
        node.inputs[8].default_value = (0.0, 0.0, 0.0,)
        node.inputs[9].default_value = (0.0, 0.0, 0.0,)
        node.inputs[10].default_value = (
            0.800000011920929, 0.800000011920929, 0.800000011920929, 1.0,)
        node.inputs[11].default_value = (
            0.800000011920929, 0.800000011920929, 0.800000011920929, 1.0,)
        node.inputs[12].default_value = ""
        node.inputs[13].default_value = ""
        node.outputs[0].default_value = 0.0
        node.outputs[1].default_value = 0
        node.outputs[2].default_value = False
        node.outputs[3].default_value = (0.0, 0.0, 0.0,)
        node.outputs[4].default_value = (0.0, 0.0, 0.0, 0.0,)
        node.outputs[5].default_value = ""
        node.outputs[7].default_value = None
        node.outputs[8].default_value = None
        node.outputs[9].default_value = None
        node.outputs[10].default_value = None
        node.outputs[11].default_value = None

        node = nodes.new("ShaderNodeVectorMath")
        node.name = "MoveXY"
        node.location = (85, 416)
        node.operation = "MULTIPLY"
        node.inputs[0].default_value = (0.0, 0.0, 0.0,)
        node.inputs[1].default_value = (1.0, 1.0, 0.0,)
        node.inputs[2].default_value = (0.0, 0.0, 0.0,)
        node.inputs[3].default_value = 1.0
        node.outputs[0].default_value = (0.0, 0.0, 0.0,)
        node.outputs[1].default_value = 0.0

        node = nodes.new("ShaderNodeCombineXYZ")
        node.name = "RotComb"
        node.location = (88, 208)
        node.inputs[0].default_value = 0.0
        node.inputs[1].default_value = 0.0
        node.inputs[2].default_value = 0.0
        node.outputs[0].default_value = (0.0, 0.0, 0.0,)

        node = nodes.new("GeometryNodeSetPosition")
        node.name = "SetMove"
        node.location = (329, 511)
        node.inputs[1].default_value = True
        node.inputs[2].default_value = (0.0, 0.0, 0.0,)
        node.inputs[3].default_value = (0.0, 0.0, 0.0,)

        node = nodes.new("GeometryNodeTransform")
        node.name = "SetHeightRot"
        node.location = (630, 406)
        node.inputs[1].default_value = (0.0, 0.0, 0.0,)
        node.inputs[2].default_value = (0.0, 0.0, 0.0,)
        node.inputs[3].default_value = (1.0, 1.0, 1.0,)

        node = nodes.new("GeometryNodeJoinGeometry")
        node.name = "JoinAll"
        node.location = (876, -294)

        node = nodes.new("NodeGroupOutput")
        node.name = "Group Output"
        node.location = (1186, -294)
        links.new(nodes['Group Input'].outputs[1],
                  nodes['FloatObj'].inputs[0])
        links.new(nodes['Group Input'].outputs[2],  nodes['Ocean'].inputs[0])
        links.new(nodes['Group Input'].outputs[3],
                  nodes['Reroute.005'].inputs[0])
        links.new(nodes['Group Input'].outputs[4],  nodes['Reroute'].inputs[0])
        links.new(nodes['Group Input'].outputs[5],
                  nodes['Reroute.001'].inputs[0])
        links.new(nodes['Group Input'].outputs[6],
                  nodes['Reroute.002'].inputs[0])
        links.new(nodes['Group Input'].outputs[7],
                  nodes['RotationY'].inputs[4])
        links.new(nodes['Group Input'].outputs[8],
                  nodes['RotationX'].inputs[5])
        links.new(nodes['Group Input'].outputs[9],
                  nodes['RotationX'].inputs[8])
        links.new(nodes['Group Input'].outputs[10],
                  nodes['RotationY'].inputs[8])
        links.new(nodes['Group Input'].outputs[11],
                  nodes['Reroute.009'].inputs[0])
        links.new(nodes['Group Input'].outputs[12],
                  nodes['Reroute.006'].inputs[0])
        links.new(nodes['Group Input'].outputs[13],
                  nodes['DisplaySwitch'].inputs[1])
        links.new(nodes['RotationY'].outputs[0],
                  nodes['JoinDisplay'].inputs['Geometry'])
        links.new(nodes['JoinAll'].outputs['Geometry'],
                  nodes['Group Output'].inputs[0])
        links.new(nodes['InstancePoint'].outputs['Mesh'],
                  nodes['InstanceOnPoint'].inputs['Points'])
        links.new(nodes['FloatObj'].outputs['Geometry'],
                  nodes['InstanceOnPoint'].inputs['Instance'])
        links.new(nodes['SetMove'].outputs['Geometry'],
                  nodes['SetHeightRot'].inputs['Geometry'])
        links.new(nodes['RotComb'].outputs['Vector'],
                  nodes['SetHeightRot'].inputs['Rotation'])
        links.new(nodes['RotationY'].outputs[1],
                  nodes['RotComb'].inputs['Y'])
        links.new(nodes['Reroute.011'].outputs['Output'],
                  nodes['RotationY'].inputs[0])
        links.new(nodes['Ocean'].outputs['Geometry'],
                  nodes['Reroute.011'].inputs['Input'])
        links.new(nodes['Reroute.011'].outputs['Output'],
                  nodes['RayHeight'].inputs['Target Geometry'])
        links.new(nodes['Reroute.009'].outputs['Output'],
                  nodes['RotationY'].inputs['X'])
        links.new(nodes['Reroute.006'].outputs['Output'],
                  nodes['RotationY'].inputs['Y'])
        links.new(nodes['Reroute.005'].outputs['Output'],
                  nodes['RotationY'].inputs['Z'])
        links.new(nodes['Reroute.011'].outputs['Output'],
                  nodes['RotationX'].inputs[0])
        links.new(nodes['Reroute.009'].outputs['Output'],
                  nodes['RotationX'].inputs['X'])
        links.new(nodes['Reroute.006'].outputs['Output'],
                  nodes['RotationX'].inputs['Y'])
        links.new(nodes['Reroute.005'].outputs['Output'],
                  nodes['RotationX'].inputs['Z'])
        links.new(nodes['RotationX'].outputs[1],
                  nodes['RotComb'].inputs['X'])
        links.new(nodes['Reroute.009'].outputs['Output'],
                  nodes['PToHeight'].inputs['X'])
        links.new(nodes['Reroute.006'].outputs['Output'],
                  nodes['PToHeight'].inputs['Y'])
        links.new(nodes['Reroute.005'].outputs['Output'],
                  nodes['PToHeight'].inputs['Z'])
        links.new(nodes['RotationX'].outputs[0],
                  nodes['JoinDisplay'].inputs['Geometry'])
        links.new(nodes['HeightSep'].outputs['X'],
                  nodes['HeightComb'].inputs['X'])
        links.new(nodes['HeightSep'].outputs['Y'],
                  nodes['HeightComb'].inputs['Y'])
        links.new(nodes['SetHeightSensitivity'].outputs['Value'],
                  nodes['HeightComb'].inputs['Z'])
        links.new(nodes['HeightSep'].outputs['Z'],
                  nodes['SetHeightSensitivity'].inputs[0])
        links.new(nodes['Reroute.002'].outputs['Output'],
                  nodes['SetHeightSensitivity'].inputs[1])
        links.new(nodes['RayHeight'].outputs['Hit Position'],
                  nodes['HeightSep'].inputs['Vector'])
        links.new(nodes['HeightComb'].outputs['Vector'],
                  nodes['SetHeightRot'].inputs['Translation'])
        links.new(nodes['InstanceOnPoint'].outputs['Instances'],
                  nodes['SetMove'].inputs['Geometry'])
        links.new(nodes['MoveXY'].outputs['Vector'],
                  nodes['SetMove'].inputs['Offset'])
        links.new(nodes['Reroute'].outputs['Output'],
                  nodes['RotationX'].inputs['RotSensitivity'])
        links.new(nodes['Reroute.001'].outputs['Output'],
                  nodes['RotationY'].inputs['RotSensitivity'])
        links.new(nodes['RotationY'].outputs[2],
                  nodes['NewCoordinatesAfterMove'].inputs['Y'])
        links.new(nodes['RotationX'].outputs[2],
                  nodes['NewCoordinatesAfterMove'].inputs['X'])
        links.new(nodes['Reroute.005'].outputs['Output'],
                  nodes['NewCoordinatesAfterMove'].inputs['Z'])
        links.new(nodes['NewCoordinatesAfterMove'].outputs['Vector'],
                  nodes['MoveXY'].inputs['Vector'])
        links.new(nodes['PToHeight'].outputs['Vector'],
                  nodes['RayHeight'].inputs['Source Position'])
        links.new(nodes['DisplaySwitch'].outputs[6],
                  nodes['JoinAll'].inputs['Geometry'])
        links.new(nodes['SetHeightRot'].outputs['Geometry'],
                  nodes['JoinAll'].inputs['Geometry'])
        links.new(nodes['JoinDisplay'].outputs['Geometry'],
                  nodes['DisplaySwitch'].inputs[15])
        mod['Input_3'] = 10.0
        mod['Input_4'] = 1.0
        mod['Input_5'] = 1.0 #yRotSens
        mod['Input_6'] = 1.0  #Heightsens
        mod['Input_7'] = 2.0    # X-detectionDistance
        mod['Input_8'] = 2.0
        mod['Input_9'] = 1.0 #movesens X
        mod['Input_10'] = 1.0 
        mod['Input_11'] = 1.0   #Xoffset
        mod['Input_12'] = 1.0   
        mod['Input_13'] = 1     # showfloat

        self.label_nodes(node_group)
        return node_group

    def set_FloatNotInstanced(self, node_group):
        nodes = node_group.nodes
        links = node_group.links

        links.new(nodes['Group Input'].outputs[0],
                  nodes['SetMove'].inputs[0])

    def set_FloatInstanced(self, node_group):
        nodes = node_group.nodes
        links = node_group.links

        links.new(nodes['InstanceOnPoint'].outputs[0],
                  nodes['SetMove'].inputs[0])

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
