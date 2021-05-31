import bpy
#from .aom import add_driver


class AOMMatHandler:

    def __init__(self, context):
        self.context = context
        self.material = self.get_material()

        #self.materialname = "AdvOceanMat"

    def get_material(self):
        newMatName = "AdvOceanMat_" + \
            self.get_preset_name(self.context.scene.aom_props.MaterialSel)
        print(f"newmaterialname is {newMatName}")
        mat = bpy.data.materials.get(newMatName)
        if mat is None:
            # create material
            mat = bpy.data.materials.new(name=newMatName)

        return mat

    def get_preset_name(self, index):
        index = int(index)
        if index == 1:
            return 'Wet Foam'
        elif index == 2:
            return 'Wet Foam2'
        elif index == 3:
            return 'Dry Foam'
        elif index == 4:
            return 'Legacy'

    def del_nodes(self):
        nodes = self.material.node_tree.nodes
        for node in nodes:
            nodes.remove(node)

    def make_material(self, ob):

        self.handle_materialslots(ob)

        self.material.use_screen_refraction = True
        self.material.use_sss_translucency = True

        node_tree = self.material.node_tree

        if self.context.scene.aom_props.MaterialSel == '1':
            self.del_nodes()
            self.outputnodes(node_tree)
            self.water_28(node_tree)
            self.foam_material_30(node_tree)
            self.FoamFac_bubbly(node_tree)
            self.foam_fac_ctl(node_tree)
            self.constructor_30(node_tree)

        elif self.context.scene.aom_props.MaterialSel == '2':
            self.del_nodes()
            self.outputnodes(node_tree)
            self.water_28(node_tree)
            self.foam_material_30(node_tree)
            self.FoamFac_legacy_improve(node_tree)
            self.FoamFac_legacy_improve_TransBub(node_tree)
            self.foam_fac_ctl(node_tree)
            self.constructor_wet2(node_tree)

        elif self.context.scene.aom_props.MaterialSel == '3':
            self.del_nodes()
            self.outputnodes(node_tree)
            self.water_28(node_tree)
            self.foam_material_30(node_tree)
            self.FoamFac_legacy_improve(node_tree)
            self.foam_fac_ctl(node_tree)
            self.constructor_legacy_improve(node_tree)

        elif self.context.scene.aom_props.MaterialSel == '4':
            self.del_nodes()
            self.outputnodes(node_tree)
            self.water_28(node_tree)
            self.foam_material_30(node_tree)
            self.FoamFac_legacy(node_tree)
            self.foam_fac_ctl(node_tree)
            self.constructor_legacy(node_tree)

        self.label_nodes(node_tree)
        return self.material

    def outputnodes(self, node_tree):
        nodes = node_tree.nodes
        links = node_tree.links

        node = nodes.new('ShaderNodeMixShader')  # mixshader machen
        node.name = 'MainMix'
        node.location = (2200, 000)

        node = nodes.new('ShaderNodeOutputMaterial')  # mixshader machen
        node.name = "MaterialOutCycles"
        node.location = (2400, 000)
        node.target = 'CYCLES'
        links.new(nodes['MainMix'].outputs['Shader'],
                  nodes['MaterialOutCycles'].inputs['Surface'])  # EndMixer in den Surface

        node = nodes.new('ShaderNodeOutputMaterial')  # mixshader machen
        node.name = "MaterialOutEevee"
        node.location = (2400, -200)
        node.target = 'EEVEE'
        links.new(nodes['MainMix'].outputs['Shader'],
                  nodes['MaterialOutEevee'].inputs['Surface'])  # EndMixer in den Surface

    def eevee_settings(self):
        REngine = self.context.scene.render.engine
        self.context.scene.render.engine = 'BLENDER_EEVEE'
        # Better 'BLEND'??????????'HASHED'
        self.context.object.active_material.blend_method = 'BLEND'
        self.context.scene.render.engine = REngine

    def handle_materialslots(self, ob):

        if ob.data.materials:
            # assign to 1st material slot
            ob.data.materials[0] = self.material
        else:
            #  no slots
            ob.data.materials.append(self.material)

        self.context.object.active_material.use_nodes = True
        self.eevee_settings()

    def water_28(self, node_tree):
        nodes = node_tree.nodes
        links = node_tree.links

        # Ocean
        node = nodes.new('ShaderNodeBsdfGlossy')  # glossyshader machen
        node.location = (-1200, 000)
        nodes["Glossy BSDF"].inputs[1].default_value = 0.06

        # dieser glossy schader muss fast schwarz werden
        node = nodes.new('ShaderNodeBsdfGlossy')
        node.location = (-1200, -200)
        nodes['Glossy BSDF.001'].inputs['Color'].default_value[1] = 0.01
        nodes['Glossy BSDF.001'].inputs['Color'].default_value[2] = 0.01
        nodes['Glossy BSDF.001'].inputs['Color'].default_value[0] = 0.01
        nodes["Glossy BSDF.001"].inputs[1].default_value = 0.06

        node = nodes.new('ShaderNodeLayerWeight')  # layerweight machen
        node.location = (-1200, 200)
        node = nodes.new('ShaderNodeMixShader')  # mixshader machen
        node.location = (-900, 000)

        # link basic OceanMaterial zum ersen Mix shader
        links.new(nodes['Layer Weight'].outputs['Fresnel'],
                  nodes['Mix Shader'].inputs['Fac'])
        links.new(nodes['Glossy BSDF'].outputs['BSDF'],
                  nodes['Mix Shader'].inputs['Shader'])
        links.new(nodes['Glossy BSDF.001'].outputs['BSDF'],
                  nodes['Mix Shader'].inputs[2])

        node = nodes.new('ShaderNodeLayerWeight')  # layerweight machen
        node.location = (-900, 200)
        nodes['Layer Weight.001'].inputs['Blend'].default_value = 0.2
        # bpy.context.area.type = 'NODE_EDITOR'
        node = nodes.new('ShaderNodeBsdfRefraction')  # mixshader machen
        node.location = (-900, -150)
        node = nodes.new('ShaderNodeMixShader')  # mixshader machen
        node.location = (-700, 000)

        # transparent mixer
        node = nodes.new('ShaderNodeLayerWeight')  # layerweight machen
        node.location = (-700, 200)
        node.inputs['Blend'].default_value = 0.1
        node = nodes.new('ShaderNodeMixShader')  # mixshader machen
        node.name = "OceanOut"
        node.location = (-500, 000)
        node = nodes.new('ShaderNodeBsdfTransparent')  # mixshader machen
        node.location = (-700, -150)

        # link basic OceanMaterial zum ersen Mix shader
        links.new(nodes['Layer Weight.001'].outputs['Fresnel'],
                  nodes['Mix Shader.001'].inputs['Fac'])
        links.new(nodes['Mix Shader'].outputs['Shader'],
                  nodes['Mix Shader.001'].inputs['Shader'])
        links.new(nodes['Refraction BSDF'].outputs['BSDF'],
                  nodes['Mix Shader.001'].inputs[2])

        links.new(nodes['Mix Shader.001'].outputs['Shader'],
                  nodes['OceanOut'].inputs[1])
        links.new(nodes['Transparent BSDF'].outputs['BSDF'],
                  nodes['OceanOut'].inputs[2])
        links.new(nodes['Layer Weight.002'].outputs['Fresnel'],
                  nodes['OceanOut'].inputs[0])

        # Rougness value and Ocean color

        node = nodes.new('ShaderNodeRGB')
        node.location = (-1400, 000)
        nodes['RGB'].outputs[0].default_value = (1, 1, 1, 1)

        links.new(nodes['RGB'].outputs[0],
                  nodes['Glossy BSDF'].inputs['Color'])
        links.new(nodes['RGB'].outputs[0],
                  nodes['Refraction BSDF'].inputs['Color'])
        links.new(nodes['RGB'].outputs[0],
                  nodes['Transparent BSDF'].inputs['Color'])

        node = nodes.new('ShaderNodeValue')
        node.location = (-1400, 200)
        nodes['Value'].outputs[0].default_value = 0.01
        links.new(nodes['Value'].outputs[0], nodes['Glossy BSDF'].inputs[1])
        links.new(nodes['Value'].outputs[0],
                  nodes['Glossy BSDF.001'].inputs[1])
        links.new(nodes['Value'].outputs[0],
                  nodes['Refraction BSDF'].inputs[1])

        # bump
        node = nodes.new('ShaderNodeBump')
        node.name = "WaterBump"
        node.location = (-1700, 000)
        node.inputs[1].default_value = 0.1

        links.new(nodes['WaterBump'].outputs[0],
                  nodes['Glossy BSDF'].inputs[2])
        links.new(nodes['WaterBump'].outputs[0],
                  nodes['Glossy BSDF.001'].inputs[2])
        links.new(nodes['WaterBump'].outputs[0],
                  nodes['Refraction BSDF'].inputs[3])
        links.new(nodes['WaterBump'].outputs[0],
                  nodes['Layer Weight'].inputs[1])
        links.new(nodes['WaterBump'].outputs[0],
                  nodes['Layer Weight.001'].inputs[1])
        links.new(nodes['WaterBump'].outputs[0],
                  nodes['Layer Weight.002'].inputs[1])

        node = nodes.new('ShaderNodeMixRGB')
        node.name = "CombTex"
        node.location = (-2000, 000)
        node.blend_type = 'ADD'
        node.inputs[0].default_value = 0.1

        node = nodes.new('ShaderNodeTexMusgrave')
        node.name = "TexMusgraveL"
        node.musgrave_dimensions = '4D'
        node.location = (-2300, 000)
        node.inputs[3].default_value = 2
        node.inputs[4].default_value = 2
        node.inputs[5].default_value = 2

        node = nodes.new('ShaderNodeTexMusgrave')
        node.name = "TexMusgraveS"
        node.location = (-2300, -300)
        node.musgrave_dimensions = '4D'
        node.inputs[3].default_value = 1
        node.inputs[4].default_value = 0.2
        node.inputs[5].default_value = 1.6

        node = nodes.new('ShaderNodeMath')
        node.name = "ScaleMultiS"
        node.location = (-2500, -300)
        node.inputs[1].default_value = 4
        node.operation = 'MULTIPLY'

        node = nodes.new('ShaderNodeValue')
        node.name = "Timer"
        node.location = (-2700, 000)
        source = node.outputs[0]
        target = bpy.context.scene
        prop = 'default_value'
        data_path = "frame_current"
        id_type = 'SCENE'
        driver = self.add_driver(source, target, prop,
                                 data_path, -1, func="0.0002*", id_type=id_type)

        node = nodes.new('ShaderNodeValue')
        node.name = "WaterBumpTexScale"
        node.location = (-2700, -300)
        node.outputs[0].default_value = 250

        node = nodes.new('ShaderNodeValue')
        node.name = "WaterBumpStrength"
        node.location = (-2700, -500)
        node.outputs[0].default_value = 0.02

        node = nodes.new('ShaderNodeMapping')
        node.name = "WaterMap"
        node.location = (-3000, 000)

        node = nodes.new('ShaderNodeTexCoord')
        node.name = "WaterTexCo"
        node.location = (-3300, 000)

        links.new(nodes['WaterTexCo'].outputs[2],
                  nodes['WaterMap'].inputs[0])
        links.new(nodes['WaterMap'].outputs[0],
                  nodes['TexMusgraveL'].inputs[0])
        links.new(nodes['WaterMap'].outputs[0],
                  nodes['TexMusgraveS'].inputs[0])

        links.new(nodes['WaterBumpTexScale'].outputs[0],
                  nodes['TexMusgraveL'].inputs[2])
        links.new(nodes['WaterBumpTexScale'].outputs[0],
                  nodes['ScaleMultiS'].inputs[0])
        links.new(nodes['ScaleMultiS'].outputs[0],
                  nodes['TexMusgraveS'].inputs[2])

        links.new(nodes['Timer'].outputs[0],
                  nodes['TexMusgraveL'].inputs[1])
        links.new(nodes['Timer'].outputs[0],
                  nodes['TexMusgraveS'].inputs[1])

        links.new(nodes['WaterBumpStrength'].outputs[0],
                  nodes['WaterBump'].inputs[0])

        links.new(nodes['TexMusgraveL'].outputs[0],
                  nodes['CombTex'].inputs[1])
        links.new(nodes['TexMusgraveS'].outputs[0],
                  nodes['CombTex'].inputs[2])

        links.new(nodes['CombTex'].outputs[0],
                  nodes['WaterBump'].inputs[2])

    def foam_material_30(self, node_tree):
        nodes = node_tree.nodes
        links = node_tree.links

        offsetx = 0
        offsety = 0
        # Foam material

        node = nodes.new('ShaderNodeBump')
        node.name = "FoamBump"
        node.location = (-200, -1500)
        node.inputs[0].default_value = 0.5

        node = nodes.new('ShaderNodeMapRange')
        node.name = "MRSubsurface"
        node.location = (-200+offsetx, -600+offsety)
        node.clamp = True
        node.inputs[1].default_value = 1.6
        node.inputs[2].default_value = 0.0
        node.inputs[3].default_value = 0.0
        node.inputs[4].default_value = 0.2

        node = nodes.new('ShaderNodeMapRange')
        node.name = "CRFoamRough"
        node.location = (-200+offsetx, -900+offsety)
        node.clamp = True
        node.inputs[1].default_value = 1.5
        node.inputs[2].default_value = 0.15
        node.inputs[3].default_value = 0.0
        node.inputs[4].default_value = 0.9

        node = nodes.new('ShaderNodeMapRange')
        node.name = "CRFoamTransmission"
        node.location = (-200+offsetx, -1200+offsety)
        node.clamp = True
        node.inputs[1].default_value = 1.0
        node.inputs[2].default_value = 2.7
        node.inputs[3].default_value = 0.0
        node.inputs[4].default_value = 0.4

        # principled shader basis für foam
        node = nodes.new('ShaderNodeBsdfPrincipled')
        node.location = (200+offsetx, -700+offsety)
        node.name = "FoamOut"
        node.inputs[0].default_value = (1.0, 1.0, 1.0, 1)
        node.inputs[1].default_value = 0.3
        node.inputs[2].default_value = (0.1, 0.1, 0.1)
        node.inputs[3].default_value = (1, 1, 1, 1)
        node.inputs[14].default_value = 1.33
        node.inputs[15].default_value = 0.2
        node.inputs[7].default_value = 0.2

        self.foam_ctl(node_tree)

    def foam_fac_ctl(self, node_tree):
        nodes = node_tree.nodes
        links = node_tree.links

        node = nodes.new('ShaderNodeValue')
        node.name = 'LowerOceanFoamCut'
        node.location = (-1600, 3000)
        node.outputs[0].default_value = 0.0
        # lower OCean foam fine edit
        node = nodes.new('ShaderNodeMath')
        node.name = 'LowerOceanFoam_Add'
        node.location = (-1300, 3000)
        node.operation = 'ADD'
        node.inputs[1].default_value = 1.0

        node = nodes.new('ShaderNodeMath')
        node.name = 'LowerOceanFoam_Log'
        node.location = (-1000, 3000)
        node.operation = 'LOGARITHM'
        node.inputs[1].default_value = 60.0

        links.new(nodes['LowerOceanFoamCut'].outputs[0],
                  nodes['LowerOceanFoam_Add'].inputs[0])
        links.new(nodes['LowerOceanFoam_Add'].outputs[0],
                  nodes['LowerOceanFoam_Log'].inputs[0])

        node = nodes.new('ShaderNodeValue')
        node.name = 'FoamBaseStrength'
        node.location = (-1600, 2700)
        node.outputs[0].default_value = 1.0

        node = nodes.new('ShaderNodeValue')
        node.name = 'LowerObjectCut'
        node.location = (-1600, 2400)
        node.outputs[0].default_value = 0.1

        node = nodes.new('ShaderNodeValue')
        node.name = 'ObjectBaseStrength'
        node.location = (-1600, 2100)
        node.outputs[0].default_value = 1

        node = nodes.new('ShaderNodeValue')
        node.name = 'Patchiness'
        node.location = (-1600, 1800)
        node.outputs[0].default_value = 0.2

        node = nodes.new('ShaderNodeValue')
        node.name = 'DisplStrength'
        node.location = (-1600, 1500)
        node.outputs[0].default_value = 0.02

        # noise scale
        node = nodes.new('ShaderNodeValue')
        node.location = (000, 1200)
        node.name = 'NoiseScale'
        node.outputs[0].default_value = 20

        node = nodes.new('ShaderNodeMath')
        node.location = (000, 900)
        node.name = 'MultiNoiseScale'
        node.inputs[1].default_value = 5

    def foam_ctl(self, node_tree):
        # controll values foam
        nodes = node_tree.nodes

        node = nodes.new('ShaderNodeValue')
        node.name = 'FoamSubsurf'
        node.location = (-600, -600)
        node.outputs[0].default_value = 0.2

        node = nodes.new('ShaderNodeRGB')
        node.name = 'FoamColor'
        node.location = (-600, -900)
        node.outputs[0].default_value = (1, 1, 1, 1)

        node = nodes.new('ShaderNodeValue')
        node.name = 'FoamRoughness'
        node.location = (-600, -1200)
        node.outputs[0].default_value = 0.2

        node = nodes.new('ShaderNodeValue')
        node.name = 'FoamTransmission'
        node.location = (-600, -1500)
        node.outputs[0].default_value = 0.0

        node = nodes.new('ShaderNodeValue')
        node.name = 'FoamBumpCtl'
        node.location = (-600, -1800)
        node.outputs[0].default_value = 0.4

    def get_BubbleNodeGroup(self):
        data = bpy.data
        if "BubbleNG" in data.node_groups:
            return data.node_groups["BubbleNG"]

        ng = data.node_groups.new(name="BubbleNG", type='ShaderNodeTree')
        ng.name = 'BubbleNG'

        # create group inputs
        group_inputs = ng.nodes.new('NodeGroupInput')
        group_inputs.location = (-850, 0)
        ng.inputs.new('NodeSocketVector', 'Vector')
        ng.inputs.new('NodeSocketFloat', 'Scale')
        ng.inputs.new('NodeSocketFloat', 'Convexness')
        ng.inputs.new('NodeSocketFloat', 'Min')
        ng.inputs.new('NodeSocketFloat', 'Amount')

        nodes = ng.nodes
        links = ng.links

        node = nodes.new('ShaderNodeTexVoronoi')
        node.location = (-400, 675)
        nodes["Voronoi Texture"].inputs[1].default_value = 100

        node = nodes.new('ShaderNodeValToRGB')
        node.location = (-000, 875)
        node.color_ramp.interpolation = 'B_SPLINE'
        node.color_ramp.elements[0].color = 0, 0, 0, 1
        node.color_ramp.elements[0].position = 0.74
        node.color_ramp.elements[1].color = 1, 1, 1, 1

        node = nodes.new('ShaderNodeMapRange')
        node.location = (400, 950)
        node.inputs[4].default_value = 0
        node.inputs[3].default_value = 1

        # bottom half

        node = nodes.new('ShaderNodeTexVoronoi')
        node.name = "VorRadius"
        node.location = (-400, 200)
        node.feature = 'N_SPHERE_RADIUS'
        #nodes["Voronoi Texture.001"].inputs[1].default_value = 50

        node = nodes.new('ShaderNodeMath')
        node.operation = 'MULTIPLY'
        node.inputs[1].default_value = 1
        node.location = (000, 000)

        node = nodes.new('ShaderNodeMath')
        node.operation = 'LESS_THAN'
        node.location = (300, 000)

        node = nodes.new('ShaderNodeMath')
        node.operation = 'MULTIPLY'
        node.location = (600, 000)

        node = nodes.new('ShaderNodeMath')
        node.operation = 'GREATER_THAN'
        node.location = (000, -200)

        # mid
        node = nodes.new('ShaderNodeMath')
        node.name = 'ArcSin'
        node.operation = 'ARCSINE'
        node.inputs[2].default_value = 0.1
        node.location = (800, 400)

        node = nodes.new('ShaderNodeMath')
        node.operation = 'MULTIPLY_ADD'
        node.inputs[2].default_value = 0.1
        node.location = (800, 200)

        links.new(nodes['Group Input'].outputs[0],
                  nodes['Voronoi Texture'].inputs[0])
        links.new(nodes['Group Input'].outputs[0],
                  nodes['VorRadius'].inputs[0])
        links.new(nodes['Group Input'].outputs[1],
                  nodes['Voronoi Texture'].inputs[2])
        links.new(nodes['Group Input'].outputs[1],
                  nodes['VorRadius'].inputs[2])

        # min
        # links.new(nodes['Group Input'].outputs[3],
        #          nodes['Map Range'].inputs[3])

        links.new(nodes['Voronoi Texture'].outputs[0],
                  nodes['ColorRamp'].inputs[0])
        links.new(nodes['Voronoi Texture'].outputs[0], nodes['Math'].inputs[0])

        links.new(nodes['ColorRamp'].outputs[0], nodes['Map Range'].inputs[0])

        links.new(nodes['Voronoi Texture'].outputs[1],
                  nodes['Math.003'].inputs[0])
        links.new(nodes['Group Input'].outputs[4], nodes['Math.003'].inputs[1])

        links.new(nodes['Math'].outputs[0], nodes['Math.001'].inputs[0])
        links.new(nodes['VorRadius'].outputs['Radius'],
                  nodes['Math.001'].inputs[1])

        links.new(nodes['Math.001'].outputs[0], nodes['Math.002'].inputs[0])
        links.new(nodes['Math.003'].outputs[0], nodes['Math.002'].inputs[1])

        links.new(nodes['Group Input'].outputs[2], nodes['Math.004'].inputs[0])
        links.new(nodes['Math.002'].outputs[0], nodes['Math.004'].inputs[1])
        #links.new(nodes['Math.004'].outputs[0], nodes['Map Range'].inputs[3])
        # links.new(nodes['Group Input'].outputs[3],
        #          nodes['Map Range'].inputs[2])

        group_inputs = ng.nodes.new('NodeGroupOutput')
        group_inputs.location = (1250, 0)
        ng.outputs.new('NodeSocketColor', 'SoftShape')
        ng.outputs.new('NodeSocketColor', 'HardShape')

        links.new(nodes['Map Range'].outputs[0],
                  nodes['ArcSin'].inputs[0])
        links.new(nodes['ArcSin'].outputs[0],
                  nodes['Group Output'].inputs[0])

        links.new(nodes['Math.002'].outputs[0],
                  nodes['Group Output'].inputs[1])

        return ng

    def FoamFac_bubbly(self, node_tree):
        nodes = node_tree.nodes
        links = node_tree.links

        # patchiness --> ctl
        # node = nodes.new('ShaderNodeValue')  # Attribute foam
        #node.name = "Patchiness"
        #node.location = (-1600, 1800)
        #node.outputs[0].default_value = 0.3

        node = nodes.new('ShaderNodeAttribute')  # Attribute foam
        node.name = "Foam"
        node.location = (-250, 2600)
        node.attribute_name = "foam"
        # node = nodes.new('ShaderNodeGamma')  # gamma für wetmap
        #node.location = (200, 1400)
        #nodes["Gamma"].inputs[1].default_value = 0.3
        node = nodes.new('ShaderNodeMapRange')
        node.name = "CRFoam"
        node.location = (000, 2700)

        node = nodes.new('ShaderNodeAttribute')  # attribute wetmap
        node.name = "Wet"
        node.location = (-250, 2450)
        node.attribute_name = "dp_wetmap"

        node = nodes.new('ShaderNodeMapRange')
        node.name = "CRWet"
        node.location = (000, 2450)

        node = nodes.new('ShaderNodeMixRGB')  # rgb mixshader machen
        node.name = "MixFoamWet"
        node.location = (400, 2475)
        node.blend_type = 'ADD'
        node.use_clamp = True
        node.inputs[0].default_value = 1.0

        # link Attribute nodes additiv
        links.new(nodes['Wet'].outputs['Fac'],
                  nodes['CRWet'].inputs[0])
        links.new(nodes['CRFoam'].outputs[0],
                  nodes['MixFoamWet'].inputs['Color2'])
        links.new(nodes['Foam'].outputs['Fac'],
                  nodes['CRFoam'].inputs[0])
        links.new(nodes['CRWet'].outputs[0],
                  nodes['MixFoamWet'].inputs['Color1'])

        node = nodes.new('ShaderNodeMixRGB')  # RGB Mix für Noise 1
        node.name = "SubNoise1"
        node.location = (800, 2175)
        node.blend_type = 'ADD'
        node.use_clamp = False
        node.inputs[0].default_value = 0.6

        # RGB mixshader für zweite Noise Texture
        node = nodes.new('ShaderNodeMixRGB')
        node.name = "SubNoise2"
        node.location = (1000, 2175)
        node.blend_type = 'SUBTRACT'
        node.use_clamp = False
        node.inputs[0].default_value = 0.6

        # link Add notes to Subtract
        links.new(nodes['MixFoamWet'].outputs['Color'],
                  nodes['SubNoise2'].inputs['Color1'])
        links.new(nodes['SubNoise1'].outputs['Color'],
                  nodes['SubNoise2'].inputs['Color2'])

        # links.new(nodes['Patchiness'].outputs[0],
        #          nodes['SubNoise1'].inputs[0])
        # links.new(nodes['Patchiness'].outputs[0],
        #          nodes['SubNoise2'].inputs[0])

        # noise texture (000)
        node = nodes.new('ShaderNodeTexNoise')  # mixshader machen
        node.name = 'Noise1'
        node.location = (400, 2300)
        node.inputs['Scale'].default_value = 100
        node.inputs['Detail'].default_value = 2
        node.inputs['Roughness'].default_value = 0.8

        # Texture Coordinate für die Noise Textures
        #node = nodes.new('ShaderNodeTexCoord')
        #node.name = 'TexCoordNoise'
        #node.location = (000, 2350)
        # Hue Saturation 000 für noise texture2

        node = nodes.new('ShaderNodeMapRange')
        node.name = 'Hue1'
        node.location = (600, 2275)
        #    nodes["Hue Saturation Value"].inputs[2].default_value = 0.1
        node.inputs[4].default_value = 0.2

        # noise texture (001)
        node = nodes.new('ShaderNodeTexNoise')
        node.name = 'Noise2'
        node.location = (400, 2100)
        node.inputs['Detail'].default_value = 2
        node.inputs['Scale'].default_value = 500
        node.inputs['Roughness'].default_value = 0.2

        # node = nodes.new('ShaderNodeTexCoord') ### mixshader machen
        # node.location = (000,150)
        # Hue Saturation 001 für noise texture2

        node = nodes.new('ShaderNodeMapRange')
        node.name = 'Hue2'
        node.location = (600, 2100)
        node.inputs[4].default_value = 1

        node = nodes.new('ShaderNodeMapRange')
        node.name = 'MPScaleNoise'
        node.location = (1300, 2175)
        node.inputs[2].default_value = 0.2
        node.inputs[3].default_value = 0.0
        node.inputs[4].default_value = 1.0

        links.new(nodes['Noise1'].outputs['Fac'],
                  nodes['Hue1'].inputs[0])
        links.new(nodes['Noise2'].outputs['Fac'],
                  nodes['Hue2'].inputs[0])
        links.new(nodes['Hue1'].outputs[0],
                  nodes['SubNoise1'].inputs['Color1'])
        links.new(nodes['Hue2'].outputs[0],
                  nodes['SubNoise1'].inputs['Color2'])
        links.new(nodes['SubNoise2'].outputs[0],
                  nodes['MPScaleNoise'].inputs[0])

        # moving foam ######################
        ####################################
        # bubblegroup textCoord
        node = nodes.new('ShaderNodeTexCoord')
        node.name = 'TexCoordBub'
        node.location = (-1200, 1800)

        node = nodes.new('ShaderNodeMapping')
        node.name = 'Map'
        node.location = (-800, 1800)

        ############################################
        ###############Driver stuff, rotation needed #################
        # value frame durch was
        #

        node = nodes.new('ShaderNodeValue')
        node.name = 'SpeedMoveWave'
        node.location = (-1400, 1300)

        source = node.outputs[0]
        target = bpy.context.scene
        prop = 'default_value'
        data_path = "frame_current"
        id_type = 'SCENE'
        driver = self.add_driver(source, target, prop,
                                 data_path, -1, func="0.0003*", id_type=id_type)

        # multiply with aligement factor driver
        node = nodes.new('ShaderNodeMath')
        node.name = 'AligmentDriver'
        node.operation = 'MULTIPLY'
        node.location = (-1200, 1300)

        source = node.inputs[1]
        target = bpy.context.object
        prop = 'default_value'
        data_path = 'modifiers["Ocean"].wave_alignment'
        id_type = 'OBJECT'
        driver = self.add_driver(source, target, prop,
                                 data_path, -1, func="", id_type=id_type)

        node = nodes.new('ShaderNodeCombineXYZ')
        node.name = 'MoveWaveCombXYZ'
        node.location = (-1000, 1300)

        node = nodes.new('ShaderNodeCombineXYZ')
        node.name = 'RotCombXYZ'
        node.location = (-1000, 1600)

        source = node.inputs[2]
        target = bpy.context.object
        prop = 'default_value'
        data_path = 'modifiers["Ocean"].wave_direction'
        id_type = 'OBJECT'
        driver = self.add_driver(source, target, prop,
                                 data_path, -1, func="", id_type=id_type)

        # link moving waves
        links.new(nodes['SpeedMoveWave'].outputs[0],
                  nodes['AligmentDriver'].inputs[0])
        links.new(nodes['AligmentDriver'].outputs[0],
                  nodes['MoveWaveCombXYZ'].inputs[0])
        links.new(nodes['MoveWaveCombXYZ'].outputs[0], nodes['Map'].inputs[1])
        links.new(nodes['RotCombXYZ'].outputs[0], nodes['Map'].inputs[2])

        links.new(nodes['TexCoordBub'].outputs['UV'],
                  nodes['Map'].inputs[0])

        # link coord to noise
        links.new(nodes['TexCoordBub'].outputs['UV'],
                  nodes['Noise1'].inputs['Vector'])
        links.new(nodes['TexCoordBub'].outputs['UV'],
                  nodes['Noise2'].inputs['Vector'])

        #####################################
        #####################################

        BubNG = self.get_BubbleNodeGroup()

        # bubble group 1
        node = nodes.new('ShaderNodeGroup')
        node.node_tree = BubNG
        node.name = 'Bub1'
        node.location = (-000, 1800)
        node.inputs[2].default_value = 1
        node.inputs[3].default_value = 0.2

        # bubble group 2
        node = nodes.new('ShaderNodeGroup')
        node.name = 'Bub2'
        node.node_tree = BubNG
        node.location = (-000, 1500)
        node.inputs[2].default_value = 1
        node.inputs[3].default_value = 0.1

        # bubble group 3
        node = nodes.new('ShaderNodeGroup')
        node.name = 'Bub3'
        node.node_tree = BubNG
        node.location = (-000, 1200)
        node.inputs[2].default_value = 1
        node.inputs[3].default_value = 0.1

        # bubble group 4
        node = nodes.new('ShaderNodeGroup')
        node.name = 'Bub4'
        node.node_tree = BubNG
        node.location = (-000, 900)
        node.inputs[2].default_value = 1
        node.inputs[3].default_value = 0.1

        # link to maping
        links.new(nodes['Map'].outputs[0], nodes['Bub1'].inputs[0])
        links.new(nodes['Map'].outputs[0], nodes['Bub2'].inputs[0])
        links.new(nodes['Map'].outputs[0], nodes['Bub3'].inputs[0])
        links.new(nodes['Map'].outputs[0], nodes['Bub4'].inputs[0])

        # BubbleScale value
        node = nodes.new('ShaderNodeValue')
        node.name = 'ScaleBub'
        node.location = (-600, 1500)
        node.outputs[0].default_value = 1500

        # multiply for different bubblesizes
        node = nodes.new('ShaderNodeMath')
        node.name = 'ScaleMulti2'
        node.location = (-300, 1500)
        node.operation = 'MULTIPLY'
        node.inputs[1].default_value = 2

        node = nodes.new('ShaderNodeMath')
        node.name = 'ScaleMulti3'
        node.location = (-300, 1200)
        node.operation = 'MULTIPLY'
        node.inputs[1].default_value = 4

        node = nodes.new('ShaderNodeMath')
        node.name = 'ScaleMulti4'
        node.location = (-300, 900)
        node.operation = 'MULTIPLY'
        node.inputs[1].default_value = 25

        # link scale bub
        links.new(nodes['ScaleBub'].outputs[0], nodes['Bub1'].inputs[1])
        links.new(nodes['ScaleBub'].outputs[0], nodes['ScaleMulti2'].inputs[0])
        links.new(nodes['ScaleBub'].outputs[0], nodes['ScaleMulti3'].inputs[0])
        links.new(nodes['ScaleBub'].outputs[0], nodes['ScaleMulti4'].inputs[0])

        links.new(nodes['ScaleMulti2'].outputs[0], nodes['Bub2'].inputs[1])
        links.new(nodes['ScaleMulti3'].outputs[0], nodes['Bub3'].inputs[1])
        links.new(nodes['ScaleMulti4'].outputs[0], nodes['Bub4'].inputs[1])

        # math for combine bubbles
        node = nodes.new('ShaderNodeMath')
        node.name = "max1bub"
        node.location = (300, 1800)
        node.operation = 'MAXIMUM'

        node = nodes.new('ShaderNodeMath')
        node.name = "max2bub"
        node.location = (300, 1500)
        node.operation = 'MAXIMUM'

        node = nodes.new('ShaderNodeMath')
        node.name = "max3bub"
        node.location = (600, 1800)
        node.operation = 'MAXIMUM'

        node = nodes.new('ShaderNodeMath')
        node.name = "max4bub"
        node.location = (600, 1500)
        node.operation = 'MAXIMUM'

        node = nodes.new('ShaderNodeMath')
        node.name = "ScaleBubL"
        node.location = (450, 1650)
        node.operation = 'MULTIPLY'
        node.inputs[1].default_value = 1.1

        node = nodes.new('ShaderNodeMath')
        node.name = "ScaleBubS"
        node.location = (450, 1950)
        node.operation = 'MULTIPLY'
        node.inputs[1].default_value = 1.1

        ###mix to bubble factor ########
        node = nodes.new('ShaderNodeMixRGB')
        node.name = "MixBub"
        node.location = (900, 1800)

        node = nodes.new('ShaderNodeMixRGB')
        node.name = "MixBubNoise"
        node.location = (1200, 1500)
        #node.use_clamp = True
        node.blend_type = 'MIX'
        node.inputs[0].default_value = 1.0
        node.inputs[1].default_value = (0, 0, 0, 1)

        node = nodes.new('ShaderNodeDisplacement')
        node.name = "Disp"
        node.location = (2100, 1800)
        node.inputs['Scale'].default_value = 0.01

        links.new(nodes['Bub1'].outputs[1], nodes['max1bub'].inputs[0])
        links.new(nodes['Bub1'].outputs[0], nodes['ScaleBubL'].inputs[0])
        links.new(nodes['ScaleBubL'].outputs[0], nodes['max3bub'].inputs[0])

        links.new(nodes['Bub2'].outputs[1], nodes['max1bub'].inputs[1])
        links.new(nodes['Bub2'].outputs[0], nodes['max2bub'].inputs[0])

        links.new(nodes['Bub3'].outputs[0], nodes['max2bub'].inputs[1])
        links.new(nodes['Bub4'].outputs[0], nodes['max4bub'].inputs[1])
        links.new(nodes['max2bub'].outputs[0], nodes['max4bub'].inputs[0])
        links.new(nodes['max2bub'].outputs[0], nodes['ScaleBubS'].inputs[0])
        links.new(nodes['ScaleBubS'].outputs[0], nodes['max3bub'].inputs[1])

        links.new(nodes['max1bub'].outputs[0], nodes['MixBub'].inputs[0])
        links.new(nodes['max4bub'].outputs[0], nodes['MixBub'].inputs[1])
        links.new(nodes['max3bub'].outputs[0], nodes['MixBub'].inputs[2])

        # mix noise and bubbles
        links.new(nodes['MixBub'].outputs[0], nodes['MixBubNoise'].inputs[2])
        links.new(nodes['MPScaleNoise'].outputs[0],
                  nodes['MixBubNoise'].inputs[0])

        # add noise (that no ocean material on foam), multiply with inverted bubbles to get ocean material on bubbles
        node = nodes.new('ShaderNodeMixRGB')
        node.name = "AddNoise"
        node.location = (1500, 1500)
       # node.use_clamp = True
        node.blend_type = 'ADD'
        node.inputs[0].default_value = 1

        node = nodes.new('ShaderNodeMixRGB')
        node.name = "MultiInvBub"
        node.location = (1800, 1500)
       # node.use_clamp = True
        node.blend_type = 'MULTIPLY'
        node.inputs[0].default_value = 0.92

        node = nodes.new('ShaderNodeMapRange')
        node.name = "MPInvBub"
        node.location = (1500, 1200)
        node.clamp = False
        node.inputs[3].default_value = 1
        node.inputs[4].default_value = 0.310

        node = nodes.new('ShaderNodeMapRange')
        node.name = "MPScaleFoamMain"
        node.location = (1800, 1200)
        node.clamp = True
        node.inputs[2].default_value = 0.1

        # too main mix
        links.new(nodes['MixBubNoise'].outputs[0], nodes['AddNoise'].inputs[1])
        links.new(nodes['MixBub'].outputs[0], nodes['MPInvBub'].inputs[0])
        links.new(nodes['MPScaleNoise'].outputs[0],
                  nodes['AddNoise'].inputs[2])
        links.new(nodes['MixBub'].outputs[0],
                  nodes['MultiInvBub'].inputs[2])
        links.new(nodes['AddNoise'].outputs[0], nodes['MultiInvBub'].inputs[1])
        links.new(nodes['MPInvBub'].outputs[0], nodes['MultiInvBub'].inputs[2])
        links.new(nodes['MultiInvBub'].outputs[0],
                  nodes['MPScaleFoamMain'].inputs[0])

        links.new(nodes['AddNoise'].outputs[0], nodes['Disp'].inputs[0])

        nodes['MPScaleFoamMain'].name = "FoamFacOut"
        nodes['AddNoise'].name = "FoamMatInfo"

    def FoamFac_legacy_improve(self, node_tree):
        nodes = node_tree.nodes
        links = node_tree.links

        node = nodes.new('ShaderNodeAttribute')  # Attribute foam
        node.location = (-250, 1400)
        node.attribute_name = "foam"
        node = nodes.new('ShaderNodeMapRange')
        node.name = "CRFoam"
        node.location = (000, 1500)

        node = nodes.new('ShaderNodeAttribute')  # attribute wetmap
        node.location = (-250, 1250)
        node.attribute_name = "dp_wetmap"
        node = nodes.new('ShaderNodeMapRange')
        node.name = "CRWet"
        node.location = (000, 1250)

        node = nodes.new('ShaderNodeMixRGB')  # rgb mixshader machen
        node.location = (400, 1275)
        node.blend_type = 'ADD'
        node.use_clamp = True
        node.inputs[0].default_value = 1.0

        # link Attribute notes additiv
        links.new(nodes['Attribute.001'].outputs['Fac'],
                  nodes['CRWet'].inputs[0])
        links.new(nodes['CRFoam'].outputs[0], nodes['Mix'].inputs['Color2'])
        links.new(nodes['Attribute'].outputs['Fac'],
                  nodes['CRFoam'].inputs[0])
        links.new(nodes['CRWet'].outputs[0],
                  nodes['Mix'].inputs['Color1'])

        node = nodes.new('ShaderNodeMixRGB')  # RGB Mix für Noise 1
        node.location = (800, 1175)
        node.name = 'SubNoise1'
        node.blend_type = 'SUBTRACT'
        node.use_clamp = True
        node.inputs[0].default_value = 0.6

        # RGB mixshader für zweite Noise Texture
        node = nodes.new('ShaderNodeMixRGB')
        node.location = (1000, 975)
        node.name = 'SubNoise2'
        node.blend_type = 'SUBTRACT'
        node.use_clamp = True
        node.inputs[0].default_value = 0.6

        # link Add notes to Subtract
        links.new(nodes['Mix'].outputs['Color'],
                  nodes['SubNoise1'].inputs['Color1'])
        links.new(nodes['SubNoise1'].outputs['Color'],
                  nodes['SubNoise2'].inputs['Color1'])

        # Texture Coordinate für die Noise Textures
        #node = nodes.new('ShaderNodeTexCoord')
        # node.location = (000, 850)

        # moving foam ######################
        ####################################
        # bubblegroup textCoord
        node = nodes.new('ShaderNodeTexCoord')
        node.name = 'TexCoordBub'
        node.location = (-1200, 1800)

        node = nodes.new('ShaderNodeMapping')
        node.name = 'Map'
        node.location = (-800, 1800)

        ############################################
        ###############Driver stuff, rotation needed #################
        # value frame durch was
        #

        node = nodes.new('ShaderNodeValue')
        node.name = 'SpeedMoveWave'
        node.location = (-1400, 1300)

        source = node.outputs[0]
        target = bpy.context.scene
        prop = 'default_value'
        data_path = "frame_current"
        id_type = 'SCENE'
        driver = self.add_driver(source, target, prop,
                                 data_path, -1, func="0.0003*", id_type=id_type)

        # multiply with aligement factor driver
        node = nodes.new('ShaderNodeMath')
        node.name = 'AligmentDriver'
        node.operation = 'MULTIPLY'
        node.location = (-1200, 1300)

        source = node.inputs[1]
        target = bpy.context.object
        prop = 'default_value'
        data_path = 'modifiers["Ocean"].wave_alignment'
        id_type = 'OBJECT'
        driver = self.add_driver(source, target, prop,
                                 data_path, -1, func="", id_type=id_type)

        node = nodes.new('ShaderNodeCombineXYZ')
        node.name = 'MoveWaveCombXYZ'
        node.location = (-1000, 1300)

        node = nodes.new('ShaderNodeCombineXYZ')
        node.name = 'RotCombXYZ'
        node.location = (-1000, 1600)

        source = node.inputs[2]
        target = bpy.context.object
        prop = 'default_value'
        data_path = 'modifiers["Ocean"].wave_direction'
        id_type = 'OBJECT'
        driver = self.add_driver(source, target, prop,
                                 data_path, -1, func="", id_type=id_type)

        # link moving waves
        links.new(nodes['SpeedMoveWave'].outputs[0],
                  nodes['AligmentDriver'].inputs[0])
        links.new(nodes['AligmentDriver'].outputs[0],
                  nodes['MoveWaveCombXYZ'].inputs[0])
        links.new(nodes['MoveWaveCombXYZ'].outputs[0], nodes['Map'].inputs[1])
        links.new(nodes['RotCombXYZ'].outputs[0], nodes['Map'].inputs[2])

        links.new(nodes['TexCoordBub'].outputs['UV'],
                  nodes['Map'].inputs[0])

        # SHORTCUT
        nodes['Map'].name = 'Texture Coordinate'

        # Hue Saturation 000 für noise texture2
        node = nodes.new('ShaderNodeMapRange')
        node.location = (600, 1075)
        node.name = "MRNoise1"
        #    nodes["Hue Saturation Value"].inputs[2].default_value = 0.1
        node.inputs[4].default_value = 0.8
        #node.inputs['Saturation'].default_value = 0.0

        # noise texture (000)
        node = nodes.new('ShaderNodeTexNoise')
        node.location = (400, 1100)
        node.name = "Noise1"
        node.inputs['Scale'].default_value = 20
        node.inputs['Detail'].default_value = 5

       # noise texture (001)
        node = nodes.new('ShaderNodeTexNoise')  # mixshader machen
        node.location = (400, 900)
        node.name = "Noise2"
        nodes['Noise2'].inputs['Detail'].default_value = 5
        nodes['Noise2'].inputs['Scale'].default_value = 100
        # node = nodes.new('ShaderNodeTexCoord') ### mixshader machen
        # node.location = (000,150)
        # Hue Saturation 001 für noise texture2
        node = nodes.new('ShaderNodeMapRange')
        node.location = (600, 900)
        node.name = "MRNoise2"
        node.inputs[4].default_value = 1.0
        #node.inputs['Saturation'].default_value = 0.0

        links.new(nodes['Texture Coordinate'].outputs[0],
                  nodes['Noise1'].inputs['Vector'])
        links.new(nodes['Texture Coordinate'].outputs[0],
                  nodes['Noise2'].inputs['Vector'])
        links.new(nodes['Noise1'].outputs['Fac'],
                  nodes['MRNoise1'].inputs[0])
        links.new(nodes['Noise2'].outputs['Fac'],
                  nodes['MRNoise2'].inputs[0])
        links.new(nodes['MRNoise1'].outputs[0],
                  nodes['SubNoise1'].inputs['Color2'])
        links.new(nodes['MRNoise2'].outputs[0],
                  nodes['SubNoise2'].inputs['Color2'])

        # Voronoi bubble setup
        node = nodes.new('ShaderNodeTexVoronoi')
        node.location = (400, 675)
        nodes["Voronoi Texture"].inputs[1].default_value = 100
        node = nodes.new('ShaderNodeValToRGB')
        node.location = (600, 675)
        node.color_ramp.interpolation = 'B_SPLINE'
        node.color_ramp.elements[0].color = 1, 1, 1, 1
        node.color_ramp.elements[0].position = 0.3
        node.color_ramp.elements[1].color = 0, 0, 0, 1

        node = nodes.new('ShaderNodeTexVoronoi')
        node.location = (400, 450)
        nodes["Voronoi Texture.001"].inputs[1].default_value = 50
        node = nodes.new('ShaderNodeValToRGB')
        node.location = (600, 450)
        node.color_ramp.interpolation = 'B_SPLINE'
        node.color_ramp.elements[0].color = 1, 1, 1, 1
        node.color_ramp.elements[0].position = 0.3
        node.color_ramp.elements[1].color = 0, 0, 0, 1

        node = nodes.new('ShaderNodeTexVoronoi')
        node.location = (400, 200)
        nodes["Voronoi Texture.002"].inputs[1].default_value = 30
        node = nodes.new('ShaderNodeValToRGB')
        node.location = (600, 200)
        node.color_ramp.interpolation = 'B_SPLINE'
        node.color_ramp.elements[0].color = 1, 1, 1, 1
        node.color_ramp.elements[0].position = 0.3
        node.color_ramp.elements[1].color = 0, 0, 0, 1

        # voronoi scale
        # Bubble extra
        node = nodes.new('ShaderNodeValue')  # Multiplier für Displacement
        node.location = (000, 400)
        node.name = 'ScaleBub'
        node.outputs[0].default_value = 3000

        node = nodes.new('ShaderNodeMath')  # Multiplier für Displacement
        node.location = (200, 600)
        node.name = 'Math.004'
        node.operation = 'MULTIPLY'
        node.inputs[1].default_value = 2

        node = nodes.new('ShaderNodeMath')  # Multiplier für Displacement
        node.location = (200, 400)
        node.name = 'Math.005'
        node.operation = 'MULTIPLY'
        node.inputs[1].default_value = 1

        node = nodes.new('ShaderNodeMath')  # Multiplier für Displacement
        node.location = (200, 200)
        node.name = 'Math.006'
        node.operation = 'MULTIPLY'
        node.inputs[1].default_value = 0.5

        links.new(nodes['ScaleBub'].outputs['Value'],
                  nodes['Math.004'].inputs[0])
        links.new(nodes['ScaleBub'].outputs['Value'],
                  nodes['Math.005'].inputs[0])
        links.new(nodes['ScaleBub'].outputs['Value'],
                  nodes['Math.006'].inputs[0])

        links.new(nodes['Math.004'].outputs['Value'],
                  nodes['Voronoi Texture'].inputs['Scale'])
        links.new(nodes['Math.005'].outputs['Value'],
                  nodes['Voronoi Texture.001'].inputs['Scale'])
        links.new(nodes['Math.006'].outputs['Value'],
                  nodes['Voronoi Texture.002'].inputs['Scale'])
        # links.new(nodes['Mix.005'].outputs['Color'],
        #          nodes['Math.003'].inputs[0])

     # mix die bubbles zu einander und nutze die noise pattern als factor
        node = nodes.new('ShaderNodeMixRGB')
        node.location = (1400, 475)
        node.name = "Mix.003"
        node.blend_type = "LIGHTEN"

        node = nodes.new('ShaderNodeMixRGB')
        node.location = (1600, 275)
        node.name = "Mix.004"
        node.blend_type = "LIGHTEN"

     # bubble verteilung durch den factor mit less and grater than

        node = nodes.new('ShaderNodeMath')
        node.location = (1200, 675)
        node.name = "Greater1"
        node.operation = "GREATER_THAN"
        node.inputs[0].default_value = 0.1

        node = nodes.new('ShaderNodeMath')
        node.location = (1400, 725)
        node.name = "Greater2"
        node.operation = "GREATER_THAN"
        node.inputs[0].default_value = 0.2

        node = nodes.new('ShaderNodeMath')
        node.location = (1700, 725)
        node.name = "Multi1"
        node.operation = "MULTIPLY"
        node.inputs[1].default_value = 30
        node.use_clamp = True

        ####voronoi teil####################################
        links.new(nodes['Texture Coordinate'].outputs[0],
                  nodes['Voronoi Texture'].inputs['Vector'])
        links.new(nodes['Texture Coordinate'].outputs[0],
                  nodes['Voronoi Texture.001'].inputs['Vector'])
        links.new(nodes['Texture Coordinate'].outputs[0],
                  nodes['Voronoi Texture.002'].inputs['Vector'])

        links.new(nodes['Voronoi Texture'].outputs['Distance'],
                  nodes['ColorRamp'].inputs['Fac'])
        links.new(nodes['Voronoi Texture.001'].outputs['Distance'],
                  nodes['ColorRamp.001'].inputs['Fac'])
        links.new(nodes['Voronoi Texture.002'].outputs['Distance'],
                  nodes['ColorRamp.002'].inputs['Fac'])

        links.new(nodes['ColorRamp'].outputs['Color'],
                  nodes['Mix.003'].inputs['Color2'])
        links.new(nodes['ColorRamp.001'].outputs['Color'],
                  nodes['Mix.003'].inputs['Color1'])
        links.new(nodes['ColorRamp.002'].outputs['Color'],
                  nodes['Mix.004'].inputs['Color1'])
        links.new(nodes['Mix.003'].outputs['Color'],
                  nodes['Mix.004'].inputs['Color2'])

        # mix voronoi mit noise
        node = nodes.new('ShaderNodeMixRGB')
        node.location = (1800, 275)
        node.name = "Mix.005"
        node.blend_type = "MULTIPLY"
        node.inputs[0].default_value = 1.0
        node.use_clamp = True

        node = nodes.new('ShaderNodeDisplacement')
        node.location = (2000, 275)
        node.name = "Disp"

        links.new(nodes['Mix.004'].outputs['Color'],
                  nodes['Mix.005'].inputs['Color2'])
        links.new(nodes['SubNoise2'].outputs['Color'],
                  nodes['Greater1'].inputs[1])
        links.new(nodes['SubNoise2'].outputs['Color'],
                  nodes["Greater2"].inputs[1])
        links.new(nodes['SubNoise2'].outputs['Color'],
                  nodes['Multi1'].inputs[0])
        links.new(nodes['Greater1'].outputs[0], nodes['Mix.003'].inputs[0])
        links.new(nodes["Greater2"].outputs[0], nodes['Mix.004'].inputs[0])
        links.new(nodes["Multi1"].outputs[0], nodes['Mix.005'].inputs[1])
        links.new(nodes["Mix.005"].outputs[0], nodes['Disp'].inputs[0])

        # patchiness of foam
        # node = nodes.new('ShaderNodeValue')  # mixshader machen
        #node.location = (600, 1300)

        nodes['Mix.005'].name = "FoamFacOut"

    def FoamFac_legacy(self, node_tree):
        nodes = node_tree.nodes
        links = node_tree.links

        node = nodes.new('ShaderNodeAttribute')  # Attribute foam
        node.location = (-250, 1400)
        node.attribute_name = "foam"
        node = nodes.new('ShaderNodeGamma')  # gamma für wetmap
        node.location = (200, 1400)
        node.inputs[1].default_value = 0.3
        node.name = "CRFoam"

        node = nodes.new('ShaderNodeAttribute')  # attribute wetmap
        node.location = (-250, 1250)
        node.attribute_name = "dp_wetmap"
        node = nodes.new('ShaderNodeGamma')  # gamma für wetmap
        node.location = (200, 1250)
        #Gamma wert wetmap##########
        node.inputs[1].default_value = 5
        node.name = "CRWet"

        node = nodes.new('ShaderNodeMixRGB')  # rgb mixshader machen
        node.location = (400, 1275)
        node.blend_type = 'ADD'
        node.use_clamp = True
        node.inputs[0].default_value = 1.0

        # link Attribute notes additiv
        links.new(nodes['Attribute.001'].outputs['Fac'],
                  nodes['CRWet'].inputs[0])
        links.new(nodes['CRFoam'].outputs[0], nodes['Mix'].inputs['Color2'])
        links.new(nodes['Attribute'].outputs['Fac'],
                  nodes['CRFoam'].inputs[0])
        links.new(nodes['CRWet'].outputs[0],
                  nodes['Mix'].inputs['Color1'])

        node = nodes.new('ShaderNodeMixRGB')  # RGB Mix für Noise 1
        node.location = (800, 1175)
        node.blend_type = 'SUBTRACT'
        node.use_clamp = True
        node.inputs[0].default_value = 0.6

        # RGB mixshader für zweite Noise Texture
        node = nodes.new('ShaderNodeMixRGB')
        node.location = (1000, 975)
        node.blend_type = 'SUBTRACT'
        node.use_clamp = True
        node.inputs[0].default_value = 0.6

        # link Add notes to Subtract
        links.new(nodes['Mix'].outputs['Color'],
                  nodes['Mix.001'].inputs['Color1'])
        links.new(nodes['Mix.001'].outputs['Color'],
                  nodes['Mix.002'].inputs['Color1'])

        # noise texture (000)
        node = nodes.new('ShaderNodeTexNoise')  # mixshader machen
        node.location = (400, 1100)
        node.inputs['Scale'].default_value = 2
        node.inputs['Detail'].default_value = 5

        # Texture Coordinate für die Noise Textures
        node = nodes.new('ShaderNodeTexCoord')
        node.location = (000, 850)
        # Hue Saturation 000 für noise texture2
        node = nodes.new('ShaderNodeHueSaturation')
        node.location = (600, 1075)
        #    nodes["Hue Saturation Value"].inputs[2].default_value = 0.1
        node.inputs['Value'].default_value = 1.3
        node.inputs['Saturation'].default_value = 0.0

       # noise texture (001)
        node = nodes.new('ShaderNodeTexNoise')  # mixshader machen
        node.location = (400, 900)
        node.inputs['Detail'].default_value = 5
        node.inputs['Scale'].default_value = 10
        # node = nodes.new('ShaderNodeTexCoord') ### mixshader machen
        # node.location = (000,150)
        # Hue Saturation 001 für noise texture2
        node = nodes.new('ShaderNodeHueSaturation')
        node.location = (600, 900)
        node.inputs['Value'].default_value = 1.3
        node.inputs['Saturation'].default_value = 0.0

        links.new(nodes['Texture Coordinate'].outputs['Object'],
                  nodes['Noise Texture'].inputs['Vector'])
        links.new(nodes['Texture Coordinate'].outputs['Object'],
                  nodes['Noise Texture.001'].inputs['Vector'])
        links.new(nodes['Noise Texture'].outputs['Fac'],
                  nodes['Hue Saturation Value'].inputs['Color'])
        links.new(nodes['Noise Texture.001'].outputs['Fac'],
                  nodes['Hue Saturation Value.001'].inputs['Color'])
        links.new(nodes['Hue Saturation Value'].outputs['Color'],
                  nodes['Mix.001'].inputs['Color2'])
        links.new(nodes['Hue Saturation Value.001'].outputs['Color'],
                  nodes['Mix.002'].inputs['Color2'])

        # BubblesizeMultiplier
        node = nodes.new('ShaderNodeValue')
        node.name = "Value.002"
        node.location = (000, 400)
        nodes['Value.002'].outputs[0].default_value = 100

        node = nodes.new('ShaderNodeMath')  # Multiplier für Displacement
        node.location = (200, 600)
        node.name = "Math.004"
        nodes['Math.004'].operation = 'MULTIPLY'
        nodes['Math.004'].inputs[1].default_value = 2

        node = nodes.new('ShaderNodeMath')  # Multiplier für Displacement
        node.location = (200, 400)
        node.name = "Math.005"
        nodes['Math.005'].operation = 'MULTIPLY'
        nodes['Math.005'].inputs[1].default_value = 1

        node = nodes.new('ShaderNodeMath')  # Multiplier für Displacement
        node.location = (200, 200)
        node.name = "Math.006"
        nodes['Math.006'].operation = 'MULTIPLY'
        nodes['Math.006'].inputs[1].default_value = 0.5

        links.new(nodes['Value.002'].outputs['Value'],
                  nodes['Math.004'].inputs[0])
        links.new(nodes['Value.002'].outputs['Value'],
                  nodes['Math.005'].inputs[0])
        links.new(nodes['Value.002'].outputs['Value'],
                  nodes['Math.006'].inputs[0])

        # Voronoi bubble setup
        node = nodes.new('ShaderNodeTexVoronoi')
        node.location = (400, 675)
        nodes["Voronoi Texture"].inputs[1].default_value = 100
        node = nodes.new('ShaderNodeValToRGB')
        node.location = (600, 675)
        node.color_ramp.interpolation = 'B_SPLINE'
        node.color_ramp.elements[0].color = 1, 1, 1, 1
        node.color_ramp.elements[0].position = 0.3
        node.color_ramp.elements[1].color = 0, 0, 0, 1

        node = nodes.new('ShaderNodeTexVoronoi')
        node.location = (400, 450)
        nodes["Voronoi Texture.001"].inputs[1].default_value = 50
        node = nodes.new('ShaderNodeValToRGB')
        node.location = (600, 450)
        node.color_ramp.interpolation = 'B_SPLINE'
        node.color_ramp.elements[0].color = 1, 1, 1, 1
        node.color_ramp.elements[0].position = 0.3
        node.color_ramp.elements[1].color = 0, 0, 0, 1

        node = nodes.new('ShaderNodeTexVoronoi')
        node.location = (400, 200)
        nodes["Voronoi Texture.002"].inputs[1].default_value = 30
        node = nodes.new('ShaderNodeValToRGB')
        node.location = (600, 200)
        node.color_ramp.interpolation = 'B_SPLINE'
        node.color_ramp.elements[0].color = 1, 1, 1, 1
        node.color_ramp.elements[0].position = 0.3
        node.color_ramp.elements[1].color = 0, 0, 0, 1

        links.new(nodes['Math.004'].outputs['Value'],
                  nodes['Voronoi Texture'].inputs['Scale'])
        links.new(nodes['Math.005'].outputs['Value'],
                  nodes['Voronoi Texture.001'].inputs['Scale'])
        links.new(nodes['Math.006'].outputs['Value'],
                  nodes['Voronoi Texture.002'].inputs['Scale'])
        # links.new(nodes['Math.005'].outputs['Color'],
        #          nodes['Math.003'].inputs[0])

     # mix die bubbles zu einander und nutze die noise pattern als factor
        node = nodes.new('ShaderNodeMixRGB')
        node.location = (1400, 475)
        node.blend_type = "LIGHTEN"

        node = nodes.new('ShaderNodeMixRGB')
        node.location = (1600, 275)
        node.blend_type = "LIGHTEN"

     # bubble verteilung durch den factor mit less and grater than

        node = nodes.new('ShaderNodeMath')
        node.location = (1200, 675)
        node.operation = "GREATER_THAN"
        node.inputs[0].default_value = 0.1

        node = nodes.new('ShaderNodeMath')
        node.location = (1400, 725)
        node.operation = "GREATER_THAN"
        node.inputs[0].default_value = 0.2

        node = nodes.new('ShaderNodeMath')
        node.location = (1700, 725)
        node.operation = "MULTIPLY"
        node.inputs[1].default_value = 30
        node.use_clamp = True

        ####voronoi teil####################################
        links.new(nodes['Texture Coordinate'].outputs['Object'],
                  nodes['Voronoi Texture'].inputs['Vector'])
        links.new(nodes['Texture Coordinate'].outputs['Object'],
                  nodes['Voronoi Texture.001'].inputs['Vector'])
        links.new(nodes['Texture Coordinate'].outputs['Object'],
                  nodes['Voronoi Texture.002'].inputs['Vector'])

        links.new(nodes['Voronoi Texture'].outputs['Distance'],
                  nodes['ColorRamp'].inputs['Fac'])
        links.new(nodes['Voronoi Texture.001'].outputs['Distance'],
                  nodes['ColorRamp.001'].inputs['Fac'])
        links.new(nodes['Voronoi Texture.002'].outputs['Distance'],
                  nodes['ColorRamp.002'].inputs['Fac'])

        links.new(nodes['ColorRamp'].outputs['Color'],
                  nodes['Mix.003'].inputs['Color2'])
        links.new(nodes['ColorRamp.001'].outputs['Color'],
                  nodes['Mix.003'].inputs['Color1'])
        links.new(nodes['ColorRamp.002'].outputs['Color'],
                  nodes['Mix.004'].inputs['Color1'])
        links.new(nodes['Mix.003'].outputs['Color'],
                  nodes['Mix.004'].inputs['Color2'])

        # mix voronoi mit noise
        node = nodes.new('ShaderNodeMixRGB')
        node.name = "Mix.005"
        node.location = (1800, 275)
        node.blend_type = "MULTIPLY"
        node.inputs[0].default_value = 1.0
        node.use_clamp = True

        node = nodes.new('ShaderNodeDisplacement')
        node.location = (2100, 275)
        node.name = 'Disp'

        links.new(nodes['Mix.004'].outputs['Color'],
                  nodes['Mix.005'].inputs['Color2'])
        links.new(nodes['Mix.002'].outputs['Color'], nodes['Math'].inputs[1])
        links.new(nodes['Mix.002'].outputs['Color'],
                  nodes['Math.001'].inputs[1])
        links.new(nodes['Mix.002'].outputs['Color'],
                  nodes['Math.002'].inputs[0])
        links.new(nodes['Math'].outputs[0], nodes['Mix.003'].inputs[0])
        links.new(nodes['Math.001'].outputs[0], nodes['Mix.004'].inputs[0])

        links.new(nodes['Math.002'].outputs[0], nodes['Mix.005'].inputs[1])
        links.new(nodes['Mix.005'].outputs[0], nodes['Disp'].inputs[1])

        # patchiness of foam
        # node = nodes.new('ShaderNodeValue')  # mixshader machen
        #node.location = (600, 1300)

        nodes['Mix.005'].name = "FoamFacOut"

        nodes['Noise Texture'].name = 'Noise1'
        nodes['Noise Texture.001'].name = 'Noise2'

    def FoamFac_legacy_improve_TransBub(self, node_tree):
        nodes = node_tree.nodes
        links = node_tree.links

        node = nodes.new('ShaderNodeMapRange')
        node.location = (1800, 000)
        node.name = "MPInvertBubs"
        node.inputs[2].default_value = 0.9
        node.inputs[3].default_value = 3.7
        node.inputs[4].default_value = 0.0

        node = nodes.new('ShaderNodeMixRGB')
        node.location = (2100, 275)
        #node.inputs[1].default_value = 0.3
        node.name = "AddBase"
        node.blend_type = 'ADD'

        node = nodes.new('ShaderNodeMixRGB')
        node.location = (2400, 275)
        node.inputs[0].default_value = 1
        node.name = "MultiInvertBub"
        node.blend_type = 'MULTIPLY'

        links.new(nodes["Multi1"].outputs[0], nodes['AddBase'].inputs[2])
        links.new(nodes["FoamFacOut"].outputs[0], nodes['AddBase'].inputs[1])
        links.new(nodes["AddBase"].outputs[0],
                  nodes['MultiInvertBub'].inputs[1])
        links.new(nodes["Mix.004"].outputs[0],
                  nodes['MPInvertBubs'].inputs[0])
        links.new(nodes["MPInvertBubs"].outputs[0],
                  nodes['MultiInvertBub'].inputs[2])

        nodes['FoamFacOut'].name = 'FoamMatInfo'
        nodes['MultiInvertBub'].name = 'FoamFacOut'

    def constructor_legacy_improve(self, node_tree):
        print('legacy')
        nodes = node_tree.nodes
        links = node_tree.links

        links.new(nodes['FoamFacOut'].outputs[0], nodes['MainMix'].inputs[0])
        links.new(nodes['OceanOut'].outputs[0], nodes['MainMix'].inputs[1])
        links.new(nodes['FoamOut'].outputs[0], nodes['MainMix'].inputs[2])

        # pathchiness
        links.new(nodes['Patchiness'].outputs[0], nodes['SubNoise1'].inputs[0])
        links.new(nodes['Patchiness'].outputs[0], nodes['SubNoise2'].inputs[0])

        links.new(nodes['LowerOceanFoam_Log'].outputs[0],
                  nodes['CRFoam'].inputs[1])
        links.new(nodes['FoamBaseStrength'].outputs[0],
                  nodes['CRFoam'].inputs[4])

        links.new(nodes['LowerObjectCut'].outputs[0],
                  nodes['CRWet'].inputs[1])
        links.new(nodes['ObjectBaseStrength'].outputs[0],
                  nodes['CRWet'].inputs[4])

        links.new(nodes['DisplStrength'].outputs[0],
                  nodes['Disp'].inputs[2])

        links.new(nodes['Disp'].outputs[0],
                  nodes['MaterialOutCycles'].inputs[2])
        links.new(nodes['Disp'].outputs[0],
                  nodes['MaterialOutEevee'].inputs[2])

        # foam mat ctl
        links.new(nodes['FoamFacOut'].outputs[0],
                  nodes['CRFoamRough'].inputs[0])
        links.new(nodes['FoamFacOut'].outputs[0],
                  nodes['CRFoamTransmission'].inputs[0])

        links.new(nodes['FoamFacOut'].outputs[0],
                  nodes['MRSubsurface'].inputs[0])
        links.new(nodes['MRSubsurface'].outputs[0],
                  nodes['FoamOut'].inputs['Subsurface'])
        links.new(nodes['FoamFacOut'].outputs[0],
                  nodes['FoamBump'].inputs[2])

        links.new(nodes['CRFoamRough'].outputs[0],
                  nodes['FoamOut'].inputs['Roughness'])
        links.new(nodes['CRFoamTransmission'].outputs[0],
                  nodes['FoamOut'].inputs['Transmission'])

        links.new(nodes['FoamBump'].outputs[0],
                  nodes['FoamOut'].inputs['Normal'])
        links.new(nodes['FoamFacOut'].outputs[0],
                  nodes['FoamBump'].inputs['Height'])
        links.new(nodes['FoamBump'].outputs[0],
                  nodes['FoamOut'].inputs['Normal'])

        links.new(nodes['FoamSubsurf'].outputs[0],
                  nodes['MRSubsurface'].inputs[4])

        links.new(nodes['FoamColor'].outputs[0],
                  nodes['FoamOut'].inputs[0])
        links.new(nodes['FoamColor'].outputs[0],
                  nodes['FoamOut'].inputs[3])

        links.new(nodes['FoamRoughness'].outputs[0],
                  nodes['CRFoamRough'].inputs[4])
        links.new(nodes['FoamTransmission'].outputs[0],
                  nodes['CRFoamTransmission'].inputs[4])
        links.new(nodes['FoamBumpCtl'].outputs[0],
                  nodes['FoamBump'].inputs[0])

        links.new(nodes['NoiseScale'].outputs[0],
                  nodes['Noise1'].inputs['Scale'])
        links.new(nodes['NoiseScale'].outputs[0],
                  nodes['MultiNoiseScale'].inputs[0])
        links.new(nodes['MultiNoiseScale'].outputs[0],
                  nodes['Noise2'].inputs['Scale'])

        nodes['LowerOceanFoamCut'].outputs[0].default_value = 0.2

    def constructor_wet2(self, node_tree):
        print('legacy')
        nodes = node_tree.nodes
        links = node_tree.links

        links.new(nodes['FoamFacOut'].outputs[0], nodes['MainMix'].inputs[0])
        links.new(nodes['OceanOut'].outputs[0], nodes['MainMix'].inputs[1])
        links.new(nodes['FoamOut'].outputs[0], nodes['MainMix'].inputs[2])

        # pathchiness
        #links.new(nodes['Patchiness'].outputs[0], nodes['SubNoise1'].inputs[0])
        links.new(nodes['Patchiness'].outputs[0], nodes['SubNoise2'].inputs[0])

        links.new(nodes['LowerOceanFoam_Log'].outputs[0],
                  nodes['CRFoam'].inputs[1])
        links.new(nodes['FoamBaseStrength'].outputs[0],
                  nodes['CRFoam'].inputs[4])

        links.new(nodes['LowerObjectCut'].outputs[0],
                  nodes['CRWet'].inputs[1])
        links.new(nodes['ObjectBaseStrength'].outputs[0],
                  nodes['CRWet'].inputs[4])

        # links.new(nodes['Patchiness'].outputs[0],
        #          nodes['SubNoise1'].inputs[0])
        # links.new(nodes['Patchiness'].outputs[0],
        #          nodes['SubNoise2'].inputs[0])
        links.new(nodes['DisplStrength'].outputs[0],
                  nodes['Disp'].inputs[2])

        links.new(nodes['Disp'].outputs[0],
                  nodes['MaterialOutCycles'].inputs[2])
        links.new(nodes['Disp'].outputs[0],
                  nodes['MaterialOutEevee'].inputs[2])

        # foam mat ctl
        links.new(nodes['FoamMatInfo'].outputs[0],
                  nodes['CRFoamRough'].inputs[0])
        links.new(nodes['FoamMatInfo'].outputs[0],
                  nodes['CRFoamTransmission'].inputs[0])

        links.new(nodes['FoamMatInfo'].outputs[0],
                  nodes['MRSubsurface'].inputs[0])
        links.new(nodes['MRSubsurface'].outputs[0],
                  nodes['FoamOut'].inputs['Subsurface'])
        links.new(nodes['FoamMatInfo'].outputs[0],
                  nodes['FoamBump'].inputs[2])

        links.new(nodes['CRFoamRough'].outputs[0],
                  nodes['FoamOut'].inputs['Roughness'])
        links.new(nodes['CRFoamTransmission'].outputs[0],
                  nodes['FoamOut'].inputs['Transmission'])

        links.new(nodes['FoamBump'].outputs[0],
                  nodes['FoamOut'].inputs['Normal'])
        links.new(nodes['FoamMatInfo'].outputs[0],
                  nodes['FoamBump'].inputs['Height'])
        links.new(nodes['FoamBump'].outputs[0],
                  nodes['FoamOut'].inputs['Normal'])

        links.new(nodes['FoamSubsurf'].outputs[0],
                  nodes['MRSubsurface'].inputs[4])

        links.new(nodes['FoamColor'].outputs[0],
                  nodes['FoamOut'].inputs[0])
        links.new(nodes['FoamColor'].outputs[0],
                  nodes['FoamOut'].inputs[3])

        links.new(nodes['FoamRoughness'].outputs[0],
                  nodes['CRFoamRough'].inputs[4])
        links.new(nodes['FoamTransmission'].outputs[0],
                  nodes['CRFoamTransmission'].inputs[4])
        links.new(nodes['FoamBumpCtl'].outputs[0],
                  nodes['FoamBump'].inputs[0])

        links.new(nodes['NoiseScale'].outputs[0],
                  nodes['Noise1'].inputs['Scale'])
        links.new(nodes['NoiseScale'].outputs[0],
                  nodes['MultiNoiseScale'].inputs[0])
        links.new(nodes['MultiNoiseScale'].outputs[0],
                  nodes['Noise2'].inputs['Scale'])

        nodes['LowerOceanFoamCut'].outputs[0].default_value = 0.2

    def constructor_legacy(self, node_tree):
        print('legacy')
        nodes = node_tree.nodes
        links = node_tree.links

        links.new(nodes['FoamFacOut'].outputs[0], nodes['MainMix'].inputs[0])
        links.new(nodes['OceanOut'].outputs[0], nodes['MainMix'].inputs[1])
        links.new(nodes['FoamOut'].outputs[0], nodes['MainMix'].inputs[2])

        # pathchiness
        links.new(nodes['Patchiness'].outputs[0], nodes['Mix.001'].inputs[0])
        links.new(nodes['Patchiness'].outputs[0], nodes['Mix.002'].inputs[0])

        links.new(nodes['Disp'].outputs[0],
                  nodes['MaterialOutCycles'].inputs[2])
        links.new(nodes['Disp'].outputs[0],
                  nodes['MaterialOutEevee'].inputs[2])

        links.new(nodes['FoamSubsurf'].outputs[0], nodes['FoamOut'].inputs[1])
        links.new(nodes['FoamColor'].outputs[0], nodes['FoamOut'].inputs[0])
        links.new(nodes['FoamColor'].outputs[0], nodes['FoamOut'].inputs[3])
        links.new(nodes['FoamRoughness'].outputs[0],
                  nodes['FoamOut'].inputs[7])
        links.new(nodes['FoamTransmission'].outputs[0],
                  nodes['FoamOut'].inputs[15])
        links.new(nodes['FoamBumpCtl'].outputs[0],
                  nodes['FoamBump'].inputs['Height'])
        links.new(nodes['FoamBump'].outputs[0],
                  nodes['FoamOut'].inputs['Normal'])

        links.new(nodes['LowerOceanFoam_Log'].outputs[0],
                  nodes['CRFoam'].inputs[1])
        links.new(nodes['LowerObjectCut'].outputs[0], nodes['CRWet'].inputs[1])

        links.new(nodes['DisplStrength'].outputs[0],
                  nodes['Disp'].inputs['Scale'])

        links.new(nodes['NoiseScale'].outputs[0],
                  nodes['Noise1'].inputs['Scale'])
        links.new(nodes['NoiseScale'].outputs[0],
                  nodes['MultiNoiseScale'].inputs[0])
        links.new(nodes['MultiNoiseScale'].outputs[0],
                  nodes['Noise2'].inputs['Scale'])

        nodes['Math.002'].name = 'BubbleNoiseThreshold'

        nodes['LowerOceanFoamCut'].outputs[0].default_value = 1.6
        nodes['LowerObjectCut'].outputs[0].default_value = 3.4
        nodes['Patchiness'].outputs[0].default_value = 0.2
        nodes['NoiseScale'].outputs[0].default_value = 2

    def constructor_30(self, node_tree):
        nodes = node_tree.nodes
        links = node_tree.links

        # main controll
        links.new(nodes['FoamFacOut'].outputs[0], nodes['MainMix'].inputs[0])
        links.new(nodes['OceanOut'].outputs[0], nodes['MainMix'].inputs[1])
        links.new(nodes['FoamOut'].outputs[0], nodes['MainMix'].inputs[2])

        # foam material
        links.new(nodes['FoamMatInfo'].outputs[0],
                  nodes['CRFoamRough'].inputs[0])
        links.new(nodes['FoamMatInfo'].outputs[0],
                  nodes['CRFoamTransmission'].inputs[0])

        links.new(nodes['FoamMatInfo'].outputs[0],
                  nodes['MRSubsurface'].inputs[0])
        links.new(nodes['MRSubsurface'].outputs[0],
                  nodes['FoamOut'].inputs['Subsurface'])
        links.new(nodes['FoamMatInfo'].outputs[0],
                  nodes['FoamBump'].inputs[2])

        links.new(nodes['CRFoamRough'].outputs[0],
                  nodes['FoamOut'].inputs['Roughness'])
        links.new(nodes['CRFoamTransmission'].outputs[0],
                  nodes['FoamOut'].inputs['Transmission'])

        links.new(nodes['FoamBump'].outputs[0],
                  nodes['FoamOut'].inputs['Normal'])

        links.new(nodes['Disp'].outputs[0],
                  nodes['MaterialOutEevee'].inputs[2])
        links.new(nodes['Disp'].outputs[0],
                  nodes['MaterialOutCycles'].inputs[2])

        # link foam ctl
        links.new(nodes['FoamSubsurf'].outputs[0],
                  nodes['MRSubsurface'].inputs[4])

        links.new(nodes['FoamColor'].outputs[0],
                  nodes['FoamOut'].inputs[0])
        links.new(nodes['FoamColor'].outputs[0],
                  nodes['FoamOut'].inputs[3])

        links.new(nodes['FoamRoughness'].outputs[0],
                  nodes['CRFoamRough'].inputs[4])
        links.new(nodes['FoamTransmission'].outputs[0],
                  nodes['CRFoamTransmission'].inputs[4])
        links.new(nodes['FoamBumpCtl'].outputs[0],
                  nodes['FoamBump'].inputs[0])

        # link foam fac ctl
        links.new(nodes['LowerOceanFoam_Log'].outputs[0],
                  nodes['CRFoam'].inputs[1])
        links.new(nodes['FoamBaseStrength'].outputs[0],
                  nodes['CRFoam'].inputs[4])

        links.new(nodes['LowerObjectCut'].outputs[0],
                  nodes['CRWet'].inputs[1])
        links.new(nodes['ObjectBaseStrength'].outputs[0],
                  nodes['CRWet'].inputs[4])

        links.new(nodes['Patchiness'].outputs[0],
                  nodes['SubNoise1'].inputs[0])
        links.new(nodes['Patchiness'].outputs[0],
                  nodes['SubNoise2'].inputs[0])
        links.new(nodes['DisplStrength'].outputs[0],
                  nodes['Disp'].inputs[2])

        links.new(nodes['NoiseScale'].outputs[0],
                  nodes['Noise1'].inputs['Scale'])
        links.new(nodes['NoiseScale'].outputs[0],
                  nodes['MultiNoiseScale'].inputs[0])
        links.new(nodes['MultiNoiseScale'].outputs[0],
                  nodes['Noise2'].inputs['Scale'])

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

    def label_nodes(self, node_tree):

        nodes = node_tree.nodes

        for node in nodes:
            node.label = node.name
