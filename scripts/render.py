'''
Render multi-view image for object with texture

Support for rgb, depth, normal, mask
'''
from multiprocessing import Pool, Process
import argparse, sys, os, time
import logging
import math
import json
import mathutils



# add current path to env
sys.path.append(os.getcwd()+'/../')
from adapted import AdaptedCameras


parser = argparse.ArgumentParser()




parser.add_argument('--color_depth', type=str, default='8',
                    help='Number of bit per channel used for output. Either 8 or 16.')
parser.add_argument('--format', type=str, default='PNG',
                    help='Format of files generated. Either PNG or OPEN_EXR')
parser.add_argument('--scene_path', type=str, default='./scenes',
                    help='the path of scene obj files')
parser.add_argument('--json_path', type=str, default='./3D-FRONT',
                    help='the path of scene json files')
parser.add_argument('--res', type=float, default=512,
                    help='render image resolution.')

argv = sys.argv[sys.argv.index("--") + 1:]
args = parser.parse_args(argv)

import bpy



def point_at(obj, target, roll=0):
    """
    Rotate obj to look at target

    :arg obj: the object to be rotated. Usually the camera
    :arg target: the location (3-tuple or Vector) to be looked at
    :arg roll: The angle of rotation about the axis from obj to target in radians. 

    Based on: https://blender.stackexchange.com/a/5220/12947 (ideasman42)      
    """
    if not isinstance(target, mathutils.Vector):
        target = mathutils.Vector(target)
    loc = obj.location
    # direction points from the object to the target
    direction = target - loc

    quat = direction.to_track_quat('-Z', 'Y')

    # /usr/share/blender/scripts/addons/add_advanced_objects_menu/arrange_on_curve.py
    quat = quat.to_matrix().to_4x4()
    rollMatrix = mathutils.Matrix.Rotation(roll, 4, 'Z')

    # remember the current location, since assigning to obj.matrix_world changes it
    loc = loc.to_tuple()
    obj.matrix_world = quat * rollMatrix
    obj.location = loc

### setting
bpy.context.scene.use_nodes = True
tree = bpy.context.scene.node_tree
links = tree.links

# Add passes for additionally dumping albedo and normals.
bpy.context.scene.render.layers["RenderLayer"].use_pass_normal = True
# bpy.context.scene.render.layers["RenderLayer"].use_pass_color = True
bpy.context.scene.render.layers["RenderLayer"].use_pass_environment = True
bpy.context.scene.render.image_settings.file_format = args.format
bpy.context.scene.render.image_settings.color_depth = args.color_depth

# Clear default nodes
for n in tree.nodes:
    tree.nodes.remove(n)

# Create input render layer node.
render_layers = tree.nodes.new('CompositorNodeRLayers')

depth_file_output = tree.nodes.new(type="CompositorNodeOutputFile")
depth_file_output.label = 'Depth Output'
if args.format == 'OPEN_EXR':
    links.new(render_layers.outputs['Depth'], depth_file_output.inputs[0])
else:
    # Remap as other types can not represent the full range of depth.
    normalize = tree.nodes.new(type="CompositorNodeNormalize")
    links.new(render_layers.outputs['Depth'], normalize.inputs[0])
    links.new(normalize.outputs[0], depth_file_output.inputs[0])




scale_normal = tree.nodes.new(type="CompositorNodeMixRGB")
scale_normal.blend_type = 'MULTIPLY'
# scale_normal.use_alpha = True
scale_normal.inputs[2].default_value = (0.5, 0.5, 0.5, 1)
links.new(render_layers.outputs['Normal'], scale_normal.inputs[1])

bias_normal = tree.nodes.new(type="CompositorNodeMixRGB")
bias_normal.blend_type = 'ADD'
# bias_normal.use_alpha = True
bias_normal.inputs[2].default_value = (0.5, 0.5, 0.5, 0)
links.new(scale_normal.outputs[0], bias_normal.inputs[1])

normal_file_output = tree.nodes.new(type="CompositorNodeOutputFile")
normal_file_output.label = 'Normal Output'
links.new(bias_normal.outputs[0], normal_file_output.inputs[0])

albedo_file_output = tree.nodes.new(type="CompositorNodeOutputFile")
albedo_file_output.label = 'Albedo Output'
links.new(render_layers.outputs['Env'], albedo_file_output.inputs[0])

# Delete default cube
bpy.data.objects['Cube'].select = True
bpy.ops.object.delete()
bpy.data.objects['Lamp'].select = True
bpy.ops.object.delete()
    
# render main function
def render_function(model_list, texture_file, cam_info, save_path):
        
    try: 
        for model in model_list:
            bpy.ops.import_scene.obj(filepath=model)
    except: 
        return None

    # bpy.context.scene.render.engine = 'CYCLES'
    for object in bpy.context.scene.objects:
        if object.name in ['Camera']:
            object.select = False
        else:
            object.select = False
            object.cycles_visibility.shadow = False
    
    bpy.data.worlds['World'].use_nodes = True
    bpy.data.worlds['World'].node_tree.nodes['Background'].inputs[0].default_value[0:3] = (0.75, 0.75, 0.75)
    
    def parent_obj_to_camera(b_camera):
        origin = (0, 0, 0)
        b_empty = bpy.data.objects.new("Empty", None)
        b_empty.location = origin
        b_camera.parent = b_empty  # setup parenting

        scn = bpy.context.scene
        scn.objects.link(b_empty)
        scn.objects.active = b_empty
        return b_empty

    scene = bpy.context.scene
    bpy.context.scene.cycles.samples = 20
    scene.render.resolution_x = args.res 
    scene.render.resolution_y = args.res 
    scene.render.resolution_percentage = 100
    scene.render.alpha_mode = 'TRANSPARENT'
    cam = scene.objects['Camera']
    
 
    scene.render.image_settings.file_format = 'PNG'  # set output format to .png



    for output_node in [depth_file_output, normal_file_output, albedo_file_output]:
        output_node.base_path = ''

    
    idx = 1
    for info in cam_info:
        cam.location = (info['pos'][0],3.2,info['pos'][1]) 
        cam.data.angle = 0.9
        point_at(cam, (info['target'][0],3.2,info['target'][1]))

        depth_file_output.file_slots[0].path = os.path.join(save_path, 'depth_%02d'%(idx))
        normal_file_output.file_slots[0].path = os.path.join(save_path, 'normal_%02d'%(idx)) 
        bpy.ops.render.render(write_still=True)
        idx += 1

    # clear sys        
    for object in bpy.context.scene.objects:
        if object.name in ['Camera']:
            object.select = False
        else:
            object.select = True
    bpy.ops.object.delete()  

    # The meshes still present after delete
    for item in bpy.data.meshes:
        bpy.data.meshes.remove(item)
    for item in bpy.data.materials:
        bpy.data.materials.remove(item)

###### render scenes


scene_list = os.listdir(args.scene_path)
for scene in scene_list:
    mesh_list = []
    tex_list=[]
    room_list = os.listdir(os.path.join(args.scene_path, scene))
    camera = AdaptedCameras(os.path.join(args.json_path, scene+'.json'))
    cam_info = camera.run()
    
    for room in room_list:
        
        if os.path.isfile(os.path.join(args.scene_path, scene, room)):
            continue
        for obj_name in os.listdir(os.path.join(args.scene_path, scene, room)):
            if not obj_name.endswith('.obj'):
                continue
            mesh_list.append(os.path.join(args.scene_path, scene, room, obj_name))
            tex_list.append(os.path.join(args.scene_path, scene, room, obj_name.replace('obj','png')))
    print(cam_info)
    render_function(mesh_list,tex_list,cam_info, os.path.join(args.scene_path, scene))

