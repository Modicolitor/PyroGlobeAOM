# todo
# [+] output sockets are not always 0 (but all called value (but value don't work)) 
# [] inputs should not be called value  but the index
# [+] reroute shouldn't have inputs
# [] node input geometry not detected *?*
# [] probably some nodes have special operation the script is not aware off, just add "mode"
# []node.transform_space = "ELEMENT" macht error bei compare node
# features
# [+] nodegroups
# [+] add frames and parent

# [] clean up get value section to bl_idname

#[+ looks done] set last values mod[input macht probleme]


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
                if node not in sortednodes:
                    sortednodes.append(node)
    return sortednodes


def get_value(ob):
    #print(f"type is {type(ob)}")
    if type(ob) is int:
        return ob
    elif type(ob) is float:
        return round(ob, 2)
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
        # hack for collections
    elif hasattr(ob, "children"):
        return ''

    elif str(type(ob)) == "<class 'bpy.types.NodeSocketVector'>" or str(type(ob)) == "<class 'bpy_prop_array'>" or str(type(ob)) == "<class 'Vector'>" or str(type(ob)) == "<class 'Euler'>":

        vecstring = "("
        for d in ob:
            vecstring = vecstring + str(d)+","
        vecstring = vecstring + ")"
        return vecstring  # return vector values
    elif 'Material' in str(type(ob)):
        return "ocean.material_slots[0].material"
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


def get_mod(context, group):
    for mod in context.object.modifiers:
        if mod.type == 'NODES':
            if mod.node_group == group:
                return mod


def nodes_to_nodecode(group):
    context = bpy.context
    nodes = group.nodes
    links = group.links
    # sort nodes left to right
    nodes = sort_nodes_list(nodes)

    print("+++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++")
    gen_maininputs(group)
    gen_frames(group)
    for node in nodes:
        if node.bl_idname != 'NodeFrame':
            print('')
            print(f'node = nodes.new("{node.bl_idname}" )')
            print(f'node.name = "{node.name}" ')
            if hasattr(node, 'parent'):
                if hasattr(node.parent, 'name'):
                    print(f'node.parent = node_group.nodes["{node.parent.name}"]')
                    
            if hasattr(node, 'rotation_type'):
                print(f'node.rotation_type = "{node.rotation_type}"')
            
            print(
                f'node.location = ({int(node.location[0])}, {int(node.location[1])})')
            check_for_Paired(node, nodes, group)
            
            if node.bl_idname == 'NodeGroupInput':
                pass
            elif node.bl_idname == 'NodeGroupOutput':
                pass
            elif node.bl_idname == 'NodeReroute':
                pass
            elif node.type == 'SIMULATION_INPUT':
                pass
            elif node.type == 'REPEAT_INPUT':
                pass
            else:
                special_operations(node)
                for a, inp in enumerate(node.inputs):
                    value = get_putput(a, inp)
                    if value != '' and value != None:
                        print(f'node.inputs[{a}].default_value = {value}')

                for a, inp in enumerate(node.outputs):
                    value = get_putput(a, inp)
                    if value != '':
                        print(f'node.outputs[{a}].default_value = {value}')
            
    
    gen_group_outputs(group)
    gen_links(group, nodes, links)
    mod = get_mod(context, group)
    set_current_maininputs(mod)

def check_for_Paired(node, nodes, group):
       
    ### ist es Simulation node 
    if node.type == 'SIMULATION_INPUT' or node.type == 'SIMULATION_OUTPUT' or node.type == 'REPEAT_INPUT' or node.type == 'REPEAT_OUTPUT':
        print('# found PairedNodes')
    else:
        return
    
    
    ###war schon eine Simulation node 
    pairedbefore = []
    for n in nodes:
        if n == node:
            break
        if node.type == 'SIMULATION_INPUT' or node.type == 'SIMULATION_OUTPUT' or node.type == 'REPEAT_INPUT' or node.type == 'REPEAT_OUTPUT':
            pairedbefore.append(n)
    ### wenn es ein Input ist 
    if hasattr(node,'paired_output'):
        if node.paired_output in pairedbefore:
            print(f'node.pair_with_output(nodes[{node.paired_output.name}])')
    elif node.type == 'REPEAT_OUTPUT' or node.type == 'SIMULATION_OUTPUT':
        for bro in pairedbefore:
            if hasattr(bro,'paired_output'):
                if bro.paired_output == node:
                    print(f'nodes["{bro.name}"].pair_with_output(nodes["{node.name}"])')
    
    
    
def special_operations(node):

    if hasattr(node, "instance_type"):
        print(f'node.instance_type = "{node.instance_type}"')
    if hasattr(node, "input_type"):
        print(f'node.input_type = "{node.input_type}"')
    if hasattr(node, "data_type"):
        print(f'node.data_type = "{node.data_type}"')
    if hasattr(node, "operation"):
        print(f'node.operation = "{node.operation}"')
    if hasattr(node, "input_type_a"):
        print(f'node.input_type_a = "{node.input_type_a}"')
    if hasattr(node, "input_type_b"):
        print(f'node.input_type_b = "{node.input_type_b}"')
    if hasattr(node, "distribute_method"):
        print(f'node.distribute_method = "{node.distribute_method}"')
    if hasattr(node, "input_type_factor"):
        print(f'node.input_type_factor = "{node.input_type_factor}"')
    if hasattr(node, "blend_type"):
        print(f'node.blend_type = "{node.blend_type}"')
    if hasattr(node, "interpolation_type"):
        print(f'node.interpolation_type = "{node.interpolation_type}"')
    if hasattr(node, "use_clamp"):
        print(f'node.use_clamp = {node.use_clamp}')
    if hasattr(node, "clamp"):
        print(f'node.clamp = {node.clamp}')
    if hasattr(node, "use_whole_collection"):
        print(f'node.use_whole_collection = {node.use_whole_collection}')
    if hasattr(node, "input_type_x"):
        print(f'node.input_type_x = "{node.input_type_x}"')
    if hasattr(node, "input_type_y"):
        print(f'node.input_type_y = "{node.input_type_y}"')
    if hasattr(node, "input_type_z"):
        print(f'node.input_type_z = "{node.input_type_z}"')
    if hasattr(node, "transform_space"):
        print(f'node.transform_space = "{node.transform_space}"')
    if hasattr(node, "node_tree"):
        print(f'node.node_tree = bpy.data.node_groups["{node.node_tree.name}"]')
    if hasattr(node, "hide"):
        print(f'node.hide = {node.hide}')
    if hasattr(node, "mode"):
        print(f'node.mode = "{node.mode}"')
    if hasattr(node, "mute"):
        print(f'node.mute = {node.mute}')

def get_sorted_InputLinks(nodes, links):
    inplinks = []
    for l in links:
        if 'NodeGroupInput' in l.from_node.bl_idname:
            inplinks.append(l)

    
    # get input
    innodes = get_inputnodes(nodes)

    sortedlinks = []
    for innode in innodes:
        for out in innode.outputs:
            if out.bl_idname != "NodeSocketVirtual":
                for l in inplinks:
                    if l.from_socket == out:
                        sortedlinks.append(l)

    return sortedlinks


def get_inputnodes(nodes):
    innodes = []
    for node in nodes:
        if node.bl_idname == 'NodeGroupInput':
            innodes.append(node)
            
    return innodes


def get_putput_index(link, node, socket, inout):
    if inout == 'OUT':
        for i, out in enumerate(node.outputs):
            for li in out.links:
                if link ==  li:
                    index = i
                    break
    elif inout == 'IN':
        for i, inp in enumerate(node.inputs):
            for li in inp.links:
                if link ==  li:
                    index = i
                    break
    return index




def get_idname_from_targetsocket(group, inp):
    #input_node = get_inputnode(group.nodes)
    targetidname = 'MOOOP'
    for link in group.links:
        # ärint(link.from_socket)
        # print(link.to_socket)
        if link.from_socket.name == inp.name:
            targetidname = link.to_socket.bl_idname

    return targetidname


def gen_maininputs(group):
    puts = group.interface.items_tree[:]
    inputs = []
    for n,it in enumerate(puts[:]):
        if it.in_out == 'INPUT':
            inputs.append(it)
        
    for inp in inputs:
        #if inp.bl_socket_idname != 'NodeSocketGeometry':
        print(       
            f"inp = node_group.interface.new_socket(name='{inp.name}', in_out='INPUT', socket_type = '{inp.socket_type}')") #{get_idname_from_targetsocket(group, inp)}
        if hasattr(inp, "default_value"):
            if get_value(inp.default_value) != '':
                print(
                    f"inp.default_value = {get_value(inp.default_value)}")
        # max min causing problems: controller will be set to min or max (inf, ) not the default
        '''if hasattr(inp, "min_value"):
            print(f"inp.min_value = {inp.max_value}")
        if hasattr(inp, "max_value"):
            print(f"inp.max_value = {inp.max_value}")'''

    # group.inputs

def gen_frames(group):
    
    for node in group.nodes:
        if node.bl_idname == 'NodeFrame':
            
            print('')
            print(f'node = nodes.new("{node.bl_idname}" )')
            print(f'node.name = "{node.name}" ')
            print(f'node.label = "{node.label}" ')
            #print(f'node.parent = "{node.name}" ')
            if hasattr(node, 'parent'):
                if hasattr(node.parent, 'name'):
                    print(f'node.parent = node_group.nodes["{node.parent.name}"]')
            print(
                f'node.location = ({int(node.location[0])}, {int(node.location[1])})')


def set_current_maininputs(mod):
    
    #Socket number doesn't fit values that get evaluated, because identifier added with adding socket and is maybe later moved 
    print("'''")
    if mod != None:
        for inp in mod.node_group.interface.items_tree:
            if inp.bl_socket_idname != 'NodeSocketGeometry':
                if get_value(mod[inp.identifier]):
                    print(
                        f"mod['{inp.identifier}'] = {get_value(mod[inp.identifier])}")
    print("'''")
            #print(f"Mööp {inp.name} ")



def gen_links(group, nodes, links):

    inplinks = get_sorted_InputLinks(nodes, links)

    # make links from Group Input Node
    for i, l in enumerate(inplinks):
        print(
            f"links.new( nodes['{l.from_node.name}'].outputs[{get_putput_index(l, l.from_node, l.from_socket, 'OUT')}],  nodes['{l.to_node.name}'].inputs[{get_putput_index(l, l.to_node, l.to_socket, 'IN')}])")


    # set- all other links 
    for l in links:
        if 'NodeGroupInput' not in l.from_node.bl_idname:
            #print(
            #   f"links.new( nodes['{l.from_node.name}'].outputs['{l.from_socket.name}'],  nodes['{l.to_node.name}'].inputs['{l.to_socket.name}'])")
            print(
                f"links.new( nodes['{l.from_node.name}'].outputs[{get_putput_index(l, l.from_node, l.from_socket, 'OUT')}],  nodes['{l.to_node.name}'].inputs[{get_putput_index(l, l.to_node, l.to_socket, 'IN')}])")
            
            
            
def gen_group_outputs(group):
    items = group.interface.items_tree[:]
    outputs=[]
    for n,out in enumerate(items[:]):
        if out.in_out == 'OUTPUT':
            outputs.append(out)
                
    for inp in outputs:
        #if inp.bl_socket_idname != 'NodeSocketGeometry':
        print(       
            f"inp = node_group.interface.new_socket(name='{inp.name}', in_out='OUTPUT', socket_type = '{inp.socket_type}')") #{get_idname_from_targetsocket(group, inp)}
    
    

group = bpy.data.node_groups['Spray']

nodes_to_nodecode(group)
