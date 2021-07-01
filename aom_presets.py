import bpy


class AOMPreset_Handler:
    def __init__(self):
        #context = context
        pass

    def set_preset(self, context, ocean):
        PresetSel = context.scene.aom_props.PresetSel
        mat = ocean.material_slots[0].material
        if PresetSel == '1':
            self.set_lovely(context, ocean, mat)
        elif PresetSel == '2':
            self.set_lively(context, ocean, mat)
        elif PresetSel == '3':
            self.set_stormy(context, ocean, mat)
        elif PresetSel == '4':
            self.set_shallow_quiet(context, ocean, mat)
        elif PresetSel == '5':
            self.set_shallow_lively(context, ocean, mat)
        elif PresetSel == '6':
            self.set_shallow_stormy(context, ocean, mat)
        elif PresetSel == '7':
            self.set_established_lovely(context, ocean, mat)
        elif PresetSel == '8':
            self.set_established_lively(context, ocean, mat)
        elif PresetSel == '9':
            self.set_established_stormy(context, ocean, mat)
        elif PresetSel == '10':
            self.set_abstract(context, ocean, mat)
        elif PresetSel == '11':
            self.set_abstract2(context, ocean, mat)
        elif PresetSel == '12':
            self.set_abstract_Watt(context, ocean, mat)

    def set_initsettings(self, context, Ocean, mat):

        # dp

        waves = context.object.modifiers["Dynamic Paint"].canvas_settings.canvas_surfaces["Waves"]
        waves.wave_damping = 0.02
        waves.wave_smoothness = 0.7

        oceanmod = Ocean.modifiers["Ocean"]
        oceanmod.foam_coverage = 0.3
        oceanmod.damping = 0.5
        oceanmod.viewport_resolution = 15

        if "AdvOceanMat" in mat.name:
            print('Init Presets')
            nodes = mat.node_tree.nodes

            nodes['LowerObjectCut'].outputs[0].default_value = 0.4
            nodes['ObjectBaseStrength'].outputs[0].default_value = 1

            nodes['DisplStrength'].outputs[0].default_value = 0.02
            nodes['Value'].outputs[0].default_value = 0.01  # rougness water =
            nodes['RGB'].outputs[0].default_value = (1, 1, 1, 1)
            nodes['WaterBumpTexScale'].outputs[0].default_value = 30
            nodes['WaterBumpStrength'].outputs[0].default_value = 0.1

            nodes['FoamSubsurf'].outputs[0].default_value = 0.2
            nodes['FoamRoughness'].outputs[0].default_value = 0.2
            nodes['FoamColor'].outputs[0].default_value = (1, 1, 1, 1)
            nodes['FoamBumpCtl'].outputs[0].default_value = 0.0
            nodes['ScaleBub'].outputs[0].default_value = 1500.0
            nodes['NoiseScale'].outputs[0].default_value = 20.0

            nodes['LowerOceanFoamCut'].outputs[0].default_value = 0.0
            nodes['FoamBaseStrength'].outputs[0].default_value = 1.0
            nodes['Patchiness'].outputs[0].default_value = 0.2
            nodes['MRNoise1'].inputs[4].default_value = 0.4
            nodes['MRNoise2'].inputs[4].default_value = 0.4

    def set_lovely(self, context, Ocean, mat):
        Ocean = Ocean.modifiers["Ocean"]
        Ocean.spectrum = 'PHILLIPS'
        Ocean.choppiness = 1.00
        Ocean.wave_scale = 0.2
        Ocean.wind_velocity = 5
        Ocean.wave_scale_min = 0.01
        Ocean.wave_alignment = 0.0
        Ocean.foam_coverage = 0.3
        Ocean.damping = 0.3

        if "AdvOceanMat" in mat.name:

            nodes = mat.node_tree.nodes

            nodes['WaterBumpStrength'].outputs['Value'].default_value = 0.01
            nodes['LowerOceanFoamCut'].outputs[0].default_value = 0.4
            nodes['FoamBaseStrength'].outputs[0].default_value = 0.5
            nodes['Patchiness'].outputs[0].default_value = 1.1
            nodes['WaterBumpStrength'].outputs[0].default_value = 0.3
            nodes['DisplStrength'].outputs[0].default_value = 0.02

    def set_lively(self, context, Ocean, mat):
        Ocean = Ocean.modifiers["Ocean"]
        Ocean.spectrum = 'PHILLIPS'
        Ocean.wave_scale = 1.0
        Ocean.choppiness = 1.00
        Ocean.wind_velocity = 6
        Ocean.wave_scale_min = 0.01
        Ocean.wave_alignment = 0.2
        Ocean.damping = 0.3
        Ocean.foam_coverage = 0.3

        if "AdvOceanMat" in mat.name:

            nodes = mat.node_tree.nodes
            nodes['LowerOceanFoamCut'].outputs[0].default_value = 0.1
            nodes['FoamBaseStrength'].outputs[0].default_value = 1.0
            nodes['Patchiness'].outputs[0].default_value = 0.4
            nodes['WaterBumpStrength'].outputs[0].default_value = 0.3
            nodes['DisplStrength'].outputs[0].default_value = 0.02

    def set_stormy(self, context, Ocean, mat):
        Ocean = Ocean.modifiers["Ocean"]
        Ocean.spectrum = 'PHILLIPS'
        Ocean.spatial_size = 54
        Ocean.wave_scale = 6
        Ocean.wave_alignment = 0.8
        Ocean.choppiness = 0.3
        Ocean.wind_velocity = 9
        Ocean.wave_scale_min = 0.01
        Ocean.foam_coverage = 0.5
        Ocean.damping = 0.5

        if "AdvOceanMat" in mat.name:

            nodes = mat.node_tree.nodes
            nodes['LowerOceanFoamCut'].outputs[0].default_value = 0.1
            nodes['FoamBaseStrength'].outputs[0].default_value = 1
            nodes['Patchiness'].outputs[0].default_value = 0.4
            nodes['WaterBumpStrength'].outputs[0].default_value = 0.1
            nodes['DisplStrength'].outputs[0].default_value = 0.02

    def set_shallow_quiet(self, context, Ocean, mat):
        Ocean = Ocean.modifiers["Ocean"]
        Ocean.spectrum = 'PHILLIPS'

        Ocean.wave_scale = 0.1
        Ocean.wave_alignment = 0
        Ocean.choppiness = 1
        Ocean.wind_velocity = 54
        Ocean.wave_scale_min = 0.00
        Ocean.foam_coverage = 0.1
        #Ocean.damping = 0.2

        if "AdvOceanMat" in mat.name:

            nodes = mat.node_tree.nodes
            nodes['LowerOceanFoamCut'].outputs[0].default_value = 0.4
            nodes['FoamBaseStrength'].outputs[0].default_value = 1.5
            nodes['Patchiness'].outputs[0].default_value = 0.6
            nodes['WaterBumpStrength'].outputs[0].default_value = 0.3
            nodes['DisplStrength'].outputs[0].default_value = 0.02

    def set_shallow_lively(self, context, Ocean, mat):
        Ocean = Ocean.modifiers["Ocean"]
        Ocean.spectrum = 'TEXEL_MARSEN_ARSLOE'

        Ocean.wave_scale = 0.4
        Ocean.wave_alignment = 0
        Ocean.choppiness = 1
        Ocean.wind_velocity = 50

        Ocean.wave_scale_min = 0.00
        Ocean.foam_coverage = 0.4
        #Ocean.damping = 0.2

        if "AdvOceanMat" in mat.name:

            nodes = mat.node_tree.nodes
            nodes['LowerOceanFoamCut'].outputs[0].default_value = 0.4
            nodes['FoamBaseStrength'].outputs[0].default_value = 1.5
            nodes['Patchiness'].outputs[0].default_value = 0.2
            nodes['WaterBumpStrength'].outputs[0].default_value = 0.3
            nodes['DisplStrength'].outputs[0].default_value = 0.06

    def set_shallow_stormy(self, context, Ocean, mat):
        Ocean = Ocean.modifiers["Ocean"]
        Ocean.spectrum = 'TEXEL_MARSEN_ARSLOE'

        Ocean.wave_scale = 0.5
        Ocean.wave_alignment = 0
        Ocean.choppiness = 1
        Ocean.wind_velocity = 15
        Ocean.wave_scale_min = 0.00
        Ocean.foam_coverage = 0.5
        #Ocean.damping = 0.2

        if "AdvOceanMat" in mat.name:

            nodes = mat.node_tree.nodes
            nodes['LowerOceanFoamCut'].outputs[0].default_value = 0.8
            nodes['FoamBaseStrength'].outputs[0].default_value = 1.5
            nodes['Patchiness'].outputs[0].default_value = 0.3
            nodes['WaterBumpStrength'].outputs[0].default_value = 0.3
            nodes['DisplStrength'].outputs[0].default_value = 0.06

    def set_established_lovely(self, context, Ocean, mat):
        Ocean = Ocean.modifiers["Ocean"]
        Ocean.spectrum = 'PIERSON_MOSKOWITZ'

        Ocean.wave_scale = 0.2
        Ocean.wave_alignment = 0.1
        Ocean.choppiness = 1
        Ocean.wind_velocity = 5
        Ocean.wave_scale_min = 0.00
        Ocean.foam_coverage = 0.0
        Ocean.damping = 0.5

        if "AdvOceanMat" in mat.name:

            nodes = mat.node_tree.nodes
            nodes['LowerOceanFoamCut'].outputs[0].default_value = 0.1
            nodes['FoamBaseStrength'].outputs[0].default_value = 1.0
            nodes['Patchiness'].outputs[0].default_value = 0.6
            nodes['WaterBumpStrength'].outputs[0].default_value = 0.3
            nodes['DisplStrength'].outputs[0].default_value = 0.02

    def set_established_lively(self, context, Ocean, mat):
        Ocean = Ocean.modifiers["Ocean"]
        Ocean.spectrum = 'PIERSON_MOSKOWITZ'

        Ocean.wave_scale = 0.8
        Ocean.wave_alignment = 0.1
        Ocean.choppiness = 1
        Ocean.wind_velocity = 5
        Ocean.wave_scale_min = 0.00
        Ocean.foam_coverage = 0.0
        Ocean.damping = 0.5

        if "AdvOceanMat" in mat.name:

            nodes = mat.node_tree.nodes
            nodes['LowerOceanFoamCut'].outputs[0].default_value = 0.1
            nodes['FoamBaseStrength'].outputs[0].default_value = 1.0
            nodes['Patchiness'].outputs[0].default_value = 0.6
            nodes['WaterBumpStrength'].outputs[0].default_value = 0.3
            nodes['DisplStrength'].outputs[0].default_value = 0.02

    def set_established_stormy(self, context, Ocean, mat):
        Ocean = Ocean.modifiers["Ocean"]
        Ocean.spectrum = 'PIERSON_MOSKOWITZ'

        Ocean.wave_scale = 2
        Ocean.wave_alignment = 0.1
        Ocean.choppiness = 0.9
        Ocean.wind_velocity = 9
        Ocean.wave_scale_min = 0.00
        Ocean.foam_coverage = 0.0
        Ocean.damping = 0.64

        if "AdvOceanMat" in mat.name:

            nodes = mat.node_tree.nodes
            nodes['LowerOceanFoamCut'].outputs[0].default_value = 0.1
            nodes['FoamBaseStrength'].outputs[0].default_value = 1.0
            nodes['Patchiness'].outputs[0].default_value = 0.6
            nodes['WaterBumpStrength'].outputs[0].default_value = 0.3
            nodes['DisplStrength'].outputs[0].default_value = 0.02

    def set_abstract(self, context, Ocean, mat):
        Ocean = Ocean.modifiers["Ocean"]
        Ocean.spectrum = 'PHILLIPS'

        Ocean.wave_scale = 2
        Ocean.wave_alignment = 0.1
        Ocean.choppiness = 0.1
        Ocean.wind_velocity = 1
        Ocean.wave_scale_min = 0.00
        Ocean.foam_coverage = 0.0
        Ocean.damping = 0.64

        if "AdvOceanMat" in mat.name:

            nodes = mat.node_tree.nodes
            nodes['LowerOceanFoamCut'].outputs[0].default_value = 0.002
            nodes['FoamBaseStrength'].outputs[0].default_value = 1.0
            nodes['Patchiness'].outputs[0].default_value = 0.0
            nodes['WaterBumpStrength'].outputs[0].default_value = 0.3
            nodes['DisplStrength'].outputs[0].default_value = 0.02

        # shallow lake
        # shallow lake
        # established large ocean quiet
        # established large ocean stromy
        # abstract
        # giant

    def set_abstract2(self, context, Ocean, mat):
        Ocean = Ocean.modifiers["Ocean"]
        Ocean.spectrum = 'PHILLIPS'

        Ocean.wave_scale = 1.6
        Ocean.wave_alignment = 0.1
        Ocean.choppiness = 0.51
        Ocean.wind_velocity = 0.8
        Ocean.wave_scale_min = 3.00
        Ocean.foam_coverage = 0.2
        Ocean.damping = 0.44

        if "AdvOceanMat" in mat.name:

            nodes = mat.node_tree.nodes
            nodes['LowerOceanFoamCut'].outputs[0].default_value = 0.002
            nodes['FoamBaseStrength'].outputs[0].default_value = 1.0
            nodes['Patchiness'].outputs[0].default_value = 0.0
            nodes['WaterBumpStrength'].outputs[0].default_value = 0.3
            nodes['DisplStrength'].outputs[0].default_value = 0.02

    def set_abstract_Watt(self, context, Ocean, mat):
        Ocean = Ocean.modifiers["Ocean"]
        Ocean.spectrum = 'PHILLIPS'

        Ocean.wave_scale = 1

        Ocean.wave_alignment = 1
        Ocean.choppiness = 2
        Ocean.wind_velocity = 1.4
        Ocean.wave_scale_min = 0.60
        Ocean.foam_coverage = 0.2
        Ocean.damping = 1.0

        if "AdvOceanMat" in mat.name:

            nodes = mat.node_tree.nodes
            nodes['LowerOceanFoamCut'].outputs[0].default_value = 0.025
            nodes['FoamBaseStrength'].outputs[0].default_value = 10.0
            nodes['Patchiness'].outputs[0].default_value = 0.15
            nodes['WaterBumpStrength'].outputs[0].default_value = 0.0
            nodes['DisplStrength'].outputs[0].default_value = 0.32


# shallow lake
# shallow lake
# established large ocean quiet
# established large ocean stromy
# abstract
# giant
