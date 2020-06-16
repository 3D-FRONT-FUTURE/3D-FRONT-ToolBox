import shapely.geometry as sg
import numpy as np


def quaternion_to_matrix(args):
    """
    Quaternion to matrix
    :param args:
    :return:
    """
    tx = args[0] + args[0]
    ty = args[1] + args[1]
    tz = args[2] + args[2]
    twx = tx * args[3]
    twy = ty * args[3]
    twz = tz * args[3]
    txx = tx * args[0]
    txy = ty * args[0]
    txz = tz * args[0]
    tyy = ty * args[1]
    tyz = tz * args[1]
    tzz = tz * args[2]

    result = np.zeros((3, 3))
    result[0, 0] = 1.0 - (tyy + tzz)
    result[0, 1] = txy - twz
    result[0, 2] = txz + twy
    result[1, 0] = txy + twz
    result[1, 1] = 1.0 - (txx + tzz)
    result[1, 2] = tyz - twx
    result[2, 0] = txz - twy
    result[2, 1] = tyz + twx
    result[2, 2] = 1.0 - (txx + tyy)
    return result


def quaternion_to_dir(qua, axis = np.array([0, 0, 1])):
    """
    Quaternion to orientation
    :param qua
    :param axis
    :return:
    """
    rotMatrix = quaternion_to_matrix(qua)
    return vector_dot_matrix3(axis, rotMatrix)


def vector_dot_matrix3(v, mat):
    rot_mat = np.mat(mat)
    vec = np.mat(v).T
    result = np.dot(rot_mat, vec)
    return np.array(result.T)[0]


def line_line_intersection(line1, line2):
    """
    intersection between lines
    :param line1:
    :param line2:
    :return: array
    """
    l1 = sg.LineString(line1)
    l2 = sg.LineString(line2)
    inter = l1.intersection(l2)

    start_pt = line1[0]
    if inter.type == 'Point':
        return np.array(inter)
    elif inter.type == 'MultiPoint':
        first = np.array(inter)[0]
        last = np.array(inter)[-1]
        if sum((first - start_pt) ** 2) < sum((last - start_pt) ** 2):
            return first
        else:
            return last
    return np.zeros(0)


def length(v):
    d = np.sqrt(np.sum(v ** 2))
    return d


def normalize(v):
    d = length(v)
    return v / d


def angle(v1, v2):
    s1 = normalize(v1)
    s2 = normalize(v2)
    cosin = s1.dot(s2)
    return np.arccos(np.clip(cosin, -1, 1))


def get_box(x,z,dx,dz):
    direction = np.array([dx, dz])
    normal = np.array([dz, -dx])
    v1 = - x * normal * 0.5 - z * direction * 0.5
    v2 = x * normal * 0.5 - z * direction * 0.5
    v3 = x * normal * 0.5 + z * direction * 0.5
    v4 = - x * normal * 0.5 + z * direction * 0.5
    return np.array([v1, v2, v3, v4])


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


def check_box_clamp_wall(floor_info, box):
    box_min, box_max = box
    x_half, z_half = (box_max - box_min) * 0.5
    center = (box_min + box_max) * 0.5
    clamp_dirs = set()
    
    for i in range(1,len(floor_info)):
        v1 = np.array(floor_info[i-1])
        v2 = np.array(floor_info[i])
        edge = v2 - v1
        if np.fabs(edge[0]) < 1e-3:
            dist = np.fabs(center[0] - v1[0])
            if np.fabs(dist - x_half) < 0.2:
                if edge[1] > 0:
                    clamp_dirs.add((-1, 0))
                else:
                    clamp_dirs.add((1, 0))
                    
        elif np.fabs(edge[1]) < 1e-3:
            dist = np.fabs(center[1] - v1[1])
            if np.fabs(dist - z_half) < 0.2:
                if edge[0] > 0:
                    clamp_dirs.add((0, -1))
                else:
                    clamp_dirs.add((0, 1))
        else:
            pass
        
    return clamp_dirs
    
    
    
    
        