import bpy


class AOMMatHandler:

    def __init__(self, context):
        self.context = context
        self.material = self.get_material()

        self.materialname = "AdvOceanMat"

    def get_material(self):
        mat = bpy.data.materials.get("AdvOceanMat")
        if mat is None:
            # create material
            mat = bpy.data.materials.new(name="AdvOceanMat")

        return mat

    def del_nodes(self):
        nodes = self.material.node_tree.nodes
        for node in nodes:
            nodes.remove(node)

    def make_material(self, ob):

        self.handle_materialslots(ob)
        node_tree = self.material.node_tree

        if self.context.scene.aom_props.MaterialSel == '1':
            self.del_nodes()
            self.water_28(node_tree)
            self.foam_material_30(node_tree)
            self.FoamFac_bubbly(node_tree)
            self.constructor_30(node_tree)

        elif self.context.scene.aom_props.MaterialSel == '2':
            self.del_nodes()
            self.water_28(node_tree)
            self.foam_material_30(node_tree)
            self.FoamFac_legacy(node_tree)
            self.constructor_legacy(node_tree)

    def handle_materialslots(self, ob):

        if ob.data.materials:
            # assign to 1st material slot
            ob.data.materials[0] = self.material
        else:
            #  no slots
            ob.data.materials.append(self.material)

        self.context.object.active_material.use_nodes = True

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
                  nodes['Mix Shader.002'].inputs[1])
        links.new(nodes['Transparent BSDF'].outputs['BSDF'],
                  nodes['Mix Shader.002'].inputs[2])
        links.new(nodes['Layer Weight.002'].outputs['Fresnel'],
                  nodes['Mix Shader.002'].inputs[0])

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

    def foam_material_30(self, node_tree):
        nodes = node_tree.nodes
        links = node_tree.links

        # Foam material

        # principled shader basis für foam
        node = nodes.new('ShaderNodeBsdfPrincipled')
        node.location = (200, -700)
        nodes['Principled BSDF'].inputs[0].default_value = (1.8, 1.8, 1.8, 1)
        nodes['Principled BSDF'].inputs[15].default_value = 0.2
        nodes['Principled BSDF'].inputs[7].default_value = 0.2
        node = nodes.new('ShaderNodeBump')  # principled shader basis für foam
        node.location = (000, -900)
        node.inputs[0].default_value = 0.5

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
        node.color_ramp.elements[0].color = 1, 1, 1, 1
        node.color_ramp.elements[0].position = 0.3
        node.color_ramp.elements[1].color = 0, 0, 0, 1

        node = nodes.new('ShaderNodeMapRange')
        node.location = (400, 950)

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
        links.new(nodes['Group Input'].outputs[3],
                  nodes['Map Range'].inputs[3])

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
        links.new(nodes['Math.004'].outputs[0], nodes['Map Range'].inputs[3])

        group_inputs = ng.nodes.new('NodeGroupOutput')
        group_inputs.location = (1250, 0)
        ng.outputs.new('NodeSocketColor', 'SoftShape')
        ng.outputs.new('NodeSocketColor', 'HardShape')

        links.new(nodes['Map Range'].outputs[0],
                  nodes['Group Output'].inputs[0])
        links.new(nodes['Math.002'].outputs[0],
                  nodes['Group Output'].inputs[1])

        return ng

    def FoamFac_bubbly(self, node_tree):
        nodes = node_tree.nodes
        links = node_tree.links

        node = nodes.new('ShaderNodeAttribute')  # Attribute foam
        node.name = "Foam"
        node.location = (-250, 2600)
        node.attribute_name = "foam"
        # node = nodes.new('ShaderNodeGamma')  # gamma für wetmap
        #node.location = (200, 1400)
        #nodes["Gamma"].inputs[1].default_value = 0.3
        node = nodes.new('ShaderNodeValToRGB')
        node.name = "CRFoam"
        node.location = (000, 2700)
        node.color_ramp.interpolation = 'B_SPLINE'
        #node.color_ramp.elements[1].color = 1, 1, 1, 1
        node.color_ramp.elements[1].position = 0.74
        #node.color_ramp.elements[1].color = 0, 0, 0, 1

        node = nodes.new('ShaderNodeAttribute')  # attribute wetmap
        node.name = "Wet"
        node.location = (-250, 2450)
        node.attribute_name = "dp_wetmap"

        node = nodes.new('ShaderNodeValToRGB')
        node.name = "CRWet"
        node.location = (000, 2450)
        node.color_ramp.interpolation = 'B_SPLINE'
        #node.color_ramp.elements[1].color = 1, 1, 1, 1
        node.color_ramp.elements[0].position = 0.5
        #node.color_ramp.elements[1].color = 0, 0, 0, 1

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
        node.blend_type = 'SUBTRACT'
        node.use_clamp = True
        node.inputs[0].default_value = 0.6

        # RGB mixshader für zweite Noise Texture
        node = nodes.new('ShaderNodeMixRGB')
        node.name = "SubNoise2"
        node.location = (1000, 2175)
        node.blend_type = 'SUBTRACT'
        node.use_clamp = True
        node.inputs[0].default_value = 0.6

        # link Add notes to Subtract
        links.new(nodes['MixFoamWet'].outputs['Color'],
                  nodes['SubNoise1'].inputs['Color1'])
        links.new(nodes['SubNoise1'].outputs['Color'],
                  nodes['SubNoise2'].inputs['Color1'])

        # noise texture (000)
        node = nodes.new('ShaderNodeTexNoise')  # mixshader machen
        node.name = 'Noise1'
        node.location = (400, 2300)
        node.inputs['Scale'].default_value = 2
        node.inputs['Detail'].default_value = 5

        # Texture Coordinate für die Noise Textures
        node = nodes.new('ShaderNodeTexCoord')
        node.name = 'TexCoordNoise'
        node.location = (000, 2350)
        # Hue Saturation 000 für noise texture2
        node = nodes.new('ShaderNodeHueSaturation')
        node.name = 'Hue1'
        node.location = (600, 2275)
        #    nodes["Hue Saturation Value"].inputs[2].default_value = 0.1
        node.inputs['Value'].default_value = 1.3
        node.inputs['Saturation'].default_value = 0.0

        # noise texture (001)
        node = nodes.new('ShaderNodeTexNoise')
        node.name = 'Noise2'
        node.location = (400, 2100)
        node.inputs['Detail'].default_value = 5
        node.inputs['Scale'].default_value = 10
        # node = nodes.new('ShaderNodeTexCoord') ### mixshader machen
        # node.location = (000,150)
        # Hue Saturation 001 für noise texture2
        node = nodes.new('ShaderNodeHueSaturation')
        node.name = 'Hue2'
        node.location = (600, 2100)
        node.inputs['Value'].default_value = 1.3
        node.inputs['Saturation'].default_value = 0.0

        links.new(nodes['TexCoordNoise'].outputs['Object'],
                  nodes['Noise1'].inputs['Vector'])
        links.new(nodes['TexCoordNoise'].outputs['Object'],
                  nodes['Noise2'].inputs['Vector'])
        links.new(nodes['Noise1'].outputs['Fac'],
                  nodes['Hue1'].inputs['Color'])
        links.new(nodes['Noise2'].outputs['Fac'],
                  nodes['Hue2'].inputs['Color'])
        links.new(nodes['Hue1'].outputs['Color'],
                  nodes['SubNoise1'].inputs['Color2'])
        links.new(nodes['Hue2'].outputs['Color'],
                  nodes['SubNoise2'].inputs['Color2'])

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
        node = nodes.new('ShaderNodeValue')
        node.name = 'SpeedMoveWave'
        node.location = (-1400, 1300)

        # multiply with aligement factor driver
        node = nodes.new('ShaderNodeMath')
        node.name = 'AligmentDriver'
        node.location = (-1200, 1300)

        node = nodes.new('ShaderNodeCombineXYZ')
        node.name = 'MoveWaveCombXYZ'
        node.location = (-1000, 1300)

        # link moving waves
        links.new(nodes['SpeedMoveWave'].outputs[0],
                  nodes['AligmentDriver'].inputs[0])
        links.new(nodes['AligmentDriver'].outputs[0],
                  nodes['MoveWaveCombXYZ'].inputs[0])
        links.new(nodes['MoveWaveCombXYZ'].outputs[0], nodes['Map'].inputs[1])

        links.new(nodes['TexCoordBub'].outputs[0], nodes['Map'].inputs[0])

        #####################################
        #####################################

        BubNG = self.get_BubbleNodeGroup()

        # bubble group 1
        node = nodes.new('ShaderNodeGroup')
        node.node_tree = BubNG
        node.name = 'Bub1'
        node.location = (-000, 1800)

        # bubble group 2
        node = nodes.new('ShaderNodeGroup')
        node.name = 'Bub2'
        node.node_tree = BubNG
        node.location = (-000, 1500)

        # bubble group 3
        node = nodes.new('ShaderNodeGroup')
        node.name = 'Bub3'
        node.node_tree = BubNG
        node.location = (-000, 1200)

        # bubble group 4
        node = nodes.new('ShaderNodeGroup')
        node.name = 'Bub4'
        node.node_tree = BubNG
        node.location = (-000, 900)

        # link to maping
        links.new(nodes['Map'].outputs[0], nodes['Bub1'].inputs[0])
        links.new(nodes['Map'].outputs[0], nodes['Bub2'].inputs[0])
        links.new(nodes['Map'].outputs[0], nodes['Bub3'].inputs[0])
        links.new(nodes['Map'].outputs[0], nodes['Bub4'].inputs[0])

        # BubbleScale value
        node = nodes.new('ShaderNodeValue')
        node.name = 'ScaleBub'
        node.location = (-600, 1500)
        node.outputs[0].default_value = 440

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

        links.new(nodes['ScaleMulti2'].outputs[0], nodes['Bub2'].inputs[0])
        links.new(nodes['ScaleMulti3'].outputs[0], nodes['Bub3'].inputs[0])
        links.new(nodes['ScaleMulti4'].outputs[0], nodes['Bub4'].inputs[0])

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

        ###mix to bubble factor ########
        node = nodes.new('ShaderNodeMixRGB')
        node.name = "MixBub"
        node.location = (900, 1800)

        node = nodes.new('ShaderNodeMixRGB')
        node.name = "MixBubNoise"
        node.location = (1200, 1500)
        node.blend_type = 'MULTIPLY'

        node = nodes.new('ShaderNodeDisplacement')
        node.name = "Disp"
        node.location = (1500, 1500)

        links.new(nodes['Bub1'].outputs[1], nodes['max1bub'].inputs[0])
        links.new(nodes['Bub1'].outputs[0], nodes['max3bub'].inputs[0])

        links.new(nodes['Bub2'].outputs[1], nodes['max1bub'].inputs[1])
        links.new(nodes['Bub2'].outputs[0], nodes['max2bub'].inputs[0])

        links.new(nodes['Bub3'].outputs[0], nodes['max2bub'].inputs[1])
        links.new(nodes['Bub4'].outputs[0], nodes['max4bub'].inputs[1])
        links.new(nodes['max2bub'].outputs[0], nodes['max4bub'].inputs[0])

        links.new(nodes['max4bub'].outputs[0], nodes['MixBub'].inputs[1])
        links.new(nodes['max3bub'].outputs[0], nodes['MixBub'].inputs[2])

        # mix noise and bubbles
        links.new(nodes['MixBub'].outputs[0], nodes['MixBubNoise'].inputs[1])
        links.new(nodes['SubNoise2'].outputs[0],
                  nodes['MixBubNoise'].inputs[2])

        # too main mix
        #links.new(nodes['MixBubNoise'].outputs[0], nodes['MainMix'].inputs[0])
        links.new(nodes['MixBubNoise'].outputs[0], nodes['Disp'].inputs[0])

    def FoamFac_legacy(self, node_tree):
        nodes = node_tree.nodes
        links = node_tree.links

        node = nodes.new('ShaderNodeAttribute')  # Attribute foam
        node.location = (-250, 1400)
        nodes['Attribute'].attribute_name = "foam"
        # node = nodes.new('ShaderNodeGamma')  # gamma für wetmap
        #node.location = (200, 1400)
        #nodes["Gamma"].inputs[1].default_value = 0.3
        node = nodes.new('ShaderNodeValToRGB')
        node.name = "CRFoam"
        node.location = (000, 1500)
        node.color_ramp.interpolation = 'B_SPLINE'
        #node.color_ramp.elements[1].color = 1, 1, 1, 1
        node.color_ramp.elements[1].position = 0.74
        #node.color_ramp.elements[1].color = 0, 0, 0, 1

        node = nodes.new('ShaderNodeAttribute')  # attribute wetmap
        node.location = (-250, 1250)
        nodes['Attribute.001'].attribute_name = "dp_wetmap"
        # node = nodes.new('ShaderNodeGamma')  # gamma für wetmap
        #node.location = (200, 1250)
        # Gamma wert wetmap##########
        #nodes["Gamma.001"].inputs[1].default_value = 5
        node = nodes.new('ShaderNodeValToRGB')
        node.name = "CRWet"
        node.location = (000, 1250)
        node.color_ramp.interpolation = 'B_SPLINE'
        #node.color_ramp.elements[1].color = 1, 1, 1, 1
        node.color_ramp.elements[0].position = 0.5
        #node.color_ramp.elements[1].color = 0, 0, 0, 1

        node = nodes.new('ShaderNodeMixRGB')  # rgb mixshader machen
        node.location = (400, 1275)
        nodes["Mix"].blend_type = 'ADD'
        nodes["Mix"].use_clamp = True
        nodes["Mix"].inputs[0].default_value = 1.0

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
        nodes["Mix.001"].blend_type = 'SUBTRACT'
        nodes["Mix.001"].use_clamp = True
        nodes["Mix.001"].inputs[0].default_value = 0.6

        # RGB mixshader für zweite Noise Texture
        node = nodes.new('ShaderNodeMixRGB')
        node.location = (1000, 975)
        nodes["Mix.002"].blend_type = 'SUBTRACT'
        nodes["Mix.002"].use_clamp = True
        nodes["Mix.002"].inputs[0].default_value = 0.6

        # link Add notes to Subtract
        links.new(nodes['Mix'].outputs['Color'],
                  nodes['Mix.001'].inputs['Color1'])
        links.new(nodes['Mix.001'].outputs['Color'],
                  nodes['Mix.002'].inputs['Color1'])

        # noise texture (000)
        node = nodes.new('ShaderNodeTexNoise')  # mixshader machen
        node.location = (400, 1100)
        nodes['Noise Texture'].inputs['Scale'].default_value = 2
        nodes['Noise Texture'].inputs['Detail'].default_value = 5

        # Texture Coordinate für die Noise Textures
        node = nodes.new('ShaderNodeTexCoord')
        node.location = (000, 850)
        # Hue Saturation 000 für noise texture2
        node = nodes.new('ShaderNodeHueSaturation')
        node.location = (600, 1075)
        #    nodes["Hue Saturation Value"].inputs[2].default_value = 0.1
        nodes['Hue Saturation Value'].inputs['Value'].default_value = 1.3
        nodes['Hue Saturation Value'].inputs['Saturation'].default_value = 0.0

       # noise texture (001)
        node = nodes.new('ShaderNodeTexNoise')  # mixshader machen
        node.location = (400, 900)
        nodes['Noise Texture.001'].inputs['Detail'].default_value = 5
        nodes['Noise Texture.001'].inputs['Scale'].default_value = 10
        # node = nodes.new('ShaderNodeTexCoord') ### mixshader machen
        # node.location = (000,150)
        # Hue Saturation 001 für noise texture2
        node = nodes.new('ShaderNodeHueSaturation')
        node.location = (600, 900)
        nodes['Hue Saturation Value.001'].inputs['Value'].default_value = 1.3
        nodes['Hue Saturation Value.001'].inputs['Saturation'].default_value = 0.0

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

     # mix die bubbles zu einander und nutze die noise pattern als factor
        node = nodes.new('ShaderNodeMixRGB')
        node.location = (1400, 475)
        nodes["Mix.003"].blend_type = "LIGHTEN"

        node = nodes.new('ShaderNodeMixRGB')
        node.location = (1600, 275)
        nodes["Mix.004"].blend_type = "LIGHTEN"

     # bubble verteilung durch den factor mit less and grater than

        node = nodes.new('ShaderNodeMath')
        node.location = (1200, 675)
        nodes["Math"].operation = "GREATER_THAN"
        nodes["Math"].inputs[0].default_value = 0.1

        node = nodes.new('ShaderNodeMath')
        node.location = (1400, 725)
        nodes["Math.001"].operation = "GREATER_THAN"
        nodes["Math.001"].inputs[0].default_value = 0.2

        node = nodes.new('ShaderNodeMath')
        node.location = (1700, 725)
        nodes["Math.002"].operation = "MULTIPLY"
        nodes["Math.002"].inputs[1].default_value = 30
        nodes["Math.002"].use_clamp = True

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
        node.location = (1800, 275)
        nodes["Mix.005"].blend_type = "MULTIPLY"
        nodes["Mix.005"].inputs[0].default_value = 1.0
        nodes["Mix.005"].use_clamp = True

        links.new(nodes['Mix.004'].outputs['Color'],
                  nodes['Mix.005'].inputs['Color2'])
        links.new(nodes['Mix.002'].outputs['Color'], nodes['Math'].inputs[1])
        links.new(nodes['Mix.002'].outputs['Color'],
                  nodes['Math.001'].inputs[1])
        links.new(nodes['Mix.002'].outputs['Color'],
                  nodes['Math.002'].inputs[0])
        links.new(nodes['Math'].outputs[0], nodes['Mix.003'].inputs[0])
        links.new(nodes['Math.001'].outputs[0], nodes['Mix.004'].inputs[0])

        # patchiness of foam
        node = nodes.new('ShaderNodeValue')  # mixshader machen
        node.location = (600, 1300)
        links.new(nodes['Value.001'].outputs[0], nodes['Mix.001'].inputs[0])
        links.new(nodes['Value.001'].outputs[0], nodes['Mix.002'].inputs[0])

    def constructor_legacy(self, node_tree):
        print('legacy')

    def constructor_30(self, node_tree):
        print('3.0')
