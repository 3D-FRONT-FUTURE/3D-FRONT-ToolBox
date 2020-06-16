import numpy as np
import shapely.geometry as sg
from Room.scene import Scene
from Room.process_json import process_json_house
import json
from Room.Preprocess.run import scene_to_floorplan



def normalize(vec):
    dist = np.sqrt(np.sum(vec ** 2))
    return vec / dist


def compute_distance(v1, v2):
    vec = v1 - v2
    return np.sqrt(np.sum(vec ** 2))


def read_scene_json(filename):
    try:
        house_content = json.load(open(filename, 'r', encoding='utf-8'))
    except Exception as e:
        print('Error1001: Failed to load scene file.', e)
        return None
    
    try:
        scene = Scene(filename, house_content)
        process_json_house(scene)
    except Exception as e:
        print('Error1002: Failed to parser json file.', e)
        return None
    return scene


def get_floor_info(filename):
    floor_dict = dict()
    room_floors = scene_to_floorplan(filename)
    if len(room_floors) == 0:
        print('Error1003: Failed to get floorplans.')
        return floor_dict
    
    for room_info in room_floors['floorplan']:
        room_id = room_info['room']
        floor_info = []
        for i in range(0, len(room_info['floor']), 2):
            floor_info.append([
                room_info['floor'][i],
                room_info['floor'][i + 1]
            ])
            
        window_info = []
        window_list = room_info['window'] + room_info['baywindow'] + room_info['hole']
        if len(window_list) > 0:
            window = window_list[0]
            window_info.append([window[0], window[1]])
            window_info.append([window[2], window[3]])
        
        floor_dict[room_id] = {
            'floor': floor_info,
            'window': window_info
        }
    
    return floor_dict


def get_camera_visible_poly(camera_info, floor_info):
    pos = camera_info['pos']
    camera_pos = np.array([pos[0], pos[2]])
    
    fov = camera_info['fov']
    target = camera_info['target']
    camera_target = np.array([target[0], target[2]])
    
    camera_dir = camera_target - camera_pos
    c_unit_dir = camera_dir / np.sqrt(np.sum(camera_dir ** 2))
    c_unit_normal = np.array([-c_unit_dir[1], c_unit_dir[0]])
    half_fov = fov / 2
    
    k1 = np.cos(np.deg2rad(half_fov)) * c_unit_dir + np.sin(np.deg2rad(half_fov)) * c_unit_normal
    k2 = np.cos(np.deg2rad(half_fov)) * c_unit_dir - np.sin(np.deg2rad(half_fov)) * c_unit_normal
    camera_insight_poly = sg.Polygon([camera_pos, camera_pos + 1e3 * k1, camera_pos + 1e3 * k2, camera_pos])
    
    floor_poly = sg.Polygon(floor_info)
    camera_visible_poly = camera_insight_poly.intersection(floor_poly)
    return camera_visible_poly
