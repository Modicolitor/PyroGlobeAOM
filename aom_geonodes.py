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
        
        node_group.outputs.new(type= 'NodeSocketGeometry', name='Geometry') 
        
        
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
        links.new(nodes['Collection Info'].outputs['Instances'],
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

        mod['Input_1'] = 0.2
        mod['Input_1_use_attribute'] = False
        mod['Input_2'] = 50.0
        mod['Input_2_use_attribute'] = False
        mod['Input_3'] = 1.0
        mod['Input_3_use_attribute'] = False
        mod['Input_4'] = 0.1
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
        node.outputs[0].default_value = 0
        #self.add_driver(target, prop, dataPath)
        

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
        
        node_group.outputs.new(type= 'NodeSocketGeometry', name='Geometry') 
        
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

        inp = node_group.inputs.new('NodeSocketGeometry','Target Geometry')
        inp = node_group.inputs.new('NodeSocketVector','DetectionPositon')
        inp.default_value = (0.0,0.0,0.0,)
        inp = node_group.inputs.new('NodeSocketFloat','XDistance')
        inp.default_value = 1.0
        inp = node_group.inputs.new('NodeSocketFloat','YDistance')
        inp.default_value = 0.0
        inp = node_group.inputs.new('NodeSocketFloat','ZDistance')
        inp.default_value = 0.0
        inp = node_group.inputs.new('NodeSocketFloat','RotSensitivity')
        inp.default_value = 1.0
        inp = node_group.inputs.new('NodeSocketFloat','MoveSensitivity')
        inp.default_value = 1.0
        inp = node_group.inputs.new('NodeSocketFloatAngle','Angle')
        inp.default_value = 0.0
        inp = node_group.inputs.new('NodeSocketFloat','ScaleX')
        inp.default_value = 0.5
        inp = node_group.inputs.new('NodeSocketFloat','ScaleY')
        inp.default_value = 0.5

        node = nodes.new("NodeFrame" )
        node.name = "Detection"
        node.location = (-820, -700)

        node = nodes.new("NodeFrame" )
        node.name = "Display Detectionline"
        node.location = (899, 1140)

        node = nodes.new("NodeFrame" )
        node.name = "Frame"
        node.location = (-47, -942)

        node = nodes.new("NodeFrame" )
        node.name = "Rotate"
        node.location = (1966, -116)

        node = nodes.new("NodeFrame" )
        node.name = "Move"
        node.location = (1994, 131)

        node = nodes.new("NodeFrame" )
        node.name = "Coordinates"
        node.location = (-2630, -275)

        node = nodes.new("NodeGroupInput" )
        node.name = "Group Input"
        node.location = (-4061, -109)

        node = nodes.new("ShaderNodeMath" )
        node.name = "Math.006"
        node.location = (-3758, -88)
        node.operation = "MULTIPLY"
        node.use_clamp = False
        node.inputs[0].default_value = 0.5
        node.inputs[1].default_value = 0.5
        node.inputs[2].default_value = 0.5
        node.outputs[0].default_value = 0.0

        node = nodes.new("ShaderNodeMath" )
        node.name = "Math.014"
        node.location = (-3753, -274)
        node.operation = "MULTIPLY"
        node.use_clamp = False
        node.inputs[0].default_value = 0.5
        node.inputs[1].default_value = 0.5
        node.inputs[2].default_value = 0.5
        node.outputs[0].default_value = 0.0

        node = nodes.new("NodeReroute" )
        node.name = "Reroute.020"
        node.location = (-3496, -239)

        node = nodes.new("NodeReroute" )
        node.name = "Reroute.021"
        node.location = (-3486, -387)

        node = nodes.new("ShaderNodeSeparateXYZ" )
        node.name = "Separate XYZ"
        node.location = (-3430, 70)
        node.inputs[0].default_value = (0.0,0.0,0.0,)
        node.outputs[0].default_value = 0.0
        node.outputs[1].default_value = 0.0
        node.outputs[2].default_value = 0.0

        node = nodes.new("NodeReroute" )
        node.name = "Reroute.006"
        node.location = (-3163, -718)

        node = nodes.new("NodeReroute" )
        node.name = "Reroute.007"
        node.location = (-3148, 57)

        node = nodes.new("NodeReroute" )
        node.name = "Reroute.003"
        node.location = (-3141, -170)

        node = nodes.new("NodeReroute" )
        node.name = "Reroute.008"
        node.location = (-3140, 9)

        node = nodes.new("NodeReroute" )
        node.name = "Reroute.009"
        node.location = (-3125, -39)

        node = nodes.new("NodeReroute" )
        node.name = "Reroute.005"
        node.location = (-3094, -463)

        node = nodes.new("NodeReroute" )
        node.name = "Reroute.014"
        node.location = (-3075, -1532)

        node = nodes.new("NodeReroute" )
        node.name = "Reroute.013"
        node.location = (-3065, -1526)

        node = nodes.new("ShaderNodeMath" )
        node.name = "RotMath1"
        node.parent = node_group.nodes["Rotate"]
        node.location = (-2205, -332)
        node.operation = "SUBTRACT"
        node.use_clamp = False
        node.inputs[0].default_value = 0.5
        node.inputs[1].default_value = 0.5
        node.inputs[2].default_value = 0.5
        node.outputs[0].default_value = 0.0

        node = nodes.new("ShaderNodeMath" )
        node.name = "MoveMath1"
        node.parent = node_group.nodes["Move"]
        node.location = (-1978, -140)
        node.operation = "MULTIPLY"
        node.use_clamp = False
        node.inputs[0].default_value = 0.5
        node.inputs[1].default_value = -1.0
        node.inputs[2].default_value = 0.5
        node.outputs[0].default_value = 0.0

        node = nodes.new("GeometryNodeInputIndex" )
        node.name = "DispayIndex"
        node.parent = node_group.nodes["Display Detectionline"]
        node.location = (-1850, -924)
        node.outputs[0].default_value = 0

        node = nodes.new("ShaderNodeMath" )
        node.name = "Math.003"
        node.parent = node_group.nodes["Rotate"]
        node.location = (-1827, -531)
        node.operation = "ADD"
        node.use_clamp = False
        node.inputs[0].default_value = 0.5
        node.inputs[1].default_value = 0.5
        node.inputs[2].default_value = 0.5
        node.outputs[0].default_value = 0.0

        node = nodes.new("NodeReroute" )
        node.name = "Reroute.017"
        node.parent = node_group.nodes["Rotate"]
        node.location = (-1795, -381)

        node = nodes.new("NodeReroute" )
        node.name = "Reroute.010"
        node.parent = node_group.nodes["Move"]
        node.location = (-1775, -320)

        node = nodes.new("NodeReroute" )
        node.name = "Reroute.004"
        node.location = (-1651, -94)

        node = nodes.new("ShaderNodeMath" )
        node.name = "MoveMath2"
        node.parent = node_group.nodes["Move"]
        node.location = (-1630, -156)
        node.operation = "MULTIPLY"
        node.use_clamp = False
        node.inputs[0].default_value = 0.5
        node.inputs[1].default_value = 1.0
        node.inputs[2].default_value = 0.5
        node.outputs[0].default_value = 0.0

        node = nodes.new("GeometryNodeMeshLine" )
        node.name = "DisplayLine"
        node.parent = node_group.nodes["Display Detectionline"]
        node.location = (-1625, -395)
        node.inputs[0].default_value = 2
        node.inputs[1].default_value = 1.0
        node.inputs[2].default_value = (0.0,0.0,0.0,)
        node.inputs[3].default_value = (1.0,0.0,0.0,)

        node = nodes.new("FunctionNodeCompare" )
        node.name = "DisplayFind0"
        node.parent = node_group.nodes["Display Detectionline"]
        node.location = (-1481, -681)
        node.data_type = "FLOAT"
        node.operation = "EQUAL"
        node.inputs[0].default_value = 0.0
        node.inputs[1].default_value = 0.0
        node.inputs[2].default_value = 0
        node.inputs[3].default_value = 0
        node.inputs[4].default_value = (0.0,0.0,0.0,)
        node.inputs[5].default_value = (0.0,0.0,0.0,)
        node.inputs[6].default_value = (0.0,0.0,0.0,0.0,)
        node.inputs[7].default_value = (0.0,0.0,0.0,0.0,)
        node.inputs[8].default_value = ""
        node.inputs[9].default_value = ""
        node.inputs[10].default_value = 0.9
        node.inputs[11].default_value = 0.09
        node.inputs[12].default_value = 0.0
        node.outputs[0].default_value = False

        node = nodes.new("FunctionNodeCompare" )
        node.name = "DisplayFind1"
        node.parent = node_group.nodes["Display Detectionline"]
        node.location = (-1480, -860)
        node.data_type = "FLOAT"
        node.operation = "EQUAL"
        node.inputs[0].default_value = 1.0
        node.inputs[1].default_value = 0.0
        node.inputs[2].default_value = 0
        node.inputs[3].default_value = 0
        node.inputs[4].default_value = (0.0,0.0,0.0,)
        node.inputs[5].default_value = (0.0,0.0,0.0,)
        node.inputs[6].default_value = (0.0,0.0,0.0,0.0,)
        node.inputs[7].default_value = (0.0,0.0,0.0,0.0,)
        node.inputs[8].default_value = ""
        node.inputs[9].default_value = ""
        node.inputs[10].default_value = 0.9
        node.inputs[11].default_value = 0.09
        node.inputs[12].default_value = 0.0
        node.outputs[0].default_value = False

        node = nodes.new("ShaderNodeMath" )
        node.name = "RotMath2.001"
        node.parent = node_group.nodes["Rotate"]
        node.location = (-1442, -329)
        node.operation = "DIVIDE"
        node.use_clamp = False
        node.inputs[0].default_value = 0.5
        node.inputs[1].default_value = 0.32
        node.inputs[2].default_value = 0.5
        node.outputs[0].default_value = 0.0

        node = nodes.new("GeometryNodeSetPosition" )
        node.name = "DisplaySetP1"
        node.parent = node_group.nodes["Display Detectionline"]
        node.location = (-1300, -395)
        node.inputs[1].default_value = True
        node.inputs[2].default_value = (0.0,0.0,0.0,)
        node.inputs[3].default_value = (0.0,0.0,0.0,)

        node = nodes.new("ShaderNodeMath" )
        node.name = "RotMath2"
        node.parent = node_group.nodes["Rotate"]
        node.location = (-1227, -332)
        node.operation = "ARCSINE"
        node.use_clamp = False
        node.inputs[0].default_value = 0.5
        node.inputs[1].default_value = 0.32
        node.inputs[2].default_value = 0.5
        node.outputs[0].default_value = 0.0

        node = nodes.new("ShaderNodeMath" )
        node.name = "Math"
        node.parent = node_group.nodes["Display Detectionline"]
        node.location = (-1191, -926)
        node.operation = "MULTIPLY"
        node.use_clamp = False
        node.inputs[0].default_value = 0.5
        node.inputs[1].default_value = -1.0
        node.inputs[2].default_value = 0.5
        node.outputs[0].default_value = 0.0

        node = nodes.new("NodeReroute" )
        node.name = "Reroute.016"
        node.location = (-1055, -1492)

        node = nodes.new("NodeReroute" )
        node.name = "Reroute.015"
        node.location = (-1048, -1472)

        node = nodes.new("GeometryNodeSetPosition" )
        node.name = "DisplaySetP2"
        node.parent = node_group.nodes["Display Detectionline"]
        node.location = (-990, -395)
        node.inputs[1].default_value = True
        node.inputs[2].default_value = (0.0,0.0,0.0,)
        node.inputs[3].default_value = (0.0,0.0,0.0,)

        node = nodes.new("ShaderNodeCombineXYZ" )
        node.name = "DisplayExtrudeCombine"
        node.parent = node_group.nodes["Display Detectionline"]
        node.location = (-977, -652)
        node.inputs[0].default_value = 0.0
        node.inputs[1].default_value = 0.0
        node.inputs[2].default_value = 0.0
        node.outputs[0].default_value = (0.0,0.0,0.0,)

        node = nodes.new("GeometryNodeExtrudeMesh" )
        node.name = "DisplayExtrude"
        node.parent = node_group.nodes["Display Detectionline"]
        node.location = (-760, -400)
        node.mode = 'VERTICES'

        node.inputs[1].default_value = True
        node.inputs[2].default_value = (0.0,0.0,0.0,)
        node.inputs[3].default_value = 1.0
        node.inputs[4].default_value = True
        node.outputs[1].default_value = False
        node.outputs[2].default_value = False

        node = nodes.new("ShaderNodeMath" )
        node.name = "RotMath3.001"
        node.parent = node_group.nodes["Rotate"]
        node.location = (-743, -263)
        node.operation = "MULTIPLY"
        node.use_clamp = False
        node.inputs[0].default_value = 0.5
        node.inputs[1].default_value = 0.57
        node.inputs[2].default_value = 0.5
        node.outputs[0].default_value = 0.0

        node = nodes.new("ShaderNodeSeparateXYZ" )
        node.name = "Separate XYZ.002"
        node.parent = node_group.nodes["Frame"]
        node.location = (-562, -58)
        node.inputs[0].default_value = (0.0,0.0,0.0,)
        node.outputs[0].default_value = 0.0
        node.outputs[1].default_value = 0.0
        node.outputs[2].default_value = 0.0

        node = nodes.new("ShaderNodeSeparateXYZ" )
        node.name = "Separate XYZ.001"
        node.parent = node_group.nodes["Frame"]
        node.location = (-546, 80)
        node.inputs[0].default_value = (0.0,0.0,0.0,)
        node.outputs[0].default_value = 0.0
        node.outputs[1].default_value = 0.0
        node.outputs[2].default_value = 0.0

        node = nodes.new("ShaderNodeMath" )
        node.name = "RotMath3"
        node.parent = node_group.nodes["Rotate"]
        node.location = (-523, -113)
        node.operation = "MULTIPLY"
        node.use_clamp = False
        node.inputs[0].default_value = 0.5
        node.inputs[1].default_value = 1.0
        node.inputs[2].default_value = 0.5
        node.outputs[0].default_value = 0.0

        node = nodes.new("ShaderNodeMath" )
        node.name = "Math.001"
        node.parent = node_group.nodes["Frame"]
        node.location = (-314, 97)
        node.operation = "ADD"
        node.use_clamp = False
        node.inputs[0].default_value = 0.5
        node.inputs[1].default_value = 0.5
        node.inputs[2].default_value = 0.5
        node.outputs[0].default_value = 0.0

        node = nodes.new("ShaderNodeMath" )
        node.name = "Math.005"
        node.parent = node_group.nodes["Coordinates"]
        node.location = (-216, -222)
        node.operation = "MULTIPLY"
        node.use_clamp = False
        node.inputs[0].default_value = 0.5
        node.inputs[1].default_value = 0.5
        node.inputs[2].default_value = 0.5
        node.outputs[0].default_value = 0.0

        node = nodes.new("NodeReroute" )
        node.name = "Reroute.018"
        node.location = (-167, -1293)

        node = nodes.new("NodeReroute" )
        node.name = "Reroute.019"
        node.location = (-159, -1311)

        node = nodes.new("ShaderNodeMath" )
        node.name = "Math.004"
        node.parent = node_group.nodes["Coordinates"]
        node.location = (-153, 230)
        node.operation = "MULTIPLY"
        node.use_clamp = False
        node.inputs[0].default_value = 0.5
        node.inputs[1].default_value = 0.5
        node.inputs[2].default_value = 0.5
        node.outputs[0].default_value = 0.0

        node = nodes.new("NodeReroute" )
        node.name = "Reroute.001"
        node.parent = node_group.nodes["Coordinates"]
        node.location = (-120, 48)

        node = nodes.new("ShaderNodeMath" )
        node.name = "Math.002"
        node.parent = node_group.nodes["Frame"]
        node.location = (-95, 80)
        node.operation = "DIVIDE"
        node.use_clamp = False
        node.inputs[0].default_value = 0.5
        node.inputs[1].default_value = 2.0
        node.inputs[2].default_value = 0.5
        node.outputs[0].default_value = 0.0

        node = nodes.new("GeometryNodeRaycast" )
        node.name = "RayP1"
        node.parent = node_group.nodes["Detection"]
        node.location = (-66, 480)
        node.data_type = "FLOAT"
        node.inputs[1].default_value = (0.0,0.0,0.0,)
        node.inputs[2].default_value = 0.0
        node.inputs[3].default_value = (0.0,0.0,0.0,0.0,)
        node.inputs[4].default_value = False
        node.inputs[5].default_value = 0
        node.inputs[6].default_value = (0.0,0.0,0.0,)
        node.inputs[7].default_value = (0.0,0.0,-1.0,)
        node.inputs[8].default_value = 100.0
        node.outputs[0].default_value = False
        node.outputs[1].default_value = (0.0,0.0,0.0,)
        node.outputs[2].default_value = (0.0,0.0,0.0,)
        node.outputs[3].default_value = 0.0
        node.outputs[4].default_value = (0.0,0.0,0.0,)
        node.outputs[5].default_value = 0.0
        node.outputs[6].default_value = (0.0,0.0,0.0,0.0,)
        node.outputs[7].default_value = False
        node.outputs[8].default_value = 0

        node = nodes.new("ShaderNodeMath" )
        node.name = "Math.007"
        node.parent = node_group.nodes["Coordinates"]
        node.location = (-64, -452)
        node.operation = "MULTIPLY"
        node.use_clamp = False
        node.inputs[0].default_value = 0.5
        node.inputs[1].default_value = 0.5
        node.inputs[2].default_value = 0.5
        node.outputs[0].default_value = 0.0

        node = nodes.new("GeometryNodeRaycast" )
        node.name = "RayP2"
        node.parent = node_group.nodes["Detection"]
        node.location = (-61, 71)
        node.data_type = "FLOAT"
        node.inputs[1].default_value = (0.0,0.0,0.0,)
        node.inputs[2].default_value = 0.0
        node.inputs[3].default_value = (0.0,0.0,0.0,0.0,)
        node.inputs[4].default_value = False
        node.inputs[5].default_value = 0
        node.inputs[6].default_value = (0.0,0.0,0.0,)
        node.inputs[7].default_value = (0.0,0.0,-1.0,)
        node.inputs[8].default_value = 100.0
        node.outputs[0].default_value = False
        node.outputs[1].default_value = (0.0,0.0,0.0,)
        node.outputs[2].default_value = (0.0,0.0,0.0,)
        node.outputs[3].default_value = 0.0
        node.outputs[4].default_value = (0.0,0.0,0.0,)
        node.outputs[5].default_value = 0.0
        node.outputs[6].default_value = (0.0,0.0,0.0,0.0,)
        node.outputs[7].default_value = False
        node.outputs[8].default_value = 0

        node = nodes.new("NodeReroute" )
        node.name = "Reroute.002"
        node.parent = node_group.nodes["Coordinates"]
        node.location = (31, -261)

        node = nodes.new("NodeReroute" )
        node.name = "Reroute.022"
        node.parent = node_group.nodes["Coordinates"]
        node.location = (183, -343)

        node = nodes.new("NodeReroute" )
        node.name = "Reroute"
        node.parent = node_group.nodes["Coordinates"]
        node.location = (252, -68)

        node = nodes.new("NodeReroute" )
        node.name = "Reroute.023"
        node.parent = node_group.nodes["Coordinates"]
        node.location = (291, 197)

        node = nodes.new("ShaderNodeMath" )
        node.name = "Math.013"
        node.parent = node_group.nodes["Coordinates"]
        node.location = (341, -933)
        node.operation = "SUBTRACT"
        node.use_clamp = False
        node.inputs[0].default_value = 0.5
        node.inputs[1].default_value = 0.5
        node.inputs[2].default_value = 0.5
        node.outputs[0].default_value = 0.0

        node = nodes.new("ShaderNodeMath" )
        node.name = "Math.009"
        node.parent = node_group.nodes["Coordinates"]
        node.location = (341, -437)
        node.operation = "SUBTRACT"
        node.use_clamp = False
        node.inputs[0].default_value = 0.5
        node.inputs[1].default_value = 0.5
        node.inputs[2].default_value = 0.5
        node.outputs[0].default_value = 0.0

        node = nodes.new("ShaderNodeMath" )
        node.name = "Math.011"
        node.parent = node_group.nodes["Coordinates"]
        node.location = (341, -685)
        node.operation = "SUBTRACT"
        node.use_clamp = False
        node.inputs[0].default_value = 0.5
        node.inputs[1].default_value = 0.5
        node.inputs[2].default_value = 0.5
        node.outputs[0].default_value = 0.0

        node = nodes.new("ShaderNodeMath" )
        node.name = "Math.012"
        node.parent = node_group.nodes["Coordinates"]
        node.location = (341, -189)
        node.operation = "ADD"
        node.use_clamp = False
        node.inputs[0].default_value = 0.5
        node.inputs[1].default_value = 0.5
        node.inputs[2].default_value = 0.5
        node.outputs[0].default_value = 0.0

        node = nodes.new("ShaderNodeMath" )
        node.name = "Math.010"
        node.parent = node_group.nodes["Coordinates"]
        node.location = (341, 58)
        node.operation = "ADD"
        node.use_clamp = False
        node.inputs[0].default_value = 0.5
        node.inputs[1].default_value = 0.5
        node.inputs[2].default_value = 0.5
        node.outputs[0].default_value = 0.0

        node = nodes.new("ShaderNodeMath" )
        node.name = "Math.008"
        node.parent = node_group.nodes["Coordinates"]
        node.location = (414, 280)
        node.operation = "ADD"
        node.use_clamp = False
        node.inputs[0].default_value = 0.5
        node.inputs[1].default_value = 0.5
        node.inputs[2].default_value = 0.5
        node.outputs[0].default_value = 0.0

        node = nodes.new("GeometryNodeStoreNamedAttribute" )
        node.name = "Store Named Attribute"
        node.location = (682, 331)
        node.data_type = "FLOAT"
        node.mute = True
        node.inputs[1].default_value = True
        node.inputs[2].default_value = "height"
        node.inputs[3].default_value = (0.0,0.0,0.0,)
        node.inputs[4].default_value = 0.0
        node.inputs[5].default_value = (0.0,0.0,0.0,0.0,)
        node.inputs[6].default_value = False
        node.inputs[7].default_value = 0

        node = nodes.new("ShaderNodeCombineXYZ" )
        node.name = "Combine XYZ.009"
        node.parent = node_group.nodes["Coordinates"]
        node.location = (793, -459)
        node.inputs[0].default_value = 1.0
        node.inputs[1].default_value = 0.0
        node.inputs[2].default_value = 0.0
        node.outputs[0].default_value = (0.0,0.0,0.0,)

        node = nodes.new("ShaderNodeCombineXYZ" )
        node.name = "Combine XYZ.008"
        node.parent = node_group.nodes["Coordinates"]
        node.location = (866, 158)
        node.inputs[0].default_value = 1.0
        node.inputs[1].default_value = 0.0
        node.inputs[2].default_value = 0.0
        node.outputs[0].default_value = (0.0,0.0,0.0,)

        node = nodes.new("ShaderNodeVectorRotate" )
        node.name = "Vector Rotate"
        node.parent = node_group.nodes["Coordinates"]
        node.location = (1027, -246)
        node.inputs[0].default_value = (0.0,0.0,0.0,)
        node.inputs[1].default_value = (0.0,0.0,0.0,)
        node.inputs[2].default_value = (0.0,0.0,1.0,)
        node.inputs[3].default_value = 0.0
        node.inputs[4].default_value = (0.0,0.0,0.0,)
        node.outputs[0].default_value = (0.0,0.0,0.0,)

        node = nodes.new("NodeReroute" )
        node.name = "Reroute.012"
        node.parent = node_group.nodes["Coordinates"]
        node.location = (1112, -265)

        node = nodes.new("ShaderNodeVectorRotate" )
        node.name = "Vector Rotate.001"
        node.parent = node_group.nodes["Coordinates"]
        node.location = (1253, 197)
        node.inputs[0].default_value = (0.0,0.0,0.0,)
        node.inputs[1].default_value = (0.0,0.0,0.0,)
        node.inputs[2].default_value = (0.0,0.0,1.0,)
        node.inputs[3].default_value = 0.0
        node.inputs[4].default_value = (0.0,0.0,0.0,)
        node.outputs[0].default_value = (0.0,0.0,0.0,)

        node = nodes.new("NodeReroute" )
        node.name = "Reroute.011"
        node.parent = node_group.nodes["Coordinates"]
        node.location = (1324, 136)

        node = nodes.new("NodeGroupOutput" )
        node.name = "Group Output"
        node.location = (1631, -13)
        node_group.outputs.new(type= 'NodeSocketGeometry', name='Detectlines')
        node_group.outputs.new(type= 'NodeSocketFloat', name='Rotation')
        node_group.outputs.new(type= 'NodeSocketFloat', name='Move')
        node_group.outputs.new(type= 'NodeSocketFloat', name='Height')
        links.new( nodes['Group Input'].outputs[0],  nodes['Reroute.004'].inputs[0])
        links.new( nodes['Group Input'].outputs[1],  nodes['Separate XYZ'].inputs[0])
        links.new( nodes['Group Input'].outputs[1],  nodes['Vector Rotate.001'].inputs[1])
        links.new( nodes['Group Input'].outputs[1],  nodes['Vector Rotate'].inputs[1])
        links.new( nodes['Group Input'].outputs[2],  nodes['Math.006'].inputs[0])
        links.new( nodes['Group Input'].outputs[3],  nodes['Math.014'].inputs[0])
        links.new( nodes['Group Input'].outputs[4],  nodes['Reroute.006'].inputs[0])
        links.new( nodes['Group Input'].outputs[5],  nodes['RotMath3'].inputs[0])
        links.new( nodes['Group Input'].outputs[6],  nodes['Reroute.010'].inputs[0])
        links.new( nodes['Group Input'].outputs[7],  nodes['Vector Rotate'].inputs[3])
        links.new( nodes['Group Input'].outputs[7],  nodes['Vector Rotate.001'].inputs[3])
        links.new( nodes['Group Input'].outputs[8],  nodes['Math.006'].inputs[1])
        links.new( nodes['Group Input'].outputs[9],  nodes['Math.014'].inputs[1])
        links.new( nodes['Reroute.007'].outputs[0],  nodes['Reroute'].inputs[0])
        links.new( nodes['Reroute.008'].outputs[0],  nodes['Reroute.001'].inputs[0])
        links.new( nodes['Reroute.009'].outputs[0],  nodes['Reroute.002'].inputs[0])
        links.new( nodes['Reroute.009'].outputs[0],  nodes['Math'].inputs[0])
        links.new( nodes['Reroute.020'].outputs[0],  nodes['Reroute.003'].inputs[0])
        links.new( nodes['Reroute.021'].outputs[0],  nodes['Reroute.005'].inputs[0])
        links.new( nodes['Reroute.004'].outputs[0],  nodes['RayP1'].inputs[0])
        links.new( nodes['Reroute.004'].outputs[0],  nodes['RayP2'].inputs[0])
        links.new( nodes['RotMath2.001'].outputs[0],  nodes['RotMath2'].inputs[0])
        links.new( nodes['Reroute.003'].outputs[0],  nodes['Math.004'].inputs[0])
        links.new( nodes['Reroute.005'].outputs[0],  nodes['Math.005'].inputs[0])
        links.new( nodes['Reroute.006'].outputs[0],  nodes['Math.007'].inputs[0])
        links.new( nodes['Reroute'].outputs[0],  nodes['Math.008'].inputs[0])
        links.new( nodes['Reroute'].outputs[0],  nodes['Math.009'].inputs[0])
        links.new( nodes['Reroute.023'].outputs[0],  nodes['Math.008'].inputs[1])
        links.new( nodes['Reroute.023'].outputs[0],  nodes['Math.009'].inputs[1])
        links.new( nodes['Reroute.022'].outputs[0],  nodes['Math.010'].inputs[1])
        links.new( nodes['Reroute.022'].outputs[0],  nodes['Math.011'].inputs[1])
        links.new( nodes['Reroute.001'].outputs[0],  nodes['Math.010'].inputs[0])
        links.new( nodes['Reroute.001'].outputs[0],  nodes['Math.011'].inputs[0])
        links.new( nodes['Math.007'].outputs[0],  nodes['Math.012'].inputs[1])
        links.new( nodes['Math.007'].outputs[0],  nodes['Math.013'].inputs[1])
        links.new( nodes['Math.008'].outputs[0],  nodes['Combine XYZ.008'].inputs[0])
        links.new( nodes['Reroute.002'].outputs[0],  nodes['Math.012'].inputs[0])
        links.new( nodes['Reroute.002'].outputs[0],  nodes['Math.013'].inputs[0])
        links.new( nodes['Math.010'].outputs[0],  nodes['Combine XYZ.008'].inputs[1])
        links.new( nodes['Math.012'].outputs[0],  nodes['Combine XYZ.008'].inputs[2])
        links.new( nodes['Math.009'].outputs[0],  nodes['Combine XYZ.009'].inputs[0])
        links.new( nodes['Math.011'].outputs[0],  nodes['Combine XYZ.009'].inputs[1])
        links.new( nodes['Math.013'].outputs[0],  nodes['Combine XYZ.009'].inputs[2])
        links.new( nodes['DisplayLine'].outputs[0],  nodes['DisplaySetP1'].inputs[0])
        links.new( nodes['DispayIndex'].outputs[0],  nodes['DisplayFind0'].inputs[1])
        links.new( nodes['DisplayFind0'].outputs[0],  nodes['DisplaySetP1'].inputs[1])
        links.new( nodes['Reroute.011'].outputs[0],  nodes['DisplaySetP1'].inputs[2])
        links.new( nodes['DisplayFind1'].outputs[0],  nodes['DisplaySetP2'].inputs[1])
        links.new( nodes['DisplaySetP1'].outputs[0],  nodes['DisplaySetP2'].inputs[0])
        links.new( nodes['Reroute.012'].outputs[0],  nodes['DisplaySetP2'].inputs[2])
        links.new( nodes['Reroute.011'].outputs[0],  nodes['RayP1'].inputs[6])
        links.new( nodes['Reroute.012'].outputs[0],  nodes['RayP2'].inputs[6])
        links.new( nodes['Reroute.010'].outputs[0],  nodes['MoveMath2'].inputs[1])
        links.new( nodes['Store Named Attribute'].outputs[0],  nodes['Group Output'].inputs[0])
        links.new( nodes['RotMath3'].outputs[0],  nodes['Group Output'].inputs[1])
        links.new( nodes['MoveMath2'].outputs[0],  nodes['Group Output'].inputs[2])
        links.new( nodes['RotMath3.001'].outputs[0],  nodes['RotMath3'].inputs[1])
        links.new( nodes['RayP2'].outputs[3],  nodes['RotMath1'].inputs[1])
        links.new( nodes['MoveMath1'].outputs[0],  nodes['MoveMath2'].inputs[0])
        links.new( nodes['RayP1'].outputs[3],  nodes['RotMath1'].inputs[0])
        links.new( nodes['RotMath1'].outputs[0],  nodes['MoveMath1'].inputs[0])
        links.new( nodes['DisplaySetP2'].outputs[0],  nodes['DisplayExtrude'].inputs[0])
        links.new( nodes['DisplayExtrudeCombine'].outputs[0],  nodes['DisplayExtrude'].inputs[2])
        links.new( nodes['Math'].outputs[0],  nodes['DisplayExtrudeCombine'].inputs[2])
        links.new( nodes['DispayIndex'].outputs[0],  nodes['DisplayFind1'].inputs[1])
        links.new( nodes['Separate XYZ'].outputs[0],  nodes['Reroute.007'].inputs[0])
        links.new( nodes['Separate XYZ'].outputs[1],  nodes['Reroute.008'].inputs[0])
        links.new( nodes['Separate XYZ'].outputs[2],  nodes['Reroute.009'].inputs[0])
        links.new( nodes['Vector Rotate.001'].outputs[0],  nodes['Reroute.011'].inputs[0])
        links.new( nodes['Vector Rotate'].outputs[0],  nodes['Reroute.012'].inputs[0])
        links.new( nodes['Combine XYZ.009'].outputs[0],  nodes['Vector Rotate'].inputs[0])
        links.new( nodes['RayP1'].outputs[1],  nodes['Separate XYZ.001'].inputs[0])
        links.new( nodes['RayP2'].outputs[1],  nodes['Separate XYZ.002'].inputs[0])
        links.new( nodes['Separate XYZ.002'].outputs[2],  nodes['Math.001'].inputs[1])
        links.new( nodes['Separate XYZ.001'].outputs[2],  nodes['Math.001'].inputs[0])
        links.new( nodes['Math.001'].outputs[0],  nodes['Math.002'].inputs[0])
        links.new( nodes['Math.002'].outputs[0],  nodes['Group Output'].inputs[3])
        links.new( nodes['Reroute.018'].outputs[0],  nodes['Math.003'].inputs[0])
        links.new( nodes['Reroute.019'].outputs[0],  nodes['Math.003'].inputs[1])
        links.new( nodes['Reroute.020'].outputs[0],  nodes['Reroute.013'].inputs[0])
        links.new( nodes['Reroute.021'].outputs[0],  nodes['Reroute.014'].inputs[0])
        links.new( nodes['Reroute.013'].outputs[0],  nodes['Reroute.015'].inputs[0])
        links.new( nodes['Reroute.014'].outputs[0],  nodes['Reroute.016'].inputs[0])
        links.new( nodes['RotMath1'].outputs[0],  nodes['Reroute.017'].inputs[0])
        links.new( nodes['Reroute.017'].outputs[0],  nodes['RotMath2.001'].inputs[0])
        links.new( nodes['Reroute.015'].outputs[0],  nodes['Reroute.018'].inputs[0])
        links.new( nodes['Reroute.016'].outputs[0],  nodes['Reroute.019'].inputs[0])
        links.new( nodes['Math.003'].outputs[0],  nodes['RotMath2.001'].inputs[1])
        links.new( nodes['DisplayExtrude'].outputs[0],  nodes['Store Named Attribute'].inputs[0])
        links.new( nodes['RotMath2'].outputs[0],  nodes['RotMath3.001'].inputs[0])
        links.new( nodes['Reroute.017'].outputs[0],  nodes['Store Named Attribute'].inputs[4])
        links.new( nodes['Combine XYZ.008'].outputs[0],  nodes['Vector Rotate.001'].inputs[0])
        links.new( nodes['Math.004'].outputs[0],  nodes['Reroute.023'].inputs[0])
        links.new( nodes['Math.005'].outputs[0],  nodes['Reroute.022'].inputs[0])
        links.new( nodes['Math.006'].outputs[0],  nodes['Reroute.020'].inputs[0])
        links.new( nodes['Math.014'].outputs[0],  nodes['Reroute.021'].inputs[0])
        
        

        self.label_nodes(node_group)
        return node_group



###############GeoFloat Start!!!!!!!!!!!!!!!!!!!!!
    def make_geofloat(self, context, goal, obj, ocean, cage, collision):
        print(f'make_geofloat goal {goal.name} obj {obj.name} ocean {ocean.name}')
        
        #get geo nodes Modifier
        mod, node_group = self.new_geonodes_mod(goal)
        
        aom_props = context.scene.aom_props
        is_GeoFloat_Smooth = aom_props.is_GeoFloat_Smooth
        instanceFloatobj = aom_props.instanceFloatobj
        
        proximity_ng = self.make_AOMFloat_ObjectFoamProximity_nodegroup()
        self.make_FloatRotMove_nodegroup()
        self.make_AOMFloat_plus_nodegroup()
        self.make_AOMFloat_Ripples_nodegroup()
        self.make_AOMFloat_Instancing_nodegroup()
        
        node_group = self.make_AOMGeoFloat_nodegroup(mod)
        
        
        
        mod.node_group = node_group
        
        #mod['Input_1'] = obj
        
        
        
        '''if is_GeoFloat_Smooth:
            mod.name = "GeoFloat_hash"
            node_group = self.make_GeoFloat_hash()  # !!!
        else:
            mod.name = "GeoFloat_plus"
            node_group = self.make_GeoFloat_plus(mod)
            #nodegroup.name = "Geoflat_plus"
        #self.move_mod_one_up(ocean, mod)'''

        

        if obj != None:
            mod['Input_1'] = obj
            # float_parent_id
            #obj.aom_data.ripple_parent = ocean
        if cage != None:
            mod['Input_4'] = cage
            #obj.aom_data.ripple_parent = ocean
        if collision != None:
            mod['Input_5'] = collision
        #obj.modifiers.active = mod

        ##buggy
        #self.move_above_DP(goal, mod)

    def make_AOMFloat_plus_nodegroup(self):
        # does it exist
        ngname = 'AOMFloat_plus'
        
        if ngname in bpy.data.node_groups:
            #mod.node_group = bpy.data.node_groups[ngname]
            return bpy.data.node_groups[ngname]

        node_group = bpy.data.node_groups.new(ngname, 'GeometryNodeTree')
        # self.remove_nodes(node_group)

        
        nodes = node_group.nodes
        links = node_group.links
        
        
        inp = node_group.inputs.new('NodeSocketGeometry','Geometry')
        inp = node_group.inputs.new('NodeSocketFloat','DetectionHeight')
        inp.default_value = 10.0
        inp = node_group.inputs.new('NodeSocketFloat','XRotSensitivity')
        inp.default_value = 1.0
        inp = node_group.inputs.new('NodeSocketFloat','YRotSensitivity')
        inp.default_value = 1.0
        inp = node_group.inputs.new('NodeSocketFloat','HeightSensitivity')
        inp.default_value = 1.0
        inp = node_group.inputs.new('NodeSocketFloat','XDetectionDistance')
        inp.default_value = 2.0
        inp = node_group.inputs.new('NodeSocketFloat','YDetectionDistance')
        inp.default_value = 3.0
        inp = node_group.inputs.new('NodeSocketFloat','MoveSensitivityX')
        inp.default_value = 0.2
        inp = node_group.inputs.new('NodeSocketFloat','MoveSensitivityY')
        inp.default_value = 0.2
        inp = node_group.inputs.new('NodeSocketFloat','XOffset')
        inp.default_value = 0.0
        inp = node_group.inputs.new('NodeSocketFloat','YOffset')
        inp.default_value = 0.0
        inp = node_group.inputs.new('NodeSocketFloat','ZOffset')
        inp.default_value = 0.0
        inp = node_group.inputs.new('NodeSocketBool','ShowFloatCage')
        inp.default_value = True
        inp = node_group.inputs.new('NodeSocketObject','Floatcage')

        node = nodes.new("NodeFrame" )
        node.name = "Frame.002"
        node.label = "ZRotation"
        node.location = (-2171, 319)

        node = nodes.new("NodeFrame" )
        node.name = "Frame.001"
        node.label = "DetectionPosition"
        node.location = (-2138, 80)

        node = nodes.new("NodeFrame" )
        node.name = "DisplayToggle"
        node.label = "DisplayToggle"
        node.location = (8, -1352)

        node = nodes.new("NodeFrame" )
        node.name = "OceanSurfaceDetection"
        node.label = "OceanSurfaceDetection"
        node.location = (-1074, -709)

        node = nodes.new("NodeFrame" )
        node.name = "Frame"
        node.label = "Move"
        node.location = (1295, 493)

        node = nodes.new("NodeFrame" )
        node.name = "Frame.005"
        node.label = "Get UV Coord at Ship Position_wird so aber immer übrspeichert"
        node.location = (1484, -785)

        node = nodes.new("NodeFrame" )
        node.name = "ShipFollowsurface"
        node.label = "ShipHeight"
        node.location = (27, 2225)

        node = nodes.new("NodeGroupInput" )
        node.name = "Group Input"
        node.location = (-3583, -434)

        node = nodes.new("NodeReroute" )
        node.name = "Reroute.015"
        node.location = (-2522, -1398)

        node = nodes.new("NodeReroute" )
        node.name = "Reroute.001"
        node.location = (-2227, -1146)

        node = nodes.new("NodeReroute" )
        node.name = "Reroute.003"
        node.location = (-2080, -626)

        node = nodes.new("NodeReroute" )
        node.name = "Reroute"
        node.location = (-1849, -377)

        node = nodes.new("ShaderNodeSeparateXYZ" )
        node.name = "Separate XYZ.001"
        node.location = (-1797, -719)
        node.hide = False
        node.inputs[0].default_value = (0.0,0.0,0.0,)
        node.outputs[0].default_value = 0.0
        node.outputs[1].default_value = 0.0
        node.outputs[2].default_value = 0.0

        node = nodes.new("NodeReroute" )
        node.name = "Reroute.004"
        node.location = (-1787, 48)

        node = nodes.new("NodeReroute" )
        node.name = "Reroute.005"
        node.location = (-1575, -643)

        node = nodes.new("ShaderNodeSeparateXYZ" )
        node.name = "HeightSep"
        node.parent = node_group.nodes["ShipFollowsurface"]
        node.location = (-1247, -2143)
        node.hide = False
        node.inputs[0].default_value = (0.0,0.0,0.0,)
        node.outputs[0].default_value = 0.0
        node.outputs[1].default_value = 0.0
        node.outputs[2].default_value = 0.0

        node = nodes.new("NodeReroute" )
        node.name = "Reroute.006"
        node.parent = node_group.nodes["ShipFollowsurface"]
        node.location = (-1219, -2334)

        node = nodes.new("NodeReroute" )
        node.name = "Reroute.002"
        node.location = (-1197, -185)

        node = nodes.new("NodeReroute" )
        node.name = "Reroute.007"
        node.location = (-1120, 523)

        node = nodes.new("ShaderNodeMath" )
        node.name = "Math.001"
        node.parent = node_group.nodes["ShipFollowsurface"]
        node.location = (-1041, -2383)
        node.operation = "DIVIDE"
        node.use_clamp = False
        node.hide = True
        node.inputs[0].default_value = 0.5
        node.inputs[1].default_value = 2.0
        node.inputs[2].default_value = 0.5
        node.outputs[0].default_value = 0.0

        node = nodes.new("ShaderNodeMath" )
        node.name = "Math"
        node.parent = node_group.nodes["ShipFollowsurface"]
        node.location = (-1040, -2352)
        node.operation = "ADD"
        node.use_clamp = False
        node.hide = True
        node.inputs[0].default_value = 0.5
        node.inputs[1].default_value = 0.5
        node.inputs[2].default_value = 0.5
        node.outputs[0].default_value = 0.0

        node = nodes.new("ShaderNodeMath" )
        node.name = "SetHeightSensitivity"
        node.parent = node_group.nodes["ShipFollowsurface"]
        node.location = (-734, -2275)
        node.operation = "MULTIPLY"
        node.use_clamp = False
        node.hide = False
        node.inputs[0].default_value = 0.5
        node.inputs[1].default_value = 1.0
        node.inputs[2].default_value = 0.5
        node.outputs[0].default_value = 0.0

        node = nodes.new("ShaderNodeCombineXYZ" )
        node.name = "RotComb"
        node.location = (-710, -312)
        node.hide = False
        node.inputs[0].default_value = 0.0
        node.inputs[1].default_value = 0.0
        node.inputs[2].default_value = 0.0
        node.outputs[0].default_value = (0.0,0.0,0.0,)

        node = nodes.new("GeometryNodeObjectInfo" )
        node.name = "Object Info"
        node.parent = node_group.nodes["Frame.001"]
        node.location = (-606, 65)
        node.transform_space = "RELATIVE"
        node.hide = False
        node.inputs[1].default_value = False
        node.outputs[0].default_value = (0.0,0.0,0.0,)
        node.outputs[1].default_value = (0.0,0.0,0.0,)
        node.outputs[2].default_value = (0.0,0.0,0.0,)

        node = nodes.new("ShaderNodeVectorMath" )
        node.name = "Vector Math.001"
        node.location = (-537, -243)
        node.operation = "MULTIPLY"
        node.hide = False
        node.inputs[0].default_value = (0.0,0.0,0.0,)
        node.inputs[1].default_value = (-1.0,1.0,-1.0,)
        node.inputs[2].default_value = (0.0,0.0,0.0,)
        node.inputs[3].default_value = 1.0
        node.outputs[0].default_value = (0.0,0.0,0.0,)
        node.outputs[1].default_value = 0.0

        node = nodes.new("ShaderNodeCombineXYZ" )
        node.name = "NewCoordinatesAfterMove"
        node.parent = node_group.nodes["Frame"]
        node.location = (-520, -70)
        node.hide = False
        node.inputs[0].default_value = 0.0
        node.inputs[1].default_value = 0.0
        node.inputs[2].default_value = 0.0
        node.outputs[0].default_value = (0.0,0.0,0.0,)

        node = nodes.new("ShaderNodeCombineXYZ" )
        node.name = "PToHeight"
        node.parent = node_group.nodes["Frame.001"]
        node.location = (-473, -216)
        node.hide = False
        node.inputs[0].default_value = 0.0
        node.inputs[1].default_value = 0.0
        node.inputs[2].default_value = 0.0
        node.outputs[0].default_value = (0.0,0.0,0.0,)

        node = nodes.new("ShaderNodeMath" )
        node.name = "Math.002"
        node.parent = node_group.nodes["ShipFollowsurface"]
        node.location = (-451, -2207)
        node.operation = "ADD"
        node.use_clamp = False
        node.hide = False
        node.inputs[0].default_value = 0.5
        node.inputs[1].default_value = 0.5
        node.inputs[2].default_value = 0.5
        node.outputs[0].default_value = 0.0

        node = nodes.new("GeometryNodeInputNamedAttribute" )
        node.name = "Named Attribute"
        node.parent = node_group.nodes["Frame.005"]
        node.location = (-416, 31)
        node.data_type = "FLOAT_VECTOR"
        node.hide = False
        node.inputs[0].default_value = "UVMap"
        node.outputs[0].default_value = (0.0,0.0,0.0,)
        node.outputs[1].default_value = 0.0
        node.outputs[2].default_value = (0.0,0.0,0.0,0.0,)
        node.outputs[3].default_value = False
        node.outputs[4].default_value = 0
        node.outputs[5].default_value = False

        node = nodes.new("GeometryNodeSampleNearest" )
        node.name = "Sample Nearest"
        node.parent = node_group.nodes["Frame.005"]
        node.location = (-382, 223)
        node.hide = False
        node.inputs[1].default_value = (0.0,0.0,0.0,)
        node.outputs[0].default_value = 0

        node = nodes.new("ShaderNodeVectorMath" )
        node.name = "MoveXY"
        node.parent = node_group.nodes["Frame"]
        node.location = (-345, -93)
        node.operation = "MULTIPLY"
        node.hide = False
        node.inputs[0].default_value = (0.0,0.0,0.0,)
        node.inputs[1].default_value = (1.0,1.0,0.0,)
        node.inputs[2].default_value = (0.0,0.0,0.0,)
        node.inputs[3].default_value = 1.0
        node.outputs[0].default_value = (0.0,0.0,0.0,)
        node.outputs[1].default_value = 0.0

        node = nodes.new("ShaderNodeSeparateXYZ" )
        node.name = "Separate XYZ"
        node.parent = node_group.nodes["Frame.002"]
        node.location = (-291, 181)
        node.hide = False
        node.inputs[0].default_value = (0.0,0.0,0.0,)
        node.outputs[0].default_value = 0.0
        node.outputs[1].default_value = 0.0
        node.outputs[2].default_value = 0.0

        node = nodes.new("GeometryNodeGroup" )
        node.name = "RotationX"
        node.parent = node_group.nodes["OceanSurfaceDetection"]
        node.location = (-285, 432)
        node.node_tree = bpy.data.node_groups["AOMFloatRotMove"]
        node.hide = False
        node.inputs[1].default_value = (0.0,0.0,0.0,)
        node.inputs[2].default_value = 0.0
        node.inputs[3].default_value = 2.3
        node.inputs[4].default_value = 0.0
        node.inputs[5].default_value = 1.0
        node.inputs[6].default_value = 1.0
        node.inputs[7].default_value = 0.0
        node.inputs[8].default_value = 1.0
        node.inputs[9].default_value = 1.0
        node.outputs[1].default_value = 0.0
        node.outputs[2].default_value = 0.0
        node.outputs[3].default_value = 0.0

        node = nodes.new("GeometryNodeGroup" )
        node.name = "RotationY"
        node.parent = node_group.nodes["OceanSurfaceDetection"]
        node.location = (-277, 45)
        node.node_tree = bpy.data.node_groups["AOMFloatRotMove"]
        node.hide = False
        node.inputs[1].default_value = (0.0,0.0,0.0,)
        node.inputs[2].default_value = 1.6
        node.inputs[3].default_value = 0.0
        node.inputs[4].default_value = 0.0
        node.inputs[5].default_value = 1.0
        node.inputs[6].default_value = 1.0
        node.inputs[7].default_value = 0.0
        node.inputs[8].default_value = -1.5
        node.inputs[9].default_value = 1.0
        node.outputs[1].default_value = 0.0
        node.outputs[2].default_value = 0.0
        node.outputs[3].default_value = 0.0

        node = nodes.new("GeometryNodeJoinGeometry" )
        node.name = "JoinDisplay"
        node.parent = node_group.nodes["DisplayToggle"]
        node.location = (-249, 246)
        node.hide = False

        node = nodes.new("NodeReroute" )
        node.name = "Reroute.009"
        node.location = (-234, -463)

        node = nodes.new("NodeReroute" )
        node.name = "Reroute.013"
        node.parent = node_group.nodes["Frame.001"]
        node.location = (-173, -288)

        node = nodes.new("ShaderNodeVectorMath" )
        node.name = "Vector Math"
        node.parent = node_group.nodes["Frame.001"]
        node.location = (-156, 3)
        node.operation = "ADD"
        node.hide = True
        node.inputs[0].default_value = (0.0,0.0,0.0,)
        node.inputs[1].default_value = (0.0,0.0,0.0,)
        node.inputs[2].default_value = (0.0,0.0,0.0,)
        node.inputs[3].default_value = 1.0
        node.outputs[0].default_value = (0.0,0.0,0.0,)
        node.outputs[1].default_value = 0.0

        node = nodes.new("GeometryNodeSampleIndex" )
        node.name = "Sample Index"
        node.parent = node_group.nodes["Frame.005"]
        node.location = (-118, 201)
        node.data_type = "FLOAT_VECTOR"
        node.clamp = False
        node.hide = False
        node.inputs[1].default_value = 0.0
        node.inputs[2].default_value = 0
        node.inputs[3].default_value = (0.0,0.0,0.0,)
        node.inputs[4].default_value = (0.0,0.0,0.0,0.0,)
        node.inputs[5].default_value = False
        node.inputs[6].default_value = 0
        node.outputs[0].default_value = 0.0
        node.outputs[1].default_value = 0
        node.outputs[2].default_value = (0.0,0.0,0.0,)
        node.outputs[3].default_value = (0.0,0.0,0.0,0.0,)
        node.outputs[4].default_value = False

        node = nodes.new("ShaderNodeCombineXYZ" )
        node.name = "HeightComb"
        node.parent = node_group.nodes["ShipFollowsurface"]
        node.location = (-86, -2126)
        node.hide = False
        node.inputs[0].default_value = 0.0
        node.inputs[1].default_value = 0.0
        node.inputs[2].default_value = 0.0
        node.outputs[0].default_value = (0.0,0.0,0.0,)

        node = nodes.new("GeometryNodeStoreNamedAttribute" )
        node.name = "Store Named Attribute"
        node.parent = node_group.nodes["Frame.005"]
        node.location = (43, 376)
        node.data_type = "FLOAT_VECTOR"
        node.hide = False
        node.inputs[1].default_value = True
        node.inputs[2].default_value = "Obj_UVCoord"
        node.inputs[3].default_value = (0.0,0.0,0.0,)
        node.inputs[4].default_value = 0.0
        node.inputs[5].default_value = (0.0,0.0,0.0,0.0,)
        node.inputs[6].default_value = False
        node.inputs[7].default_value = 0

        node = nodes.new("GeometryNodeSwitch" )
        node.name = "DisplaySwitch"
        node.parent = node_group.nodes["DisplayToggle"]
        node.location = (70, 246)
        node.input_type = "GEOMETRY"
        node.hide = False
        node.inputs[0].default_value = False
        node.inputs[1].default_value = False
        node.inputs[2].default_value = 0.0
        node.inputs[3].default_value = 0.0
        node.inputs[4].default_value = 0
        node.inputs[5].default_value = 0
        node.inputs[6].default_value = False
        node.inputs[7].default_value = True
        node.inputs[8].default_value = (0.0,0.0,0.0,)
        node.inputs[9].default_value = (0.0,0.0,0.0,)
        node.inputs[10].default_value = (0.800000011920929,0.800000011920929,0.800000011920929,1.0,)
        node.inputs[11].default_value = (0.800000011920929,0.800000011920929,0.800000011920929,1.0,)
        node.inputs[12].default_value = ""
        node.inputs[13].default_value = ""
        node.outputs[0].default_value = 0.0
        node.outputs[1].default_value = 0
        node.outputs[2].default_value = False
        node.outputs[3].default_value = (0.0,0.0,0.0,)
        node.outputs[4].default_value = (0.0,0.0,0.0,0.0,)
        node.outputs[5].default_value = ""
        node.outputs[7].default_value = None
        node.outputs[8].default_value = None
        node.outputs[9].default_value = None
        node.outputs[10].default_value = None
        node.outputs[11].default_value = None

        node = nodes.new("NodeReroute" )
        node.name = "Reroute.010"
        node.parent = node_group.nodes["ShipFollowsurface"]
        node.location = (171, -2156)

        node = nodes.new("ShaderNodeCombineXYZ" )
        node.name = "Combine XYZ"
        node.parent = node_group.nodes["Frame.002"]
        node.location = (260, 243)
        node.hide = False
        node.inputs[0].default_value = 0.0
        node.inputs[1].default_value = 0.0
        node.inputs[2].default_value = 0.0
        node.outputs[0].default_value = (0.0,0.0,0.0,)

        node = nodes.new("NodeReroute" )
        node.name = "Reroute.008"
        node.location = (349, -319)

        node = nodes.new("ShaderNodeVectorMath" )
        node.name = "Vector Math.003"
        node.location = (1280, -27)
        node.operation = "ADD"
        node.hide = False
        node.inputs[0].default_value = (0.0,0.0,0.0,)
        node.inputs[1].default_value = (0.0,0.0,0.0,)
        node.inputs[2].default_value = (0.0,0.0,0.0,)
        node.inputs[3].default_value = 1.0
        node.outputs[0].default_value = (0.0,0.0,0.0,)
        node.outputs[1].default_value = 0.0

        node = nodes.new("NodeReroute" )
        node.name = "Reroute.016"
        node.location = (1995, -1093)

        node = nodes.new("NodeReroute" )
        node.name = "Reroute.012"
        node.location = (2083, -456)

        node = nodes.new("NodeReroute" )
        node.name = "Reroute.011"
        node.location = (2590, -317)

        node = nodes.new("GeometryNodeJoinGeometry" )
        node.name = "JoinAll"
        node.location = (2920, -263)
        node.hide = False

        node = nodes.new("NodeReroute" )
        node.name = "Reroute.014"
        node.location = (3035, -1295)

        node = nodes.new("NodeGroupOutput" )
        node.name = "Group Output"
        node.location = (3521, -251)
        node_group.outputs.new(type= 'NodeSocketGeometry', name='Geometry')
        node_group.outputs.new(type= 'NodeSocketVector', name='XY-Rotation')
        node_group.outputs.new(type= 'NodeSocketVector', name='Z-Rotation')
        node_group.outputs.new(type= 'NodeSocketVector', name='Position')
        node_group.outputs.new(type= 'NodeSocketVector', name='Scale')
        links.new( nodes['Group Input'].outputs[0],  nodes['Reroute.003'].inputs[0])
        links.new( nodes['Group Input'].outputs[1],  nodes['PToHeight'].inputs[2])
        links.new( nodes['Group Input'].outputs[1],  nodes['NewCoordinatesAfterMove'].inputs[2])
        links.new( nodes['Group Input'].outputs[2],  nodes['Reroute'].inputs[0])
        links.new( nodes['Group Input'].outputs[3],  nodes['Reroute.001'].inputs[0])
        links.new( nodes['Group Input'].outputs[4],  nodes['Reroute.002'].inputs[0])
        links.new( nodes['Group Input'].outputs[5],  nodes['RotationY'].inputs[2])
        links.new( nodes['Group Input'].outputs[6],  nodes['RotationX'].inputs[3])
        links.new( nodes['Group Input'].outputs[7],  nodes['RotationX'].inputs[6])
        links.new( nodes['Group Input'].outputs[8],  nodes['RotationY'].inputs[6])
        links.new( nodes['Group Input'].outputs[9],  nodes['PToHeight'].inputs[0])
        links.new( nodes['Group Input'].outputs[10],  nodes['PToHeight'].inputs[1])
        links.new( nodes['Group Input'].outputs[11],  nodes['Reroute.006'].inputs[0])
        links.new( nodes['Group Input'].outputs[12],  nodes['DisplaySwitch'].inputs[1])
        links.new( nodes['Group Input'].outputs[13],  nodes['Object Info'].inputs[0])
        links.new( nodes['RotationY'].outputs[0],  nodes['JoinDisplay'].inputs[0])
        links.new( nodes['JoinAll'].outputs[0],  nodes['Group Output'].inputs[0])
        links.new( nodes['RotationY'].outputs[1],  nodes['RotComb'].inputs[1])
        links.new( nodes['RotationX'].outputs[1],  nodes['RotComb'].inputs[0])
        links.new( nodes['RotationX'].outputs[0],  nodes['JoinDisplay'].inputs[0])
        links.new( nodes['HeightSep'].outputs[0],  nodes['HeightComb'].inputs[0])
        links.new( nodes['HeightSep'].outputs[1],  nodes['HeightComb'].inputs[1])
        links.new( nodes['Math.002'].outputs[0],  nodes['HeightComb'].inputs[2])
        links.new( nodes['Reroute.002'].outputs[0],  nodes['SetHeightSensitivity'].inputs[1])
        links.new( nodes['Reroute'].outputs[0],  nodes['RotationX'].inputs[5])
        links.new( nodes['Reroute.001'].outputs[0],  nodes['RotationY'].inputs[5])
        links.new( nodes['RotationY'].outputs[2],  nodes['NewCoordinatesAfterMove'].inputs[1])
        links.new( nodes['RotationX'].outputs[2],  nodes['NewCoordinatesAfterMove'].inputs[0])
        links.new( nodes['NewCoordinatesAfterMove'].outputs[0],  nodes['MoveXY'].inputs[0])
        links.new( nodes['Reroute.016'].outputs[0],  nodes['JoinAll'].inputs[0])
        links.new( nodes['JoinDisplay'].outputs[0],  nodes['DisplaySwitch'].inputs[15])
        links.new( nodes['Reroute.003'].outputs[0],  nodes['RotationX'].inputs[0])
        links.new( nodes['Reroute.003'].outputs[0],  nodes['RotationY'].inputs[0])
        links.new( nodes['PToHeight'].outputs[0],  nodes['Vector Math'].inputs[0])
        links.new( nodes['Object Info'].outputs[0],  nodes['Vector Math'].inputs[1])
        links.new( nodes['Reroute.004'].outputs[0],  nodes['RotationX'].inputs[1])
        links.new( nodes['Reroute.004'].outputs[0],  nodes['RotationY'].inputs[1])
        links.new( nodes['Object Info'].outputs[1],  nodes['Separate XYZ'].inputs[0])
        links.new( nodes['Separate XYZ'].outputs[2],  nodes['Combine XYZ'].inputs[2])
        links.new( nodes['Vector Math'].outputs[0],  nodes['Reroute.004'].inputs[0])
        links.new( nodes['Reroute.005'].outputs[0],  nodes['RotationY'].inputs[7])
        links.new( nodes['Reroute.005'].outputs[0],  nodes['RotationX'].inputs[7])
        links.new( nodes['Separate XYZ'].outputs[2],  nodes['Reroute.005'].inputs[0])
        links.new( nodes['RotationX'].outputs[3],  nodes['Math'].inputs[0])
        links.new( nodes['RotationY'].outputs[3],  nodes['Math'].inputs[1])
        links.new( nodes['Math'].outputs[0],  nodes['Math.001'].inputs[0])
        links.new( nodes['Reroute.004'].outputs[0],  nodes['HeightSep'].inputs[0])
        links.new( nodes['SetHeightSensitivity'].outputs[0],  nodes['Math.002'].inputs[0])
        links.new( nodes['RotComb'].outputs[0],  nodes['Vector Math.001'].inputs[0])
        links.new( nodes['Math.001'].outputs[0],  nodes['SetHeightSensitivity'].inputs[0])
        links.new( nodes['Reroute.006'].outputs[0],  nodes['Math.002'].inputs[1])
        links.new( nodes['Vector Math.001'].outputs[0],  nodes['Reroute.008'].inputs[0])
        links.new( nodes['Reroute.008'].outputs[0],  nodes['Group Output'].inputs[1])
        links.new( nodes['Vector Math.003'].outputs[0],  nodes['Group Output'].inputs[3])
        links.new( nodes['HeightComb'].outputs[0],  nodes['Reroute.010'].inputs[0])
        links.new( nodes['Reroute.009'].outputs[0],  nodes['Sample Index'].inputs[0])
        links.new( nodes['Named Attribute'].outputs[0],  nodes['Sample Index'].inputs[1])
        links.new( nodes['Reroute.003'].outputs[0],  nodes['Reroute.009'].inputs[0])
        links.new( nodes['Reroute.011'].outputs[0],  nodes['JoinAll'].inputs[0])
        links.new( nodes['Reroute.010'].outputs[0],  nodes['Vector Math.003'].inputs[0])
        links.new( nodes['MoveXY'].outputs[0],  nodes['Vector Math.003'].inputs[1])
        links.new( nodes['Vector Math.003'].outputs[0],  nodes['Sample Nearest'].inputs[1])
        links.new( nodes['Reroute.009'].outputs[0],  nodes['Store Named Attribute'].inputs[0])
        links.new( nodes['Named Attribute'].outputs[0],  nodes['Sample Index'].inputs[3])
        links.new( nodes['Sample Nearest'].outputs[0],  nodes['Sample Index'].inputs[6])
        links.new( nodes['Sample Index'].outputs[2],  nodes['Store Named Attribute'].inputs[3])
        links.new( nodes['Reroute.009'].outputs[0],  nodes['Sample Nearest'].inputs[0])
        links.new( nodes['Reroute.012'].outputs[0],  nodes['Reroute.011'].inputs[0])
        links.new( nodes['Store Named Attribute'].outputs[0],  nodes['Reroute.012'].inputs[0])
        links.new( nodes['Object Info'].outputs[2],  nodes['Reroute.013'].inputs[0])
        links.new( nodes['Reroute.014'].outputs[0],  nodes['Group Output'].inputs[4])
        links.new( nodes['Separate XYZ.001'].outputs[0],  nodes['RotationY'].inputs[8])
        links.new( nodes['Separate XYZ.001'].outputs[0],  nodes['RotationX'].inputs[8])
        links.new( nodes['Separate XYZ.001'].outputs[1],  nodes['RotationX'].inputs[9])
        links.new( nodes['Separate XYZ.001'].outputs[1],  nodes['RotationY'].inputs[9])
        links.new( nodes['Reroute.013'].outputs[0],  nodes['Separate XYZ.001'].inputs[0])
        links.new( nodes['Reroute.015'].outputs[0],  nodes['Reroute.014'].inputs[0])
        links.new( nodes['Reroute.013'].outputs[0],  nodes['Reroute.015'].inputs[0])
        links.new( nodes['Combine XYZ'].outputs[0],  nodes['Reroute.007'].inputs[0])
        links.new( nodes['Reroute.007'].outputs[0],  nodes['Group Output'].inputs[2])
        links.new( nodes['DisplaySwitch'].outputs[6],  nodes['Reroute.016'].inputs[0])

        self.label_nodes(node_group)
        return node_group

    
    def make_AOMFloat_ObjectFoamProximity_nodegroup(self):
        # does it exist
        ngname = 'AOMFloat_ObjectFoamProximity'
        if ngname in bpy.data.node_groups:
            return bpy.data.node_groups[ngname]

        node_group = bpy.data.node_groups.new(ngname, 'GeometryNodeTree')
        # self.remove_nodes(node_group)
        nodes = node_group.nodes
        links = node_group.links
        
        
        inp = node_group.inputs.new('NodeSocketGeometry','Input')
        inp = node_group.inputs.new('NodeSocketBool','Use Object Foam')
        inp.default_value = False
        inp = node_group.inputs.new('NodeSocketVectorTranslation','Position')
        inp.default_value = (0.0,0.0,0.0,)
        inp = node_group.inputs.new('NodeSocketVector','Rotation')
        inp.default_value = (0.0,0.0,0.0,)
        inp = node_group.inputs.new('NodeSocketVectorEuler','Z-Rotation')
        inp.default_value = (0.0,0.0,0.0,)
        inp = node_group.inputs.new('NodeSocketVectorXYZ','Scale')
        inp.default_value = (1.0,1.0,1.0,)
        inp = node_group.inputs.new('NodeSocketString','Foam Attribute')
        inp.default_value = "foam"
        inp = node_group.inputs.new('NodeSocketObject','Collision Object')
        inp = node_group.inputs.new('NodeSocketBool','Show CollisionObject')
        inp.default_value = False
        inp = node_group.inputs.new('NodeSocketFloat','FoamDistance')
        inp.default_value = 11.0
        inp = node_group.inputs.new('NodeSocketFloat','FoamAmount?')
        inp.default_value = 0.2

        node = nodes.new("NodeFrame" )
        node.name = "Frame.001"
        node.label = "Coordinates"
        node.location = (-1100, 0)

        node = nodes.new("NodeFrame" )
        node.name = "Frame.002"
        node.label = "Proximity+Ranging"
        node.location = (-203, 194)

        node = nodes.new("NodeFrame" )
        node.name = "Frame"
        node.label = "Add To FoamAttribute"
        node.location = (738, 112)

        node = nodes.new("NodeGroupInput" )
        node.name = "Group Input"
        node.location = (-2629, -212)

        node = nodes.new("NodeReroute" )
        node.name = "Reroute.007"
        node.location = (-1952, -425)

        node = nodes.new("GeometryNodeObjectInfo" )
        node.name = "Object Info"
        node.parent = node_group.nodes["Frame.001"]
        node.location = (-1171, 493)
        node.transform_space = "ORIGINAL"
        node.inputs[1].default_value = False
        node.outputs[0].default_value = (0.0,0.0,0.0,)
        node.outputs[1].default_value = (0.0,0.0,0.0,)
        node.outputs[2].default_value = (0.0,0.0,0.0,)

        node = nodes.new("ShaderNodeVectorMath" )
        node.name = "Vector Math.002"
        node.parent = node_group.nodes["Frame.001"]
        node.location = (-926, 185)
        node.mute = True
        node.operation = "MULTIPLY"
        node.inputs[0].default_value = (0.0,0.0,0.0,)
        node.inputs[1].default_value = (-1.0,-1.0,-1.0,)
        node.inputs[2].default_value = (0.0,0.0,0.0,)
        node.inputs[3].default_value = 1.0
        node.outputs[0].default_value = (0.0,0.0,0.0,)
        node.outputs[1].default_value = 0.0

        node = nodes.new("NodeReroute" )
        node.name = "Reroute.001"
        node.location = (-773, -386)

        node = nodes.new("GeometryNodeInputPosition" )
        node.name = "Position.001"
        node.parent = node_group.nodes["Frame.001"]
        node.location = (-714, 185)
        node.outputs[0].default_value = (0.0,0.0,0.0,)

        node = nodes.new("GeometryNodeTransform" )
        node.name = "Transform Geometry.002"
        node.parent = node_group.nodes["Frame.001"]
        node.location = (-706, 480)
        node.inputs[1].default_value = (0.0,0.0,0.0,)
        node.inputs[2].default_value = (0.0,0.0,0.0,)
        node.inputs[3].default_value = (1.0,1.0,1.0,)

        node = nodes.new("GeometryNodeProximity" )
        node.name = "Geometry Proximity"
        node.parent = node_group.nodes["Frame.002"]
        node.location = (-656, 226)
        node.inputs[1].default_value = (0.0,0.0,0.0,)
        node.outputs[0].default_value = (0.0,0.0,0.0,)
        node.outputs[1].default_value = 0.0

        node = nodes.new("ShaderNodeVectorRotate" )
        node.name = "Vector Rotate"
        node.parent = node_group.nodes["Frame.001"]
        node.rotation_type = "EULER_XYZ"
        node.location = (-540, 262)
        node.inputs[0].default_value = (0.0,0.0,0.0,)
        node.inputs[1].default_value = (0.0,0.0,0.0,)
        node.inputs[2].default_value = (0.0,0.0,1.0,)
        node.inputs[3].default_value = 0.0
        node.inputs[4].default_value = (0.0,0.0,0.0,)
        node.outputs[0].default_value = (0.0,0.0,0.0,)

        node = nodes.new("NodeReroute" )
        node.name = "Reroute.002"
        node.location = (-444, -386)

        node = nodes.new("GeometryNodeInputNamedAttribute" )
        node.name = "Named Attribute"
        node.parent = node_group.nodes["Frame"]
        node.location = (-381, -145)
        node.data_type = "FLOAT"
        node.inputs[0].default_value = "foam"
        node.outputs[0].default_value = (0.0,0.0,0.0,)
        node.outputs[1].default_value = 0.0
        node.outputs[2].default_value = (0.0,0.0,0.0,0.0,)
        node.outputs[3].default_value = False
        node.outputs[4].default_value = 0
        node.outputs[5].default_value = False

        node = nodes.new("NodeReroute" )
        node.name = "Reroute.005"
        node.location = (-328, 77)

        node = nodes.new("GeometryNodeSetPosition" )
        node.name = "Set Position"
        node.parent = node_group.nodes["Frame.001"]
        node.location = (-327, 436)
        node.inputs[1].default_value = True
        node.inputs[2].default_value = (0.0,0.0,0.0,)
        node.inputs[3].default_value = (0.0,0.0,0.0,)

        node = nodes.new("ShaderNodeMath" )
        node.name = "Math.002"
        node.parent = node_group.nodes["Frame.002"]
        node.location = (-326, 298)
        node.operation = "DIVIDE"
        node.use_clamp = False
        node.inputs[0].default_value = 1.0
        node.inputs[1].default_value = 0.5
        node.inputs[2].default_value = 0.5
        node.outputs[0].default_value = 0.0

        node = nodes.new("NodeReroute" )
        node.name = "Reroute.003"
        node.parent = node_group.nodes["Frame.001"]
        node.location = (-211, 30)

        node = nodes.new("ShaderNodeMath" )
        node.name = "Math.001"
        node.parent = node_group.nodes["Frame"]
        node.location = (-187, -48)
        node.operation = "ADD"
        node.use_clamp = True
        node.inputs[0].default_value = 0.0
        node.inputs[1].default_value = 0.5
        node.inputs[2].default_value = 0.5
        node.outputs[0].default_value = 0.0

        node = nodes.new("GeometryNodeSwitch" )
        node.name = "Switch"
        node.location = (-116, -251)
        node.input_type = "GEOMETRY"
        node.inputs[0].default_value = False
        node.inputs[1].default_value = False
        node.inputs[2].default_value = 0.0
        node.inputs[3].default_value = 0.0
        node.inputs[4].default_value = 0
        node.inputs[5].default_value = 0
        node.inputs[6].default_value = False
        node.inputs[7].default_value = True
        node.inputs[8].default_value = (0.0,0.0,0.0,)
        node.inputs[9].default_value = (0.0,0.0,0.0,)
        node.inputs[10].default_value = (0.800000011920929,0.800000011920929,0.800000011920929,1.0,)
        node.inputs[11].default_value = (0.800000011920929,0.800000011920929,0.800000011920929,1.0,)
        node.inputs[12].default_value = ""
        node.inputs[13].default_value = ""
        node.outputs[0].default_value = 0.0
        node.outputs[1].default_value = 0
        node.outputs[2].default_value = False
        node.outputs[3].default_value = (0.0,0.0,0.0,)
        node.outputs[4].default_value = (0.0,0.0,0.0,0.0,)
        node.outputs[5].default_value = ""
        node.outputs[7].default_value = None
        node.outputs[8].default_value = None
        node.outputs[9].default_value = None
        node.outputs[10].default_value = None
        node.outputs[11].default_value = None

        node = nodes.new("GeometryNodeTransform" )
        node.name = "Transform Geometry.001"
        node.parent = node_group.nodes["Frame.001"]
        node.location = (-114, 455)
        node.inputs[1].default_value = (0.0,0.0,0.0,)
        node.inputs[2].default_value = (0.0,0.0,0.0,)
        node.inputs[3].default_value = (1.0,1.0,1.0,)

        node = nodes.new("ShaderNodeMapRange" )
        node.name = "Map Range.001"
        node.parent = node_group.nodes["Frame.002"]
        node.location = (-113, 298)
        node.data_type = "FLOAT"
        node.interpolation_type = "LINEAR"
        node.clamp = False
        node.inputs[0].default_value = 1.0
        node.inputs[1].default_value = 0.0
        node.inputs[2].default_value = 11.0
        node.inputs[3].default_value = 0.0
        node.inputs[4].default_value = 0.2
        node.inputs[5].default_value = 4.0
        node.inputs[6].default_value = (0.0,0.0,0.0,)
        node.inputs[7].default_value = (0.0,0.0,0.0,)
        node.inputs[8].default_value = (1.0,1.0,1.0,)
        node.inputs[9].default_value = (0.0,0.0,0.0,)
        node.inputs[10].default_value = (1.0,1.0,1.0,)
        node.inputs[11].default_value = (4.0,4.0,4.0,)
        node.outputs[0].default_value = 0.0
        node.outputs[1].default_value = (0.0,0.0,0.0,)

        node = nodes.new("NodeReroute" )
        node.name = "Reroute"
        node.location = (-19, -193)

        node = nodes.new("NodeReroute" )
        node.name = "Reroute.006"
        node.parent = node_group.nodes["Frame"]
        node.location = (87, -541)

        node = nodes.new("GeometryNodeSwitch" )
        node.name = "Switch.001"
        node.parent = node_group.nodes["Frame"]
        node.location = (122, -151)
        node.input_type = "FLOAT"
        node.inputs[0].default_value = False
        node.inputs[1].default_value = False
        node.inputs[2].default_value = 0.0
        node.inputs[3].default_value = 0.0
        node.inputs[4].default_value = 0
        node.inputs[5].default_value = 0
        node.inputs[6].default_value = False
        node.inputs[7].default_value = True
        node.inputs[8].default_value = (0.0,0.0,0.0,)
        node.inputs[9].default_value = (0.0,0.0,0.0,)
        node.inputs[10].default_value = (0.800000011920929,0.800000011920929,0.800000011920929,1.0,)
        node.inputs[11].default_value = (0.800000011920929,0.800000011920929,0.800000011920929,1.0,)
        node.inputs[12].default_value = ""
        node.inputs[13].default_value = ""
        node.outputs[0].default_value = 0.0
        node.outputs[1].default_value = 0
        node.outputs[2].default_value = False
        node.outputs[3].default_value = (0.0,0.0,0.0,)
        node.outputs[4].default_value = (0.0,0.0,0.0,0.0,)
        node.outputs[5].default_value = ""
        node.outputs[7].default_value = None
        node.outputs[8].default_value = None
        node.outputs[9].default_value = None
        node.outputs[10].default_value = None
        node.outputs[11].default_value = None

        node = nodes.new("GeometryNodeJoinGeometry" )
        node.name = "Join Geometry"
        node.location = (135, -232)

        node = nodes.new("GeometryNodeStoreNamedAttribute" )
        node.name = "Store Named Attribute"
        node.parent = node_group.nodes["Frame"]
        node.location = (342, -246)
        node.data_type = "FLOAT"
        node.inputs[1].default_value = True
        node.inputs[2].default_value = "foam"
        node.inputs[3].default_value = (0.0,0.0,0.0,)
        node.inputs[4].default_value = 0.0
        node.inputs[5].default_value = (0.0,0.0,0.0,0.0,)
        node.inputs[6].default_value = False
        node.inputs[7].default_value = 1

        node = nodes.new("NodeGroupInput" )
        node.name = "Group Input.001"
        node.location = (377, 456)

        node = nodes.new("NodeReroute" )
        node.name = "Reroute.004"
        node.location = (1063, 96)

        node = nodes.new("NodeGroupOutput" )
        node.name = "Group Output"
        node.location = (1488, -58)
        node_group.outputs.new(type= 'NodeSocketGeometry', name='Geometry')
        node_group.outputs.new(type= 'NodeSocketFloat', name='Distance')
        links.new( nodes['Group Input'].outputs[0],  nodes['Reroute'].inputs[0])
        links.new( nodes['Group Input'].outputs[2],  nodes['Reroute.003'].inputs[0])
        links.new( nodes['Group Input'].outputs[3],  nodes['Vector Math.002'].inputs[0])
        links.new( nodes['Group Input'].outputs[4],  nodes['Transform Geometry.002'].inputs[2])
        links.new( nodes['Group Input'].outputs[5],  nodes['Transform Geometry.002'].inputs[3])
        links.new( nodes['Group Input'].outputs[6],  nodes['Named Attribute'].inputs[0])
        links.new( nodes['Group Input'].outputs[6],  nodes['Reroute.007'].inputs[0])
        links.new( nodes['Group Input'].outputs[7],  nodes['Object Info'].inputs[0])
        links.new( nodes['Group Input'].outputs[8],  nodes['Switch'].inputs[1])
        links.new( nodes['Group Input'].outputs[9],  nodes['Map Range.001'].inputs[2])
        links.new( nodes['Group Input'].outputs[10],  nodes['Map Range.001'].inputs[4])
        links.new( nodes['Group Input.001'].outputs[1],  nodes['Switch.001'].inputs[0])
        links.new( nodes['Switch.001'].outputs[0],  nodes['Store Named Attribute'].inputs[4])
        links.new( nodes['Named Attribute'].outputs[1],  nodes['Math.001'].inputs[1])
        links.new( nodes['Join Geometry'].outputs[0],  nodes['Store Named Attribute'].inputs[0])
        links.new( nodes['Store Named Attribute'].outputs[0],  nodes['Group Output'].inputs[0])
        links.new( nodes['Reroute.006'].outputs[0],  nodes['Store Named Attribute'].inputs[2])
        links.new( nodes['Reroute'].outputs[0],  nodes['Join Geometry'].inputs[0])
        links.new( nodes['Transform Geometry.001'].outputs[0],  nodes['Reroute.001'].inputs[0])
        links.new( nodes['Reroute.001'].outputs[0],  nodes['Reroute.002'].inputs[0])
        links.new( nodes['Reroute.002'].outputs[0],  nodes['Switch'].inputs[15])
        links.new( nodes['Switch'].outputs[6],  nodes['Join Geometry'].inputs[0])
        links.new( nodes['Set Position'].outputs[0],  nodes['Transform Geometry.001'].inputs[0])
        links.new( nodes['Transform Geometry.002'].outputs[0],  nodes['Set Position'].inputs[0])
        links.new( nodes['Vector Math.002'].outputs[0],  nodes['Vector Rotate'].inputs[4])
        links.new( nodes['Position.001'].outputs[0],  nodes['Vector Rotate'].inputs[0])
        links.new( nodes['Vector Rotate'].outputs[0],  nodes['Set Position'].inputs[2])
        links.new( nodes['Reroute.003'].outputs[0],  nodes['Transform Geometry.001'].inputs[1])
        links.new( nodes['Math.002'].outputs[0],  nodes['Map Range.001'].inputs[0])
        links.new( nodes['Map Range.001'].outputs[0],  nodes['Math.001'].inputs[0])
        links.new( nodes['Transform Geometry.001'].outputs[0],  nodes['Geometry Proximity'].inputs[0])
        links.new( nodes['Geometry Proximity'].outputs[1],  nodes['Math.002'].inputs[1])
        links.new( nodes['Reroute.004'].outputs[0],  nodes['Group Output'].inputs[1])
        links.new( nodes['Geometry Proximity'].outputs[1],  nodes['Reroute.005'].inputs[0])
        links.new( nodes['Reroute.007'].outputs[0],  nodes['Reroute.006'].inputs[0])
        links.new( nodes['Object Info'].outputs[3],  nodes['Transform Geometry.002'].inputs[0])
        links.new( nodes['Reroute.005'].outputs[0],  nodes['Reroute.004'].inputs[0])
        links.new( nodes['Math.001'].outputs[0],  nodes['Switch.001'].inputs[3])
        links.new( nodes['Named Attribute'].outputs[1],  nodes['Switch.001'].inputs[2])

        
        return node_group


    def make_AOMFloat_Ripples_nodegroup(self):
        # does it exist
        ngname = 'AOMFloat_Ripples'
        if ngname in bpy.data.node_groups:
            return bpy.data.node_groups[ngname]

        node_group = bpy.data.node_groups.new(ngname, 'GeometryNodeTree')
        # self.remove_nodes(node_group)
        nodes = node_group.nodes
        links = node_group.links
        
        
        inp = node_group.inputs.new('NodeSocketGeometry','Geometry')
        inp = node_group.inputs.new('NodeSocketVector','Position')
        inp.default_value = (0.0,0.0,0.0,)
        inp = node_group.inputs.new('NodeSocketVector','Z-Rotation')
        inp.default_value = (0.0,0.0,0.0,)
        inp = node_group.inputs.new('NodeSocketBool','Use Ripples')
        inp.default_value = True
        inp = node_group.inputs.new('NodeSocketFloat','Distance')
        inp.default_value = 0.0
        inp = node_group.inputs.new('NodeSocketFloat','Wavelength')
        inp.default_value = 0.31
        inp = node_group.inputs.new('NodeSocketFloat','Amplitude')
        inp.default_value = 2.0
        inp = node_group.inputs.new('NodeSocketFloat','OuterFalloff')
        inp.default_value = 20.0
        inp = node_group.inputs.new('NodeSocketFloat','Innercut')
        inp.default_value = 25.0
        inp = node_group.inputs.new('NodeSocketFloat','Wave Speed')
        inp.default_value = 10.0
        inp = node_group.inputs.new('NodeSocketBool','Show Front Arrow')
        inp.default_value = False
        inp = node_group.inputs.new('NodeSocketFloat','Set Front Direction')
        inp.default_value = 0.16
        inp = node_group.inputs.new('NodeSocketFloat','Bow-Wave Offset')
        inp.default_value = 1.6
        inp = node_group.inputs.new('NodeSocketFloatFactor','Circular <--> Bow Wave')
        inp.default_value = 1.0
        inp = node_group.inputs.new('NodeSocketFloat','Turbulence')
        inp.default_value = 7.4

        node = nodes.new("NodeFrame" )
        node.name = "Frame"
        node.label = "V-Mask"
        node.location = (260, 1249)

        node = nodes.new("NodeFrame" )
        node.name = "Frame.002"
        node.label = "Make Arrow"
        node.location = (1846, 976)

        node = nodes.new("NodeFrame" )
        node.name = "Frame.003"
        node.label = "Time Move"
        node.location = (501, 650)

        node = nodes.new("NodeFrame" )
        node.name = "Frame.001"
        node.label = "ArrowZRotation"
        node.location = (4182, 1031)

        node = nodes.new("NodeGroupInput" )
        node.name = "Group Input"
        node.location = (-2108, 366)

        node = nodes.new("GeometryNodeInputPosition" )
        node.name = "Position"
        node.location = (-2071, 865)
        node.hide = False
        node.mute = False
        node.outputs[0].default_value = (0.0,0.0,0.0,)

        node = nodes.new("ShaderNodeSeparateXYZ" )
        node.name = "Separate XYZ.002"
        node.location = (-1773, 504)
        node.hide = False
        node.mute = False
        node.inputs[0].default_value = (0.0,0.0,-0.47999998927116394,)
        node.outputs[0].default_value = 0.0
        node.outputs[1].default_value = 0.0
        node.outputs[2].default_value = 0.0

        node = nodes.new("ShaderNodeVectorMath" )
        node.name = "Vector Math"
        node.location = (-1750, 759)
        node.operation = "SUBTRACT"
        node.hide = False
        node.mute = False
        node.inputs[0].default_value = (0.0,0.0,0.0,)
        node.inputs[1].default_value = (0.0,0.0,0.0,)
        node.inputs[2].default_value = (0.0,0.0,0.0,)
        node.inputs[3].default_value = 1.0
        node.outputs[0].default_value = (0.0,0.0,0.0,)
        node.outputs[1].default_value = 0.0

        node = nodes.new("ShaderNodeMath" )
        node.name = "Math.015"
        node.location = (-1556, 560)
        node.operation = "MULTIPLY"
        node.use_clamp = False
        node.hide = False
        node.mute = False
        node.inputs[0].default_value = 0.5
        node.inputs[1].default_value = -1.0
        node.inputs[2].default_value = 0.5
        node.outputs[0].default_value = 0.0

        node = nodes.new("ShaderNodeVectorRotate" )
        node.name = "Vector Rotate.001"
        node.rotation_type = "AXIS_ANGLE"
        node.location = (-1531, 891)
        node.hide = False
        node.mute = False
        node.inputs[0].default_value = (0.0,0.0,0.0,)
        node.inputs[1].default_value = (0.0,0.0,0.0,)
        node.inputs[2].default_value = (0.0,0.0,1.0,)
        node.inputs[3].default_value = 0.16
        node.inputs[4].default_value = (0.0,0.0,0.0,)
        node.outputs[0].default_value = (0.0,0.0,0.0,)

        node = nodes.new("ShaderNodeMath" )
        node.name = "Math.016"
        node.location = (-1337, 617)
        node.operation = "ADD"
        node.use_clamp = False
        node.hide = False
        node.mute = False
        node.inputs[0].default_value = 0.5
        node.inputs[1].default_value = -1.57
        node.inputs[2].default_value = 0.5
        node.outputs[0].default_value = 0.0

        node = nodes.new("NodeReroute" )
        node.name = "Reroute.003"
        node.location = (-1265, 383)

        node = nodes.new("ShaderNodeCombineXYZ" )
        node.name = "Combine XYZ.001"
        node.location = (-1237, 1024)
        node.hide = False
        node.mute = False
        node.inputs[0].default_value = 0.0
        node.inputs[1].default_value = 1.6
        node.inputs[2].default_value = 0.0
        node.outputs[0].default_value = (0.0,0.0,0.0,)

        node = nodes.new("ShaderNodeVectorRotate" )
        node.name = "Vector Rotate.004"
        node.rotation_type = "AXIS_ANGLE"
        node.location = (-1114, 875)
        node.hide = False
        node.mute = False
        node.inputs[0].default_value = (0.0,0.0,0.0,)
        node.inputs[1].default_value = (0.0,0.0,0.0,)
        node.inputs[2].default_value = (0.0,0.0,1.0,)
        node.inputs[3].default_value = -0.74
        node.inputs[4].default_value = (0.0,0.0,0.0,)
        node.outputs[0].default_value = (0.0,0.0,0.0,)

        node = nodes.new("ShaderNodeVectorMath" )
        node.name = "Vector Math.002"
        node.parent = node_group.nodes["Frame.002"]
        node.location = (-1090, 301)
        node.operation = "ADD"
        node.hide = False
        node.mute = False
        node.inputs[0].default_value = (0.0,0.0,0.0,)
        node.inputs[1].default_value = (0.0,-1.2999999523162842,6.299999713897705,)
        node.inputs[2].default_value = (0.0,0.0,0.0,)
        node.inputs[3].default_value = 1.0
        node.outputs[0].default_value = (0.0,0.0,0.0,)
        node.outputs[1].default_value = 0.0

        node = nodes.new("GeometryNodeInputPosition" )
        node.name = "Position.001"
        node.parent = node_group.nodes["Frame.001"]
        node.location = (-998, -186)
        node.hide = False
        node.mute = False
        node.outputs[0].default_value = (0.0,0.0,0.0,)

        node = nodes.new("GeometryNodeMeshCylinder" )
        node.name = "Cylinder"
        node.parent = node_group.nodes["Frame.002"]
        node.location = (-970, 811)
        node.hide = False
        node.mute = False
        node.inputs[0].default_value = 4
        node.inputs[1].default_value = 1
        node.inputs[2].default_value = 1
        node.inputs[3].default_value = 0.5
        node.inputs[4].default_value = 2.0
        node.outputs[1].default_value = False
        node.outputs[2].default_value = False
        node.outputs[3].default_value = False
        node.outputs[4].default_value = (0.0,0.0,0.0,)

        node = nodes.new("ShaderNodeVectorRotate" )
        node.name = "Vector Rotate"
        node.parent = node_group.nodes["Frame"]
        node.rotation_type = "AXIS_ANGLE"
        node.location = (-846, 83)
        node.hide = False
        node.mute = False
        node.inputs[0].default_value = (0.0,0.0,0.0,)
        node.inputs[1].default_value = (0.0,0.0,0.0,)
        node.inputs[2].default_value = (0.0,0.0,1.0,)
        node.inputs[3].default_value = -7.11
        node.inputs[4].default_value = (0.0,0.0,0.0,)
        node.outputs[0].default_value = (0.0,0.0,0.0,)

        node = nodes.new("ShaderNodeVectorMath" )
        node.name = "Vector Math.001"
        node.location = (-820, 991)
        node.operation = "ADD"
        node.hide = False
        node.mute = False
        node.inputs[0].default_value = (0.0,0.0,0.0,)
        node.inputs[1].default_value = (0.0,1.1299998760223389,0.0,)
        node.inputs[2].default_value = (0.0,0.0,0.0,)
        node.inputs[3].default_value = 1.0
        node.outputs[0].default_value = (0.0,0.0,0.0,)
        node.outputs[1].default_value = 0.0

        node = nodes.new("ShaderNodeSeparateXYZ" )
        node.name = "Separate XYZ.003"
        node.parent = node_group.nodes["Frame.001"]
        node.location = (-781, -406)
        node.hide = False
        node.mute = False
        node.inputs[0].default_value = (0.0,0.0,0.0,)
        node.outputs[0].default_value = 0.0
        node.outputs[1].default_value = 0.0
        node.outputs[2].default_value = 0.0

        node = nodes.new("ShaderNodeMath" )
        node.name = "Math.005"
        node.location = (-773, 116)
        node.operation = "SUBTRACT"
        node.use_clamp = False
        node.hide = False
        node.mute = False
        node.inputs[0].default_value = 0.5
        node.inputs[1].default_value = 0.5
        node.inputs[2].default_value = 0.5
        node.outputs[0].default_value = 0.0

        node = nodes.new("NodeReroute" )
        node.name = "Reroute.002"
        node.location = (-734, 328)

        node = nodes.new("ShaderNodeVectorRotate" )
        node.name = "Vector Rotate.002"
        node.parent = node_group.nodes["Frame.001"]
        node.rotation_type = "AXIS_ANGLE"
        node.location = (-720, -27)
        node.hide = False
        node.mute = False
        node.inputs[0].default_value = (0.0,0.0,0.0,)
        node.inputs[1].default_value = (0.0,0.0,0.0,)
        node.inputs[2].default_value = (0.0,0.0,1.0,)
        node.inputs[3].default_value = 0.0
        node.inputs[4].default_value = (0.0,0.0,0.0,)
        node.outputs[0].default_value = (0.0,0.0,0.0,)

        node = nodes.new("NodeReroute" )
        node.name = "Reroute.008"
        node.location = (-676, 0)

        node = nodes.new("GeometryNodeTransform" )
        node.name = "Transform Geometry"
        node.parent = node_group.nodes["Frame.002"]
        node.location = (-676, 516)
        node.hide = False
        node.mute = False
        node.inputs[1].default_value = (0.0,0.0,0.0,)
        node.inputs[2].default_value = (1.5707963705062866,0.0,0.0,)
        node.inputs[3].default_value = (1.0,1.0,1.0,)

        node = nodes.new("ShaderNodeMath" )
        node.name = "Math.002"
        node.location = (-663, 670)
        node.operation = "DIVIDE"
        node.use_clamp = False
        node.hide = False
        node.mute = False
        node.inputs[0].default_value = 5.84
        node.inputs[1].default_value = 0.5
        node.inputs[2].default_value = 0.5
        node.outputs[0].default_value = 0.0

        node = nodes.new("GeometryNodeInputIndex" )
        node.name = "Index"
        node.parent = node_group.nodes["Frame.002"]
        node.location = (-569, 151)
        node.hide = False
        node.mute = False
        node.outputs[0].default_value = 0

        node = nodes.new("ShaderNodeMath" )
        node.name = "Math.025"
        node.parent = node_group.nodes["Frame.001"]
        node.location = (-556, -327)
        node.operation = "MULTIPLY"
        node.use_clamp = False
        node.hide = False
        node.mute = False
        node.inputs[0].default_value = 0.0
        node.inputs[1].default_value = 1.0
        node.inputs[2].default_value = 0.5
        node.outputs[0].default_value = 0.0

        node = nodes.new("GeometryNodeSetPosition" )
        node.name = "Set Position.003"
        node.parent = node_group.nodes["Frame.001"]
        node.location = (-551, 72)
        node.hide = False
        node.mute = False
        node.inputs[1].default_value = True
        node.inputs[2].default_value = (0.0,0.0,0.0,)
        node.inputs[3].default_value = (0.0,0.0,0.0,)

        node = nodes.new("ShaderNodeValue" )
        node.name = "Time"
        node.location = (-541, 154)
        node.hide = False
        node.mute = False
        node.outputs[0].default_value = 0.0

        node = nodes.new("ShaderNodeSeparateXYZ" )
        node.name = "Separate XYZ.001"
        node.parent = node_group.nodes["Frame"]
        node.location = (-535, 22)
        node.hide = False
        node.mute = False
        node.inputs[0].default_value = (0.0,0.0,0.0,)
        node.outputs[0].default_value = 0.0
        node.outputs[1].default_value = 0.0
        node.outputs[2].default_value = 0.0

        node = nodes.new("ShaderNodeMath" )
        node.name = "Math.009"
        node.location = (-522, 425)
        node.operation = "DIVIDE"
        node.use_clamp = False
        node.hide = False
        node.mute = False
        node.inputs[0].default_value = 0.5
        node.inputs[1].default_value = 0.0
        node.inputs[2].default_value = 0.5
        node.outputs[0].default_value = 0.0

        node = nodes.new("ShaderNodeSeparateXYZ" )
        node.name = "Separate XYZ"
        node.location = (-519, 870)
        node.hide = False
        node.mute = False
        node.inputs[0].default_value = (0.0,0.0,0.0,)
        node.outputs[0].default_value = 0.0
        node.outputs[1].default_value = 0.0
        node.outputs[2].default_value = 0.0

        node = nodes.new("NodeReroute" )
        node.name = "Reroute.009"
        node.location = (-406, 38)

        node = nodes.new("ShaderNodeMath" )
        node.name = "Math.007"
        node.location = (-367, -19)
        node.operation = "SUBTRACT"
        node.use_clamp = False
        node.hide = False
        node.mute = False
        node.inputs[0].default_value = 20.0
        node.inputs[1].default_value = 0.5
        node.inputs[2].default_value = 0.5
        node.outputs[0].default_value = 0.0

        node = nodes.new("ShaderNodeMath" )
        node.name = "Math.006"
        node.location = (-367, -193)
        node.operation = "GREATER_THAN"
        node.use_clamp = False
        node.hide = False
        node.mute = False
        node.inputs[0].default_value = 0.0
        node.inputs[1].default_value = 0.0
        node.inputs[2].default_value = 0.5
        node.outputs[0].default_value = 0.0

        node = nodes.new("ShaderNodeMath" )
        node.name = "Math.011"
        node.location = (-348, 193)
        node.operation = "DIVIDE"
        node.use_clamp = False
        node.hide = False
        node.mute = False
        node.inputs[0].default_value = 0.5
        node.inputs[1].default_value = 0.0
        node.inputs[2].default_value = 0.5
        node.outputs[0].default_value = 0.0

        node = nodes.new("FunctionNodeCompare" )
        node.name = "Compare"
        node.parent = node_group.nodes["Frame.002"]
        node.location = (-338, 307)
        node.data_type = "FLOAT"
        node.operation = "LESS_THAN"
        node.hide = False
        node.mode = "ELEMENT"
        node.mute = False
        node.inputs[0].default_value = 0.0
        node.inputs[1].default_value = 1.0
        node.inputs[2].default_value = 0
        node.inputs[3].default_value = 0
        node.inputs[4].default_value = (0.0,0.0,0.0,)
        node.inputs[5].default_value = (0.0,0.0,0.0,)
        node.inputs[6].default_value = (0.0,0.0,0.0,0.0,)
        node.inputs[7].default_value = (0.0,0.0,0.0,0.0,)
        node.inputs[8].default_value = ""
        node.inputs[9].default_value = ""
        node.inputs[10].default_value = 0.9
        node.inputs[11].default_value = 0.09
        node.inputs[12].default_value = 0.0
        node.outputs[0].default_value = False

        node = nodes.new("ShaderNodeMath" )
        node.name = "Math.017"
        node.parent = node_group.nodes["Frame.001"]
        node.location = (-336, -322)
        node.operation = "ADD"
        node.use_clamp = False
        node.hide = False
        node.mute = False
        node.inputs[0].default_value = 0.5
        node.inputs[1].default_value = 1.57
        node.inputs[2].default_value = 0.5
        node.outputs[0].default_value = 0.0

        node = nodes.new("ShaderNodeMapRange" )
        node.name = "Map Range.002"
        node.parent = node_group.nodes["Frame"]
        node.location = (-334, 249)
        node.data_type = "FLOAT"
        node.interpolation_type = "LINEAR"
        node.clamp = True
        node.hide = False
        node.mute = False
        node.inputs[0].default_value = 1.0
        node.inputs[1].default_value = 0.0
        node.inputs[2].default_value = 4.12
        node.inputs[3].default_value = 0.0
        node.inputs[4].default_value = 1.0
        node.inputs[5].default_value = 4.0
        node.inputs[6].default_value = (0.0,0.0,0.0,)
        node.inputs[7].default_value = (0.0,0.0,0.0,)
        node.inputs[8].default_value = (1.0,1.0,1.0,)
        node.inputs[9].default_value = (0.0,0.0,0.0,)
        node.inputs[10].default_value = (1.0,1.0,1.0,)
        node.inputs[11].default_value = (4.0,4.0,4.0,)
        node.outputs[0].default_value = 0.0
        node.outputs[1].default_value = (0.0,0.0,0.0,)

        node = nodes.new("ShaderNodeMapRange" )
        node.name = "Map Range.003"
        node.parent = node_group.nodes["Frame"]
        node.location = (-333, -5)
        node.data_type = "FLOAT"
        node.interpolation_type = "LINEAR"
        node.clamp = True
        node.hide = False
        node.mute = False
        node.inputs[0].default_value = 1.0
        node.inputs[1].default_value = 0.0
        node.inputs[2].default_value = 4.0
        node.inputs[3].default_value = 0.0
        node.inputs[4].default_value = 1.0
        node.inputs[5].default_value = 4.0
        node.inputs[6].default_value = (0.0,0.0,0.0,)
        node.inputs[7].default_value = (0.0,0.0,0.0,)
        node.inputs[8].default_value = (1.0,1.0,1.0,)
        node.inputs[9].default_value = (0.0,0.0,0.0,)
        node.inputs[10].default_value = (1.0,1.0,1.0,)
        node.inputs[11].default_value = (4.0,4.0,4.0,)
        node.outputs[0].default_value = 0.0
        node.outputs[1].default_value = (0.0,0.0,0.0,)

        node = nodes.new("ShaderNodeMath" )
        node.name = "Math"
        node.location = (-232, 676)
        node.operation = "ADD"
        node.use_clamp = False
        node.hide = False
        node.mute = False
        node.inputs[0].default_value = 0.5
        node.inputs[1].default_value = 7.4
        node.inputs[2].default_value = 0.5
        node.outputs[0].default_value = 0.0

        node = nodes.new("NodeReroute" )
        node.name = "Reroute.006"
        node.location = (-171, 889)

        node = nodes.new("ShaderNodeMapRange" )
        node.name = "Map Range.001"
        node.location = (-171, 908)
        node.data_type = "FLOAT"
        node.interpolation_type = "LINEAR"
        node.clamp = True
        node.hide = False
        node.mute = False
        node.inputs[0].default_value = 1.0
        node.inputs[1].default_value = 0.0
        node.inputs[2].default_value = 12.13
        node.inputs[3].default_value = 0.0
        node.inputs[4].default_value = 1.0
        node.inputs[5].default_value = 4.0
        node.inputs[6].default_value = (0.0,0.0,0.0,)
        node.inputs[7].default_value = (0.0,0.0,0.0,)
        node.inputs[8].default_value = (1.0,1.0,1.0,)
        node.inputs[9].default_value = (0.0,0.0,0.0,)
        node.inputs[10].default_value = (1.0,1.0,1.0,)
        node.inputs[11].default_value = (4.0,4.0,4.0,)
        node.outputs[0].default_value = 0.0
        node.outputs[1].default_value = (0.0,0.0,0.0,)

        node = nodes.new("ShaderNodeMath" )
        node.name = "Math.003"
        node.parent = node_group.nodes["Frame"]
        node.location = (-146, 23)
        node.operation = "MULTIPLY"
        node.use_clamp = False
        node.hide = False
        node.mute = False
        node.inputs[0].default_value = 0.5
        node.inputs[1].default_value = 0.5
        node.inputs[2].default_value = 0.5
        node.outputs[0].default_value = 0.0

        node = nodes.new("ShaderNodeMixRGB" )
        node.name = "Mix"
        node.location = (-135, -19)
        node.blend_type = "MIX"
        node.use_clamp = False
        node.hide = False
        node.mute = False
        node.inputs[0].default_value = 0.5
        node.inputs[1].default_value = (0.5,0.5,0.5,1.0,)
        node.inputs[2].default_value = (0.0,0.0,0.0,1.0,)
        node.outputs[0].default_value = (0.0,0.0,0.0,0.0,)

        node = nodes.new("ShaderNodeMath" )
        node.name = "Math.008"
        node.location = (-135, 154)
        node.operation = "GREATER_THAN"
        node.use_clamp = False
        node.hide = False
        node.mute = False
        node.inputs[0].default_value = 0.5
        node.inputs[1].default_value = 0.0
        node.inputs[2].default_value = 0.5
        node.outputs[0].default_value = 0.0

        node = nodes.new("ShaderNodeMath" )
        node.name = "Math.010"
        node.location = (-132, 379)
        node.operation = "ADD"
        node.use_clamp = False
        node.hide = False
        node.mute = False
        node.inputs[0].default_value = 0.5
        node.inputs[1].default_value = 0.0
        node.inputs[2].default_value = 0.5
        node.outputs[0].default_value = 0.0

        node = nodes.new("ShaderNodeVectorRotate" )
        node.name = "Vector Rotate.003"
        node.parent = node_group.nodes["Frame.001"]
        node.rotation_type = "AXIS_ANGLE"
        node.location = (-116, -107)
        node.hide = False
        node.mute = False
        node.inputs[0].default_value = (0.0,0.0,0.0,)
        node.inputs[1].default_value = (0.0,0.0,0.0,)
        node.inputs[2].default_value = (0.0,0.0,1.0,)
        node.inputs[3].default_value = -0.49
        node.inputs[4].default_value = (0.0,0.0,0.0,)
        node.outputs[0].default_value = (0.0,0.0,0.0,)

        node = nodes.new("NodeReroute" )
        node.name = "Reroute.010"
        node.location = (-116, 444)

        node = nodes.new("GeometryNodeExtrudeMesh" )
        node.name = "Extrude Mesh"
        node.parent = node_group.nodes["Frame.002"]
        node.location = (-96, 525)
        node.hide = False
        node.mode = "FACES"
        node.mute = False
        node.inputs[1].default_value = True
        node.inputs[2].default_value = (0.0,0.0,0.0,)
        node.inputs[3].default_value = 1.0
        node.inputs[4].default_value = True
        node.outputs[1].default_value = False
        node.outputs[2].default_value = False

        node = nodes.new("ShaderNodeCombineXYZ" )
        node.name = "Combine XYZ.002"
        node.parent = node_group.nodes["Frame.002"]
        node.location = (-91, 275)
        node.hide = False
        node.mute = False
        node.inputs[0].default_value = 0.0
        node.inputs[1].default_value = -2.4
        node.inputs[2].default_value = 0.0
        node.outputs[0].default_value = (0.0,0.0,0.0,)

        node = nodes.new("ShaderNodeMath" )
        node.name = "Math.021"
        node.parent = node_group.nodes["Frame.003"]
        node.location = (-86, 69)
        node.operation = "MULTIPLY"
        node.use_clamp = False
        node.hide = True
        node.mute = False
        node.inputs[0].default_value = -1.0
        node.inputs[1].default_value = -1.0
        node.inputs[2].default_value = 0.5
        node.outputs[0].default_value = 0.0

        node = nodes.new("ShaderNodeMath" )
        node.name = "Math.020"
        node.parent = node_group.nodes["Frame.003"]
        node.location = (-82, 34)
        node.operation = "DIVIDE"
        node.use_clamp = False
        node.hide = False
        node.mute = False
        node.inputs[0].default_value = -1.0
        node.inputs[1].default_value = -1.0
        node.inputs[2].default_value = 0.5
        node.outputs[0].default_value = 0.0

        node = nodes.new("GeometryNodeInputNormal" )
        node.name = "Normal"
        node.parent = node_group.nodes["Frame.002"]
        node.location = (-60, 143)
        node.hide = False
        node.mute = False
        node.outputs[0].default_value = (0.0,0.0,0.0,)

        node = nodes.new("NodeReroute" )
        node.name = "Reroute.005"
        node.parent = node_group.nodes["Frame"]
        node.location = (64, -252)

        node = nodes.new("GeometryNodeSetPosition" )
        node.name = "Set Position.004"
        node.parent = node_group.nodes["Frame.001"]
        node.location = (95, 4)
        node.hide = False
        node.mute = False
        node.inputs[1].default_value = True
        node.inputs[2].default_value = (0.0,0.0,0.0,)
        node.inputs[3].default_value = (0.0,0.0,0.0,)

        node = nodes.new("ShaderNodeMixRGB" )
        node.name = "Mix.001"
        node.location = (116, 193)
        node.blend_type = "MIX"
        node.use_clamp = False
        node.hide = False
        node.mute = False
        node.inputs[0].default_value = 0.5
        node.inputs[1].default_value = (0.0,0.0,0.0,1.0,)
        node.inputs[2].default_value = (0.0,0.0,0.0,1.0,)
        node.outputs[0].default_value = (0.0,0.0,0.0,0.0,)

        node = nodes.new("ShaderNodeVectorMath" )
        node.name = "Vector Math.003"
        node.parent = node_group.nodes["Frame.002"]
        node.location = (141, 300)
        node.operation = "MULTIPLY"
        node.hide = False
        node.mute = False
        node.inputs[0].default_value = (0.0,0.0,0.0,)
        node.inputs[1].default_value = (0.46000003814697266,0.46000003814697266,0.46000003814697266,)
        node.inputs[2].default_value = (0.0,0.0,0.0,)
        node.inputs[3].default_value = 1.0
        node.outputs[0].default_value = (0.0,0.0,0.0,)
        node.outputs[1].default_value = 0.0

        node = nodes.new("GeometryNodeInputNormal" )
        node.name = "Normal.001"
        node.parent = node_group.nodes["Frame.002"]
        node.location = (146, -81)
        node.hide = False
        node.mute = False
        node.outputs[0].default_value = (0.0,0.0,0.0,)

        node = nodes.new("ShaderNodeMath" )
        node.name = "Math.001"
        node.location = (157, 870)
        node.operation = "MULTIPLY"
        node.use_clamp = False
        node.hide = False
        node.mute = False
        node.inputs[0].default_value = 0.5
        node.inputs[1].default_value = -0.5
        node.inputs[2].default_value = 0.5
        node.outputs[0].default_value = 0.0

        node = nodes.new("GeometryNodeExtrudeMesh" )
        node.name = "Extrude Mesh.001"
        node.parent = node_group.nodes["Frame.002"]
        node.location = (172, 676)
        node.hide = False
        node.mode = "FACES"
        node.mute = False
        node.inputs[1].default_value = True
        node.inputs[2].default_value = (0.0,0.0,0.0,)
        node.inputs[3].default_value = 1.0
        node.inputs[4].default_value = True
        node.outputs[1].default_value = False
        node.outputs[2].default_value = False

        node = nodes.new("NodeReroute" )
        node.name = "Reroute.007"
        node.parent = node_group.nodes["Frame.002"]
        node.location = (249, 392)

        node = nodes.new("ShaderNodeVectorMath" )
        node.name = "Vector Math.004"
        node.parent = node_group.nodes["Frame.002"]
        node.location = (330, 383)
        node.operation = "ADD"
        node.hide = False
        node.mute = False
        node.inputs[0].default_value = (0.0,0.0,0.0,)
        node.inputs[1].default_value = (0.0,1.2699999809265137,0.0,)
        node.inputs[2].default_value = (0.0,0.0,0.0,)
        node.inputs[3].default_value = 1.0
        node.outputs[0].default_value = (0.0,0.0,0.0,)
        node.outputs[1].default_value = 0.0

        node = nodes.new("ShaderNodeVectorMath" )
        node.name = "Vector Math.005"
        node.parent = node_group.nodes["Frame.002"]
        node.location = (348, 76)
        node.operation = "MULTIPLY"
        node.hide = False
        node.mute = False
        node.inputs[0].default_value = (0.0,0.0,0.0,)
        node.inputs[1].default_value = (-1.0,-1.0,-1.0,)
        node.inputs[2].default_value = (0.0,0.0,0.0,)
        node.inputs[3].default_value = 1.0
        node.outputs[0].default_value = (0.0,0.0,0.0,)
        node.outputs[1].default_value = 0.0

        node = nodes.new("ShaderNodeMapRange" )
        node.name = "Map Range"
        node.location = (464, -38)
        node.data_type = "FLOAT"
        node.interpolation_type = "LINEAR"
        node.clamp = False
        node.hide = False
        node.mute = False
        node.inputs[0].default_value = 1.0
        node.inputs[1].default_value = 0.0
        node.inputs[2].default_value = 1.0
        node.inputs[3].default_value = 0.0
        node.inputs[4].default_value = 0.01
        node.inputs[5].default_value = 4.0
        node.inputs[6].default_value = (0.0,0.0,0.0,)
        node.inputs[7].default_value = (0.0,0.0,0.0,)
        node.inputs[8].default_value = (1.0,1.0,1.0,)
        node.inputs[9].default_value = (0.0,0.0,0.0,)
        node.inputs[10].default_value = (1.0,1.0,1.0,)
        node.inputs[11].default_value = (4.0,4.0,4.0,)
        node.outputs[0].default_value = 0.0
        node.outputs[1].default_value = (0.0,0.0,0.0,)

        node = nodes.new("ShaderNodeVectorMath" )
        node.name = "Vector Math.006"
        node.parent = node_group.nodes["Frame.002"]
        node.location = (538, 158)
        node.operation = "ADD"
        node.hide = False
        node.mute = True
        node.inputs[0].default_value = (0.0,0.0,0.0,)
        node.inputs[1].default_value = (0.0,2.3999998569488525,0.0,)
        node.inputs[2].default_value = (0.0,0.0,0.0,)
        node.inputs[3].default_value = 1.0
        node.outputs[0].default_value = (0.0,0.0,0.0,)
        node.outputs[1].default_value = 0.0

        node = nodes.new("GeometryNodeSetPosition" )
        node.name = "Set Position.001"
        node.parent = node_group.nodes["Frame.002"]
        node.location = (589, 626)
        node.hide = False
        node.mute = False
        node.inputs[1].default_value = True
        node.inputs[2].default_value = (0.0,0.0,0.0,)
        node.inputs[3].default_value = (0.0,1.4900000095367432,0.0,)

        node = nodes.new("ShaderNodeMath" )
        node.name = "Math.004"
        node.location = (634, 929)
        node.operation = "MULTIPLY"
        node.use_clamp = False
        node.hide = False
        node.mute = False
        node.inputs[0].default_value = 0.5
        node.inputs[1].default_value = -0.5
        node.inputs[2].default_value = 0.5
        node.outputs[0].default_value = 0.0

        node = nodes.new("GeometryNodeSetPosition" )
        node.name = "Set Position.002"
        node.parent = node_group.nodes["Frame.002"]
        node.location = (795, 273)
        node.hide = False
        node.mute = False
        node.inputs[1].default_value = True
        node.inputs[2].default_value = (0.0,0.0,0.0,)
        node.inputs[3].default_value = (0.0,0.0,0.0,)

        node = nodes.new("GeometryNodeDeleteGeometry" )
        node.name = "Delete Geometry"
        node.parent = node_group.nodes["Frame.002"]
        node.location = (943, 278)
        node.hide = False
        node.mode = "ONLY_FACE"
        node.mute = False
        node.inputs[1].default_value = True

        node = nodes.new("ShaderNodeMath" )
        node.name = "Math.019"
        node.location = (950, 715)
        node.operation = "ADD"
        node.use_clamp = False
        node.hide = False
        node.mute = False
        node.inputs[0].default_value = 0.5
        node.inputs[1].default_value = 0.0
        node.inputs[2].default_value = 0.5
        node.outputs[0].default_value = 0.0

        node = nodes.new("NodeReroute" )
        node.name = "Reroute"
        node.location = (1044, 425)

        node = nodes.new("ShaderNodeMix" )
        node.name = "Mix.002"
        node.location = (1162, 444)
        node.data_type = "FLOAT"
        node.blend_type = "MIX"
        node.hide = False
        node.mute = False
        node.inputs[0].default_value = 1.0
        node.inputs[1].default_value = (0.5,0.5,0.5,)
        node.inputs[2].default_value = 0.0
        node.inputs[3].default_value = 0.0
        node.inputs[4].default_value = (0.0,0.0,0.0,)
        node.inputs[5].default_value = (0.0,0.0,0.0,)
        node.inputs[6].default_value = (0.5,0.5,0.5,1.0,)
        node.inputs[7].default_value = (0.5,0.5,0.5,1.0,)
        node.outputs[0].default_value = 0.0
        node.outputs[1].default_value = (0.0,0.0,0.0,)
        node.outputs[2].default_value = (0.0,0.0,0.0,0.0,)

        node = nodes.new("NodeReroute" )
        node.name = "Reroute.001"
        node.location = (1218, 425)

        node = nodes.new("NodeReroute" )
        node.name = "Reroute.004"
        node.location = (1218, 522)

        node = nodes.new("ShaderNodeMath" )
        node.name = "Math.012"
        node.location = (1414, 328)
        node.operation = "SINE"
        node.use_clamp = False
        node.hide = False
        node.mute = False
        node.inputs[0].default_value = 0.5
        node.inputs[1].default_value = 0.0
        node.inputs[2].default_value = 0.5
        node.outputs[0].default_value = 0.0

        node = nodes.new("ShaderNodeMath" )
        node.name = "Math.013"
        node.location = (1607, 328)
        node.operation = "MULTIPLY"
        node.use_clamp = False
        node.hide = False
        node.mute = False
        node.inputs[0].default_value = 0.5
        node.inputs[1].default_value = 0.0
        node.inputs[2].default_value = 0.5
        node.outputs[0].default_value = 0.0

        node = nodes.new("ShaderNodeMath" )
        node.name = "Math.014"
        node.location = (1858, 328)
        node.operation = "MULTIPLY"
        node.use_clamp = False
        node.hide = False
        node.mute = False
        node.inputs[0].default_value = 0.5
        node.inputs[1].default_value = 0.0
        node.inputs[2].default_value = 0.5
        node.outputs[0].default_value = 0.0

        node = nodes.new("ShaderNodeCombineXYZ" )
        node.name = "Combine XYZ"
        node.location = (2129, 328)
        node.hide = False
        node.mute = False
        node.inputs[0].default_value = 0.0
        node.inputs[1].default_value = 0.0
        node.inputs[2].default_value = 0.0
        node.outputs[0].default_value = (0.0,0.0,0.0,)

        node = nodes.new("GeometryNodeSetPosition" )
        node.name = "Set Position"
        node.location = (2322, 406)
        node.hide = False
        node.mute = False
        node.inputs[1].default_value = True
        node.inputs[2].default_value = (0.0,0.0,0.0,)
        node.inputs[3].default_value = (0.0,0.0,0.0,)

        node = nodes.new("NodeGroupInput" )
        node.name = "Group Input.001"
        node.location = (2405, 845)

        node = nodes.new("GeometryNodeSwitch" )
        node.name = "Switch"
        node.location = (2819, 452)
        node.input_type = "GEOMETRY"
        node.hide = False
        node.mute = False
        node.inputs[0].default_value = False
        node.inputs[1].default_value = True
        node.inputs[2].default_value = 0.0
        node.inputs[3].default_value = 0.0
        node.inputs[4].default_value = 0
        node.inputs[5].default_value = 0
        node.inputs[6].default_value = False
        node.inputs[7].default_value = True
        node.inputs[8].default_value = (0.0,0.0,0.0,)
        node.inputs[9].default_value = (0.0,0.0,0.0,)
        node.inputs[10].default_value = (0.800000011920929,0.800000011920929,0.800000011920929,1.0,)
        node.inputs[11].default_value = (0.800000011920929,0.800000011920929,0.800000011920929,1.0,)
        node.inputs[12].default_value = ""
        node.inputs[13].default_value = ""
        node.outputs[0].default_value = 0.0
        node.outputs[1].default_value = 0
        node.outputs[2].default_value = False
        node.outputs[3].default_value = (0.0,0.0,0.0,)
        node.outputs[4].default_value = (0.0,0.0,0.0,0.0,)
        node.outputs[5].default_value = ""
        node.outputs[7].default_value = None
        node.outputs[8].default_value = None
        node.outputs[9].default_value = None
        node.outputs[10].default_value = None
        node.outputs[11].default_value = None

        node = nodes.new("ShaderNodeMath" )
        node.name = "Math.018"
        node.location = (2858, 615)
        node.operation = "MULTIPLY"
        node.use_clamp = False
        node.hide = False
        node.mute = False
        node.inputs[0].default_value = 0.5
        node.inputs[1].default_value = -1.0
        node.inputs[2].default_value = 0.5
        node.outputs[0].default_value = 0.0

        node = nodes.new("NodeReroute" )
        node.name = "Reroute.011"
        node.location = (3352, 744)

        node = nodes.new("NodeGroupInput" )
        node.name = "Group Input.002"
        node.location = (4498, 1348)

        node = nodes.new("GeometryNodeSwitch" )
        node.name = "Switch.001"
        node.location = (4697, 902)
        node.input_type = "GEOMETRY"
        node.hide = False
        node.mute = False
        node.inputs[0].default_value = False
        node.inputs[1].default_value = False
        node.inputs[2].default_value = 0.0
        node.inputs[3].default_value = 0.0
        node.inputs[4].default_value = 0
        node.inputs[5].default_value = 0
        node.inputs[6].default_value = False
        node.inputs[7].default_value = True
        node.inputs[8].default_value = (0.0,0.0,0.0,)
        node.inputs[9].default_value = (0.0,0.0,0.0,)
        node.inputs[10].default_value = (0.800000011920929,0.800000011920929,0.800000011920929,1.0,)
        node.inputs[11].default_value = (0.800000011920929,0.800000011920929,0.800000011920929,1.0,)
        node.inputs[12].default_value = ""
        node.inputs[13].default_value = ""
        node.outputs[0].default_value = 0.0
        node.outputs[1].default_value = 0
        node.outputs[2].default_value = False
        node.outputs[3].default_value = (0.0,0.0,0.0,)
        node.outputs[4].default_value = (0.0,0.0,0.0,0.0,)
        node.outputs[5].default_value = ""
        node.outputs[7].default_value = None
        node.outputs[8].default_value = None
        node.outputs[9].default_value = None
        node.outputs[10].default_value = None
        node.outputs[11].default_value = None

        node = nodes.new("GeometryNodeJoinGeometry" )
        node.name = "Join Geometry"
        node.location = (4887, 599)
        node.hide = False
        node.mute = False

        node = nodes.new("NodeGroupOutput" )
        node.name = "Group Output"
        node.location = (5196, 599)
        node_group.outputs.new(type= 'NodeSocketGeometry', name='Geometry')
        links.new( nodes['Group Input'].outputs[0],  nodes['Reroute'].inputs[0])
        links.new( nodes['Group Input'].outputs[1],  nodes['Vector Math'].inputs[1])
        links.new( nodes['Group Input'].outputs[1],  nodes['Vector Math.002'].inputs[0])
        links.new( nodes['Group Input'].outputs[2],  nodes['Separate XYZ.002'].inputs[0])
        links.new( nodes['Group Input'].outputs[3],  nodes['Reroute.003'].inputs[0])
        links.new( nodes['Group Input'].outputs[4],  nodes['Reroute.002'].inputs[0])
        links.new( nodes['Group Input'].outputs[4],  nodes['Math.002'].inputs[1])
        links.new( nodes['Group Input'].outputs[5],  nodes['Math.009'].inputs[1])
        links.new( nodes['Group Input'].outputs[6],  nodes['Map Range'].inputs[0])
        links.new( nodes['Group Input'].outputs[7],  nodes['Math.005'].inputs[0])
        links.new( nodes['Group Input'].outputs[8],  nodes['Math.008'].inputs[0])
        links.new( nodes['Group Input'].outputs[9],  nodes['Reroute.008'].inputs[0])
        links.new( nodes['Group Input'].outputs[11],  nodes['Vector Rotate.001'].inputs[3])
        links.new( nodes['Group Input'].outputs[12],  nodes['Combine XYZ.001'].inputs[1])
        links.new( nodes['Group Input'].outputs[13],  nodes['Mix.002'].inputs[0])
        links.new( nodes['Group Input'].outputs[14],  nodes['Math'].inputs[1])
        links.new( nodes['Group Input.001'].outputs[1],  nodes['Reroute.011'].inputs[0])
        links.new( nodes['Group Input.001'].outputs[2],  nodes['Separate XYZ.003'].inputs[0])
        links.new( nodes['Group Input.001'].outputs[11],  nodes['Math.018'].inputs[0])
        links.new( nodes['Group Input.002'].outputs[10],  nodes['Switch.001'].inputs[1])
        links.new( nodes['Reroute'].outputs[0],  nodes['Set Position'].inputs[0])
        links.new( nodes['Reroute.009'].outputs[0],  nodes['Math.011'].inputs[1])
        links.new( nodes['Reroute.002'].outputs[0],  nodes['Math.005'].inputs[1])
        links.new( nodes['Math.006'].outputs[0],  nodes['Mix'].inputs[0])
        links.new( nodes['Math.005'].outputs[0],  nodes['Mix'].inputs[1])
        links.new( nodes['Reroute.002'].outputs[0],  nodes['Math.007'].inputs[1])
        links.new( nodes['Mix'].outputs[0],  nodes['Mix.001'].inputs[2])
        links.new( nodes['Math.008'].outputs[0],  nodes['Mix.001'].inputs[0])
        links.new( nodes['Reroute.002'].outputs[0],  nodes['Math.009'].inputs[0])
        links.new( nodes['Time'].outputs[0],  nodes['Math.011'].inputs[0])
        links.new( nodes['Math.011'].outputs[0],  nodes['Math.010'].inputs[1])
        links.new( nodes['Mix.001'].outputs[0],  nodes['Math.013'].inputs[1])
        links.new( nodes['Map Range'].outputs[0],  nodes['Math.014'].inputs[1])
        links.new( nodes['Join Geometry'].outputs[0],  nodes['Group Output'].inputs[0])
        links.new( nodes['Combine XYZ'].outputs[0],  nodes['Set Position'].inputs[3])
        links.new( nodes['Math.007'].outputs[0],  nodes['Math.008'].inputs[1])
        links.new( nodes['Math.005'].outputs[0],  nodes['Math.006'].inputs[1])
        links.new( nodes['Set Position'].outputs[0],  nodes['Switch'].inputs[15])
        links.new( nodes['Reroute.001'].outputs[0],  nodes['Switch'].inputs[14])
        links.new( nodes['Reroute'].outputs[0],  nodes['Reroute.001'].inputs[0])
        links.new( nodes['Reroute.004'].outputs[0],  nodes['Switch'].inputs[1])
        links.new( nodes['Reroute.003'].outputs[0],  nodes['Reroute.004'].inputs[0])
        links.new( nodes['Math.013'].outputs[0],  nodes['Math.014'].inputs[0])
        links.new( nodes['Vector Math.001'].outputs[0],  nodes['Separate XYZ'].inputs[0])
        links.new( nodes['Map Range.001'].outputs[0],  nodes['Math.001'].inputs[1])
        links.new( nodes['Separate XYZ'].outputs[1],  nodes['Map Range.001'].inputs[0])
        links.new( nodes['Math.014'].outputs[0],  nodes['Combine XYZ'].inputs[2])
        links.new( nodes['Position'].outputs[0],  nodes['Vector Math'].inputs[0])
        links.new( nodes['Vector Rotate.004'].outputs[0],  nodes['Vector Math.001'].inputs[0])
        links.new( nodes['Math.002'].outputs[0],  nodes['Map Range.001'].inputs[4])
        links.new( nodes['Combine XYZ.001'].outputs[0],  nodes['Vector Math.001'].inputs[1])
        links.new( nodes['Map Range.003'].outputs[0],  nodes['Math.003'].inputs[1])
        links.new( nodes['Map Range.002'].outputs[0],  nodes['Math.003'].inputs[0])
        links.new( nodes['Vector Rotate'].outputs[0],  nodes['Separate XYZ.001'].inputs[0])
        links.new( nodes['Separate XYZ.001'].outputs[0],  nodes['Map Range.002'].inputs[0])
        links.new( nodes['Separate XYZ.001'].outputs[1],  nodes['Map Range.003'].inputs[0])
        links.new( nodes['Vector Math.001'].outputs[0],  nodes['Vector Rotate'].inputs[0])
        links.new( nodes['Math.001'].outputs[0],  nodes['Math.004'].inputs[0])
        links.new( nodes['Reroute.005'].outputs[0],  nodes['Math.004'].inputs[1])
        links.new( nodes['Math.003'].outputs[0],  nodes['Reroute.005'].inputs[0])
        links.new( nodes['Separate XYZ'].outputs[0],  nodes['Reroute.006'].inputs[0])
        links.new( nodes['Vector Math'].outputs[0],  nodes['Vector Rotate.001'].inputs[0])
        links.new( nodes['Switch'].outputs[6],  nodes['Join Geometry'].inputs[0])
        links.new( nodes['Switch.001'].outputs[6],  nodes['Join Geometry'].inputs[0])
        links.new( nodes['Vector Math.002'].outputs[0],  nodes['Transform Geometry'].inputs[1])
        links.new( nodes['Cylinder'].outputs[0],  nodes['Transform Geometry'].inputs[0])
        links.new( nodes['Transform Geometry'].outputs[0],  nodes['Extrude Mesh'].inputs[0])
        links.new( nodes['Index'].outputs[0],  nodes['Compare'].inputs[0])
        links.new( nodes['Compare'].outputs[0],  nodes['Extrude Mesh'].inputs[1])
        links.new( nodes['Extrude Mesh.001'].outputs[0],  nodes['Set Position.001'].inputs[0])
        links.new( nodes['Reroute.007'].outputs[0],  nodes['Set Position.001'].inputs[1])
        links.new( nodes['Normal'].outputs[0],  nodes['Vector Math.003'].inputs[0])
        links.new( nodes['Vector Math.004'].outputs[0],  nodes['Set Position.001'].inputs[3])
        links.new( nodes['Vector Math.003'].outputs[0],  nodes['Vector Math.004'].inputs[0])
        links.new( nodes['Extrude Mesh'].outputs[0],  nodes['Extrude Mesh.001'].inputs[0])
        links.new( nodes['Extrude Mesh'].outputs[1],  nodes['Extrude Mesh.001'].inputs[1])
        links.new( nodes['Extrude Mesh'].outputs[1],  nodes['Reroute.007'].inputs[0])
        links.new( nodes['Combine XYZ.002'].outputs[0],  nodes['Extrude Mesh.001'].inputs[2])
        links.new( nodes['Set Position.001'].outputs[0],  nodes['Set Position.002'].inputs[0])
        links.new( nodes['Extrude Mesh.001'].outputs[1],  nodes['Set Position.002'].inputs[1])
        links.new( nodes['Normal.001'].outputs[0],  nodes['Vector Math.005'].inputs[0])
        links.new( nodes['Vector Math.005'].outputs[0],  nodes['Vector Math.006'].inputs[0])
        links.new( nodes['Vector Math.006'].outputs[0],  nodes['Set Position.002'].inputs[3])
        links.new( nodes['Set Position.002'].outputs[0],  nodes['Delete Geometry'].inputs[0])
        links.new( nodes['Delete Geometry'].outputs[0],  nodes['Set Position.003'].inputs[0])
        links.new( nodes['Vector Rotate.002'].outputs[0],  nodes['Set Position.003'].inputs[2])
        links.new( nodes['Position.001'].outputs[0],  nodes['Vector Rotate.002'].inputs[0])
        links.new( nodes['Reroute.011'].outputs[0],  nodes['Vector Rotate.002'].inputs[1])
        links.new( nodes['Math.012'].outputs[0],  nodes['Math.013'].inputs[0])
        links.new( nodes['Math.019'].outputs[0],  nodes['Mix.002'].inputs[3])
        links.new( nodes['Math'].outputs[0],  nodes['Math.001'].inputs[0])
        links.new( nodes['Mix.002'].outputs[0],  nodes['Math.012'].inputs[0])
        links.new( nodes['Math.009'].outputs[0],  nodes['Math.010'].inputs[0])
        links.new( nodes['Math.010'].outputs[0],  nodes['Mix.002'].inputs[2])
        links.new( nodes['Math.004'].outputs[0],  nodes['Math.019'].inputs[0])
        links.new( nodes['Math.021'].outputs[0],  nodes['Math.020'].inputs[0])
        links.new( nodes['Reroute.008'].outputs[0],  nodes['Reroute.009'].inputs[0])
        links.new( nodes['Reroute.009'].outputs[0],  nodes['Math.020'].inputs[1])
        links.new( nodes['Time'].outputs[0],  nodes['Reroute.010'].inputs[0])
        links.new( nodes['Reroute.010'].outputs[0],  nodes['Math.021'].inputs[0])
        links.new( nodes['Math.020'].outputs[0],  nodes['Math.019'].inputs[1])
        links.new( nodes['Math.009'].outputs[0],  nodes['Math'].inputs[0])
        links.new( nodes['Set Position.003'].outputs[0],  nodes['Set Position.004'].inputs[0])
        links.new( nodes['Position.001'].outputs[0],  nodes['Vector Rotate.003'].inputs[0])
        links.new( nodes['Reroute.011'].outputs[0],  nodes['Vector Rotate.003'].inputs[1])
        links.new( nodes['Vector Rotate.003'].outputs[0],  nodes['Set Position.004'].inputs[2])
        links.new( nodes['Math.018'].outputs[0],  nodes['Vector Rotate.002'].inputs[3])
        links.new( nodes['Math.017'].outputs[0],  nodes['Vector Rotate.003'].inputs[3])
        links.new( nodes['Vector Rotate.001'].outputs[0],  nodes['Vector Rotate.004'].inputs[0])
        links.new( nodes['Math.016'].outputs[0],  nodes['Vector Rotate.004'].inputs[3])
        links.new( nodes['Separate XYZ.002'].outputs[2],  nodes['Math.015'].inputs[0])
        links.new( nodes['Math.015'].outputs[0],  nodes['Math.016'].inputs[0])
        links.new( nodes['Separate XYZ.003'].outputs[2],  nodes['Math.025'].inputs[0])
        links.new( nodes['Math.025'].outputs[0],  nodes['Math.017'].inputs[0])
        links.new( nodes['Set Position.004'].outputs[0],  nodes['Switch.001'].inputs[15])
        
        
        source = nodes['Time'].outputs[0]
        target = bpy.context.scene
        prop = 'default_value'
        data_path = "frame_current"
        id_type = 'SCENE'
        driver = self.add_driver(source, target, prop,
                                 data_path, -1, func="-", id_type=id_type)
        
    def make_AOMFloat_Instancing_nodegroup(self):
        # does it exist
        ngname = 'AOMFloat_Instancing'
        if ngname in bpy.data.node_groups:
            return bpy.data.node_groups[ngname]

        node_group = bpy.data.node_groups.new(ngname, 'GeometryNodeTree')
        # self.remove_nodes(node_group)
        nodes = node_group.nodes
        links = node_group.links
        
        inp = node_group.inputs.new('NodeSocketGeometry','Geometry')
        inp = node_group.inputs.new('NodeSocketVectorEuler','XY-Rotation')
        inp.default_value = (0.0,0.0,0.0,)
        inp = node_group.inputs.new('NodeSocketVector','Z-Rotation')
        inp.default_value = (0.0,0.0,0.0,)
        inp = node_group.inputs.new('NodeSocketVectorTranslation','Position')
        inp.default_value = (0.0,0.0,0.0,)
        inp = node_group.inputs.new('NodeSocketVector','Scale')
        inp.default_value = (0.0,0.0,0.0,)
        inp = node_group.inputs.new('NodeSocketObject','Visible Object')
        inp = node_group.inputs.new('NodeSocketCollection','Visible Collection')
        inp = node_group.inputs.new('NodeSocketBool','Use Collection')
        inp.default_value = False

        node = nodes.new("NodeFrame" )
        node.name = "ShipInstancing"
        node.label = "ShipInstancing"
        node.location = (1664, 2222)

        node = nodes.new("NodeReroute" )
        node.name = "Reroute.019"
        node.parent = node_group.nodes["ShipInstancing"]
        node.location = (-2327, -2522)

        node = nodes.new("NodeReroute" )
        node.name = "Reroute.018"
        node.parent = node_group.nodes["ShipInstancing"]
        node.location = (-2325, -2363)

        node = nodes.new("NodeReroute" )
        node.name = "Reroute.017"
        node.parent = node_group.nodes["ShipInstancing"]
        node.location = (-2324, -2302)

        node = nodes.new("NodeReroute" )
        node.name = "Reroute.016"
        node.parent = node_group.nodes["ShipInstancing"]
        node.location = (-2317, -2229)

        node = nodes.new("GeometryNodeObjectInfo" )
        node.name = "FloatObj"
        node.parent = node_group.nodes["ShipInstancing"]
        node.location = (-2219, -2367)
        node.transform_space = "ORIGINAL"
        node.hide = False
        node.inputs[1].default_value = False
        node.outputs[0].default_value = (0.0,0.0,0.0,)
        node.outputs[1].default_value = (0.0,0.0,0.0,)
        node.outputs[2].default_value = (0.0,0.0,0.0,)

        node = nodes.new("GeometryNodeMeshLine" )
        node.name = "InstancePoint"
        node.parent = node_group.nodes["ShipInstancing"]
        node.location = (-2213, -1919)
        node.hide = False
        node.inputs[0].default_value = 1
        node.inputs[1].default_value = 1.0
        node.inputs[2].default_value = (0.0,0.0,0.0,)
        node.inputs[3].default_value = (0.0,0.0,0.0,)

        node = nodes.new("GeometryNodeCollectionInfo" )
        node.name = "Collection Info"
        node.parent = node_group.nodes["ShipInstancing"]
        node.location = (-2206, -2212)
        node.transform_space = "ORIGINAL"
        node.hide = False
        node.inputs[1].default_value = False
        node.inputs[2].default_value = False

        node = nodes.new("GeometryNodeSwitch" )
        node.name = "Switch"
        node.parent = node_group.nodes["ShipInstancing"]
        node.location = (-1959, -2256)
        node.input_type = "GEOMETRY"
        node.hide = False
        node.inputs[0].default_value = False
        node.inputs[1].default_value = False
        node.inputs[2].default_value = 0.0
        node.inputs[3].default_value = 0.0
        node.inputs[4].default_value = 0
        node.inputs[5].default_value = 0
        node.inputs[6].default_value = False
        node.inputs[7].default_value = True
        node.inputs[8].default_value = (0.0,0.0,0.0,)
        node.inputs[9].default_value = (0.0,0.0,0.0,)
        node.inputs[10].default_value = (0.800000011920929,0.800000011920929,0.800000011920929,1.0,)
        node.inputs[11].default_value = (0.800000011920929,0.800000011920929,0.800000011920929,1.0,)
        node.inputs[12].default_value = ""
        node.inputs[13].default_value = ""
        node.outputs[0].default_value = 0.0
        node.outputs[1].default_value = 0
        node.outputs[2].default_value = False
        node.outputs[3].default_value = (0.0,0.0,0.0,)
        node.outputs[4].default_value = (0.0,0.0,0.0,0.0,)
        node.outputs[5].default_value = ""
        node.outputs[7].default_value = None
        node.outputs[8].default_value = None
        node.outputs[9].default_value = None
        node.outputs[10].default_value = None
        node.outputs[11].default_value = None

        node = nodes.new("GeometryNodeInstanceOnPoints" )
        node.name = "InstanceOnPoint"
        node.parent = node_group.nodes["ShipInstancing"]
        node.location = (-1714, -2043)
        node.hide = False
        node.inputs[1].default_value = True
        node.inputs[3].default_value = False
        node.inputs[4].default_value = 0
        node.inputs[5].default_value = (0.0,0.0,0.0,)
        node.inputs[6].default_value = (1.0,1.0,1.0,)

        node = nodes.new("NodeReroute" )
        node.name = "Reroute.007"
        node.parent = node_group.nodes["ShipInstancing"]
        node.location = (-1701, -2566)

        node = nodes.new("GeometryNodeTransform" )
        node.name = "Transform Geometry"
        node.parent = node_group.nodes["ShipInstancing"]
        node.location = (-1383, -2105)
        node.hide = False
        node.inputs[1].default_value = (0.0,0.0,0.0,)
        node.inputs[2].default_value = (0.0,0.0,0.0,)
        node.inputs[3].default_value = (1.0,1.0,1.0,)

        node = nodes.new("NodeGroupInput" )
        node.name = "Group Input"
        node.location = (-997, -38)

        node = nodes.new("GeometryNodeTransform" )
        node.name = "SetHeightRot"
        node.parent = node_group.nodes["ShipInstancing"]
        node.location = (-948, -2228)
        node.hide = False
        node.inputs[1].default_value = (0.0,0.0,0.0,)
        node.inputs[2].default_value = (0.0,0.0,0.0,)
        node.inputs[3].default_value = (1.0,1.0,1.0,)

        node = nodes.new("NodeReroute" )
        node.name = "Reroute.001"
        node.location = (-711, 402)

        node = nodes.new("NodeReroute" )
        node.name = "Reroute"
        node.location = (950, 429)

        node = nodes.new("GeometryNodeJoinGeometry" )
        node.name = "Join Geometry"
        node.location = (1176, -12)
        node.hide = False

        node = nodes.new("NodeGroupOutput" )
        node.name = "Group Output"
        node.location = (1395, -24)
        node_group.outputs.new(type= 'NodeSocketGeometry', name='Geometry')
        links.new( nodes['Group Input'].outputs[0],  nodes['Reroute.001'].inputs[0])
        links.new( nodes['Group Input'].outputs[1],  nodes['InstanceOnPoint'].inputs[5])
        links.new( nodes['Group Input'].outputs[2],  nodes['Reroute.007'].inputs[0])
        links.new( nodes['Group Input'].outputs[3],  nodes['SetHeightRot'].inputs[1])
        links.new( nodes['Group Input'].outputs[4],  nodes['Reroute.016'].inputs[0])
        links.new( nodes['Group Input'].outputs[5],  nodes['Reroute.019'].inputs[0])
        links.new( nodes['Group Input'].outputs[6],  nodes['Reroute.017'].inputs[0])
        links.new( nodes['Group Input'].outputs[7],  nodes['Reroute.018'].inputs[0])
        links.new( nodes['Reroute.017'].outputs[0],  nodes['Collection Info'].inputs[0])
        links.new( nodes['Reroute.019'].outputs[0],  nodes['FloatObj'].inputs[0])
        links.new( nodes['Switch'].outputs[6],  nodes['InstanceOnPoint'].inputs[2])
        links.new( nodes['Reroute.016'].outputs[0],  nodes['InstanceOnPoint'].inputs[6])
        links.new( nodes['Reroute.007'].outputs[0],  nodes['Transform Geometry'].inputs[2])
        links.new( nodes['Transform Geometry'].outputs[0],  nodes['SetHeightRot'].inputs[0])
        links.new( nodes['InstanceOnPoint'].outputs[0],  nodes['Transform Geometry'].inputs[0])
        links.new( nodes['Reroute.018'].outputs[0],  nodes['Switch'].inputs[1])
        links.new( nodes['InstancePoint'].outputs[0],  nodes['InstanceOnPoint'].inputs[0])
        links.new( nodes['Collection Info'].outputs[0],  nodes['Switch'].inputs[15])
        links.new( nodes['FloatObj'].outputs[3],  nodes['Switch'].inputs[14])
        links.new( nodes['Join Geometry'].outputs[0],  nodes['Group Output'].inputs[0])
        links.new( nodes['SetHeightRot'].outputs[0],  nodes['Join Geometry'].inputs[0])
        links.new( nodes['Reroute'].outputs[0],  nodes['Join Geometry'].inputs[0])
        links.new( nodes['Reroute.001'].outputs[0],  nodes['Reroute'].inputs[0])

    def make_AOMGeoFloat_nodegroup(self, mod):
        # does it exist
        ngname = 'AOMGeoFloat'
        if ngname in bpy.data.node_groups:
            return bpy.data.node_groups[ngname]

        node_group = bpy.data.node_groups.new(ngname, 'GeometryNodeTree')
        # self.remove_nodes(node_group)
        nodes = node_group.nodes
        links = node_group.links
        
               
        
        inp = node_group.inputs.new('NodeSocketGeometry','Geometry')
        inp = node_group.inputs.new('NodeSocketObject','Visible Object')
        inp = node_group.inputs.new('NodeSocketBool','Use Collection')
        inp.default_value = False
        inp = node_group.inputs.new('NodeSocketCollection','Visible Collection')
        inp = node_group.inputs.new('NodeSocketObject','Floatcage')
        inp = node_group.inputs.new('NodeSocketObject','Collision Object')
        inp = node_group.inputs.new('NodeSocketBool','Show CollisionObject')
        inp.default_value = False
        inp = node_group.inputs.new('NodeSocketBool','Show Detection Marks')
        inp.default_value = True
        inp = node_group.inputs.new('NodeSocketFloat','XDetectionDistance')
        inp.default_value = 2.0
        inp = node_group.inputs.new('NodeSocketFloat','YDetectionDistance')
        inp.default_value = 2.0
        inp = node_group.inputs.new('NodeSocketFloat','DetectionHeight')
        inp.default_value = 0.0
        inp = node_group.inputs.new('NodeSocketFloat','XRotSensitivity')
        inp.default_value = 1.0
        inp = node_group.inputs.new('NodeSocketFloat','YRotSensitivity')
        inp.default_value = 1.0
        inp = node_group.inputs.new('NodeSocketFloat','MoveSensitivityX')
        inp.default_value = 0.5
        inp = node_group.inputs.new('NodeSocketFloat','MoveSensitivityY')
        inp.default_value = 0.5
        inp = node_group.inputs.new('NodeSocketFloat','HeightSensitivity')
        inp.default_value = 1.0
        inp = node_group.inputs.new('NodeSocketFloat','XOffset')
        inp.default_value = 0.0
        inp = node_group.inputs.new('NodeSocketFloat','YOffset')
        inp.default_value = 0.0
        inp = node_group.inputs.new('NodeSocketFloat','ZOffset')
        inp.default_value = 0.0
        inp = node_group.inputs.new('NodeSocketBool','Use Object Foam')
        inp.default_value = True
        inp = node_group.inputs.new('NodeSocketFloat','FoamDistance')
        inp.default_value = 65
        inp = node_group.inputs.new('NodeSocketBool','Use Ripples')
        inp.default_value = True
        inp = node_group.inputs.new('NodeSocketFloat','Wavelength')
        inp.default_value = 0.1
        inp = node_group.inputs.new('NodeSocketFloat','Amplitude')
        inp.default_value = 3.0
        inp = node_group.inputs.new('NodeSocketFloat','OuterFalloff')
        inp.default_value = 3.0
        inp = node_group.inputs.new('NodeSocketFloat','Innercut')
        inp.default_value = 20.0
        inp = node_group.inputs.new('NodeSocketFloat','Wave Speed')
        inp.default_value = 10.0
        inp = node_group.inputs.new('NodeSocketBool','Show Front')
        inp.default_value = False
        inp = node_group.inputs.new('NodeSocketFloatFactor','Circular <--> Bow Wave')
        inp.default_value = 0.0
        inp.min_value = 0.0
        inp.max_value = 1.0
        inp = node_group.inputs.new('NodeSocketFloat','Set Front Direction')
        inp.default_value = 0.0
        inp = node_group.inputs.new('NodeSocketFloat','Bow-Wave Offset')
        inp.default_value = 1.0
        inp = node_group.inputs.new('NodeSocketFloat','Turbulence')
        inp.default_value = 1.0

        node = nodes.new("NodeGroupInput" )
        node.name = "Group Input"
        node.location = (-1972, 657)

        node = nodes.new("NodeReroute" )
        node.name = "Reroute"
        node.location = (-1314, 174)

        node = nodes.new("GeometryNodeGroup" )
        node.name = "Group.001"
        node.location = (-982, 621)
        node.node_tree = bpy.data.node_groups["AOMFloat_plus"]
        node.hide = False
        node.mute = False
        node.inputs[1].default_value = 0.0
        node.inputs[2].default_value = 1.0
        node.inputs[3].default_value = 1.0
        node.inputs[4].default_value = 1.0
        node.inputs[5].default_value = 0.59
        node.inputs[6].default_value = 0.89
        node.inputs[7].default_value = 0.0
        node.inputs[8].default_value = 0.0
        node.inputs[9].default_value = 0.0
        node.inputs[10].default_value = 0.0
        node.inputs[11].default_value = 0.0
        node.inputs[12].default_value = True
        node.outputs[1].default_value = (0.0,0.0,0.0,)
        node.outputs[2].default_value = (0.0,0.0,0.0,)
        node.outputs[3].default_value = (0.0,0.0,0.0,)
        node.outputs[4].default_value = (0.0,0.0,0.0,)

        node = nodes.new("NodeReroute" )
        node.name = "Reroute.009"
        node.location = (-453, 187)

        node = nodes.new("NodeGroupInput" )
        node.name = "Group Input.001"
        node.location = (-386, 1411)

        node = nodes.new("NodeReroute" )
        node.name = "Reroute.002"
        node.location = (-295, 396)

        node = nodes.new("NodeReroute" )
        node.name = "Reroute.003"
        node.location = (-162, 218)

        node = nodes.new("NodeReroute" )
        node.name = "Reroute.001"
        node.location = (-123, 285)

        node = nodes.new("GeometryNodeGroup" )
        node.name = "Group.002"
        node.location = (68, 770)
        node.node_tree = bpy.data.node_groups["AOMFloat_ObjectFoamProximity"]
        node.hide = False
        node.mute = False
        node.inputs[1].default_value = False
        node.inputs[2].default_value = (0.0,0.0,0.0,)
        node.inputs[3].default_value = (0.0,0.0,0.0,)
        node.inputs[4].default_value = (0.0,0.0,0.0,)
        node.inputs[5].default_value = (1.0,1.0,1.0,)
        node.inputs[6].default_value = "obj_foam"
        node.inputs[8].default_value = False
        node.inputs[9].default_value = 83.52
        node.inputs[10].default_value = 2.54
        node.outputs[1].default_value = 0.0

        node = nodes.new("NodeGroupInput" )
        node.name = "Group Input.002"
        node.location = (599, 1411)

        node = nodes.new("NodeReroute" )
        node.name = "Reroute.007"
        node.location = (818, 347)

        node = nodes.new("GeometryNodeGroup" )
        node.name = "Group.005"
        node.location = (889, 715)
        node.node_tree = bpy.data.node_groups["AOMFloat_Ripples"]
        node.hide = False
        node.mute = False
        node.inputs[1].default_value = (0.0,0.0,0.0,)
        node.inputs[2].default_value = (0.0,0.0,0.0,)
        node.inputs[3].default_value = True
        node.inputs[4].default_value = 0.0
        node.inputs[5].default_value = 0.23
        node.inputs[6].default_value = 0.8
        node.inputs[7].default_value = 12.13
        node.inputs[8].default_value = 19.93
        node.inputs[9].default_value = 10.0
        node.inputs[10].default_value = False
        node.inputs[11].default_value = 1.83
        node.inputs[12].default_value = 3.79
        node.inputs[13].default_value = 1.0
        node.inputs[14].default_value = 7.4

        node = nodes.new("NodeReroute" )
        node.name = "Reroute.008"
        node.location = (903, 298)

        node = nodes.new("NodeReroute" )
        node.name = "Reroute.010"
        node.location = (953, 242)

        node = nodes.new("NodeReroute" )
        node.name = "Reroute.011"
        node.location = (963, 208)

        node = nodes.new("NodeGroupInput" )
        node.name = "Group Input.003"
        node.location = (1256, 1392)

        node = nodes.new("GeometryNodeGroup" )
        node.name = "Group.006"
        node.location = (1527, 696)
        node.node_tree = bpy.data.node_groups["AOMFloat_Instancing"]
        node.hide = False
        node.mute = False
        node.inputs[1].default_value = (0.0,0.0,0.0,)
        node.inputs[2].default_value = (0.0,0.0,0.0,)
        node.inputs[3].default_value = (0.0,0.0,0.0,)
        node.inputs[4].default_value = (0.0,0.0,0.0,)
        node.inputs[7].default_value = True

        node = nodes.new("NodeGroupOutput" )
        node.name = "Group Output"
        node.location = (1981, 697)
        node_group.outputs.new(type= 'NodeSocketGeometry', name='Geometry')
        links.new( nodes['Group Input'].outputs[0],  nodes['Group.001'].inputs[0])
        links.new( nodes['Group Input'].outputs[4],  nodes['Reroute'].inputs[0])
        links.new( nodes['Group Input'].outputs[7],  nodes['Group.001'].inputs[12])
        links.new( nodes['Group Input'].outputs[8],  nodes['Group.001'].inputs[5])
        links.new( nodes['Group Input'].outputs[9],  nodes['Group.001'].inputs[6])
        links.new( nodes['Group Input'].outputs[10],  nodes['Group.001'].inputs[1])
        links.new( nodes['Group Input'].outputs[11],  nodes['Group.001'].inputs[2])
        links.new( nodes['Group Input'].outputs[12],  nodes['Group.001'].inputs[3])
        links.new( nodes['Group Input'].outputs[13],  nodes['Group.001'].inputs[7])
        links.new( nodes['Group Input'].outputs[14],  nodes['Group.001'].inputs[8])
        links.new( nodes['Group Input'].outputs[15],  nodes['Group.001'].inputs[4])
        links.new( nodes['Group Input'].outputs[16],  nodes['Group.001'].inputs[9])
        links.new( nodes['Group Input'].outputs[17],  nodes['Group.001'].inputs[10])
        links.new( nodes['Group Input'].outputs[18],  nodes['Group.001'].inputs[11])
        links.new( nodes['Group Input.001'].outputs[5],  nodes['Group.002'].inputs[7])
        links.new( nodes['Group Input.001'].outputs[6],  nodes['Group.002'].inputs[8])
        links.new( nodes['Group Input.001'].outputs[19],  nodes['Group.002'].inputs[1])
        links.new( nodes['Group Input.001'].outputs[20],  nodes['Group.002'].inputs[9])
        links.new( nodes['Group Input.002'].outputs[21],  nodes['Group.005'].inputs[3])
        links.new( nodes['Group Input.002'].outputs[22],  nodes['Group.005'].inputs[5])
        links.new( nodes['Group Input.002'].outputs[23],  nodes['Group.005'].inputs[6])
        links.new( nodes['Group Input.002'].outputs[24],  nodes['Group.005'].inputs[7])
        links.new( nodes['Group Input.002'].outputs[25],  nodes['Group.005'].inputs[8])
        links.new( nodes['Group Input.002'].outputs[26],  nodes['Group.005'].inputs[9])
        links.new( nodes['Group Input.002'].outputs[27],  nodes['Group.005'].inputs[10])
        links.new( nodes['Group Input.002'].outputs[28],  nodes['Group.005'].inputs[13])
        links.new( nodes['Group Input.002'].outputs[29],  nodes['Group.005'].inputs[11])
        links.new( nodes['Group Input.002'].outputs[30],  nodes['Group.005'].inputs[12])
        links.new( nodes['Group Input.002'].outputs[31],  nodes['Group.005'].inputs[14])
        links.new( nodes['Group Input.003'].outputs[1],  nodes['Group.006'].inputs[5])
        links.new( nodes['Group Input.003'].outputs[2],  nodes['Group.006'].inputs[7])
        links.new( nodes['Group Input.003'].outputs[3],  nodes['Group.006'].inputs[6])
        links.new( nodes['Group.006'].outputs[0],  nodes['Group Output'].inputs[0])
        links.new( nodes['Reroute'].outputs[0],  nodes['Group.001'].inputs[13])
        links.new( nodes['Group.001'].outputs[0],  nodes['Group.002'].inputs[0])
        links.new( nodes['Reroute.003'].outputs[0],  nodes['Group.002'].inputs[2])
        links.new( nodes['Reroute.002'].outputs[0],  nodes['Group.002'].inputs[3])
        links.new( nodes['Group.001'].outputs[1],  nodes['Reroute.002'].inputs[0])
        links.new( nodes['Group.001'].outputs[3],  nodes['Reroute.003'].inputs[0])
        links.new( nodes['Reroute.009'].outputs[0],  nodes['Group.002'].inputs[5])
        links.new( nodes['Group.002'].outputs[1],  nodes['Group.005'].inputs[4])
        links.new( nodes['Group.002'].outputs[0],  nodes['Group.005'].inputs[0])
        links.new( nodes['Group.005'].outputs[0],  nodes['Group.006'].inputs[0])
        links.new( nodes['Reroute.007'].outputs[0],  nodes['Group.006'].inputs[1])
        links.new( nodes['Reroute.002'].outputs[0],  nodes['Reroute.007'].inputs[0])
        links.new( nodes['Reroute.008'].outputs[0],  nodes['Group.006'].inputs[2])
        links.new( nodes['Reroute.001'].outputs[0],  nodes['Reroute.008'].inputs[0])
        links.new( nodes['Group.001'].outputs[4],  nodes['Reroute.009'].inputs[0])
        links.new( nodes['Reroute.011'].outputs[0],  nodes['Group.006'].inputs[4])
        links.new( nodes['Reroute.010'].outputs[0],  nodes['Group.006'].inputs[3])
        links.new( nodes['Reroute.003'].outputs[0],  nodes['Reroute.010'].inputs[0])
        links.new( nodes['Reroute.001'].outputs[0],  nodes['Group.002'].inputs[4])
        links.new( nodes['Reroute.009'].outputs[0],  nodes['Reroute.011'].inputs[0])
        links.new( nodes['Reroute.003'].outputs[0],  nodes['Group.005'].inputs[1])
        links.new( nodes['Group.001'].outputs[2],  nodes['Reroute.001'].inputs[0])
        links.new( nodes['Reroute.001'].outputs[0],  nodes['Group.005'].inputs[2])
        '''mod['Input_18'] = True
        mod['Input_6'] = True
        mod['Input_7'] = 2.0
        mod['Input_8'] = 2.0
        mod['Input_10'] = 1.0
        mod['Input_11'] = 1.0
        mod['Input_12'] = 0.5
        mod['Input_13'] = 0.5
        mod['Input_14'] = 0.5
        mod['Input_19'] = True
        mod['Input_20'] = 65.0
        mod['Input_21'] = True
        mod['Input_22'] = 0.1
        mod['Input_23'] = 3.0
        mod['Input_24'] = 0.1
        mod['Input_25'] = 3.0
        mod['Input_26'] = 6.0
        mod['Input_30'] = 1.0
        mod['Input_31'] = 1.0'''
        
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
