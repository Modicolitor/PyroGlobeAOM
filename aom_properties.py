import bpy
from bpy.types import Scene, Image, Object, PropertyGroup


class AOMPropertyGroup(bpy.types.PropertyGroup):
    # IgnoreMainCut = bpy.props.BoolProperty(
    #    name="Keep Connector", default=False)

    OceanFoamBool: bpy.props.BoolProperty(
        name="OceanFoamBool", default=True)
    ObjFoamBool: bpy.props.BoolProperty(
        name="ObjFoamBool", default=True)

    AdvMaterialOptions: bpy.props.BoolProperty(
        name="OceanFoamBool", default=False)

    OceAniSpeed: bpy.props.FloatProperty(
        name="ObjFoamSpeed", default=1)

    OceAniStart: bpy.props.IntProperty(  # definiere neue Variable, als integer ...irgendwie
        name="Start Frame",  # was soll im eingabefeld stehen
        default=1,  # start wert
        # min=0,     ## kleinster Wert
        # max=10,    ## größter Wert
        description="Animation Start Frame")

    # Define End Frame Animat
    OceAniEnd: bpy.props.IntProperty(  # definiere neue Variable, als integer ...irgendwie
        name="End Frame",  # was soll im eingabefeld stehen
        default=250,  # start wert
        # min=0,     ## kleinster Wert
        # max=10,    ## größter Wert
        description="Animation End Frame")

    LastNamNum: bpy.props.IntProperty(default=-1)

    MaterialSel: bpy.props.EnumProperty(
        name='Material Selector',
        description='Show available Materials',
        default='1',
        items=[('1', 'Ocean 3.0', ''),
               ('2', 'Ocean 2.9', ''),
               ('3', 'Legacy Improved', ''),
               ('4', 'Legacy', ''),
               ])

    PresetSel: bpy.props.EnumProperty(
        name='Global Presets',  # SingleCoupltypes
        description='Global Presets',
        default='2',
        items=[('1', 'Lovely', ''),
               ('2', 'Lively', ''),
               ('3', 'Stormy', ''),
               ('4', 'Shallow Lovely', ''),
               ('5', 'Shallow Lively', ''),
               ('6', 'Shallow Stormy', ''),
               ('7', 'Established Lovely', ''),
               ('8', 'Established Lively', ''),
               ('9', 'Established Stormy', ''),
               ('10', 'Abstract1', ''),
               ('11', 'Abstract2', ''),
               ('12', 'Abstract3', ''),
               ]

    )


class AOMObjProperties(bpy.types.PropertyGroup):
    is_ocean: bpy.props.BoolProperty(default=False)
    is_floatcage: bpy.props.BoolProperty(default=False)
    ocean_id: bpy.props.IntProperty(default=-1)
    interaction_type: bpy.props.StringProperty(default='')
    float_parent_id: bpy.props.IntProperty(default=-1)
    namenum: bpy.props.IntProperty(default=-1)
    is_loop: bpy.props.BoolProperty(
        name="Is Looping", default=False)
    ripple_parent = bpy.props.PointerProperty(default=None)


'''
class FloatdataItem(bpy.types.PropertyGroup):
    ocean_id: bpy.props.StringProperty(default=None)
    float_parent: bpy.props.StringProperty(default=None)
    namenum: bpy.props.IntProperty(default=99999)
    # obj: bpy.props.PointerProperty()
'''
# bpy.types.Scene.my_settings = bpy.props.CollectionProperty(type=SceneSettingItem)


# Assume an armature object selected.
#print("Adding 2 values!")

# my_item = bpy.context.scene.my_settings.add()
# my_item.name = "Spam"
# my_item.value = 1000

# my_item = bpy.context.scene.my_settings.add()
# my_item.name = "Eggs"
# my_item.value = 30

# for my_item in bpy.context.scene.my_settings:
#    print(my_item.name, my_item.value)
