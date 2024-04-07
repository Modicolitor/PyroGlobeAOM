
import bpy
from .aom import get_active_ocean
from .aom_def import is_ocean_material

'''
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
                subcol.alignment = 'EXPAND'
                # , icon="IPO_QUAD"
                subcol.operator("gen.ocean", text="Add Ocean")
                # , icon="IPO_CUBIC")
                subcol.operator("aom.deleteocean", text="Delete Ocean")
                # subcol.operator("set.storm")  # , icon="IPO_CUBIC")
            else:
                subcol.operator("gen.ocean", icon="MOD_WAVE")'''


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

        ocean = get_active_ocean(context)
        if hasattr(context.scene, "aom_props"):

            ocean = get_active_ocean(context)

            if ocean == None:
                subcol.operator("gen.ocean", icon="MOD_WAVE",
                                text="Add Ocean")

            else:
                subcol.operator("gen.ocean", text="Add Ocean")
                # , icon="IPO_CUBIC")
                subcol.operator("aom.deleteocean", text="Delete Ocean")
                # subcol.operator("set.storm")  # , icon="IPO_CUBIC")
                # if "AdvOcean" in bpy.data.objects:

                subcol = col.column()
                subcol.label(text="Ocean Presets")
                # row = layout.row(align=True)
                subcol = col.column()
                subcol.alignment = 'EXPAND'

                subcol.prop(context.scene.aom_props, "PresetSel")
                subcol.operator("aom.set_preset", icon='LINENUMBERS_ON')

                # subcol.operator("set.lov")  # , icon="IPO_QUAD"
                # subcol.operator("set.mod")  # , icon="IPO_CUBIC")
                # subcol.operator("set.storm")  # , icon="IPO_CUBIC")

                subcol = col.column()
                # row = layout.row(align=True)
                ocean_mod = get_ocean_mod(ocean)
                if ocean_mod != None:
                    subcol.label(text="Ocean Settings")
                    # layout.row(align=True)
                    subcol.prop(
                        ocean_mod, "resolution")
                    try:
                        subcol.prop(
                            ocean_mod, "viewport_resolution")
                    except:
                        pass
                    try:
                        subcol.prop(
                            ocean_mod, "spectrum")
                    except:
                        pass

                    # row = layout.row(align=True)
                    subcol.prop(
                        ocean_mod, "repeat_x")
                    subcol.prop(
                        ocean_mod, "repeat_y")
                    subcol.prop(
                        ocean_mod, "spatial_size")

                    # subcol = col.column()
                    # row = layout.row(align=True)
                    subcol.prop(
                        ocean_mod, "wave_alignment")
                    # subcol = col.column()
                    # row = layout.row(align=True)
                    subcol.prop(
                        ocean_mod, "wave_scale")
                    subcol.prop(
                        ocean_mod, "wave_scale_min")
                    # subcol = col.column()
                    # row = layout.row(align=True)
                    subcol.prop(
                        ocean_mod, "wind_velocity", text="Pointiness 1")
                    subcol.prop(
                        ocean_mod, "choppiness", text="Pointiness 2")

                    try:
                        if ocean_mod.spectrum == 'TEXEL_MARSEN_ARSLOE' or ocean_mod.spectrum == 'JONSWAP':
                            subcol.prop(
                                ocean_mod, "fetch_jonswap", text="fetch")
                    except:
                        pass

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

        # elif ocean != None:
        #    subcol.operator("initialize.aom", icon="MOD_WAVE", text="Initialize")
        else:
            subcol.operator("aom.initialize", icon="MOD_WAVE")


class BE_PT_AdvOceanInteract(bpy.types.Panel):
    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"
    bl_label = "Ocean Object Interaction"
    bl_category = "Adv-Ocean"
    bl_options = {'DEFAULT_CLOSED'}

    @classmethod
    def poll(cls, context):
        return hasattr(context.scene, "aom_props")

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
                #subcol.operator("float.sel", icon="MOD_OCEAN")
                subcol.operator(
                    "aom.geofloat", icon="MOD_OCEAN", text='Geofloat Object(s)')
                subcol.operator(
                    "aom.geofree", icon="PINNED", text='Free Object(s)')
                # row = layout.row(align=True)
                subcol.operator("stat.ob", icon="PINNED", text="Free (Dynamic Paint)")

                # row = layout.row(align=True)
                subcol.operator("rmv.interac", icon="CANCEL")

                # row = layout.row(align=True)
                subcol.operator("cag.vis", icon="RESTRICT_VIEW_OFF")
                aom_props = context.scene.aom_props
                #subcol.prop(aom_props, 'use_GeoFloat', text='Use GeoFloat')
                
                box = col.box()
                #box.operator()
                box.label(text='Bake Interaction')
                box.operator("object.simulation_nodes_cache_calculate_to_frame", text="Calculate to Frame").selected = True
                
                row = box.row(align=True)
                row.operator("object.simulation_nodes_cache_bake", text="Bake").selected = True
                row.operator("object.simulation_nodes_cache_delete", text="", icon='TRASH').selected = True

                box.use_property_split = True
                box.use_property_decorate = False
                ob = get_active_ocean(context)
                box.prop(ob, "use_simulation_cache", text="Cache")
                
                '''if aom_props.use_GeoFloat:
                    subcol.prop(aom_props, 'instanceFloatobj',
                                text='Instance Object')
                    subcol.prop(aom_props, 'is_GeoFloat_Smooth',
                                text='SmootherDetection')
                
                else:
                    subcol = col.column()
                    subcol.enabled = False
                    subcol.prop(aom_props, 'instanceFloatobj',
                                text='Instance Object', emboss=True)
                    subcol.prop(aom_props, 'is_GeoFloat_Smooth',
                                text='SmootherDetection', emboss=True)'''


class BE_PT_AdvOceanWaves(bpy.types.Panel):
    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"
    bl_label = "Object Wave Settings"
    bl_category = "Adv-Ocean"
    bl_options = {'DEFAULT_CLOSED'}

    @classmethod
    def poll(cls, context):
        return hasattr(context.scene, "aom_props")

    def get_waveSim_mod(self, context, oc):
        #print (f'in get mod {oc.name} candidate {candidate.name}')
        for mod in oc.modifiers:
            #print (f'in Schleife {mod.name} candidate {candidate.name}')
            if hasattr(mod, 'node_group'):
                #print (f'has node_group mod {mod.name} candidate {mod.node_group.name}')
                if mod.node_group.name ==  'AOM_ObjectWaveSim':
                    #print (f'found modifier {mod.node_group.name}')
                    return mod 
        return None
    
    
    
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
                dp_mod = get_dynpaint_mod(ocean)
                if dp_mod != None:
                    subcol = col.column()
                    canvas_settings = dp_mod.canvas_settings
                    #subcol.prop(
                    #    canvas_settings.canvas_surfaces["Waves"], "wave_timescale")

                    #subcol.prop(
                    #    canvas_settings.canvas_surfaces["Waves"], "wave_speed", text="Speed")
                    oc = get_active_ocean(context)
                    mod = self.get_waveSim_mod(context, oc)
                    
                    if mod != None:
                        subcol.label(text='GeoNodes Simulation')
                        for inp in mod.node_group.interface.items_tree:
                            if inp.bl_socket_idname != 'NodeSocketGeometry':
                                prop = '["' + inp.identifier +  '"]'
                                subcol.prop(data= mod, property=prop, text=inp.name)
                        #subcol.prop(
                        #    mod['Socket_1'], "wave_damping", text="Displacement Strength")
                    
                    subcol.label(text='Dynamic Paint')
                    subcol.prop(
                    canvas_settings.canvas_surfaces["Waves"], "wave_damping", text="Damping")
                    subcol.prop(
                            canvas_settings.canvas_surfaces["Waves"], "wave_spring", text="Spring")
                    subcol.prop(
                            canvas_settings.canvas_surfaces["Waves"], "wave_smoothness", text="Smoothness")
                            


class BE_PT_AdvOceanMat(bpy.types.Panel):
    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"
    bl_label = "Ocean Material Settings"
    bl_category = "Adv-Ocean"
    bl_options = {'DEFAULT_CLOSED'}

    @ classmethod
    def poll(cls, context):
        return hasattr(context.scene, "aom_props")

    def draw(self, context):

        if hasattr(context.scene, "aom_props"):
            aom_props = context.scene.aom_props
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
            subcol.prop(context.scene.aom_props, "AddMaxPerformance",
                        text="Add with best performance")

            ocean = get_active_ocean(context)

            # if "AdvOcean" in bpy.data.objects and bpy.data.objects['AdvOcean'].material_slots:
            # got a valid ocean
            if ocean != None:
                mat = ocean.material_slots[0].material
                is_advanced = context.scene.aom_props.AdvMaterialOptions
                if is_ocean_material(context, mat) and hasattr(mat.node_tree, "nodes"):

                    subcol = col.box()
                    subcol.label(text="Water Material Settings")

                    node_tree = mat.node_tree
                    nodes = mat.node_tree.nodes

                    try:

                        subcol.prop(nodes['OceanTint'].outputs[0],
                                    'default_value', text='Color')
                    except:
                        pass
                    try:
                        subcol.prop(nodes['OceanSubsurface'].outputs[0],
                                    'default_value', text='Subsurface')
                    except:
                        pass

                    try:
                        subcol.prop(nodes['Roughness'].outputs['Value'],
                                    'default_value', text='Roughness')
                    except:
                        pass

                    try:
                        subcol.prop(nodes['IOR'].outputs['Value'],
                                    'default_value', text='IOR')
                    except:
                        pass

                    try:
                        subcol.prop(nodes['Transmission'].outputs['Value'],
                                    'default_value', text='Transparency')
                    except:
                        pass

                    try:
                        subcol.prop(nodes['Transparency'].outputs['Value'],
                                    'default_value', text='Alpha')
                    except:
                        pass
                    subcol.label(text='Bump Waves')
                    try:
                        subcol.prop(nodes['WaterBumpStrength'].outputs[0],
                                    'default_value', text='Wave Strength')
                    except:
                        pass

                    try:
                        subcol.prop(nodes['WaterBumpTexScale'].outputs[0],
                                    'default_value', text='Wave Texture Scale')
                    except:
                        pass

                    try:
                        subcol.prop(nodes['TimerWaveScale'].outputs[1],
                                    'default_value', text='Fake Wave Speed')
                    except:
                        pass

                    subcol = col.box()
                    subcol.label(text="Foam Material Settings")
                    subcol.prop(context.scene.aom_props,
                                'AdvMaterialOptions', text='Advanced Options')
                    try:
                        subcol.prop(nodes['FoamColor'].outputs[0],
                                    'default_value', text='Foam Color')
                    except:
                        pass
                    try:
                        subcol.prop(nodes['FoamSubsurf'].outputs[0],
                                    'default_value', text='Foam Subsurface')
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

                    ocean_mod = get_ocean_mod(ocean)
                    dp_mod = get_dynpaint_mod(ocean)
                    if ocean_mod != None:
                        subcol.prop(ocean_mod, 'foam_coverage')
                    if dp_mod != None:
                        subcol.prop(
                            dp_mod.canvas_settings.canvas_surfaces["Wetmap"], "dry_speed", text="Object Foam Fade")
                    if is_advanced:
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
                    if is_advanced:
                        try:
                            subcol.prop(nodes['NoiseScale'].outputs[0],
                                        'default_value', text='Noise Scale')
                        except:
                            pass
                    # subcol.label(text="Bubbles")
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

                    # subcol.prop(context.scene.aom_props,
                    #            'is_WindRippleUi', text='Wind Ripple Ui')

                    subcol = col.column()
                    subcol.label(text="Performance")
                    row = subcol.row(align=True)
                    row.label(text="All Bump                  ")
                    if self.is_all_bump_on(node_tree):
                        row.operator("aom.connect_bump",
                                     icon="PINNED", text="On", depress=True)
                        row.operator("aom.disconnect_bump",
                                     icon="UNPINNED", text="Off", depress=False)
                    else:
                        row.operator("aom.connect_bump",
                                     icon="PINNED", text="On", depress=False)
                        row.operator("aom.disconnect_bump",
                                     icon="UNPINNED", text="Off", depress=True)

                    row = subcol.row(align=True)
                    row.label(text="Wave Bump             ")
                    if not self.is_all_bump_on(node_tree):

                        row.operator("aom.connect_bumpwaves",
                                     icon="PINNED", text="On", emboss=False)
                        row.operator("aom.disconnect_bumpwaves",
                                     icon="UNPINNED", text="Off", emboss=False)
                    else:
                        if not self.is_wave_bump_on(node_tree):
                            row.operator("aom.connect_bumpwaves",
                                         icon="PINNED", text="On", depress=False)
                            row.operator("aom.disconnect_bumpwaves",
                                         icon="UNPINNED", text="Off", depress=True)
                        else:
                            row.operator("aom.connect_bumpwaves",
                                         icon="PINNED", text="On", depress=True)
                            row.operator("aom.disconnect_bumpwaves",
                                         icon="UNPINNED", text="Off", depress=False)

                    row = subcol.row(align=True)
                    row.label(text="Wind Ripples            ")
                    if not self.is_all_bump_on(node_tree):
                        row.operator("aom.windripples_on",
                                     icon="PINNED", text="On", emboss=False)
                        row.operator("aom.windripples_off",
                                     icon="UNPINNED", text="Off", emboss=False)
                    else:
                        if self.is_windripples_on(node_tree):
                            row.operator("aom.windripples_on",
                                         icon="PINNED", text="On", depress=True)
                            row.operator("aom.windripples_off",
                                         icon="UNPINNED", text="Off", depress=False)
                        else:
                            row.operator("aom.windripples_on",
                                         icon="PINNED", text="On", depress=False)
                            row.operator("aom.windripples_off",
                                         icon="UNPINNED", text="Off", depress=True)

                    '''row = subcol.row(align=True)
                    row.label(text="Wind Ripples            ")
                    row.operator("aom.windripples_on",
                                 icon="PINNED", text="On")
                    row.operator("aom.windripples_off",
                                 icon="UNPINNED", text="Off")'''

                    row = subcol.row(align=True)
                    row.label(text="Foam Bump             ")
                    if not self.is_foam_bump_on(node_tree):
                        row.operator("aom.connect_foambump",
                                     icon="PINNED", text="On", depress=False)
                        row.operator("aom.disconnect_foambump",
                                     icon="UNPINNED", text="Off", depress=True)
                    else:
                        row.operator("aom.connect_foambump",
                                     icon="PINNED", text="On", depress=True)
                        row.operator("aom.disconnect_foambump",
                                     icon="UNPINNED", text="Off", depress=False)

                    row = subcol.row(align=True)
                    row.label(text="Foam Displacement")
                    if not self.is_foam_disp_on(node_tree):
                        row.operator("aom.connect_foamdisp",
                                     icon="PINNED", text="On", depress=False)
                        row.operator("aom.disconnect_foamdisp",
                                     icon="UNPINNED", text="Off", depress=True)
                    else:
                        row.operator("aom.connect_foamdisp",
                                     icon="PINNED", text="On", depress=True)
                        row.operator("aom.disconnect_foamdisp",
                                     icon="UNPINNED", text="Off", depress=False)

                    row = subcol.row(align=True)
                    row.label(text="Transparency          ")
                    if not self.is_transparency_on(mat):
                        row.operator("aom.transparency_on",
                                     icon="PINNED", text="On", depress=False)
                        row.operator("aom.transparency_off",
                                     icon="UNPINNED", text="Off", depress=True)
                    else:
                        row.operator("aom.transparency_on",
                                     icon="PINNED", text="On", depress=True)
                        row.operator("aom.transparency_off",
                                     icon="UNPINNED", text="Off", depress=False)

                    row = subcol.row(align=True)
                    row.label(text="Dynamic Paint        ")
                    if self.is_dynpaint_off(get_dynpaint_mod(ocean)):
                        row.operator("aom.dynpaint_on",
                                     icon="PINNED", text="On", depress=False)
                        row.operator("aom.dynpaint_off",
                                     icon="UNPINNED", text="Off", depress=True)
                    else:
                        row.operator("aom.dynpaint_on",
                                     icon="PINNED", text="On", depress=True)
                        row.operator("aom.dynpaint_off",
                                     icon="UNPINNED", text="Off", depress=False)

    def is_all_bump_on(self, node_tree):
        nodes = node_tree.nodes
        links = node_tree.links
        # if 'WaterBump' in nodes:
        #    if 'Water' in nodes:
        for link in links:
            if link.to_node.name == 'WaterNormalIn':
                if link.from_node.name == 'WaterBump':
                    return True
        return False

    def is_wave_bump_on(self, node_tree):
        nodes = node_tree.nodes
        links = node_tree.links
        # if 'WaterBump' in nodes:
        #    if 'Water' in nodes:
        for link in links:
            if link.to_node.name == 'WaterBumpTexOut':
                if link.from_node.name == 'CombTex':
                    return True
        return False

    def is_windripples_on(self, node_tree):
        nodes = node_tree.nodes
        links = node_tree.links
        # if 'WaterBump' in nodes:
        #    if 'Water' in nodes:
        for link in links:
            if link.to_node.name == 'WaterBumpTexOut':
                if link.from_node.name == 'WindRipples':
                    return True
        return False

    def is_foam_bump_on(self, node_tree):
        nodes = node_tree.nodes
        links = node_tree.links
        # if 'WaterBump' in nodes:
        #    if 'Water' in nodes:
        for link in links:
            if link.to_node.name == 'FoamOut':
                if link.from_node.name == 'FoamBump':
                    return True
        return False

    def is_foam_disp_on(self, node_tree):
        nodes = node_tree.nodes
        links = node_tree.links
        # if 'WaterBump' in nodes:
        #    if 'Water' in nodes:
        for link in links:
            if link.from_node.name == 'Disp':
                return True
        return False

    def is_transparency_on(self, material):

        if not material.blend_method == 'OPAQUE':
            return True
        return False

    def is_dynpaint_off(self, mod):
        if not mod == None:
            if mod.show_viewport == False:
                if mod.show_render == False:
                    return True
        return False

        #  box = row.box()
        # row = layout.row(align=True)

    # Generate OCean  Button


class BE_PT_AdvOceanSpecial(bpy.types.Panel):
    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"
    bl_label = "Ocean Specials"
    bl_category = "Adv-Ocean"
    bl_options = {'DEFAULT_CLOSED'}

    @ classmethod
    def poll(cls, context):
        return hasattr(context.scene, "aom_props")

    def is_windripples_on(self, node_tree):
        nodes = node_tree.nodes
        links = node_tree.links
        # if 'WaterBump' in nodes:
        #    if 'Water' in nodes:
        for link in links:
            if link.to_node.name == 'WaterBumpTexOut':
                if link.from_node.name == 'WindRipples':
                    return True
        return False

    def draw(self, context):

        if hasattr(context.scene, "aom_props"):
            aom_props = context.scene.aom_props
            layout = self.layout

            layout.use_property_split = True
            layout.use_property_decorate = False  # No animation.

            flow = layout.grid_flow(row_major=True, columns=0,
                                    even_columns=False, even_rows=False, align=True)
            col = flow.column()

            subcol = col.column()

            ocean = get_active_ocean(context)
            if ocean != None:
                mods = ocean.modifiers

                subcol = subcol.box()
                subcol.label(text='Loop')
                subcol.operator("aom.loop", icon="CON_FOLLOWPATH")
                if "OceanLoop" in mods:
                    subcol.operator("aom.removeloop", icon="CON_FOLLOWPATH")

                subcol = col.column()
                subcol = subcol.box()
                subcol.label(text='Spray')
                subcol.operator("aom.spray", icon="MOD_FLUIDSIM")

                boo, mod = in_mods("Spray", mods)
                if boo:
                    subcol.operator("aom.remove_spray", icon="MOD_FLUIDSIM")

                    subcol.label(
                        text='Look in the modifiers tap for settings. Instanced object in "Spray" collection.', icon='QUESTION')
                    subcol.label(
                        text='Probably you need to change a value to kick the instancing.', icon='ERROR')

                subcol = col.column()
                subcol = subcol.box()

                subcol.label(text='Object Ripples')
                subcol.operator("aom.ripples", icon="MOD_INSTANCE")
                boo, mod = in_mods_multi("Ripples", mods)
                if boo:
                    subcol.operator("aom.remove_ripples", icon="MOD_INSTANCE")
                    subcol.label(
                        text='Look in the modifiers tap for settings.', icon='QUESTION')
                    # ripple options

                    if mod['Input_6'] == None:
                        subcol.label(
                            text='Please set an object in the  "Ripples" modifier!', icon='ERROR')

            #   subcol = col.column()
                subcol = subcol.box()

                subcol.label(text='Wind Ripples')
                subcol.operator("aom.windripples_on",
                                icon="OUTLINER_DATA_LIGHTPROBE")
                '''
                row.operator("aom.windripples_on",
                                 icon="PINNED", text="On")
                row.operator("aom.windripples_off",
                                icon="UNPINNED", text="Off")'''
                node_tree = ocean.material_slots[0].material.node_tree
                nodes = node_tree.nodes
                # nodes["AddWindRipples"].inputs[0].default_value > 0:
                if self.is_windripples_on(node_tree):
                    subcol.operator("aom.windripples_off",
                                    icon="OUTLINER_DATA_LIGHTPROBE")
                    subcol.prop(context.scene.aom_props,
                                'is_WindRippleUi', text='Wind Ripple Ui')

                    if aom_props.is_WindRippleUi:
                        if "WindRipples" in nodes:
                            subcol.prop(nodes['WindRipples'].inputs['RippleHeight'],
                                        'default_value', text='RippleHeight')
                            subcol.prop(nodes['WindRipples'].inputs['RippleTexScale'],
                                        'default_value', text='Ripple TexScale')
                            subcol.prop(nodes['WindRipples'].inputs['Roughness'],
                                        'default_value', text='Ripple Roughness')
                            subcol.prop(nodes['WindRipples'].inputs['RipplesDeform'],
                                        'default_value', text='Ripple Deform')

                            subcol.prop(nodes['WindRipples'].inputs['Direction'],
                                        'default_value', text='Rotation')
                            subcol.prop(nodes['WindRipples'].inputs['Ripplespeed'],
                                        'default_value', text='Ripple Speed')

                            subcol.prop(nodes['WindRipples'].inputs['Coverage'],
                                        'default_value', text='Coverage')
                            subcol.prop(nodes['WindRipples'].inputs['PatchSize'],
                                        'default_value', text='Patch Size')
                            subcol.prop(nodes['WindRipples'].inputs['Morphspeed'],
                                        'default_value', text='Morph Speed')
                            subcol.prop(nodes['WindRipples'].inputs['MappingMoveSpeed'],
                                        'default_value', text='Patch Speed')


def in_mods_multi(str, mods):
    if str in mods.active.name:
        return True, mods.active
    for mod in mods:
        if str in mod.name:
            a = True
            return a, mod
    return False, None


def in_mods(str, mods):
    for mod in mods:
        if str in mod.name:
            a = True
            return a, mod
    return False, None


def get_ocean_mod(ocean):
    for mod in ocean.modifiers:
        if mod.type == 'OCEAN':
            return mod
    return None


def get_dynpaint_mod(ocean):
    for mod in ocean.modifiers:
        if mod.type == 'DYNAMIC_PAINT':
            return mod
    return None



####UI float object

class BE_PT_FloatObj_UI(bpy.types.Panel):
    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"
    bl_label = "Float Parameters"
    bl_category = "Adv-Ocean"
    bl_options = {'DEFAULT_CLOSED'}

    @ classmethod
    def poll(cls, context):
        return hasattr(context.scene, "aom_props")

    def get_float_mod(self, context, oc):
        candidate = context.object
        #print (f'in get mod {oc.name} candidate {candidate.name}')
        for mod in oc.modifiers:
            #print (f'in Schleife {mod.name} candidate {candidate.name}')
            if hasattr(mod, 'node_group'):
                #print (f'has node_group mod {mod.name} candidate {mod.node_group.name}')
                if mod.node_group.name ==  'AOMGeoFloat' or mod.node_group.name ==  'AOMGeoFree':
                    #print (f'found modifier {mod.node_group.name}')
                    if mod["Socket_4"] == candidate:
                        #print (f'found candidate {candidate.name}')
                        return mod 
        return None
        
    def get_waveSim_mod(self, context, oc):
        candidate = context.object
        #print (f'in get mod {oc.name} candidate {candidate.name}')
        for mod in oc.modifiers:
            #print (f'in Schleife {mod.name} candidate {candidate.name}')
            if hasattr(mod, 'node_group'):
                #print (f'has node_group mod {mod.name} candidate {mod.node_group.name}')
                if mod.node_group.name ==  'AOM_ObjectWaveSim':
                    #print (f'found modifier {mod.node_group.name}')
                    return mod 
        return None
    
        
        
        
        
    
    def draw(self, context):

        if hasattr(context.scene, "aom_props"):
            aom_props = context.scene.aom_props
            layout = self.layout

            layout.use_property_split = True
            layout.use_property_decorate = False  # No animation.

            flow = layout.grid_flow(row_major=True, columns=0,
                                    even_columns=False, even_rows=False, align=True)
            col = flow.column()

            subcol = col.column()

            ocean = get_active_ocean(context)
            if ocean != None:
                mods = ocean.modifiers

                #subcol = subcol.box()
                
                mod = self.get_float_mod(context, ocean)
                
                
                
                #for inp in mod.keys():
                if mod != None:
                    txt = 'fail'
                    if mod['Socket_2']:
                        if mod['Socket_3'] != None:
                            txt = 'Settings for ' + mod['Socket_3'].name
                        else:
                            txt = 'Add Visibile Collection'
                    else:
                        if mod['Socket_1'] != None:
                            txt = 'Settings for ' + mod['Socket_1'].name
                        else:
                            txt = 'Add Visible Object'
                        
                    subcol.label(text=txt)
                    
                    ##controller obj visibility
                    cage = mod["Socket_4"]
                    subcol.prop(data=cage, property="show_in_front", text = "Controller in front")
                    
                    #print(f'mod keys are{mod.keys()}')
                    for inp in mod.node_group.interface.items_tree:
                        if inp.bl_socket_idname != 'NodeSocketGeometry':
                            if inp.bl_socket_idname == 'NodeSocketCollection':
                                ##collection prop, because greyed out
                                prop = '["' + inp.identifier +  '"]'
                                subcol.prop_search(data= mod, property=prop, search_data = bpy.data, search_property='collections', text=inp.name)
                            else:
                                ###main list
                                prop = '["' + inp.identifier +  '"]'
                                subcol.prop(data= mod, property=prop, text=inp.name)
                
                
                
                '''mod = self.get_waveSim_mod(context, ocean)    
                if mod != None:
                    subcol.label(text=)
                    for inp in mod.node_group.interface.items_tree:
                        if inp.bl_socket_idname != 'NodeSocketGeometry':        
                            prop = '["' + inp.identifier +  '"]'
                            subcol.prop(data= mod, property=prop, text=inp.name)'''
                    
                    #subcol.prop_search(data= mod, property=prop, search_data = bpy.data, search_property='collections', text='test')
                    
            

                
                
                #subcol.label(text='FloatParameters')
                #subcol.operator("aom.loop", icon="CON_FOLLOWPATH")