import bpy
from .aom import get_active_ocean
from .aom_def import is_ocean_material


class BE_PT_AdvOceanAdd(bpy.types.Panel):
    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"
    bl_label = "Advanced Ocean Modifier"
    bl_category = "Adv-Ocean"

    # schreibe auf den Bildschirm

    def draw(self, context):
        layout = self.layout

        layout.use_property_split = True
        layout.use_property_decorate = False  # No animation.

        flow = layout.grid_flow(row_major=True, columns=0,
                                even_columns=False, even_rows=False, align=True)
        col = flow.column()

        subcol = col.column()

       # col = layout.column(align=True)  ### col befehl packt die werte in einen kasten
    #    row = layout.row(align=True)
        if hasattr(context.scene, "aom_props"):
            ocean = get_active_ocean(context)

            if ocean != None:
                # if "AdvOcean" in bpy.data.objects:

                subcol = col.column()
                # subcol.label(text="Ocean Presets")
                # row = layout.row(align=True)
                subcol = col.column()
                subcol.alignment = 'EXPAND'
                # , icon="IPO_QUAD"
                subcol.operator("gen.ocean", text="Add Ocean")
                # , icon="IPO_CUBIC")
                subcol.operator("aom.deleteocean", text="Delete Ocean")
                # subcol.operator("set.storm")  # , icon="IPO_CUBIC")
            else:
                subcol.operator("gen.ocean", icon="MOD_WAVE")


class BE_PT_AdvOceanMenu(bpy.types.Panel):
    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"
    bl_label = "Advanced Ocean Modifier"
    bl_category = "Adv-Ocean"

    # schreibe auf den Bildschirm

    def draw(self, context):
        layout = self.layout

        layout.use_property_split = True
        layout.use_property_decorate = False  # No animation.

        flow = layout.grid_flow(row_major=True, columns=0,
                                even_columns=False, even_rows=False, align=True)
        col = flow.column()

        subcol = col.column()

       # col = layout.column(align=True)  ### col befehl packt die werte in einen kasten
    #    row = layout.row(align=True)
        if hasattr(context.scene, "aom_props"):
            ocean = get_active_ocean(context)

            if ocean != None:
                # if "AdvOcean" in bpy.data.objects:

                subcol = col.column()
                subcol.label(text="Ocean Presets")
                # row = layout.row(align=True)
                subcol = col.column()
                subcol.alignment = 'EXPAND'

                subcol.prop(context.scene.aom_props, "PresetSel")
                subcol.operator("aom.set_preset")

                # subcol.operator("set.lov")  # , icon="IPO_QUAD"
                # subcol.operator("set.mod")  # , icon="IPO_CUBIC")
                # subcol.operator("set.storm")  # , icon="IPO_CUBIC")

                subcol = col.column()
                # row = layout.row(align=True)

                subcol.label(text="Ocean Settings")

                # layout.row(align=True)
                subcol.prop(
                    ocean.modifiers['Ocean'], "resolution")
                try:
                    subcol.prop(
                        ocean.modifiers['Ocean'], "viewport_resolution")
                except:
                    pass
                try:
                    subcol.prop(
                        ocean.modifiers['Ocean'], "spectrum")
                except:
                    pass

                # row = layout.row(align=True)
                subcol.prop(
                    ocean.modifiers['Ocean'], "repeat_x")
                subcol.prop(
                    ocean.modifiers['Ocean'], "repeat_y")
                subcol.prop(
                    ocean.modifiers['Ocean'], "spatial_size")

                # subcol = col.column()
                # row = layout.row(align=True)
                subcol.prop(
                    ocean.modifiers['Ocean'], "wave_alignment")
                # subcol = col.column()
                # row = layout.row(align=True)
                subcol.prop(
                    ocean.modifiers['Ocean'], "wave_scale")
                subcol.prop(
                    ocean.modifiers['Ocean'], "wave_scale_min")
                # subcol = col.column()
                # row = layout.row(align=True)
                subcol.prop(
                    ocean.modifiers['Ocean'], "wind_velocity", text="Pointiness 1")
                subcol.prop(
                    ocean.modifiers['Ocean'], "choppiness", text="Pointiness 2")

                oceanmod = ocean.modifiers['Ocean']
                try:
                    if oceanmod.spectrum == 'TEXEL_MARSEN_ARSLOE' or oceanmod.spectrum == 'JONSWAP':
                        subcol.prop(
                            ocean.modifiers['Ocean'], "fetch_jonswap", text="fetch")
                except:
                    pass

        else:
            subcol.operator("gen.ocean", icon="MOD_WAVE")


class BE_PT_AdvOceanInteract(bpy.types.Panel):
    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"
    bl_label = "Ocean Object Interaction"
    bl_category = "Adv-Ocean"

    # schreibe auf den Bildschirm

    def draw(self, context):
        layout = self.layout

        layout.use_property_split = True
        layout.use_property_decorate = False  # No animation.

        flow = layout.grid_flow(row_major=True, columns=0,
                                even_columns=False, even_rows=False, align=True)
        col = flow.column()

        subcol = col.column()

       # col = layout.column(align=True)  ### col befehl packt die werte in einen kasten
    #    row = layout.row(align=True)
        if hasattr(context.scene, "aom_props"):
            ocean = get_active_ocean(context)

            if ocean != None:

                # if "AdvOcean" in bpy.data.objects:

                subcol = col.column()
                # row = layout.row(align=True)
            #  subcol.label(text="Interacting Objects")
                # row = layout.row(align=True)
                # zeige button an
                subcol.operator("float.sel", icon="MOD_OCEAN")

                # row = layout.row(align=True)
                subcol.operator("stat.ob", icon="PINNED")

                # row = layout.row(align=True)
                subcol.operator("rmv.interac", icon="CANCEL")

                # row = layout.row(align=True)
                subcol.operator("cag.vis", icon="RESTRICT_VIEW_OFF")

                # row = layout.row(align=True)

                box = subcol.box()
                box.label(text="Duration of Simulation")
                box.prop(context.scene.aom_props, "OceAniStart")
                box.prop(context.scene.aom_props, "OceAniEnd")
                box.prop(context.scene.aom_props, "OceAniSpeed", text="Speed")
                box.label(text="Foam")
                box.prop(context.scene.aom_props, "OceanFoamBool")
                box.prop(context.scene.aom_props, "ObjFoamBool")

                row = layout.row(align=True)
                box.operator("upd.oceaniframe", text="Update",
                             icon="FILE_TICK")  # update foam and Frames


class BE_PT_AdvOceanFoam(bpy.types.Panel):
    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"
    bl_label = "Ocean Foam Settings"
    bl_category = "Adv-Ocean"

    # schreibe auf den Bildschirm

    def draw(self, context):
        layout = self.layout

        layout.use_property_split = True
        layout.use_property_decorate = False  # No animation.

        flow = layout.grid_flow(row_major=True, columns=0,
                                even_columns=False, even_rows=False, align=True)
        col = flow.column()

        subcol = col.column()

       # col = layout.column(align=True)  ### col befehl packt die werte in einen kasten
    #    row = layout.row(align=True)
        if hasattr(context.scene, "aom_props"):
            ocean = get_active_ocean(context)

            if ocean != None:
                # if "AdvOcean" in bpy.data.objects:
                # subcol = col.column()
                # row = layout.row(align=True)
                subcol.label(text="Object Foam Settings")
                subcol = col.column()
                subcol.prop(ocean.modifiers["Dynamic Paint"]
                            .canvas_settings.canvas_surfaces["Wetmap"], "dry_speed", text="Fade")
                # row = layout.row(align=True)

    # !!!!!!            subcol.prop(bpy.data.objects["AdvOcean"].modifiers["Dynamic Paint"].canvas_settings.canvas_surfaces["Wetmap"], "dry_speed", text="Fade")
                subcol.label(text="Ocean Foam Settings")
                subcol = col.column()
                # row = layout.row(align=True)
                subcol.prop(
                    ocean.modifiers["Ocean"], "foam_coverage", text="Coverage")


class BE_PT_AdvOceanWaves(bpy.types.Panel):
    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"
    bl_label = "Ocean Wave Settings"
    bl_category = "Adv-Ocean"

    # schreibe auf den Bildschirm

    def draw(self, context):
        layout = self.layout

        layout.use_property_split = True
        layout.use_property_decorate = False  # No animation.

        flow = layout.grid_flow(row_major=True, columns=0,
                                even_columns=False, even_rows=False, align=True)
        col = flow.column()

        subcol = col.column()

       # col = layout.column(align=True)  ### col befehl packt die werte in einen kasten
    #    row = layout.row(align=True)
        if hasattr(context.scene, "aom_props"):
            ocean = get_active_ocean(context)

            if ocean != None:
                # subcol = col.column()
                # row = layout.row(align=True)
                subcol = col.column()
                canvas_settings = ocean.modifiers["Dynamic Paint"].canvas_settings
                subcol.prop(
                    canvas_settings.canvas_surfaces["Waves"], "wave_damping", text="Damping")
                subcol.prop(
                    canvas_settings.canvas_surfaces["Waves"], "wave_spring", text="Spring")
                subcol.prop(
                    canvas_settings.canvas_surfaces["Waves"], "wave_smoothness", text="Smoothness")
                # row = layout.row(align=True)


class BE_PT_AdvOceanMat(bpy.types.Panel):
    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"
    bl_label = "Ocean Material Settings"
    bl_category = "Adv-Ocean"

    # schreibe auf den Bildschirm

    def draw(self, context):

        if hasattr(context.scene, "aom_props"):
            layout = self.layout

            layout.use_property_split = True
            layout.use_property_decorate = False  # No animation.

            flow = layout.grid_flow(row_major=True, columns=0,
                                    even_columns=False, even_rows=False, align=True)
            col = flow.column()

            subcol = col.column()
            try:
                subcol.prop(context.scene.aom_props, "MaterialSel")
            except:
                pass
            subcol.operator("gen.ocmat", icon="MATERIAL")

            ocean = get_active_ocean(context)

            # if "AdvOcean" in bpy.data.objects and bpy.data.objects['AdvOcean'].material_slots:
            # got a valid ocean
            if ocean != None:
                mat = ocean.material_slots[0].material
                if is_ocean_material(context, mat):
                    nodes = mat.node_tree.nodes
                    subcol.label(text="Water Material Settings")
                    try:

                        subcol.prop(nodes['RGB'].outputs[0],
                                    'default_value', text='Color')
                    except:
                        pass
                    try:
                        # Rougness value for the ocean
                        subcol.prop(nodes['Value'].outputs['Value'],
                                    'default_value', text='Roughness')
                    except:
                        pass
                    try:
                        subcol.prop(nodes['Layer Weight.002'].inputs[0],
                                    'default_value', text='Transparency')
                    except:
                        pass

                    try:
                        subcol.prop(nodes['Layer Weight.001'].inputs[0],
                                    'default_value', text='Refraction')
                    except:
                        pass

                    try:
                        subcol.prop(nodes['Refraction BSDF'].inputs[2],
                                    'default_value', text='IOR')
                    except:
                        pass

                    subcol.label(text="Fake Bump Waves")

                    try:
                        subcol.prop(nodes['WaterBumpTexScale'].outputs[0],
                                    'default_value', text='Wave Texture Scale')
                    except:
                        pass

                    try:
                        subcol.prop(nodes['WaterBumpStrength'].outputs[0],
                                    'default_value', text='Bump Strength')
                    except:
                        pass

                    subcol.label(text="Foam Material Settings")
                    try:
                        subcol.prop(nodes['FoamColor'].outputs[0],
                                    'default_value', text='Color')
                    except:
                        pass
                    try:
                        subcol.prop(nodes['FoamSubsurf'].outputs[0],
                                    'default_value', text='Subsurface Scattering')
                    except:
                        pass
                    try:
                        subcol.prop(nodes['FoamRoughness'].ouputs[0],
                                    'default_value', text='Roughness')
                    except:
                        pass
                    try:
                        subcol.prop(nodes['FoamTransmission'].outputs[0],
                                    'default_value', text='Transmission')
                    except:
                        pass

                    subcol.label(text="Ocean Foam Finetune")
                    try:
                        subcol.prop(nodes['FoamBaseStrength'].outputs[0],
                                    'default_value', text='Base Strength')
                    except:
                        pass

                    try:
                        subcol.prop(nodes['LowerOceanFoamCut'].outputs[0],  # LowerFoamCut, FoamBasestrength, LowerObjFoamCut, ObjectFoam Basestrength,
                                    'default_value', text='Low Cut')
                    except:
                        pass

                    subcol.label(text="Object Foam Finetune")
                    try:
                        subcol.prop(nodes['ObjectBaseStrength'].outputs[0],
                                    'default_value', text='Base Strength')
                    except:
                        pass

                    try:
                        subcol.prop(nodes['LowerObjectCut'].outputs[0],
                                    'default_value', text='Low Cut')
                    except:
                        pass
                    subcol.label(text="Foam Patches")
                    try:
                        subcol.prop(nodes['Patchiness'].outputs[0],
                                    'default_value', text='Patchiness')
                    except:
                        pass
                    try:
                        subcol.prop(nodes['NoiseScale'].outputs[0],
                                    'default_value', text='Noise Scale')
                    except:
                        pass
                    subcol.label(text="Bubbles")
                    try:
                        subcol.prop(nodes['ScaleBub'].outputs[0],
                                    'default_value', text='Bubblesize')
                    except:
                        pass

                    try:
                        subcol.prop(nodes['BubbleNoiseThreshold'].inputs[1],
                                    'default_value', text='Bubble Noise Threshold')
                        ###################################
                    except:
                        pass
                    try:
                        subcol.prop(nodes['FoamBumpCtl'].outputs[0],
                                    'default_value', text='BumpStrength')
                    except:
                        pass
                    try:
                        subcol.prop(nodes['DisplStrength'].outputs[0],
                                    'default_value', text='Displacement')
                    except:
                        pass

            #  box = row.box()
            # row = layout.row(align=True)

    # Generate OCean  Button


class BE_PT_AdvOceanSpecial(bpy.types.Panel):
    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"
    bl_label = "Ocean Specials"
    bl_category = "Adv-Ocean"

    # schreibe auf den Bildschirm

    def draw(self, context):

        if hasattr(context.scene, "aom_props"):
            layout = self.layout

            layout.use_property_split = True
            layout.use_property_decorate = False  # No animation.

            flow = layout.grid_flow(row_major=True, columns=0,
                                    even_columns=False, even_rows=False, align=True)
            col = flow.column()

            subcol = col.column()

            if hasattr(context.scene, "aom_props"):
                subcol.label(text='Loop')
                subcol.operator("aom.loop", icon="MATERIAL")
                subcol.operator("aom.removeloop", icon="MATERIAL")
                subcol.label(text='Spray')
                subcol.operator("aom.spray", icon="MATERIAL")
                subcol.operator("aom.remove_spray", icon="MATERIAL")

                subcol.label(text='Ripples')
                subcol.operator("aom.ripples", icon="MATERIAL")
                subcol.operator("aom.remove_ripples", icon="MATERIAL")

            # if "AdvOcean" in bpy.data.objects and bpy.data.objects['AdvOcean'].material_slots:
            # got a valid ocean

            #subcol.label(text="Water Material Settings")

            #  box = row.box()
            # row = layout.row(align=True)

    # Generate OCean  Button
