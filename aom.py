from bpy.props import *
import bpy
import mathutils
from .aom_def import is_ocean, is_floatcage
from .aom_properties import FloatdataItem


bl_info = {  # für export als addon
    "name": "Advanced Ocean Modifier",
    "author": "Modicolitor",
    "version": (3, 00),
    "blender": (3, 00, 0),
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
    ob = bpy.context.object
    ob.name = "AdvOcean"
    newname = ob.name

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
    # bpy.context.object.modifiers["Ocean"].size = 2
    ob.modifiers["Ocean"].use_foam = True
    ob.modifiers["Ocean"].use_normals = True
    ob.modifiers["Ocean"].foam_layer_name = "foam"

    # dieser wert bestimmt die Menge an Schaum, Lohnt sich bestimmt auszulagern
    bpy.context.object.modifiers["Ocean"].foam_coverage = 0.6

    # Animation
    ob.modifiers['Ocean'].time = 1
    context.scene.frame_current = 1
    ob.modifiers[0].time = 1
    ob.modifiers[0].keyframe_insert(data_path="time")  # uses current frame

    context.scene.frame_current = 250
    ob.modifiers[0].time = 10
    ob.modifiers[0].keyframe_insert(data_path="time")  # uses current frame
    context.scene.frame_current = 250
    # animation muss eingebaut werden, aber ich kenne den code zum keyframe setzen nicht
    context.area.type = 'GRAPH_EDITOR'
    bpy.ops.graph.extrapolation_type(type='LINEAR')
    context.area.type = 'VIEW_3D'  # umschalten später muss hier 3d view hin

    context.scene.frame_current = 1
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


def PreSetLov():
    Ocean = bpy.data.objects['AdvOcean'].modifiers['Ocean']
    Ocean.choppiness = 1.00
    Ocean.wave_scale = 0.2
    Ocean.wind_velocity = 5
    Ocean.wave_scale_min = 0.01
    Ocean.wave_alignment = 0.0
    Ocean.foam_coverage = 0.3

    try:
        mat = bpy.data.materials['AdvOceanMat']
        nodes = mat.node_tree.nodes
        bpy.data.objects['AdvOcean'].material_slots['AdvOceanMat'].material.node_tree.nodes['Value.001'].outputs['Value'].default_value = 0.7

    except:
        print("There seems to be no AdvOceanMaterial")


def PreSetMod():
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


def PreSetStorm():
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


# neue Floatvariable für die min größe
bpy.types.Scene.WeatherX = FloatProperty(
    name="Weather",
    default=0.0,
    min=0.0,
    max=1.0,
    description="From Lovely (0) to Stormy (1)")


def WeatherSlid():
    Ocean = bpy.data.objects['AdvOcean'].modifiers['Ocean']
    WeatherX = bpy.context.scene.WeatherX

    Ocean.wave_scale = WeatherX * 5.5 + 0.2

    Ocean.wind_velocity = 7 * WeatherX + 7
    Ocean.choppiness = -0.7 * WeatherX + 1
    Ocean.wave_alignment = 7 * WeatherX
    Ocean.foam_coverage = 0.3 * WeatherX

##################################################################################
#####Start and End Frame der Ocean Animation################
#############################################


# Define Start Frame Animat
bpy.types.Scene.OceAniStart = bpy.props.IntProperty(  # definiere neue Variable, als integer ...irgendwie
    name="Start Frame",  # was soll im eingabefeld stehen
    default=1,  # start wert
    # min=0,     ## kleinster Wert
    # max=10,    ## größter Wert
    description="Animation Start Frame")


# Define End Frame Animat
bpy.types.Scene.OceAniEnd = bpy.props.IntProperty(  # definiere neue Variable, als integer ...irgendwie
    name="End Frame",  # was soll im eingabefeld stehen
    default=250,  # start wert
    # min=0,     ## kleinster Wert
    # max=10,    ## größter Wert
    description="Animation End Frame")


def initialize_addon(context):
    from .aom_properties import AOMPropertyGroup
    bpy.types.Object.aom = bpy.props.PointerProperty(type=AOMPropertyGroup)

    bpy.types.Object.aom_data = bpy.props.CollectionProperty(
        type=FloatdataItem)

    #my_item = bpy.context.scene.my_settings.add()
    #my_item.name = "Spam"
    #my_item.value = 1000


def OceAniFrame():
    scene = bpy.context.scene
    data = bpy.data
    context = bpy.context

    canvas = bpy.data.objects['AdvOcean'].modifiers['Dynamic Paint'].canvas_settings
    OceAniStart = bpy.context.scene.OceAniStart
    OceAniEnd = bpy.context.scene.OceAniEnd

    for can in canvas.canvas_surfaces:
        canvas.canvas_surfaces[can.name].frame_start = OceAniStart
        canvas.canvas_surfaces[can.name].frame_end = OceAniEnd

    bpy.data.objects['AdvOcean'].modifiers["Ocean"].frame_start = OceAniStart
    bpy.data.objects['AdvOcean'].modifiers["Ocean"].frame_end = OceAniEnd


def floatablelist(context, list):
    floatable = []
    for ob in list:
        if not is_ocean(context, ob) and not is_floatcage(context, ob) and ob.type == 'MESH':
            floatable.append(ob)
    return floatable


# lasse soviele objecte wie du willst auf einmal floaten
def FloatSel():  # fügt dann ein Ei hinzu das zum Brush wird
    # if
    scene = bpy.context.scene
    data = bpy.data
    context = bpy.context

    active = bpy.context.view_layer.objects.active
    nameori = active.name
    print("nameori: " + nameori)

    sellistori = bpy.context.selected_objects[:]
    sellist = []

    for obj in sellistori:  # vorsortieren der selcted objects
        if obj.name == "AdvOcean" or ".FloatAnimCage" in obj.name or obj.type != 'MESH':
            print(str(obj.name) +
                  " does not float!!, wird nicht in die floatliste aufgenommen")
        else:
            sellist.append(obj)
            print(str(obj.name) + " wurde in die floatliste zugefügt")

    print("sellist: " + str(sellist))
    # for schleife; range = in der reinfolge; len = zähle alle objekte in Array
    for a, obj in enumerate(sellist):
        # bpy.context.selected_objects = sellist
        active = bpy.context.view_layer.objects.active
        active = obj

        print(obj.name + " For schleife" + str(a))

        # if obj.name in bpy.data.collections["Paint"].objects or obj.name in bpy.data.collections["Wave"].objects:  # test ob obj in Paint ist
        bpy.context.view_layer.objects.active = RemoveInterActSingle(
            obj)  # wenn ja entfernt mit der eigenen Funktion
       # else:
        #    print(str(obj.name) + "denkt es wäre nicht in Wave oder Paint. Remove Single nicht aktiv")
        # active = obj    ###macht das SelectedObejct actives Object
        Namenum = len(
            bpy.data.objects['AdvOcean'].modifiers['Dynamic Paint'].canvas_settings.canvas_surfaces)

        print("active: " + active.name + " obj name: " +
              obj.name + " nach else active" + str(a))
        #########

    # weisst paint gruppe zu oder erzeugt sie

        col = bpy.data.collections

        bpy.context.view_layer.objects.active = obj
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
        # bpy.context.space_data.context = 'OBJECT'   ### die ansicht ändern
        try:
            # Paint source auf Mesh Volume and Proximity
            bpy.context.object.modifiers["Dynamic Paint"].brush_settings.paint_source = 'VOLUME_DISTANCE'
            print('try ob dynamic paint brush richtig ist, hat keinen !fehler ignoriert')
        except:
            print("Toggle Dynamic Paint add Brush exception raised")
            bpy.ops.object.modifier_remove(modifier="Dynamic Paint")
            bpy.ops.object.modifier_add(type='DYNAMIC_PAINT')
            bpy.context.object.modifiers["Dynamic Paint"].ui_type = 'BRUSH'
            bpy.ops.dpaint.type_toggle(type='BRUSH')

        bpy.context.view_layer.objects.active = obj = sellist[a]

        print(str(obj.modifiers['Dynamic Paint'].brush_settings) +
              "modifierliste des aktuellen objectes")

        context.object.modifiers["Dynamic Paint"].brush_settings.paint_source = 'VOLUME_DISTANCE'
        context.object.modifiers["Dynamic Paint"].brush_settings.paint_distance = 1.0
        context.object.modifiers["Dynamic Paint"].brush_settings.wave_factor = 1

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
        bpy.context.scene.collection.children[MColName].children[Brush].children.link(
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
        conRot1.target = bpy.data.objects["AdvOcean"]
        conRot1.subtarget = "dp_weight.00" + str(Namenum)
        conRot1.use_z = False
        conRot1.invert_x = True
        conRot1.invert_y = True

        contLoc = empty.constraints.new('COPY_LOCATION')
        contLoc.target = bpy.data.objects["AdvOcean"]
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
        bpy.context.object.name = name + ".FloatAnimCage"
        name = bpy.context.object.name
        ob = bpy.data.objects[name]

        if dx > dy:
            print(obj.name + "x")
            dy = 0.9*dy
            dx = 0.9*dx
            ob.scale[0] = dx
            ob.scale[1] = dx
        else:
            print(obj.name + "y")
            dy = 0.9*dy
            dx = 0.9*dx
            print(dy)
            ob.scale[0] = dy
            ob.scale[1] = dy

        # x = bpy.data.objects["Cube"]
        # x.location = (5,0,0)

        # bpy.data.objects[name].location = (locx,locy,locz)
 #            bpy.data.objects[name].location = locy
 #            bpy.data.objects[name].location = locz

        bpy.ops.transform.resize(value=(1, 1, 7), constraint_axis=(
            False, False, True))  # in z=richtung 3 hoch machen

        # bpy.ops.object.transform_apply(location=True, rotation=True, scale=True) ### apply rotation, scale, location

        bpy.context.object.display_type = 'WIRE'
        # das zum Brush wird zugefügt
        bpy.ops.object.modifier_add(type='DYNAMIC_PAINT')
        bpy.context.object.modifiers["Dynamic Paint"].ui_type = 'BRUSH'
        bpy.ops.dpaint.type_toggle(type='BRUSH')
        bpy.data.objects[name].hide_render = True

        # jedesobject bekommt seine eigene Collection

        # index = CollectionIndex('OceanBrushes')

        # colweight = data.collections.new("Weight.00"+str(Namenum))  ###collection erschaffen
        # bpy.context.scene.collection.children[MColName].children[Brush].children.link(colweight) ### in die Brush Collection der aktuellen Szene

        data.collections[colweight.name].objects.link(ob)
        for col in ob.users_collection:  # suchen der collection in dem der Cage zuerste generiert wurde dann löschen des object instance
            if col.name != "Weight.00"+str(Namenum):
                data.collections[col.name].objects.unlink(ob)
                # print("Cage entfernt aus " + str(col.name))
                break

        # helper transferEmpty as parent of object

        bpy.context.view_layer.objects.active = bpy.data.objects["AdvOcean"]

        # print(active.name + "Akrives Objekt vor der AdvOcean")

        ocean = data.objects['AdvOcean']

        Namenum = len(
            bpy.data.objects['AdvOcean'].modifiers['Dynamic Paint'].canvas_settings.canvas_surfaces)
        print("Wenn dynamic paint surfaces weniger werden müsste diese Zahl kleiner Werden: " + str(Namenum))
        bpy.ops.dpaint.surface_slot_add()  # erzeugt neue Canvas

        try:
            bpy.context.object.modifiers["Dynamic Paint"].canvas_settings.canvas_surfaces["Surface.00"+str(
                Namenum)].name = "Weight.00"+str(Namenum)
        except:
            bpy.context.object.modifiers["Dynamic Paint"].canvas_settings.canvas_surfaces[
                "Surface"].name = "Weight.00"+str(Namenum)

        bpy.context.object.modifiers["Dynamic Paint"].canvas_settings.canvas_surfaces["Weight.00"+str(
            Namenum)].surface_type = 'WEIGHT'  # setzt den typ auf weight paint
        bpy.context.object.modifiers["Dynamic Paint"].canvas_settings.canvas_surfaces["Weight.00"+str(
            Namenum)].use_dissolve = True        # fade option wird Aktiv geklickt... das weight paint verschwindet
        bpy.context.object.modifiers["Dynamic Paint"].canvas_settings.canvas_surfaces["Weight.00"+str(
            Namenum)].dissolve_speed = 1         # nach 1 Frame
        # dynamic paint output  Vertex group wird erstellt  <--  könnte später ein Bug geben wenn schon weight paint existiert
        bpy.ops.dpaint.output_toggle(output='A')
        bpy.context.object.modifiers["Dynamic Paint"].canvas_settings.canvas_surfaces["Weight.00"+str(
            Namenum)].output_name_a = "dp_weight.00"+str(Namenum)
        bpy.ops.dpaint.output_toggle(output='A')
        bpy.context.object.modifiers["Dynamic Paint"].canvas_settings.canvas_surfaces["Weight.00"+str(
            Namenum)].brush_collection = bpy.data.collections["Weight.00"+str(Namenum)]
        # bpy.context.object.modifiers["Dynamic Paint"].canvas_settings.canvas_surfaces["Weight.00"+str(Namenum)].show_preview = False

        # for i in bpy.context.object.modifiers["Dynamic Paint"].canvas_settings.canvas_surfaces:
        #    print(i)

 #   except:
        # print("!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!Schleife fertig!!!!!!!!!!!!!!!!!!!!!!")
    ################Gruppe fehlt hier--> !!!##############
        conRot2.target = bpy.data.objects[name]
        conRot2.use_z = True
        conRot2.use_y = False
        conRot2.use_x = False

        active = sellist[a]

        # register in objects flotdata
        print(f"add data to {context.object}")
        print("____________________________________________________________________________________________________________________________________________________________")
        my_item = context.object.aom_data.add()  # old reference renew
        my_item.name = obj.name
        my_item.obj = obj
        my_item.namenum = Namenum


##############################################################
# erzeugt Schaum um statische obejkten
# Erzeugt in einem Statischen Objekt einen Brush der die wetmap an
# und fügt die paintgruppe hinzu
#############
def BrushStatic():
    scene = bpy.context.scene
    data = bpy.data
    context = bpy.context

    sellistori = bpy.context.selected_objects[:]
    sellist = []

    for obj in sellistori:
        if obj.name == "AdvOcean" or ".FloatAnimCage" in obj.name or obj.type != 'MESH':
            print(str(obj.name) +
                  " does not float!!, wird nicht in die Staticliste aufgenommen")
        else:
            sellist.append(obj)
            print(str(obj.name) + " wurde in die staticliste zugefügt")

    # print("sellist: " +str(sellist) )

    # for schleife; range = in der reinfolge; len = zähle alle objekte in Array
    for a, obj in enumerate(sellist):
        # wenn diese Object floated erstmal das floaten entfernen
       # bpy.context.view_layer.objects.active = obj
       # if obj.name in bpy.data.collections["Paint"].objects or obj.name in bpy.data.collections["Wave"].objects:
        bpy.context.view_layer.objects.active = RemoveInterActSingle(obj)
       # else:
        #    print(str(obj.name) + "wird nicht an Remove single weiter gegeben")
        try:  # gibt es schon einen Dynmaic Paint Brush???
            bpy.context.object.modifiers["Dynamic Paint"].brush_settings.paint_source = 'VOLUME'
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


def RemoveInterAct():
    scene = bpy.context.scene
    data = bpy.data
    context = bpy.context

    sellistori = bpy.context.selected_objects[:]
    sellist = []

    for obj in sellistori:
        if obj.name == "AdvOcean" or ".FloatAnimCage" in obj.name or obj.type != 'MESH':
            print(str(obj.name) +
                  " does not float!!, wird nicht in die Removeliste aufgenommen")
        else:
            sellist.append(obj)
            print(str(obj.name) + " wurde in die Löschliste zugefügt")

    print("sellist: " + str(sellist))

    # for schleife; range = in der reinfolge; len = zähle alle objekte in Array
    for a, obj in enumerate(sellist):
       # print("sellist: " +str(sellist) )
        # print(str(obj.name) + "steht vor der überprüfung in Remove Interaction, ob mesh, ")
        # if obj.name == "AdvOcean" or ".FloatAnimCage" in obj.name or obj.type != 'MESH':
        #    print(str(obj.name) + " does not float!!")
        # else:
        print(str(obj.name) + ": Its interacting, starting removing interaction")
        bpy.context.view_layer.objects.active = obj

    #    try:
        bpy.ops.object.constraints_clear()  # !!!!
        bpy.ops.object.modifier_remove(
            modifier="Dynamic Paint")  # remove dynamic paint
        emptylocation = obj.parent.location
        parent = obj.parent
        # obj.parent.remove(parent, do_unlink=True)
        obj.parent = None
        obj.location = emptylocation

        # for o in context.selectable_objects:
        # o.select_set(False)

        deletelist = []
        deletelist.append(obj.parent)
        bpy.ops.object.delete({"selected_objects": deletelist})

    # remove colletions (2.8)
        if obj.name in bpy.data.collections['Wave'].objects:
            bpy.ops.collection.objects_remove_active(collection='Wave')
        else:
            print(str(obj.name) + "was not in Wave collection")

        if obj.name in bpy.data.collections['Paint'].objects:
            bpy.ops.collection.objects_remove_active(collection='Paint')
        else:
            print(str(obj.name) + " was not in Paint collection")

        print(str(obj.name) + ' aus wave und paint entfernt, jetzt nur noch den cage')
        if obj.name + ".FloatAnimCage" in bpy.data.objects:
            for col in bpy.data.collections:
                print("Suche" + str(obj.name) +
                      " in Collection" + str(col.name))
                if obj.name + ".FloatAnimCage" in col.objects:
                    print(str(obj.name) + "gefunden in " + str(col.name))
                    bpy.data.objects.remove(
                        bpy.data.objects[obj.name + ".FloatAnimCage"], do_unlink=True)
                    bpy.data.objects['AdvOcean'].modifiers['Dynamic Paint'].canvas_settings.canvas_surfaces[col.name].is_active = False
                    bpy.data.collections.remove(col)

        else:

            print("es gab kein Float Animation Cage")
           # except:
            #    print("Wasn't floating or something went wrong")

            # dynamic paint


def RemoveInterActSingle(obj):  # remove interaction aber mit nur einem Object
    objinitial = obj

    print("Remove Single Interaction actvated for object " + str(obj.name))
    bpy.context.view_layer.objects.active = obj
    # if obj.name == "AdvOcean" or ".FloatAnimCage" in obj.name or obj.type != 'MESH':
    #       print("Its not floating!")
    # bpy.context.selected_objects[a]
    # AdvOceanMat()  #### setting option muss angepasst werden
    # else:
    # bpy.context.selected_objects = sellist
 #    bpy.context.view_layer.objects.active = obj

    #    try:
    if 'Copy Location' in obj.constraints:
        print("Constraint Copy Location will be removed from " + str(obj.name))
        obj.constraints.remove(obj.constraints['Copy Location'])
    if 'Copy Rotation' in obj.constraints:
        print("Constraint Copy Rotation will be removed from " + str(obj.name))
        obj.constraints.remove(obj.constraints['Copy Rotation'])

        bpy.ops.object.constraints_clear()  # !!!!
    if "Dynamic Paint" in obj.modifiers:
        bpy.ops.object.modifier_remove(
            modifier="Dynamic Paint")  # remove dynamic paint
 # remove colletions (2.8)
    if obj.name in bpy.data.collections['Wave'].objects:
        bpy.ops.collection.objects_remove_active(collection='Wave')
    else:
        print(str(obj.name) + " was not in Wave collection")
    if obj.name in bpy.data.collections['Paint'].objects:
        bpy.ops.collection.objects_remove_active(collection='Paint')
    else:
        print(str(obj.name) + " was not in Paint collection")

    if obj.name + ".FloatAnimCage" in bpy.data.objects:
        for col in bpy.data.collections:
            print("Suche" + str(obj.name) + " in Collection" + str(col.name))
            if obj.name + ".FloatAnimCage" in col.objects:
                print(str(obj.name) + "gefunden in " + str(col.name))
                bpy.data.objects.remove(
                    bpy.data.objects[obj.name + ".FloatAnimCage"], do_unlink=True)
                bpy.data.objects['AdvOcean'].modifiers['Dynamic Paint'].canvas_settings.canvas_surfaces[col.name].is_active = False
                bpy.data.collections.remove(col)

    else:
        print("kein Float Animation Cage zum entfenen gefunden")

    return objinitial


# def BrushCanvas():

    # bpy.data.objects['AdvOcean'].modifiers['Dynamic Paint'].canvas_settings.canvas_surfaces['Surface'].brush_collection = bpy.data.groups["Paint"] # für die zweite Canvas wird Paint als beeinflussende Gruppe bestimmt


#    print(bpy.context.active_object.name + " in BrushCanvas" )

def AdvOceanMat(ocean):
    scene = bpy.context.scene
    data = bpy.data
    context = bpy.context

    ob = ocean
    print(bpy.context.active_object.name + " in AdvOceanMat")

    # cycles engine wird gestartet wenn das noch nicht geschehen ist
    # scn = bpy.context.scene
    # if not scn.render.engine == 'CYCLES':
    #    scn.render.engine = 'CYCLES'

    # material zuweisen aus dem internet
    # Get material
    mat = bpy.data.materials.get("AdvOceanMat")
    if mat is None:
        # create material
        mat = bpy.data.materials.new(name="AdvOceanMat")

    # Assign it to object
    if ob.data.materials:
        # assign to 1st material slot
        ob.data.materials[0] = mat
    else:
      #  no slots
        ob.data.materials.append(mat)

    bpy.context.object.active_material.use_nodes = True

    # Nodes bauen
    # bpy.data.materials['AdvOceanMat'].node_tree.nodes.active.color   erinnerung an den langen pfad
    # bpy.data.materials['AdvOceanMat'].node_tree.nodes['Layer Weight.001'].inputs['Blend'].default_value
    active = bpy.data.materials['AdvOceanMat'].node_tree.nodes.active
    mat = bpy.data.materials['AdvOceanMat']
    # macht einen Diffuseshader
    # mat.node_tree.nodes.new('ShaderNodeBsdfDiffuse')
    nodes = mat.node_tree.nodes

    links = mat.node_tree.links

    for node in nodes:
        nodes.remove(node)

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

    links.new(nodes['RGB'].outputs[0], nodes['Glossy BSDF'].inputs['Color'])
    links.new(nodes['RGB'].outputs[0],
              nodes['Refraction BSDF'].inputs['Color'])
    links.new(nodes['RGB'].outputs[0],
              nodes['Transparent BSDF'].inputs['Color'])

    node = nodes.new('ShaderNodeValue')
    node.location = (-1400, 200)
    nodes['Value'].outputs[0].default_value = 0.01
    links.new(nodes['Value'].outputs[0], nodes['Glossy BSDF'].inputs[1])
    links.new(nodes['Value'].outputs[0], nodes['Glossy BSDF.001'].inputs[1])
    links.new(nodes['Value'].outputs[0], nodes['Refraction BSDF'].inputs[1])

    # Foamfactor
    node = nodes.new('ShaderNodeAttribute')  # Attribute foam
    node.location = (000, 1400)
    nodes['Attribute'].attribute_name = "foam"
    node = nodes.new('ShaderNodeGamma')  # gamma für wetmap
    node.location = (200, 1400)
    nodes["Gamma"].inputs[1].default_value = 0.3

    node = nodes.new('ShaderNodeAttribute')  # attribute wetmap
    node.location = (000, 1250)
    nodes['Attribute.001'].attribute_name = "dp_wetmap"
    node = nodes.new('ShaderNodeGamma')  # gamma für wetmap
    node.location = (200, 1250)
    # Gamma wert wetmap##########
    nodes["Gamma.001"].inputs[1].default_value = 5

    node = nodes.new('ShaderNodeMixRGB')  # rgb mixshader machen
    node.location = (400, 1275)
    nodes["Mix"].blend_type = 'ADD'
    nodes["Mix"].use_clamp = True
    nodes["Mix"].inputs[0].default_value = 1.0

    # link Attribute notes additiv
    links.new(nodes['Attribute.001'].outputs['Fac'],
              nodes['Gamma.001'].inputs['Color'])
    links.new(nodes['Gamma'].outputs['Color'], nodes['Mix'].inputs['Color2'])
    links.new(nodes['Attribute'].outputs['Fac'],
              nodes['Gamma'].inputs['Color'])
    links.new(nodes['Gamma.001'].outputs['Color'],
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
    links.new(nodes['Mix'].outputs['Color'], nodes['Mix.001'].inputs['Color1'])
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
    links.new(nodes['Mix.002'].outputs['Color'], nodes['Math.001'].inputs[1])
    links.new(nodes['Mix.002'].outputs['Color'], nodes['Math.002'].inputs[0])
    links.new(nodes['Math'].outputs[0], nodes['Mix.003'].inputs[0])
    links.new(nodes['Math.001'].outputs[0], nodes['Mix.004'].inputs[0])

    # patchiness of foam
    node = nodes.new('ShaderNodeValue')  # mixshader machen
    node.location = (600, 1300)
    links.new(nodes['Value.001'].outputs[0], nodes['Mix.001'].inputs[0])
    links.new(nodes['Value.001'].outputs[0], nodes['Mix.002'].inputs[0])

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
    links.new(nodes['Bump'].outputs['Normal'],
              nodes['Principled BSDF'].inputs['Normal'])
    links.new(nodes['Mix.005'].outputs['Color'],
              nodes['Bump'].inputs['Height'])

    # node = nodes.new('ShaderNodeRGB') ### mixshader machen
    # node.location = (-200,-200)
    # nodes['RGB'].outputs['Color'].default_value[0] = 1
    # nodes['RGB'].outputs['Color'].default_value[1] = 1
    # nodes['RGB'].outputs['Color'].default_value[2] = 1
    # node = nodes.new('ShaderNodeHueSaturation') ### Hue saturation.001
    # node.location = (000,-200)
    # node = nodes.new('ShaderNodeBsdfGlossy') ### Glossy shader .002
    # node.location = (200,-100)
    # node = nodes.new('ShaderNodeAddShader') ### mixshader machen
    # node.location = (400,-200)

    # link foam material
    #links.new(nodes['RGB'].outputs['Color'], nodes['Hue Saturation Value.002'].inputs['Color']) #
    #links.new(nodes['Hue Saturation Value.002'].outputs['Color'], nodes['Ambient Occlusion'].inputs['Color']) #
    #links.new(nodes['Hue Saturation Value.002'].outputs['Color'], nodes['Glossy BSDF.002'].inputs['Color']) #
    #links.new(nodes['Glossy BSDF.002'].outputs['BSDF'], nodes['Add Shader'].inputs[0]) #
   # links.new(nodes['Ambient Occlusion'].outputs['AO'], nodes['Add Shader'].inputs[1]) #

    ###Finaler Mix in den Material Output#################################

    node = nodes.new('ShaderNodeMath')  # Multiplier für Displacement
    node.location = (2200, 200)
    node.operation = 'MULTIPLY'
    node.use_clamp = True
    node.inputs[1].default_value = 0.0

    node = nodes.new('ShaderNodeMixShader')  # mixshader machen
    node.location = (2200, 000)

    links.new(nodes['Mix.005'].outputs['Color'],
              nodes['Mix Shader.003'].inputs[0])  # Factor des Schaumes
    # Schaum material in den EndMixer
    links.new(nodes['Principled BSDF'].outputs['BSDF'],
              nodes['Mix Shader.003'].inputs[2])
    links.new(nodes['Mix Shader.002'].outputs['Shader'],
              nodes['Mix Shader.003'].inputs[1])  # Oceanmateril in den EndMixer

    try:
        links.new(nodes['Mix Shader.003'].outputs['Shader'],
                  nodes['Material Output'].inputs[0])  # EndMixer in den Surface
    except:
        node = nodes.new('ShaderNodeOutputMaterial')  # mixshader machen
        node.location = (2400, 000)
        node.target = 'CYCLES'
        links.new(nodes['Mix Shader.003'].outputs['Shader'],
                  nodes['Material Output'].inputs['Surface'])  # EndMixer in den Surface

    try:
        links.new(nodes['Mix Shader.003'].outputs['Shader'],
                  nodes['Material Output.001'].inputs[0])  # EndMixer in den Surface
    except:
        node = nodes.new('ShaderNodeOutputMaterial')  # mixshader machen
        node.location = (2400, -200)
        node.name = 'Material Output Eevee'
        node.target = 'EEVEE'
        links.new(nodes['Mix Shader.003'].outputs['Shader'],
                  nodes['Material Output Eevee'].inputs['Surface'])  # EndMixer in den Surface

    # Displacement connect
    # EndMixer in den Surface
    links.new(nodes['Math.002'].outputs[0], nodes['Mix.005'].inputs[1])

    links.new(nodes['Math.003'].outputs['Value'],
              nodes['Material Output'].inputs['Displacement'])
   # links.new(nodes['Math.002'].outputs['Value'], nodes['Material Output'].inputs['Displacement']) #EndMixer in den Surface

    links.new(nodes['Math.003'].outputs['Value'],
              nodes['Material Output'].inputs['Displacement'])

    # Bubble extra
    node = nodes.new('ShaderNodeValue')  # Multiplier für Displacement
    node.location = (000, 400)
    nodes['Value.002'].outputs[0].default_value = 100

    node = nodes.new('ShaderNodeMath')  # Multiplier für Displacement
    node.location = (200, 600)
    nodes['Math.004'].operation = 'MULTIPLY'
    nodes['Math.004'].inputs[1].default_value = 2

    node = nodes.new('ShaderNodeMath')  # Multiplier für Displacement
    node.location = (200, 400)
    nodes['Math.005'].operation = 'MULTIPLY'
    nodes['Math.005'].inputs[1].default_value = 1

    node = nodes.new('ShaderNodeMath')  # Multiplier für Displacement
    node.location = (200, 200)
    nodes['Math.006'].operation = 'MULTIPLY'
    nodes['Math.006'].inputs[1].default_value = 0.5

    links.new(nodes['Value.002'].outputs['Value'], nodes['Math.004'].inputs[0])
    links.new(nodes['Value.002'].outputs['Value'], nodes['Math.005'].inputs[0])
    links.new(nodes['Value.002'].outputs['Value'], nodes['Math.006'].inputs[0])

    links.new(nodes['Math.004'].outputs['Value'],
              nodes['Voronoi Texture'].inputs['Scale'])
    links.new(nodes['Math.005'].outputs['Value'],
              nodes['Voronoi Texture.001'].inputs['Scale'])
    links.new(nodes['Math.006'].outputs['Value'],
              nodes['Voronoi Texture.002'].inputs['Scale'])
    links.new(nodes['Mix.005'].outputs['Color'], nodes['Math.003'].inputs[0])

    # seperated material outputs for eevee and cycles

    # Set eevee transparency
    REngine = bpy.context.scene.render.engine
    bpy.context.scene.render.engine = 'BLENDER_EEVEE'
    bpy.context.object.active_material.blend_method = 'HASHED'
    bpy.context.scene.render.engine = REngine


# Bool für Foam an aus definieren
bpy.types.Scene.ObjFoamBool = bpy.props.BoolProperty(  # definiere neue Variable, als integer ...irgendwie
    name="Object Foam",  # was soll im eingabefeld stehen
    default=True,
    description="Controls Ocean and Object Foam")

bpy.types.Scene.OceanFoamBool = bpy.props.BoolProperty(  # definiere neue Variable, als integer ...irgendwie
    name="Ocean Foam",  # was soll im eingabefeld stehen
    default=True,
    description="Controls Ocean and Object Foam")

bpy.types.Scene.CageVisBool = bpy.props.BoolProperty(  # definiere neue Variable, als integer ...irgendwie
    # name="Cage Visibility",      ### was soll im eingabefeld stehen
    # default=True,
    # description="Cremembers Cage visibility";
)


def FoamAnAus():
    scene = bpy.context.scene
    data = bpy.data
    context = bpy.context
    #    mat=bpy.data.materials['AdvOceanMat']
    #    nodes = mat.node_tree.nodes
    #    links = mat.node_tree.links

    ObjFoamBool = bpy.context.scene.ObjFoamBool
    OceanFoamBool = bpy.context.scene.OceanFoamBool

    bpy.data.objects['AdvOcean'].modifiers["Dynamic Paint"].canvas_settings.canvas_surfaces["Wetmap"].is_active = ObjFoamBool
    bpy.data.objects['AdvOcean'].modifiers["Ocean"].use_foam = OceanFoamBool


def CageVis(Bool):
    scene = bpy.context.scene
    data = bpy.data
    context = bpy.context

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


class BE_OT_GenObjFoam(bpy.types.Operator):
    bl_label = "Object Foam"
    bl_idname = "gen.obfoam"
    bl_options = {"REGISTER", "UNDO"}

    def execute(self, context):
        bpy.data.objects['AdvOcean'].modifiers['Ocean'].use_foam

        return{"FINISHED"}


class BE_OT_RemBtn(bpy.types.Operator):
    bl_label = "Remove Interaction"
    bl_idname = "rmv.interac"
    bl_options = {"REGISTER", "UNDO"}

    def execute(self, context):

        RemoveInterAct()

        return{"FINISHED"}

    # Generate OCean  Button


class BE_OT_CageVisability(bpy.types.Operator):
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
    bl_label = "Generate Ocean"
    bl_idname = "gen.ocean"

    def execute(self, context):
        initialize_addon(context)
        ocean = GenOcean(context)

        AdvOceanMat(ocean)
        # PreSetMod()

        return{"FINISHED"}


class BE_OT_UpdateWeather(bpy.types.Operator):
    bl_label = "Update"
    bl_idname = "upd.weather"
    bl_options = {"REGISTER", "UNDO"}

    def execute(self, context):
        WeatherSlid()

        return{"FINISHED"}


class BE_OT_UpdateOceAniFrame(bpy.types.Operator):
    bl_label = "Update"
    bl_idname = "upd.oceaniframe"
    bl_options = {"REGISTER", "UNDO"}

    def execute(self, context):
        OceAniFrame()
        FoamAnAus()

        return{"FINISHED"}


class BE_OT_SetLov(bpy.types.Operator):
    bl_label = "Lovely"
    bl_idname = "set.lov"
    bl_options = {"REGISTER", "UNDO"}

    def execute(self, context):
        PreSetLov()

        return{"FINISHED"}


class BE_OT_SetMod(bpy.types.Operator):
    bl_label = "Lively"
    bl_idname = "set.mod"
    bl_options = {"REGISTER", "UNDO"}

    def execute(self, context):
        PreSetMod()

        return{"FINISHED"}


class BE_OT_SetStorm(bpy.types.Operator):
    bl_label = "Stormy"
    bl_idname = "set.storm"
    bl_options = {"REGISTER", "UNDO"}

    def execute(self, context):
        PreSetStorm()

        return{"FINISHED"}

        # Generate Ocena Material  Button


class BE_OT_GenOceanMat(bpy.types.Operator):
    bl_label = "Generate Ocean Material"
    bl_idname = "gen.ocmat"
    bl_options = {"REGISTER", "UNDO"}

    def execute(self, context):
        AdvOceanMat()

        return{"FINISHED"}


class BE_OT_StaticOb(bpy.types.Operator):
    bl_label = "Static Object(s)"
    bl_idname = "stat.ob"
    bl_options = {"REGISTER", "UNDO"}

    def execute(self, context):
        BrushStatic()

        return{"FINISHED"}

    ### Float Selected  Button    ########################


class BE_OT_FloatSelButt(bpy.types.Operator):
    bl_label = "Float Object(s)"
    bl_idname = "float.sel"
    bl_options = {"REGISTER", "UNDO"}

    def execute(self, context):
        FloatSel()
        # BrushCanvas()    ##hier ist der code unsauber: bei vielen objekten werden ganz oft paint und Weight als Gruppe eingetragen .... könnte trotzdem gehen weil es immerwieder überschrieben wird

        return{"FINISHED"}

    # regristry ding


class BE_OT_DeleteOcean(bpy.types.Operator):
    bl_label = "Float Object(s)"
    bl_idname = "aom.deleteocean"
    bl_options = {"REGISTER", "UNDO"}

    def execute(self, context):

        if is_ocean(context.object):
            deselectall(context)
            bpy.ops.object.delete(use_global=True)

        return{"FINISHED"}
