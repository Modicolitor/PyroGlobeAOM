import bpy


bl_info = {  # für export als addon
    "name": "Blelper",
    "author": "Modicolitor",
    "version": (2, 93, 3),
    "blender": (2, 93, 0),
    "location": "View3D > Tools",
    "description": "Don't Do the same thing over and over",
    "category": "Object"}


# Properties saved with blender

class BlelperPropertyGroup(bpy.types.PropertyGroup):

    audio: bpy.props.BoolProperty(
        name="Audio", default=False)

    alpha: bpy.props.BoolProperty(
        name="Audio", default=False)


bpy.types.Scene.blelper = bpy.props.PointerProperty(
    type=BlelperPropertyGroup)


# operator

class BE_OT_SetVideo(bpy.types.Operator):
    '''Sets video settings.'''
    bl_label = "Video Settings"
    bl_idname = "blelp.setvideo"
    bl_options = {"REGISTER", "UNDO"}

    def execute(self, context):
        context.scene.render.filepath = "//Render\\"
        context.scene.render.image_settings.file_format = 'FFMPEG'
        context.scene.render.ffmpeg.format = 'MPEG4'
        context.scene.render.ffmpeg.constant_rate_factor = 'HIGH'
        if context.scene.blelper.audio:
            context.scene.render.ffmpeg.audio_codec = 'AAC'
        return{"FINISHED"}


class BE_OT_SetPNG(bpy.types.Operator):
    '''Sets video settings.'''
    bl_label = "Video Settings"
    bl_idname = "blelp.setpng"
    bl_options = {"REGISTER", "UNDO"}

    def execute(self, context):
        context.scene.render.image_settings.file_format = 'PNG'
        context.scene.render.image_settings.compression = 85

        if context.scene.blelper.alpha:
            context.scene.render.image_settings.color_mode = 'RGBA'
        else:
            context.scene.render.image_settings.color_mode = 'RGB'
        return{"FINISHED"}


# ui

class BE_PT_BlelperRenderUI(bpy.types.Panel):
    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"
    bl_label = "RenderSettings"
    bl_category = "Blelper"
    bl_options = {'DEFAULT_CLOSED'}

    @ classmethod
    def poll(cls, context):
        return hasattr(context.scene, "aom_props")

    def draw(self, context):

        blelper = context.scene.blelper
        layout = self.layout

        layout.use_property_split = True
        layout.use_property_decorate = False  # No animation.

        flow = layout.grid_flow(row_major=True, columns=0,
                                even_columns=False, even_rows=False, align=True)
        col = flow.column()

        subcol = col.column()

        subcol.operator("blelper.setvideo", icon="OUTLINER_OB_CAMERA")
        subcol.property(blelper, "audio")
        subcol.operator("blelper.setpng", icon="OUTLINER_OB_IMAGE")
        subcol.property(blelper, "alpha")


# Register Unregister in Blender
classes = (BlelperPropertyGroup,
           BE_PT_BlelperRenderUI,
           BE_OT_SetVideo,
           BE_OT_SetPNG
           )

register, unregister = bpy.utils.register_classes_factory(classes)
