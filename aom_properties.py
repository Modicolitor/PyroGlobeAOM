import bpy
from bpy.types import Scene, Image, Object, PropertyGroup


class AOMPropertyGroup(bpy.types.PropertyGroup):
    IgnoreMainCut = bpy.props.BoolProperty(
        name="Keep Connector", default=False)

    Floatobjs = bpy.props.EnumProperty(
        name='',  # SingleCoupltypes
        description='List of forms avaiable in single connector mode',
        items=[('1', 'Flat', ''),
               ('2', 'Joint', ''),
               ]
    )


class FloatdataItem(bpy.types.PropertyGroup):
    name: bpy.props.StringProperty(default="Unknown")
    namenum: bpy.props.IntProperty(default=99999)
    #obj: bpy.props.PointerProperty()

#bpy.types.Scene.my_settings = bpy.props.CollectionProperty(type=SceneSettingItem)


# Assume an armature object selected.
print("Adding 2 values!")

#my_item = bpy.context.scene.my_settings.add()
#my_item.name = "Spam"
#my_item.value = 1000

#my_item = bpy.context.scene.my_settings.add()
#my_item.name = "Eggs"
#my_item.value = 30

# for my_item in bpy.context.scene.my_settings:
#    print(my_item.name, my_item.value)
