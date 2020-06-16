# -*- coding: utf-8 -*
import json
import numpy as np
import os

from Room.instance import Instance
from Room.room import Room
from Room.mesh import Mesh


def process_json_house(scene):
    """
    parse json
    :param scene:
    :return:
    """
    house_content = scene.content

    # furniture
    furniture_content = house_content['furniture']
    for furniture_info in furniture_content:
        uid = furniture_info['uid']
        if scene.find_instance_for_furniture(uid) != 0:
            print("Warning - process_json_house, furniture %s is repeat" % uid)
            continue

        instance = Instance(uid)
        instance.jid = furniture_info['jid']
        instance.aid = furniture_info['aid']
        instance.type = 'furniture'
        scene.add_instance_for_furniture(uid, instance)

    # mesh
    mesh_content = house_content['mesh']
    for mesh_info in mesh_content:
        uid = mesh_info['uid']
        if scene.find_instance_for_mesh(uid) != 0:
            print("Warning - process_json_house, mesh %s is repeat" % uid)
            continue

        instance = Instance(uid)
        instance.jid = mesh_info['jid']
        instance.aid = mesh_info['aid']
        instance.type = mesh_info['type']
        instance.mesh = Mesh()
        instance.mesh.set_data(mesh_info['xyz'], mesh_info['faces'])
        instance.mesh.set_normal_uv(mesh_info['normal'], mesh_info['uv'])
        scene.add_instance_for_mesh(uid, instance)

    # scene
    scene_content = house_content['scene']
    scene.position = np.array(scene_content['pos'])
    scene.rotation = np.array(scene_content['rot'])
    scene.scale = np.array(scene_content['scale'])

    # room
    process_room(scene, scene_content['room'])


def process_room(scene, room_content):
    """
    parse room
    :param scene:
    :param room_content:
    :return:
    """
    if len(room_content) < 1:
        return

    for room_info in room_content:
        room_id = room_info['instanceid']
        if scene.find_room(id) != 0:
            print("Warning - process_room, room %s is repeat" % id)
            continue

        room = Room(room_id, scene)
        room.type = room_info['type']

        if 'pos' in room_info:
            room.position = np.array(room_info['pos'])
            room.rotation = np.array(room_info['rot'])
            room.scale = np.array(room_info['scale'])

        scene.add_room(room_id, room)

        # child
        child_content = room_info['children']
        for i, child_info in enumerate(child_content):
            uid = child_info['ref']

            if 'instanceid' not in child_info:
                child_info['instanceid'] = room_id + '/' + str(i)

            instance_info = {
                'id': uid,
                'pos': np.array(child_info['pos']).astype(np.float),
                'rot': np.array(child_info['rot']).astype(np.float),
                'scale': np.array(child_info['scale']).astype(np.float),
                'instanceid': child_info['instanceid']
            }

            instance = scene.find_instance_for_mesh(uid)
            if instance != 0:
                instance.ref += 1
                room.children_for_mesh.append(instance_info)
            else:
                instance = scene.find_instance_for_furniture(uid)
                if instance != 0:
                    instance.ref += 1
                    room.children_for_furniture.append(instance_info)
                else:
                    print("Warning - process_room, instance %s isn't find" % uid)

