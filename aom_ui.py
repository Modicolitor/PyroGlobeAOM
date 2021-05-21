import bpy


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

        if "AdvOcean" in bpy.data.objects:

            subcol = col.column()
            #subcol.label(text="Ocean Presets")
            # row = layout.row(align=True)
            subcol = col.column()
            subcol.alignment = 'EXPAND'
            subcol.operator("gen.ocean", text="Add Ocean")  # , icon="IPO_QUAD"
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

        if "AdvOcean" in bpy.data.objects:

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
                bpy.data.objects['AdvOcean'].modifiers['Ocean'], "resolution")
            try:
                subcol.prop(
                    bpy.data.objects['AdvOcean'].modifiers['Ocean'], "viewport_resolution")
            except:
                pass
            try:
                subcol.prop(
                    bpy.data.objects['AdvOcean'].modifiers['Ocean'], "spectrum")
            except:
                pass

            # row = layout.row(align=True)
            subcol.prop(
                bpy.data.objects['AdvOcean'].modifiers['Ocean'], "repeat_x")
            subcol.prop(
                bpy.data.objects['AdvOcean'].modifiers['Ocean'], "repeat_y")
            subcol.prop(
                bpy.data.objects['AdvOcean'].modifiers['Ocean'], "spatial_size")

            # subcol = col.column()
            # row = layout.row(align=True)
            subcol.prop(
                bpy.data.objects['AdvOcean'].modifiers['Ocean'], "wave_alignment")
            # subcol = col.column()
            # row = layout.row(align=True)
            subcol.prop(
                bpy.data.objects['AdvOcean'].modifiers['Ocean'], "wave_scale")
            subcol.prop(
                bpy.data.objects['AdvOcean'].modifiers['Ocean'], "wave_scale_min")
            # subcol = col.column()
            # row = layout.row(align=True)
            subcol.prop(
                bpy.data.objects['AdvOcean'].modifiers['Ocean'], "wind_velocity", text="Pointiness 1")
            subcol.prop(
                bpy.data.objects['AdvOcean'].modifiers['Ocean'], "choppiness", text="Pointiness 2")

            oceanmod = bpy.data.objects['AdvOcean'].modifiers['Ocean']
            try:
                if oceanmod.spectrum == 'TEXEL_MARSEN_ARSLOE' or oceanmod.spectrum == 'JONSWAP':
                    subcol.prop(
                        bpy.data.objects['AdvOcean'].modifiers['Ocean'], "fetch_jonswap", text="fetch")
            except:
                pass
          #  col.label("Weather Slider")
           # col.prop(bpy.context.scene, "WeatherX")
           # col.operator("upd.weather")

           # subcol = col.column()
            # row = layout.row(align=True)

            # col.label("Start End Frame")
          #  subcol = col.column()
            # row = layout.row(align=True)

            # col.operator("gen.obfoam", icon="IPO_CUBIC")

            # col.prop(bpy.data.objects['AdvOcean'].modifiers['Dynamic Paint'].canvas_settings.canvas_surfaces['Wetmap'], "is_active")
            # col.prop(bpy.data.objects['AdvOcean'].modifiers['Ocean'], "use_foam")
            # col.prop(bpy.context.active_object, "FoamBool")

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

        if "AdvOcean" in bpy.data.objects:

            subcol = col.column()
            # row = layout.row(align=True)
          #  subcol.label(text="Interacting Objects")
            # row = layout.row(align=True)
            subcol.operator("float.sel", icon="MOD_OCEAN")  # zeige button an

            # row = layout.row(align=True)
            subcol.operator("stat.ob", icon="PINNED")

            # row = layout.row(align=True)
            subcol.operator("rmv.interac", icon="CANCEL")

            # row = layout.row(align=True)
            subcol.operator("cag.vis", icon="RESTRICT_VIEW_OFF")

            # row = layout.row(align=True)

            box = subcol.box()
            box.label(text="Duration of Simulation")
            box.prop(bpy.context.scene, "OceAniStart")
            box.prop(bpy.context.scene, "OceAniEnd")
            box.label(text="Foam")
            box.prop(bpy.context.scene, "OceanFoamBool")
            box.prop(bpy.context.scene, "ObjFoamBool")

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

        if "AdvOcean" in bpy.data.objects:
            # subcol = col.column()
            # row = layout.row(align=True)
            subcol.label(text="Object Foam Settings")
            subcol = col.column()
            subcol.prop(bpy.data.objects["AdvOcean"].modifiers["Dynamic Paint"]
                        .canvas_settings.canvas_surfaces["Wetmap"], "dry_speed", text="Fade")
            # row = layout.row(align=True)

 # !!!!!!            subcol.prop(bpy.data.objects["AdvOcean"].modifiers["Dynamic Paint"].canvas_settings.canvas_surfaces["Wetmap"], "dry_speed", text="Fade")
            subcol.label(text="Ocean Foam Settings")
            subcol = col.column()
            # row = layout.row(align=True)
            subcol.prop(
                bpy.data.objects["AdvOcean"].modifiers["Ocean"], "foam_coverage", text="Coverage")


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

        if "AdvOcean" in bpy.data.objects:
            # subcol = col.column()
            # row = layout.row(align=True)
            subcol = col.column()
            canvas_settings = bpy.data.objects["AdvOcean"].modifiers["Dynamic Paint"].canvas_settings
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

        if "AdvOcean" in bpy.data.objects and bpy.data.objects['AdvOcean'].material_slots:
            subcol.label(text="Water Material Settings")
            try:
                # Rougness value for the ocean
                subcol.prop(bpy.data.objects['AdvOcean'].material_slots['AdvOceanMat']
                            .material.node_tree.nodes['RGB'].outputs[0], 'default_value', text='Color')
            except:
                pass
            try:
                subcol.prop(bpy.data.objects['AdvOcean'].material_slots['AdvOceanMat'].material.node_tree.nodes[
                            'Value'].outputs['Value'], 'default_value', text='Roughness')  # Rougness value for the ocean
            except:
                pass
            try:
                subcol.prop(bpy.data.objects['AdvOcean'].material_slots['AdvOceanMat']
                            .material.node_tree.nodes['Layer Weight.002'].inputs[0], 'default_value', text='Transparency')
            except:
                pass
            try:
                subcol.prop(bpy.data.objects['AdvOcean'].material_slots['AdvOceanMat']
                            .material.node_tree.nodes['Refraction BSDF'].inputs[2], 'default_value', text='IOR')
            except:
                pass

            subcol.label(text="Foam Material Settings")
            try:
                subcol.prop(bpy.data.objects['AdvOcean'].material_slots['AdvOceanMat']
                            .material.node_tree.nodes['Principled BSDF'].inputs[0], 'default_value', text='Color')
            except:
                pass
            try:
                subcol.prop(bpy.data.objects['AdvOcean'].material_slots['AdvOceanMat']
                            .material.node_tree.nodes['Principled BSDF'].inputs[7], 'default_value', text='Rougness')
            except:
                pass
            try:
                subcol.prop(bpy.data.objects['AdvOcean'].material_slots['AdvOceanMat']
                            .material.node_tree.nodes['Principled BSDF'].inputs[15], 'default_value', text='Transmission')
            except:
                pass
            try:
                subcol.prop(bpy.data.objects['AdvOcean'].material_slots['AdvOceanMat']
                            .material.node_tree.nodes['Value.001'].outputs[0], 'default_value', text='Patchiness')
            except:
                pass
            try:
                subcol.prop(bpy.data.objects['AdvOcean'].material_slots['AdvOceanMat']
                            .material.node_tree.nodes['Value.002'].outputs[0], 'default_value', text='Bubblesize')
            except:
                pass
            try:
                subcol.prop(bpy.data.objects['AdvOcean'].material_slots['AdvOceanMat']
                            .material.node_tree.nodes['Math.002'].inputs[1], 'default_value', text='BubbleNoiseThreshold')
            except:
                pass
            try:
                subcol.prop(bpy.data.objects['AdvOcean'].material_slots['AdvOceanMat']
                            .material.node_tree.nodes['Bump'].inputs[0], 'default_value', text='BumpStrength')
            except:
                pass
            try:
                subcol.prop(bpy.data.objects['AdvOcean'].material_slots['AdvOceanMat']
                            .material.node_tree.nodes['Math.003'].inputs[1], 'default_value', text='Displacement')
            except:
                pass

          #  box = row.box()
           # row = layout.row(align=True)

    # Generate OCean  Button
