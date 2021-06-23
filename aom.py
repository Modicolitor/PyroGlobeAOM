from bpy.props import *
import bpy
import mathutils
import copy
from .aom_def import is_ocean, is_floatcage
#from .aom_properties import FloatdataItem
from .aom_materials import AOMMatHandler
from .aom_presets import AOMPreset_Handler
from .aom_geonodes import AOMGeoNodesHandler
from .aom_properties import AOMPropertyGroup
from .aom_properties import AOMObjProperties

bl_info = {  # für export als addon
    "name": "Advanced Ocean Modifier",
    "author": "Modicolitor",
    "version": (3, 00),
    "blender": (2, 93, 0),
    "location": "View3D > Tools",
    "description": "Create an Ocean with all Material properties set and add as many floating Objects as you like.",
    "category": "Object"}


# ob = bpy.context.object
# scene = bpy.context.scene
# active = bpy.context.active_object


# bpy.context.scene.render.engine = 'CYCLES' #stellt auf cycles um


# Namen der Hauptcollections
MColName = "AdvOceanCollections"  # name der Übercollection
Brush = "OceanBrushes"  # Name des Brushfolders
Paint = "Paint"
Wave = "Wave"


def GenOcean(context):

    ########2.8. collections ###############################################
    # initial die standard collection struktur: hauptordner, brushes paint und wave collections

    scene = bpy.context.scene
    data = bpy.data

    # siehe ganz oben nach import definition der Namen

    # macht die übercollection
    if bpy.data.collections.find(MColName) < 0:
        collection = bpy.data.collections.new(
            name=MColName)  # makes collection
        # putts in the mastercollection of this scene
        scene.collection.children.link(collection)

    if bpy.data.collections.find(Brush) < 0:  # gibts schon den Brushordner
        collection = bpy.data.collections.new(name=Brush)  # makes collection
        # putts in the mastercollection of this scene
        scene.collection.children[MColName].children.link(collection)

    if bpy.data.collections.find(Paint) < 0:  # gibts schon den Brushordner
        collection = bpy.data.collections.new(name=Paint)  # makes collection
        scene.collection.children[MColName].children[Brush].children.link(
            collection)

    if bpy.data.collections.find(Wave) < 0:  # gibts schon den Brushordner
        collection = bpy.data.collections.new(name=Wave)  # makes collection
        scene.collection.children[MColName].children[Brush].children.link(
            collection)

    # copies Advances Oceans to the Main Ocean Collection

    # set active colection
    context.view_layer.active_layer_collection = context.view_layer.layer_collection.children[
        MColName]

    bpy.ops.mesh.primitive_plane_add()
    ob = context.object
    ob.name = "AdvOcean"
    newname = ob.name
    ob.aom_data.ocean_id = get_ocean_id(context)
    ob.aom_data.is_ocean = True

    # data.collections[MColName].objects.link(data.objects['AdvOcean'])

    # Ocean Modifier
    bpy.ops.object.modifier_add(type='OCEAN')
    ob.modifiers["Ocean"].choppiness = 0.80
    ob.modifiers["Ocean"].resolution = 15
    ob.modifiers["Ocean"].wind_velocity = 8.68
    ob.modifiers["Ocean"].wave_scale = 1.3
    ob.modifiers["Ocean"].wave_scale_min = 0.01
    ob.modifiers["Ocean"].wave_alignment = 0.2
    ob.modifiers["Ocean"].random_seed = 1
    ob.modifiers["Ocean"].use_foam = True
    ob.modifiers["Ocean"].use_normals = True
    ob.modifiers["Ocean"].foam_layer_name = "foam"

    # dieser wert bestimmt die Menge an Schaum, Lohnt sich bestimmt auszulagern
    #context.object.modifiers["Ocean"].foam_coverage = 0.6

    start, end = get_time_animation_keys(context)

    # Animation
    set_ocean_keyframes(context, context.object,
                        ob.modifiers["Ocean"], start, end, True)

    #print(get_ocean_keyframes(context, context.object))

    #####Dynamic Paint modifier und einstellungen##########

    ##dynamic paint#####
    bpy.ops.object.modifier_add(type='DYNAMIC_PAINT')
    ob.modifiers["Dynamic Paint"].ui_type = 'CANVAS'
    bpy.ops.dpaint.type_toggle(type='CANVAS')
    canvas = ob.modifiers["Dynamic Paint"].canvas_settings.canvas_surfaces

    # waves

    canvas["Surface"].name = "Waves"
    canvas["Waves"].surface_type = 'WAVE'
    canvas["Waves"].use_antialiasing = True
    canvas["Waves"].wave_speed = 0.4

    bpy.ops.dpaint.surface_slot_add()
    ob.modifiers["Dynamic Paint"].canvas_settings.canvas_surfaces["Surface"].name = "Wetmap"
    bpy.ops.dpaint.output_toggle(output='A')    # dp paintmap wird erzeugt
    bpy.ops.dpaint.output_toggle(output='B')    # dp wetmap wird erzeugt
    canvas["Wetmap"].use_antialiasing = True  # antialising hacken setzt
    # canvas["Wetmap"].preview_id = 'WETMAP'
    canvas["Wetmap"].dry_speed = 100
    canvas["Wetmap"].use_spread = True
    ob.modifiers["Ocean"].use_normals = True
    canvas["Wetmap"].use_dissolve = True
    canvas["Wetmap"].dissolve_speed = 80
    canvas["Wetmap"].spread_speed = 0.3

    # die collections werden zugeordnet zu den Dynamic paint canvases
    canvas['Wetmap'].brush_collection = bpy.data.collections["Paint"]
    canvas['Waves'].brush_collection = bpy.data.collections["Wave"]

    return ob


def get_time_animation_keys(context):
    # *2  is the bjoern faktor
    f = context.scene.aom_props.OceAniSpeed / (2*context.scene.render.fps)
    start = context.scene.aom_props.OceAniStart
    end = context.scene.aom_props.OceAniEnd

    time = (end-start)*f
    startkey = (start, time)
    endkey = (end, 2*time)
    return startkey, endkey


def CollectionIndex(ColName):
    scene = bpy.context.scene
    data = bpy.data
    context = bpy.context

    a = 0
    cols = bpy.data.collections
    while a <= len(cols)-1:
        print("a" + str(a) + str(cols[a].name))
        if cols[a].name == str(ColName):
            return a

        a += 1

    return -1


def get_ocean_id(context):
    l = []
    for ob in context.scene.objects:
        if is_ocean(context, ob):
            l.append(ob.aom_data.ocean_id)
    l.sort()  # bug in python 3. update
    # print(l)
    if len(l) == 0:
        return 0
    else:
        #largest = -1
        # for i in l:
        #    if i > largest:
        #        largest = i
        #print(f'largest id is {l[len(l)-1]}')
        return l[len(l)-1]+1  # largest + 1


def get_ocean_from_id(context, ocean_id):

    for ob in context.scene.objects:
        if ob.aom_data.ocean_id == ocean_id:
            print(f"ocean found: {ob}")
            return ob


# neue Floatvariable für die min größe
bpy.types.Scene.WeatherX = FloatProperty(
    name="Weather",
    default=0.0,
    min=0.0,
    max=1.0,
    description="From Lovely (0) to Stormy (1)")


def initialize_addon(context):

    bpy.types.Scene.aom_props = bpy.props.PointerProperty(
        type=AOMPropertyGroup)

    bpy.types.Object.aom_data = bpy.props.PointerProperty(
        type=AOMObjProperties)

    context.scene.eevee.use_ssr = True
    context.scene.eevee.use_ssr_refraction = True


def remove_oceankeyframes(context, ocean):
    if hasattr(ocean.animation_data, "action"):

        for fcu in ocean.animation_data.action.fcurves[:]:
            ocean.animation_data.action.fcurves.remove(fcu)
            #
            # for keyframe in fcu.keyframe_points:
            #    fcu.keyframe_points.remove(keyframe)


def update_OceAniFrame(context, ocean):

    remove_oceankeyframes(context, ocean)
    start, end = get_time_animation_keys(context)
    #start = (context.scene.aom_props.OceAniStart, 1)
    # end = (context.scene.aom_props.OceAniEnd, get_animationlengthfromEnd(
    #    context, context.scene.aom_props.OceAniEnd))
    # Animation
    set_ocean_keyframes(context, context.object,
                        ocean.modifiers["Ocean"], start, end, True)

    canvas = ocean.modifiers['Dynamic Paint'].canvas_settings
    OceAniStart = context.scene.aom_props.OceAniStart
    OceAniEnd = context.scene.aom_props.OceAniEnd

    for can in canvas.canvas_surfaces:
        can.frame_start = OceAniStart
        can.frame_end = OceAniEnd

    ocean.modifiers["Ocean"].frame_start = OceAniStart
    ocean.modifiers["Ocean"].frame_end = OceAniEnd


def floatablelist(context, list):
    floatable = []
    for ob in list:
        if not is_ocean(context, ob) and not is_floatcage(context, ob) and ob.type == 'MESH':
            floatable.append(ob)
            print(f"Floatables are: {ob.name}")
    return floatable


def oceanlist(context, list):
    oceans = []
    for ob in list:
        if is_ocean(context, ob):
            oceans.append(ob)
    return oceans


def get_new_namenum(context):
    if context.scene.aom_props.LastNamNum == -1:
        context.scene.aom_props.LastNamNum = 2
    else:
        context.scene.aom_props.LastNamNum += 1
    return context.scene.aom_props.LastNamNum


# lasse soviele objecte wie du willst auf einmal floaten


def FloatSel(context, ocean):  # fügt dann ein Ei hinzu das zum Brush wird
    data = bpy.data

    active = context.view_layer.objects.active
    nameori = active.name
    print("nameori: " + nameori)

    sellistori = context.selected_objects[:]

    sellist = floatablelist(context, sellistori)

    #print("sellist: " + str(sellist))

    for a, obj in enumerate(sellist):
        # bpy.context.selected_objects = sellist
        active = obj
        print(obj.name + " For schleife" + str(a))

        context.view_layer.objects.active = RemoveInterActSingle(context, obj)

        Namenum = get_new_namenum(context)

        # len(
        # ocean.modifiers['Dynamic Paint'].canvas_settings.canvas_surfaces)

        print("active: " + active.name + " obj name: " +
              obj.name + " nach else active" + str(a))
        #########

        col = bpy.data.collections

        context.view_layer.objects.active = obj
        # index = CollectionIndex('Paint')
        # print("Paintindex: " + str(index))

        if col.find('Paint') > 0:
            if obj.name in col['Paint'].objects:
                print("es gibt schon das Object in der Paintcollection")
            else:
                print(obj.name + "wird in Paint verschoben")
                col['Paint'].objects.link(obj)
        else:
            print("Es gibt keine Paint Collection in Advanced Ocean Ordner")

        if col.find('Wave') > 0:
            if obj.name in col['Wave'].objects:
                print("es gibt schon das Object in der Paintcollection")
            else:
                print(obj.name + "wird in Wave verschoben")
                col['Wave'].objects.link(obj)
        else:
            print("Es gibt keine Wave Collection in Advanced Ocean Ordner")

        # Dynamic paint

        obj.modifiers.new(name='Dynamic Paint', type='DYNAMIC_PAINT')
        obj.modifiers['Dynamic Paint'].ui_type = 'BRUSH'

        bpy.ops.dpaint.type_toggle(type='BRUSH')
        try:
            # Paint source auf Mesh Volume and Proximity
            context.object.modifiers["Dynamic Paint"].brush_settings.paint_source = 'VOLUME_DISTANCE'
            print('try ob dynamic paint brush richtig ist, hat keinen !fehler ignoriert')
        except:
            print("Toggle Dynamic Paint add Brush exception raised")
            bpy.ops.object.modifier_remove(modifier="Dynamic Paint")
            bpy.ops.object.modifier_add(type='DYNAMIC_PAINT')
            obj.modifiers["Dynamic Paint"].ui_type = 'BRUSH'
            bpy.ops.dpaint.type_toggle(type='BRUSH')

        context.view_layer.objects.active = obj

        print(str(obj.modifiers['Dynamic Paint'].brush_settings) +
              "modifierliste des aktuellen objectes")

        obj.modifiers["Dynamic Paint"].brush_settings.paint_source = 'VOLUME_DISTANCE'
        obj.modifiers["Dynamic Paint"].brush_settings.paint_distance = 1.0
        obj.modifiers["Dynamic Paint"].brush_settings.wave_factor = 1

        print('jetzt gibt es rotation auf objekt in der schleifen nr.' + str(a))
        print('das active object for dem rotation constraint' + obj.name)

        # generate empty for loc rot tranfer via parent
        bpy.ops.object.empty_add(
            type='PLAIN_AXES', align='WORLD', location=obj.location)
        empty = context.object
        empty.name = "Transferempty.00"+str(Namenum)

        # maker collection
        colweight = data.collections.new(
            "Weight.00"+str(Namenum))  # collection erschaffen
        context.scene.collection.children[MColName].children[Brush].children.link(
            colweight)  # in die Brush Collection der aktuellen Szene

        # move empty to collection and remove from old place
        data.collections[colweight.name].objects.link(empty)
        for col in empty.users_collection:  # suchen der collection in dem der Cage zuerste generiert wurde dann löschen des object instance
            if col.name != "Weight.00"+str(Namenum):
                col.objects.unlink(empty)
                # print("Cage entfernt aus " + str(col.name))
                break

        # die constraints auf das Empty packen
        conRot1 = empty.constraints.new('COPY_ROTATION')
        conRot1.target = ocean
        conRot1.subtarget = "dp_weight.00" + str(Namenum)
        conRot1.use_z = False
        conRot1.invert_x = True
        conRot1.invert_y = True

        contLoc = empty.constraints.new('COPY_LOCATION')
        contLoc.target = ocean
        contLoc.subtarget = "dp_weight.00" + str(Namenum)

        conRot2 = empty.constraints.new('COPY_ROTATION')
        # see setting at the endof the function

        print('das active object nach dem rotation constraint' + obj.name)

        obj.parent = empty

        obj.location = mathutils.Vector((0, 0, 0))

        #####################################################
        # ab hier der cage des objctes
        #####################################################

        # holllt die dimensionen der aktiven elemente .... muss bestimmt dimensionen des selected obejct im aktuellen schleifen durch lauf sein
        locx = empty.location[0]
        locy = empty.location[1]
        locz = empty.location[2]

        print("locx " + str(locx))
        dx = obj.dimensions[0]
        dy = obj.dimensions[1]

        print(dx)
        print(dy)
        # generiert Name.FloatCage
        name = obj.name
        print(name)
        bpy.ops.mesh.primitive_uv_sphere_add(location=empty.location)
        cage = context.object
        cage.name = name + ".FloatAnimCage"
        cage.aom_data.is_floatcage = True
        cage.display_type = 'WIRE'
        cage.hide_render = True
        MatHandler = AOMMatHandler(context)
        mat = MatHandler.make_cagematerial(cage)

        if dx > dy:
            print(obj.name + "x")
            dy = 1.0*dy
            dx = 1.0*dx
            cage.scale[0] = dx
            cage.scale[1] = dx
        else:
            print(obj.name + "y")
            dy = 1.0*dy
            dx = 1.0*dx
            print(dy)
            cage.scale[0] = dy
            cage.scale[1] = dy

        # x = bpy.data.objects["Cube"]
        # x.location = (5,0,0)

        # bpy.data.objects[name].location = (locx,locy,locz)
 #            bpy.data.objects[name].location = locy
 #            bpy.data.objects[name].location = locz

        bpy.ops.transform.resize(value=(1, 1, 7), constraint_axis=(
            False, False, True))  # in z=richtung 3 hoch machen

        # bpy.ops.object.transform_apply(location=True, rotation=True, scale=True) ### apply rotation, scale, location

        context.object.display_type = 'WIRE'
        # das zum Brush wird zugefügt
        bpy.ops.object.modifier_add(type='DYNAMIC_PAINT')
        context.object.modifiers["Dynamic Paint"].ui_type = 'BRUSH'
        bpy.ops.dpaint.type_toggle(type='BRUSH')
        #bpy.data.objects[name].hide_render = True

        # jedesobject bekommt seine eigene Collection

        # index = CollectionIndex('OceanBrushes')

        # colweight = data.collections.new("Weight.00"+str(Namenum))  ###collection erschaffen
        # bpy.context.scene.collection.children[MColName].children[Brush].children.link(colweight) ### in die Brush Collection der aktuellen Szene

        data.collections[colweight.name].objects.link(cage)
        for col in cage.users_collection:  # suchen der collection in dem der Cage zuerste generiert wurde dann löschen des object instance
            if col.name != "Weight.00"+str(Namenum):
                data.collections[col.name].objects.unlink(cage)
                # print("Cage entfernt aus " + str(col.name))
                break

        # helper transferEmpty as parent of object

        # print(active.name + "Akrives Objekt vor der AdvOcean")
        #################################################################################################################
        #################################################################################################################
        #ocean = data.objects['AdvOcean']
        context.view_layer.objects.active = ocean

        # Namenum = len(
        #    bpy.data.objects['AdvOcean'].modifiers['Dynamic Paint'].canvas_settings.canvas_surfaces)

        bpy.ops.dpaint.surface_slot_add()  # erzeugt neue Canvas

        try:
            context.object.modifiers["Dynamic Paint"].canvas_settings.canvas_surfaces["Surface.00"+str(
                Namenum)].name = "Weight.00"+str(Namenum)
        except:
            context.object.modifiers["Dynamic Paint"].canvas_settings.canvas_surfaces[
                "Surface"].name = "Weight.00"+str(Namenum)

        ocean.modifiers["Dynamic Paint"].canvas_settings.canvas_surfaces["Weight.00"+str(
            Namenum)].surface_type = 'WEIGHT'  # setzt den typ auf weight paint
        ocean.modifiers["Dynamic Paint"].canvas_settings.canvas_surfaces["Weight.00"+str(
            Namenum)].use_dissolve = True        # fade option wird Aktiv geklickt... das weight paint verschwindet
        ocean.modifiers["Dynamic Paint"].canvas_settings.canvas_surfaces["Weight.00"+str(
            Namenum)].dissolve_speed = 1         # nach 1 Frame
        # dynamic paint output  Vertex group wird erstellt  <--  könnte später ein Bug geben wenn schon weight paint existiert
        bpy.ops.dpaint.output_toggle(output='A')
        ocean.modifiers["Dynamic Paint"].canvas_settings.canvas_surfaces["Weight.00"+str(
            Namenum)].output_name_a = "dp_weight.00"+str(Namenum)
        bpy.ops.dpaint.output_toggle(output='A')
        ocean.modifiers["Dynamic Paint"].canvas_settings.canvas_surfaces["Weight.00"+str(
            Namenum)].brush_collection = bpy.data.collections["Weight.00"+str(Namenum)]
        # context.object.modifiers["Dynamic Paint"].canvas_settings.canvas_surfaces["Weight.00"+str(Namenum)].show_preview = False

        # for i in context.object.modifiers["Dynamic Paint"].canvas_settings.canvas_surfaces:
        #    print(i)

        ################Gruppe fehlt hier--> !!!##############
        conRot2.target = bpy.data.objects[name]
        conRot2.use_z = True
        conRot2.use_y = False
        conRot2.use_x = False

        active = sellist[a]

        # register in objects flotdata
        print(f"add data to {context.object}")
        print("____________________________________________________________________________________________________________________________________________________________")

        active.aom_data.interaction_type = 'FLOAT'
        active.aom_data.float_parent_id = ocean.aom_data.ocean_id
        active.aom_data.namenum = Namenum


def remove_floats(context, ocean):
    ocean_id = ocean.aom_data.ocean_id

    for ob in context.scene.objects[:]:
        if ob.aom_data.float_parent_id == ocean_id:
            RemoveInterActSingle(context, ob)

##############################################################
# erzeugt Schaum um statische obejkten
# Erzeugt in einem Statischen Objekt einen Brush der die wetmap an
# und fügt die paintgruppe hinzu
#############


def BrushStatic(context):
    scene = bpy.context.scene
    data = bpy.data
    context = bpy.context

    sellistori = bpy.context.selected_objects[:]
    #sellist = []

    sellist = floatablelist(context, sellistori)

    '''
    for obj in sellistori:
        if obj.name == "AdvOcean" or ".FloatAnimCage" in obj.name or obj.type != 'MESH':
            print(str(obj.name) +
                  " does not float!!, wird nicht in die Staticliste aufgenommen")
        else:
            sellist.append(obj)
            print(str(obj.name) + " wurde in die staticliste zugefügt")
    '''
    # print("sellist: " +str(sellist) )

    # for schleife; range = in der reinfolge; len = zähle alle objekte in Array
    for a, obj in enumerate(sellist):
        # wenn diese Object floated erstmal das floaten entfernen
       # bpy.context.view_layer.objects.active = obj
       # if obj.name in bpy.data.collections["Paint"].objects or obj.name in bpy.data.collections["Wave"].objects:
        context.view_layer.objects.active = RemoveInterActSingle(context, obj)
        obj.aom_data.interaction_type = 'STATIC'

       # else:
        #    print(str(obj.name) + "wird nicht an Remove single weiter gegeben")
        try:  # gibt es schon einen Dynmaic Paint Brush???
            context.object.modifiers["Dynamic Paint"].brush_settings.paint_source = 'VOLUME'
        except:  # wenn nicht
            print(
                "Exception raised! NO dyn Paint, I'll create now. Obj: " + str(obj.name))
            obj.modifiers.new(name='Dynamic Paint', type='DYNAMIC_PAINT')
            obj.modifiers["Dynamic Paint"].ui_type = 'BRUSH'

            bpy.ops.dpaint.type_toggle(type='BRUSH')

        data.collections[Wave].objects.link(obj)
        data.collections[Paint].objects.link(obj)

       #     bpy.ops.object.link_to_collection(collection_index=index, is_new=False, new_collection_name="Paint")
        #    bpy.ops.object.link_to_collection(collection_index=index, is_new=False, new_collection_name="Wave")


def RemoveInterAct(context):
    scene = bpy.context.scene
    data = bpy.data

    sellist = floatablelist(context, context.selected_objects)
    # for schleife; range = in der reinfolge; len = zähle alle objekte in Array
    for obj in sellist:
        RemoveInterActSingle(context, obj)


# remove interaction aber mit nur einem Object


def RemoveInterActSingle(context, obj):
    if obj.aom_data.interaction_type == '':
        return obj

    context.view_layer.objects.active = obj
    bpy.ops.object.constraints_clear()

    if "Dynamic Paint" in obj.modifiers:
        bpy.ops.object.modifier_remove(
            modifier="Dynamic Paint")  # remove dynamic paint

    empty = obj.parent
    if empty != None:
        emptylocation = empty.location
        obj.parent = None
        obj.location = emptylocation

    deletelist = []
    deletelist.append(empty)
    bpy.ops.object.delete({"selected_objects": deletelist})

 # remove colletions (2.8)
    if obj.name in bpy.data.collections['Wave'].objects:
        bpy.data.collections['Wave'].objects.unlink(obj)
        # bpy.ops.collection.objects_remove_active(collection='Wave')
    else:
        print(str(obj.name) + " was not in Wave collection")
    if obj.name in bpy.data.collections['Paint'].objects:
        bpy.data.collections['Paint'].objects.unlink(obj)
        # bpy.ops.collection.objects_remove_active(collection='Paint')
    else:
        print(str(obj.name) + " was not in Paint collection")

    ocean_id = obj.aom_data.float_parent_id
    ocean = get_ocean_from_id(context, ocean_id)
    if obj.name + ".FloatAnimCage" in bpy.data.objects:
        for col in bpy.data.collections:
            print("Suche" + str(obj.name) + " in Collection" + str(col.name))
            if obj.name + ".FloatAnimCage" in col.objects:
                print(str(obj.name) + "gefunden in " + str(col.name))
                bpy.data.objects.remove(
                    bpy.data.objects[obj.name + ".FloatAnimCage"], do_unlink=True)
                ocean.modifiers['Dynamic Paint'].canvas_settings.canvas_surfaces[col.name].is_active = False
                bpy.data.collections.remove(col)

    else:
        print("kein Float Animation Cage zum entfenen gefunden")

    obj.aom_data.interaction_type = ''
    obj.aom_data.float_parent_id = -1
    obj.aom_data.namenum = -1

    return obj

    # def BrushCanvas():

    # bpy.data.objects['AdvOcean'].modifiers['Dynamic Paint'].canvas_settings.canvas_surfaces['Surface'].brush_collection = bpy.data.groups["Paint"] # für die zweite Canvas wird Paint als beeinflussende Gruppe bestimmt

    #    print(bpy.context.active_object.name + " in BrushCanvas" )


def AdvOceanMat(context, ocean):
    MatHandler = AOMMatHandler(context)
    mat = MatHandler.make_material(ocean)

    MatHandler.find_mat_to_adjust_for_preset(context, ocean)
    return mat


def add_driver(
    source, target, prop, dataPath,
    index=-1, negative=False, func=''
):
    ''' Add driver to source prop (at index), driven by target dataPath '''

    if index != -1:
        d = source.driver_add(prop, index).driver
    else:
        d = source.driver_add(prop).driver

    v = d.variables.new()
    v.name = prop
    v.targets[0].id = target
    v.targets[0].data_path = dataPath

    d.expression = func + "(" + v.name + ")" if func else v.name
    d.expression = d.expression if not negative else "-1 * " + d.expression


def FoamAnAus(context, ocean):
    #scene = bpy.context.scene
    #data = bpy.data
    #context = bpy.context
    #    mat=bpy.data.materials['AdvOceanMat']
    #    nodes = mat.node_tree.nodes
    #    links = mat.node_tree.links

    ObjFoamBool = context.scene.aom_props.ObjFoamBool
    OceanFoamBool = context.scene.aom_props.OceanFoamBool

    ocean.modifiers["Dynamic Paint"].canvas_settings.canvas_surfaces["Wetmap"].is_active = ObjFoamBool
    ocean.modifiers["Ocean"].use_foam = OceanFoamBool


def CageVis(Bool):
    objects = bpy.data.objects

    # print("Bool in function: " + str(Bool))
    for obj in objects:
        # wenn obj name hat FloatAnimCage im namen mach es aus
        if "FloatAnimCage" in obj.name:
            if Bool == False:
                objects[obj.name].hide_viewport = True
            else:
                objects[obj.name].hide_viewport = False

    return Bool


def deselectall(context):
    selected = context.selected_objects[:]
    for ob in selected:
        ob.select_set(False)


class BE_OT_RemBtn(bpy.types.Operator):
    '''Removes float and static interaction of the selected object(s).'''
    bl_label = "Remove Interaction"
    bl_idname = "rmv.interac"
    bl_options = {"REGISTER", "UNDO"}

    def execute(self, context):

        RemoveInterAct(context)

        return{"FINISHED"}

    # Generate OCean  Button


class BE_OT_CageVisability(bpy.types.Operator):
    '''Toggles the Cage Visibility'''
    bl_label = "Cage Visibility"
    bl_idname = "cag.vis"
    bl_options = {"REGISTER", "UNDO"}

    def execute(self, context):
        # CageVisBool =
        objects = bpy.data.objects

        CageVisBool = True

        for obj in objects:
            if "FloatAnimCage" in obj.name:
                CageVisBool = objects[obj.name].hide_viewport

        # print("Cage Bool im Knopf" + str(CageVisBool))

        CageVisBool = CageVis(CageVisBool)

        return{"FINISHED"}

    # Generate OCean  Button


class BE_OT_GenOceanButton(bpy.types.Operator):
    '''Adds an Ocean  to the scene.'''
    bl_label = "Generate Ocean"
    bl_idname = "gen.ocean"
    bl_options = {"REGISTER", "UNDO"}

    def execute(self, context):
        pres = AOMPreset_Handler()
        if not hasattr(context.scene, "aom_props"):
            initialize_addon(context)
            ocean = GenOcean(context)
            mat = AdvOceanMat(context, ocean)
            pres.set_initsettings(context, ocean, mat)
            pres.set_preset(context, ocean)
        else:
            ocean = GenOcean(context)
            mat = AdvOceanMat(context, ocean)
            pres.set_initsettings(context, ocean, mat)
            pres.set_preset(context, ocean)

        return{"FINISHED"}


class BE_OT_UpdateOceAniFrame(bpy.types.Operator):
    '''Updates all simlation ranges and animation speed.'''
    bl_label = "Update"
    bl_idname = "upd.oceaniframe"
    bl_options = {"REGISTER", "UNDO"}

    def execute(self, context):
        oceans = get_ocean_from_list(context, context.scene.objects)
        for oc in oceans:
            update_OceAniFrame(context, oc)
            FoamAnAus(context, oc)

        return{"FINISHED"}


class BE_OT_SetPreset(bpy.types.Operator):
    '''Applys the preset from the dropdown to the selected ocean(s).'''
    bl_label = "Apply Preset"
    bl_idname = "aom.set_preset"
    bl_options = {"REGISTER", "UNDO"}

    def execute(self, context):

        pre = AOMPreset_Handler()
        MatHandler = AOMMatHandler(context)
        #oceans = get_ocean_from_list(context, context.scene.objects)
        oc = get_active_ocean(context)
        # for oc in oceans:
        pre.set_preset(context, oc)

        MatHandler.find_mat_to_adjust_for_preset(context, oc)

        return{"FINISHED"}


def get_ocean_from_list(context, list):
    oceans = []
    for ob in list:
        if is_ocean(context, ob):
            oceans.append(ob)
    return oceans


def get_active_ocean(context):
    oceans = get_ocean_from_list(context, context.selected_objects)
    # when ocean is active
    if is_ocean(context, context.object):
        return context.object
    # when oceans are in the selected
    elif len(oceans) != 0:
        return highest_ocean_id(context, oceans)  # oceans[0]
    # no ocean selected
    else:
        for ob in context.scene.objects:
            if is_ocean(context, ob):
                return ob
    return None


def highest_ocean_id(context, list):
    ids = []
    for oc in list:
        ids.append(oc.aom_data.ocean_id)
    ids.sort()
    highestid = ids[len(ids)-1]
    for oc in list:
        if oc.aom_data.ocean_id == highestid:
            return oc


def copy_oceanmodprops(oldmod, mod):
    mod.resolution = oldmod.resolution
    mod.viewport_resolution = oldmod.viewport_resolution
    mod.spectrum = oldmod.spectrum
    mod.repeat_x = oldmod.repeat_x
    mod.repeat_y = oldmod.repeat_y
    mod.spatial_size = oldmod.spatial_size
    mod.wave_alignment = oldmod.wave_alignment
    mod.wave_scale = oldmod.wave_scale
    mod.wave_scale_min = oldmod.wave_scale_min
    mod.wind_velocity = oldmod.wind_velocity
    mod.choppiness = oldmod.choppiness
    mod.random_seed = oldmod.random_seed
    mod.wave_direction = oldmod.wave_direction
    mod.damping = oldmod.damping
    mod.size = oldmod.size
    mod.depth = oldmod.depth
    mod.use_foam = oldmod.use_foam
    mod.use_normals = oldmod.use_normals
    mod.foam_coverage = oldmod.foam_coverage
    mod.use_spray = oldmod.use_spray
    mod.spray_layer_name = oldmod.spray_layer_name


def get_ocean_keyframes(context, ocean):

    keyframes = []
    if not hasattr(ocean.animation_data, "action"):
        return None
    else:
        for fcu in ocean.animation_data.action.fcurves:
            for keyframe in fcu.keyframe_points:
                keyframes.append(keyframe.co)
    # print(keyframes)
    return keyframes


def set_ocean_keyframes(context, ocean, mod, start, end, is_extrapolate):
    oriframecurrent = copy.copy(context.scene.frame_current)
    ###

    # if not hasattr(ocean.animation_data, "action"):
    context.scene.frame_current = start[0]
    mod.time = start[1]
    mod.keyframe_insert(data_path="time")

    context.scene.frame_current = end[0]
    mod.time = end[1]
    mod.keyframe_insert(data_path="time")

    for fcu in ocean.animation_data.action.fcurves:
        for keyframe in fcu.keyframe_points:
            keyframe.interpolation = 'LINEAR'

    if is_extrapolate:
        context.area.type = 'GRAPH_EDITOR'
        bpy.ops.graph.extrapolation_type(type='LINEAR')
        context.area.type = 'VIEW_3D'
    context.scene.frame_current = oriframecurrent


def loop_ocean(context, ocean):
    # find original oc
    #remove_loop(context, ocean)
    update_OceAniFrame(context, ocean)

    for mod in ocean.modifiers:
        if mod.type == "OCEAN" and mod.name == "Ocean":
            oldmod = mod
        else:
            print("no ocean modifier found in ocean")

    if mod != None:
        ocean.aom_data.is_loop = True
        # add second ocean modifier (dynPaint muss druntersein )
        mod = ocean.modifiers.new(name="OceanLoop", type="OCEAN")
        # move to second place, could be better
        bpy.ops.object.modifier_move_to_index(modifier=mod.name, index=1)

        mod.geometry_mode = "DISPLACE"
        mod.foam_layer_name = 'LoopFoam'

        copy_oceanmodprops(oldmod, mod)

        # get original keyframes set invert keyframes
        #keyframes = get_ocean_keyframes(context, ocean)
        start, end = get_time_animation_keys(context)

        loopstart = (start[0], 0)
        loopend = (end[0], start[1])
        # 1 (1,0) <-- (1,5)
        # 2 (250,5) <-- (250,10)
        #print(f"doppelt 11 : {2 * keyframes[1][1]} ")
        # if keyframes != None:
        set_ocean_keyframes(context, ocean, mod, loopstart, loopend, False)

        # set scale
        wave_scalemax = copy.copy(oldmod.wave_scale)
        set_keyframes(context, oldmod, "wave_scale",
                      wave_scalemax, context.scene.aom_props.OceAniStart)
        set_keyframes(context, oldmod, "wave_scale",
                      0, context.scene.aom_props.OceAniEnd)

        set_keyframes(context, mod, "wave_scale",
                      0, context.scene.aom_props.OceAniStart)
        set_keyframes(context, mod, "wave_scale",
                      wave_scalemax, context.scene.aom_props.OceAniEnd)

        ###modifiers["Ocean.001"].foam_layer_name = loopfoam
        mat = ocean.material_slots[0].material
        node_tree = mat.node_tree
        nodes = node_tree.nodes
        links = node_tree.links
        # test for loop nodes and maybe delete
        remove_loop_nodes(context, node_tree)
        # add nodes for looping
        node_attr = nodes.new('ShaderNodeAttribute')
        node_attr.location = (-250, 2900)
        node_attr.name = 'LoopData'
        node_attr.attribute_name = mod.foam_layer_name

        # add nodes for looping
        nodeMix = nodes.new('ShaderNodeMixRGB')
        nodeMix.location = (-000, 2900)
        nodeMix.name = 'LoopOut'

        nodeVal = nodes.new('ShaderNodeValue')
        nodeVal.location = (-000, 2900)
        nodeVal.name = 'LoopVal'

        # set keyframes for in material
        set_keyframes(context, nodeVal.outputs[0], "default_value",
                      0, context.scene.aom_props.OceAniStart)
        set_keyframes(context, nodeVal.outputs[0], "default_value",
                      1, context.scene.aom_props.OceAniEnd)
        nodeafter = get_node_after(context, node_tree, "Foam")
        # link nodes in existing material
        links.new(nodes['Foam'].outputs[0], nodeMix.inputs[1])
        links.new(node_attr.outputs[0], nodeMix.inputs[2])
        links.new(nodeVal.outputs[0], nodeMix.inputs[0])
        links.new(nodeMix.outputs[0], nodeafter.inputs[0])

        make_keyframes_linear(context, ocean)
        make_keyframes_linear(context, mat)

        scene = context.scene
        scene.frame_start = scene.aom_props.OceAniStart
        scene.frame_end = scene.aom_props.OceAniEnd


def set_keyframes(context, path, target,  value, frame):
    oriframe = copy.copy(context.scene.frame_current)
    context.scene.frame_current = frame
    setattr(path, target, value)

    path.keyframe_insert(data_path=target)

    context.scene.frame_current = oriframe


def make_keyframes_linear(context, ob):
    if hasattr(ob.animation_data, "action"):
        for fc in ob.animation_data.action.fcurves:
            for key in fc.keyframe_points:
                key.interpolation = 'LINEAR'


def get_node_after(context, node_tree, name):
    for link in node_tree.links:
        if link.from_node.name == name:
            return link.to_node


def remove_loop_nodes(context, node_tree):
    nodes = node_tree.nodes
    links = node_tree.links
    if "LoopOut" in nodes:
        after = get_node_after(context, node_tree, "LoopOut")
        links.new(nodes['Foam'].outputs[0], after.inputs[0])
        for node in nodes:
            if "Loop" in node.name:
                nodes.remove(node)


def remove_loop(context, ocean):
    if ocean.aom_data.is_loop:
        ocean.aom_data.is_loop = False

        # delete node setup
        remove_loop_nodes(context, ocean.material_slots[0].material.node_tree)

        if "OceanLoop" in ocean.modifiers:
            mod = ocean.modifiers["OceanLoop"]
            ocean.modifiers.remove(mod)

        # delete scale keyframes
        keys = get_keyframes_data_path(
            context, ocean, 'modifiers["Ocean"].wave_scale')
        wave_scale = get_largest_keyvalue(context, keys)

        mod = ocean.modifiers['Ocean']
        for key in keys:
            mod.keyframe_delete(data_path="wave_scale",
                                index=-1, frame=key.co[0])
        mod.wave_scale = wave_scale


def get_keyframes_data_path(context, object, data_path):

    if hasattr(object.animation_data, "action"):
        keys = []
        action = object.animation_data.action
        for fc in action.fcurves:
            if fc.data_path == data_path:
                for key in fc.keyframe_points:
                    keys.append(key)
    return keys


def get_largest_keyvalue(context, keys):
    if len(keys) == 0:
        return 0
    else:
        val = -9000000000000
        for key in keys:
            if key.co[1] > val:
                val = key.co[1]
        return val


class BE_OT_GenOceanMat(bpy.types.Operator):
    '''Generates the material set in the dropdown on the selected ocean(s).'''
    bl_label = "Generate Ocean Material"
    bl_idname = "gen.ocmat"
    bl_options = {"REGISTER", "UNDO"}

    def execute(self, context):
        oceans = get_ocean_from_list(context, context.selected_objects)

        if len(oceans) != 0:
            # one or more ocean selected
            for oc in oceans:
                AdvOceanMat(context, oc)
        else:
            # no oceans selected
            active = get_active_ocean(context)
            if active != None:
                AdvOceanMat(context, active)

        return{"FINISHED"}


class BE_OT_StaticOb(bpy.types.Operator):
    '''Gives the selected object(s) the ability to interact with all oceans, produce waves and foam. The ocean will not influence the object(s).'''
    bl_label = "Static Object(s)"
    bl_idname = "stat.ob"
    bl_options = {"REGISTER", "UNDO"}

    def execute(self, context):
        BrushStatic(context)

        return{"FINISHED"}

    ### Float Selected  Button    ########################


class BE_OT_FloatSelButt(bpy.types.Operator):
    '''Gives the selected object(s) the ability to float on the a defined ocean. Floating will only work on one ocean at a time only (the selected or the last set).'''
    bl_label = "Float Object(s)"
    bl_idname = "float.sel"
    bl_options = {"REGISTER", "UNDO"}

    def execute(self, context):
        # ocean active?
        ocean = get_active_ocean(context)
        if ocean != None:
            FloatSel(context, ocean)
        # BrushCanvas()    ##hier ist der code unsauber: bei vielen objekten werden ganz oft paint und Weight als Gruppe eingetragen .... könnte trotzdem gehen weil es immerwieder überschrieben wird

        return{"FINISHED"}

    # regristry ding


class BE_OT_DeleteOcean(bpy.types.Operator):
    '''Deletes the selected ocean(s).'''
    bl_label = "Float Object(s)"
    bl_idname = "aom.deleteocean"
    bl_options = {"REGISTER", "UNDO"}

    def execute(self, context):
        oceans = oceanlist(context, context.selected_objects)
        deselectall(context)
        for ob in oceans:
            remove_floats(context, ob)
            ob.select_set(True)
            bpy.ops.object.delete(use_global=True)

        return{"FINISHED"}


class BE_OT_LoopOcean(bpy.types.Operator):
    '''Loops the ocean in the simulation range. Object interations will not be included.'''
    bl_label = "Loop Ocean Animation"
    bl_idname = "aom.loop"
    bl_options = {"REGISTER", "UNDO"}

    def execute(self, context):
        oceans = oceanlist(context, context.selected_objects)

        for ob in oceans:
            remove_loop(context, ob)
            loop_ocean(context, ob)

        return{"FINISHED"}


class BE_OT_LoopOceanRemove(bpy.types.Operator):
    '''Removes the Loop from the ocean.'''
    bl_label = "Remove Loop"
    bl_idname = "aom.removeloop"
    bl_options = {"REGISTER", "UNDO"}

    def execute(self, context):
        oceans = oceanlist(context, context.selected_objects)

        for ob in oceans:
            remove_loop(context, ob)

        return{"FINISHED"}


class BE_OT_OceanSpray(bpy.types.Operator):
    '''Add (experimental) Spray particle to the selected ocean via geometrie nodes. Please find the controls in the modifier tab. You might need to change at least one value to see an effect (kick it!!)'''
    bl_label = "Add Spray"
    bl_idname = "aom.spray"
    bl_options = {"REGISTER", "UNDO"}

    def execute(self, context):
        oceans = oceanlist(context, context.selected_objects)
        advcol = bpy.data.collections[MColName]
        GN = AOMGeoNodesHandler(context, advcol)

        for ob in oceans:
            GN.remove_spray(context, ob)
            GN.new_spray(context, ob)

        return{"FINISHED"}


class BE_OT_RemoveOceanSpray(bpy.types.Operator):
    '''Removes the spray modifier from the selected ocean(s).'''
    bl_label = "Remove Spray"
    bl_idname = "aom.remove_spray"
    bl_options = {"REGISTER", "UNDO"}

    def execute(self, context):
        oceans = oceanlist(context, context.selected_objects)
        GN = AOMGeoNodesHandler(context)

        for ob in oceans:
            GN.remove_spray(context, ob)

        return{"FINISHED"}


class BE_OT_OceanRippels(bpy.types.Operator):
    '''Makes objects produce ripples (declining sinus around the object). Have the object and the ocean selected to determine the target ocean.'''
    bl_label = "Add Ripples"
    bl_idname = "aom.ripples"
    bl_options = {"REGISTER", "UNDO"}

    def execute(self, context):

        advcol = bpy.data.collections[MColName]
        GN = AOMGeoNodesHandler(context, advcol)

        # selection plan
        # nichts selektiert --> empty ripples mod to single active ocean
        # nur object --> std active ocean
        # one ocean one object
        # many oceans selected and many objects --> every ob gets mod in every ocean
        #

        oceans = oceanlist(context, context.selected_objects)

        if len(oceans) == 0:
            oceans = [get_active_ocean(context)]
            print(f"got active {oceans}")
        obs = floatablelist(context, context.selected_objects)

        for oc in oceans:
            print(f"oc.name {oc.name}")
            if len(obs) != 0:
                for ob in obs:
                    #GN.remove_ripples(context, ob)
                    GN.new_ripples(context, oc, ob)
            else:
                GN.new_ripples(context, oc, None)

        return{"FINISHED"}


def get_all_scene_oceans(context):
    lis = []
    for ob in context.scene.objects:
        if is_ocean(context, ob):
            lis.append(ob)
    return lis


class BE_OT_RemoveOceanRippels(bpy.types.Operator):
    '''Removes Ripples Modifier. If several Ripples are present the active or the last modifier in the stack will be remove. If an object is selected that is used for Ripples, this Ripple is removed in all oceans. If objects and oceans are selected, removing will be limited to the ripples that concern both groups. If nothing is selected it looks in the last applied for the last ripple modifier.'''
    bl_label = "Remove Ripples"
    bl_idname = "aom.remove_ripples"
    bl_options = {"REGISTER", "UNDO"}

    def execute(self, context):
        oceans = oceanlist(context, context.selected_objects)
        advcol = bpy.data.collections[MColName]
        GN = AOMGeoNodesHandler(context, advcol)

        # with or without ocean
        # with or without ob
        obs = floatablelist(context, context.selected_objects)

        oceans = oceanlist(context, context.selected_objects)
        # pure object path
        if len(oceans) == 0:
            if len(obs) != 0:
                oceans = get_all_scene_oceans(context)
                for oc in oceans:
                    for ob in obs:
                        GN.remove_ripples(context, oc, ob)
            else:
                # nothing selected
                print("nothing")
                oc = get_active_ocean(context)
                GN.remove_ripples(context, oc, None)
        else:
            # viele oceane
            for ocean in oceans:
                if len(obs) != 0:
                    for ob in obs:
                        GN.remove_ripples(context, ocean, ob)
                else:
                    GN.remove_ripples(context, ocean, None)
        return{"FINISHED"}
