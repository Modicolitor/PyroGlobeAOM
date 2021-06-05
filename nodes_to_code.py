

import bpy


def sort_nodes_list(nodes):
    # sort the nodes in the list left to right
    xlocs = []
    for node in nodes:
        xlocs.append(node.location[0])
    xlocs.sort()
    sortednodes = []
    for xloc in xlocs:
        for node in nodes:
            if xloc == node.location[0]:
                sortednodes.append(node)
    return sortednodes


def get_value(ob):
    #print(f"type is {type(ob)}")
    if type(ob) is int:
        return ob
    elif type(ob) is float:
        return int(ob)
    elif type(ob) is str:
        return '"' + ob + '"'
    elif str(type(ob)) == "<class 'bool'>":
        return ob
    # elif isinstance(ob, 'bpy_prop_array')
    elif "NodeSocketGeometry" in str(type(ob)):
        return ""
    elif "NodeSocketVirtual" in str(type(ob)):
        return ""
    elif str(type(ob)) == "<class 'NoneType'>":
        return ""
    elif "bpy_types.Object" in str(type(ob)):
        return ''

    elif str(type(ob)) == "<class 'bpy.types.NodeSocketVector'>" or str(type(ob)) == "<class 'bpy_prop_array'>" or str(type(ob)) == "<class 'Vector'>":

        vecstring = "("
        for d in ob:
            vecstring = vecstring + str(d)+","
        vecstring = vecstring + ")"
        return vecstring  # return vector values
    else:

        print(f'#MöpMöp {type(ob)}')


def get_putput(a, inp):
    if hasattr(inp, "default_value"):
        if get_value(inp.default_value) != "":
            return get_value(inp.default_value)

    #    print(f'#check output socket {a} type {type(inp)}')
    else:
        if "NodeSocketGeometry" in str(type(inp)):
            return ''
        elif "NodeSocketVirtual" in str(type(inp)):
            return ''

        else:
            print(f'#has no value at {a} with {inp} ')


def nodes_to_nodecode(group):
    nodes = group.nodes
    links = group.links
    nodes = sort_nodes_list(nodes)

    print("+++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++")
    for node in nodes:
        print('')
        print(f'node = nodes.new("{node.bl_idname}" )')
        print(f'node.name = "{node.name}" ')
        print(
            f'node.location = ({int(node.location[0])}, {int(node.location[1])})')

        if node.bl_idname == 'NodeGroupInput':
            for out in node.outputs:
                if out.bl_idname != "NodeSocketVirtual" or out.bl_idname == "Geometry":
                    # code geht so nicht!!!
                    print(f'node.outputs.new("{out.bl_idname}", "{out.name}")')

        elif node.bl_idname == 'NodeGroupOutput':
            for out in node.inputs:
                if out.bl_idname != "NodeSocketVirtual" or out.bl_idname == "Geometry":
                    print(f'node.inputs.new("{out.bl_idname}", "{out.name}")')
        else:
            for a, inp in enumerate(node.inputs):
                value = get_putput(a, inp)
                if value != '':
                    print(f'node.inputs[{a}].default_value = {value}')

            for a, inp in enumerate(node.outputs):
                value = get_putput(a, inp)
                if value != '':
                    print(f'node.outputs[{a}].default_value = {value}')

    gen_links(links)


def gen_links(links):
    for l in links:
        # links.new(nodes['Group Input'].outputs[0],
        #          nodes['Voronoi Texture'].inputs[0])
        print(
            f"links.new( nodes['{l.from_node.name}'].outputs['{l.from_socket.name}'],  nodes['{l.to_node.name}'].inputs['{l.to_socket.name}'])")


group = bpy.data.node_groups['OceanSpray']

nodes = group.nodes
links = group.links

nodes_to_nodecode(group)
