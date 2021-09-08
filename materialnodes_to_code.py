import bpy


# problems:
# math node inputs are all called "value" --> enumerate
# operations and blend_type not covered
# group input Output

context = bpy.context
sel = [x for x in bpy.data.materials['AdvOceanMat_Ocean 3.0Windpatch'].node_tree.nodes if x.select]


for s in sel:
    new = "node =  nodes.new('" + s.bl_idname + "')"
    print(new)
    print("#node.parent= ")
    print("node.location= (" +
          str(int(s.location[0])) + "+xoff" + "," + str(int(s.location[1])) + "+yoff)")
    print("node.label= '" + s.label + "'")
    print("node.name= '" + s.label + "'")

    print("node.hide= " + str(s.hide))
    for n, inp in enumerate(s.inputs):
        print("node.inputs[" + str(n) +
              "].default_value = " + str(inp.default_value))
    print('')
    print("##################################################")


def gen_links(links):
    for l in links:
        print(
            f"links.new( nodes['{l.from_node.name}'].outputs['{l.from_socket.name}'],  nodes['{l.to_node.name}'].inputs['{l.to_socket.name}'])")


for s in sel:
    if s.bl_idname != "NodeFrame":
        for inp in s.inputs:
            gen_links(inp.links)


print("#################################################################")
print("#################################################################")
