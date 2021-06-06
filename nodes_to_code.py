# todo

# [] nodegroups
# [] test material node trees
# [] clean up get value section to bl_idname


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
    # sort nodes left to right
    nodes = sort_nodes_list(nodes)

    print("+++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++")
    gen_maininputs(group)
    for node in nodes:
        print('')
        print(f'node = nodes.new("{node.bl_idname}" )')
        print(f'node.name = "{node.name}" ')
        print(
            f'node.location = ({int(node.location[0])}, {int(node.location[1])})')

        if node.bl_idname == 'NodeGroupInput':
            pass
            # for out in node.outputs:
            # f out.bl_idname != "NodeSocketVirtual" or out.bl_idname == "Geometry":
            # code geht so nicht!!!
            #print(f'node.outputs.new("{out.bl_idname}", "{out.name}")')

            # elif node.bl_idname == 'NodeGroupOutput':
            # for out in node.inputs:
            #    if out.bl_idname != "NodeSocketVirtual" or out.bl_idname == "Geometry":
            #       print(f'node.inputs.new("{out.bl_idname}", "{out.name}")')

            '''
            nodes["Point Scale"].input_type
            data_type 
            operation 

            nodes["Attribute Vector Math"].input_type_b nodes["Attribute Vector Math"].input_type_a
            nodes["Point Distribute"].distribute_method

            nodes["Attribute Mix"].input_type_factor
            blend_type 
            nodes["Attribute Map Range"].interpolation_type
            nodes["Math.001"].use_clamp
            '''
        else:
            for a, inp in enumerate(node.inputs):
                value = get_putput(a, inp)
                if value != '':
                    print(f'node.inputs[{a}].default_value = {value}')
                special_operations(node)

            for a, inp in enumerate(node.outputs):
                value = get_putput(a, inp)
                if value != '':
                    print(f'node.outputs[{a}].default_value = {value}')

    gen_links(group, nodes, links)


def special_operations(node):

    if hasattr(node, "instance_type"):
        print(f'node.instance_type = "{node.instance_type}"')
    elif hasattr(node, "input_type"):
        print(f'node.input_type = "{node.input_type}"')
    elif hasattr(node, "data_type"):
        print(f'node.data_type = "{node.data_type}"')
    elif hasattr(node, "operation"):
        print(f'node.operation = "{node.operation}"')
    elif hasattr(node, "input_type_a"):
        print(f'node.input_type_a = "{node.input_type_a}"')
    elif hasattr(node, "input_type_b"):
        print(f'node.input_type_b = "{node.input_type_b}"')

    elif hasattr(node, "distribute_method"):
        print(f'node.distribute_method = "{node.distribute_method}"')
    elif hasattr(node, "input_type_factor"):
        print(f'node.input_type_factor = "{node.input_type_factor}"')
    elif hasattr(node, "blend_type"):
        print(f'node.blend_type = {node.blend_type}')
    elif hasattr(node, "interpolation_type"):
        print(f'node.interpolation_type = "{node.interpolation_type}"')
    elif hasattr(node, "use_clamp"):
        print(f'node.use_clamp = "{node.use_clamp}"')


def get_sorted_InputLinks(nodes, links):
    inplinks = []
    for l in links:
        if 'NodeGroupInput' in l.from_node.bl_idname:
            inplinks.append(l)

    # get input
    innode = get_inputnode(nodes)

    sortedlinks = []
    for out in innode.outputs:
        if out.bl_idname != "NodeSocketVirtual":
            for l in inplinks:
                if l.from_socket == out:
                    sortedlinks.append(l)

    return sortedlinks


def get_inputnode(nodes):
    for node in nodes:
        if node.bl_idname == 'NodeGroupInput':
            innode = node
            break
    return innode


def get_putput_index(node, socket):
    for i, out in enumerate(node.outputs):
        if out.name == socket.name:
            index = i
            break
    return index


def gen_maininputs(group):
    for inp in group.inputs:
        print(f"node_group.inputs.new('{inp.bl_socket_idname}','{inp.name}')")
    group.inputs


def gen_links(group, nodes, links):

    inplinks = get_sorted_InputLinks(nodes, links)

    # make new input sockets

    for i, l in enumerate(inplinks):
        print(
            f"links.new( nodes['{l.from_node.name}'].outputs['{get_putput_index(l.from_node, l.from_socket)}'],  nodes['{l.to_node.name}'].inputs['{get_putput_index(l.to_node, l.to_socket)}'])")

    # set- input names

    for l in links:
        if 'NodeGroupInput' not in l.from_node.bl_idname:
            print(
                f"links.new( nodes['{l.from_node.name}'].outputs['{l.from_socket.name}'],  nodes['{l.to_node.name}'].inputs['{l.to_socket.name}'])")


group = bpy.data.node_groups['OceanSpray']

nodes_to_nodecode(group)
