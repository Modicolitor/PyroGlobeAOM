import bpy


class AOMPreset_Handler:
    def __init__(self):
        #context = context
        pass

    def set_preset(self, context):
        PresetSel = context.scene.aom_props.PresetSel
        if PresetSel == '1':
            self.set_lovely(context)
        elif PresetSel == '2':
            self.set_lively(context)
        elif PresetSel == '3':
            self.set_stormy(context)

    def set_lovely(self, context):
        Ocean = bpy.data.objects['AdvOcean'].modifiers['Ocean']
        Ocean.choppiness = 1.00
        Ocean.wave_scale = 0.2
        Ocean.wind_velocity = 5
        Ocean.wave_scale_min = 0.01
        Ocean.wave_alignment = 0.0
        Ocean.foam_coverage = 0.3

        if "AdvOceanMat" in bpy.data.materials:
            mat = bpy.data.materials['AdvOceanMat']
            nodes = mat.node_tree.nodes
            nodes['WaterBumpStrength'].outputs['Value'].default_value = 0.01

    def set_lively(self, context):
        Ocean = bpy.data.objects['AdvOcean'].modifiers['Ocean']
        Ocean.wave_scale = 1.0
        Ocean.choppiness = 1.00
        Ocean.wind_velocity = 6
        Ocean.wave_scale_min = 0.01
        Ocean.wave_alignment = 0.2

        Ocean.foam_coverage = 0.3
        try:
            mat = bpy.data.materials['AdvOceanMat']
            # nodes = mat.node_tree.nodes
            bpy.data.objects['AdvOcean'].material_slots['AdvOceanMat'].material.node_tree.nodes['Value.001'].outputs['Value'].default_value = 0.6

        except:
            print("There seems to be no AdvOceanMaterial")

            pass

    def set_stormy(self, context):
        Ocean = bpy.data.objects['AdvOcean'].modifiers['Ocean']
        Ocean.wave_scale = 3
        Ocean.wave_alignment = 3
        Ocean.choppiness = 0.7
        Ocean.wind_velocity = 15
        Ocean.wave_scale_min = 0.01
        Ocean.foam_coverage = 0.3

        try:
            mat = bpy.data.materials['AdvOceanMat']
            nodes = mat.node_tree.nodes
            bpy.data.objects['AdvOcean'].material_slots['AdvOceanMat'].material.node_tree.nodes['Value.001'].outputs['Value'].default_value = 0.45

        except:
            print("There seems to be no AdvOceanMaterial")
