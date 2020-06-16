# # -*- coding: utf-8 -*
import numpy as np
import math
import sys
import shapely.geometry as sg

epsilon = 1e-7
identity_rot = np.array([0.0, 0.0, 0.0, 1.0])


def to_utf8(str):
    """
    string convertor
    :param str:
    :return:
    """
    return str.encode('utf-8', 'surrogateescape').decode('utf-8')


def clamp(value, low, high):
    return max(low, min(value, high))


def to_radian(v):
    """
    degree to radian
    :param v:
    :return:
    """
    return v / 180.0 * math.pi


def to_degree(v):
    """
    radian to degree
    :param v:
    :return:
    """
    return v / math.pi * 180.0


def vector_dot_matrix3(v, mat):
    rot_mat = np.mat(mat)
    vec = np.mat(v).T
    result = np.dot(rot_mat, vec)
    return np.array(result.T)[0]


def vector_dot_matrix4(v, rotMat, trans):
    return vector_dot_matrix3(v, rotMat) + trans


def vector_dot_matrix4(v4, mat):
    vec = np.mat(v4).T
    result = np.dot(mat, vec)
    return np.array(result.T)[0]


def calculate_degree(p1, p2):
    """
    calculate degree by vectors
    :param p1:
    :param p2:
    :return:
    """
    dot = np.dot(p1, p2)
    if math.fabs(dot - 1.0) <= epsilon:
        return 0.0
    elif math.fabs(dot + 1.0) <= epsilon:
        return 180.0

    p1pow = p1 ** 2
    p2pow = p2 ** 2
    angle = math.acos(dot / math.sqrt((p1pow[0] + p1pow[2]) * (p2pow[0] + p2pow[2])))
    cross = p1[0] * p2[2] - p1[2] * p2[0]
    if cross < 0.0:
        angle = 2 * math.pi - angle

    return to_degree(angle)

    # p1pow = p1 ** 2
    # p2pow = p2 ** 2
    # d = 0
    # try:
    #     d = math.acos(dot / math.sqrt((p1pow[0] + p1pow[2]) * (p2pow[0] + p2pow[2])))
    # except Exception as e:
    #     d = 0
    # d = to_degree(d)
    # 角度用0-180
    # if(d > 90.0):
    #     d = 180.0 - d
    # return d


def cross(va, vb):
    return np.array([va[1]*vb[2]-va[2]*vb[1], va[2]*vb[0]-va[0]*vb[2], va[0]*vb[1]-va[1]*vb[0]])


def cross_2d(v1, v2):
    return v1[0]*v2[1] - v1[1]*v2[0]


def normalize(v):
    len = 1.0 / math.sqrt(v[0]*v[0] + v[1]*v[1] + v[2]*v[2])
    return np.array([v[0]*len, v[1]*len, v[2]*len])


def normallize_2d(v):
    len = 1.0 / math.sqrt(v[0] * v[0] + v[1] * v[1])
    return np.array([v[0] * len, v[1] * len])


def length2(v):
    return v[0] * v[0] + v[1] * v[1] + v[2] * v[2]


def length2_2d(v):
    return v[0]*v[0] + v[1]*v[1]


# boolean operation
def polygon_polygon_contains(poly1, poly2):
    """
    plane inclusion
    :param poly1:
    :param poly2:
    :return: boolean
    """
    p1 = sg.Polygon(poly1)
    p2 = sg.Polygon(poly2)
    return p1.contains(p2)


def polygon_polygon_intersects(poly1, poly2):
    """
    intersection between plane
    :param poly1:
    :param poly2:
    :return: boolean
    """
    p1 = sg.Polygon(poly1)
    p2 = sg.Polygon(poly2)
    return p1.intersects(p2)

    # if (inter.type != 'Polygon' and p1.intersects(p2) == True):
    #     return True
    # return False


def polygon_polygon_intersection(poly1, poly2):
    """
    intersection between plane
    :param poly1:
    :param poly2:
    :return: array
    """
    p1 = sg.Polygon(poly1)
    p2 = sg.Polygon(poly2)
    inter = p1.intersection(p2)

    if inter.type != 'Polygon':
        return np.zeros(0)

    ar = np.array(inter.exterior.coords.xy)
    ar = list(zip(ar[0], ar[1]))
    ar.pop()
    return np.array(ar)

    # if(result.type == 'Point'):
    #     return np.array([result.x, 0.0, result.y])
    # elif(result.type == 'LineString'):
    #     ar = np.array(result.xy)
    #     n = np.zeros(int(ar.size / 2))
    #     return np.array(list(zip(ar[0], n, ar[1])))
    # elif(result.type == 'Polygon'):
    #     ar = np.array(result.exterior.coords.xy)
    #     n = np.zeros(int(ar.size / 2))
    #     ar = list(zip(ar[0], n, ar[1]))
    #     ar.pop()
    #     return np.array(ar)
    #
    # return np.zeros(0)


def line_polygon_intersects(line, polygon, enable_touch = False):
    """
    intersection between line and plane
    :param line:
    :param polygon:
    :param enable_touch: enable_touch = True 
    :return: boolean
    """
    p1 = sg.Polygon(polygon)
    l1 = sg.LineString(line)
    inter = l1.intersection(p1)
    if inter.type == 'GeometryCollection':
        return False

    if not enable_touch:
        loop = sg.LinearRing(polygon)
        inter_lp = inter.intersection(loop)
        if inter_lp.type == 'Point' or inter_lp.type == 'MultiPoint':
            return True
        return False
    else:
        return True


def line_polygon_intersection(line, polygon):
    """
    intersection between line and plane
    :param line:
    :param polygon:
    :return: boolean
    """
    p1 = sg.Polygon(polygon)
    l1 = sg.LineString(line)
    inter = l1.intersection(p1)
    if inter.type == 'GeometryCollection':
        return np.zeros(0)

    ar = np.array(inter)
    return np.array(list(zip(ar[:,0], ar[:,1])))


def line_to_polygon_by_line(line, dir, offset):
    """
    :param line: 
    :param dir: 
    :param offset: 
    :return:
    """
    point_a = line[0]
    point_b = line[1]
    result = []
    result.append(point_a)
    result.append(point_b)

    point_c = point_b + dir * offset
    point_d = point_a + dir * offset
    result.append(point_c)
    result.append(point_d)
    result.append(point_a)

    return np.array(result)


def polygon_polygon_touch(poly1, poly2):
    """
    :param poly1:
    :param poly2:
    :return: boolean
    """
    p1 = sg.LinearRing(poly1)
    p2 = sg.LinearRing(poly2)
    inter = p1.intersection(p2)

    if inter.type == 'LineString':
        return np.array(inter)
    elif inter.type == 'MultiLineString':
        ar = []
        for line in inter:
            ar += list(zip(line.xy[0], line.xy[1]))
        return np.array(ar)
    return np.zeros(0)


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


def line_line_intersects(line1, line2):
    """
    intersection between lines
    :param line1:
    :param line2:
    :return: boolean
    """
    l1 = sg.LineString(line1)
    l2 = sg.LineString(line2)
    return l1.intersects(l2)


def check_common_line(v1, v2, v3):
    """
    
    :param v1:
    :param v2:
    :param v3:
    :return:
    """
    vec1 = v2 - v1
    vec2 = v3 - v2

    if abs(cross_2d(vec1, vec2)) < 0.001:
        return True
    return False


def merge_polygon(vertex_array, index_array):
    """
    merge_polygon
    :param vertex_array
    :param index_array
    :return: array
    """
    # p1 = sg.Polygon([[0,0], [1,1], [2,2]])
    # p2 = sg.Polygon([[10,10], [11,11], [12,12]])
    # poly = p1.union(p2)

    poly = 0
    for i in range(0, len(index_array), 3):
        v_list = []
        for j in range(3):
            v1 = vertex_array[3 * index_array[i + j] + 0]
            v2 = vertex_array[3 * index_array[i + j] + 2]
            v_list.append([v1, v2])

        if check_common_line(np.array(v_list[0]), np.array(v_list[1]), np.array(v_list[2])):
            continue

        if poly == 0:
            poly = sg.Polygon(v_list)
        else:
            p = sg.Polygon(v_list)
            poly = poly.union(p)

    if poly == 0:
        return []

    if poly.type == 'MultiPolygon':
        tt = poly.wkt

    ar_xy = poly.exterior.coords.xy
    length_ar = len(ar_xy[0]) - 1
    result = []

    for i in range(length_ar):
        v_list = []
        for j in range(3):
            index = (i + j) % length_ar
            v_list.append(np.array([ar_xy[0][index], ar_xy[1][index]]))

        if check_common_line(v_list[0], v_list[1], v_list[2]) == True:
            continue

        index = (i + 1) % length_ar
        result.append([ar_xy[0][index], ar_xy[1][index]])

    return result


def get_area(poly):
    """
    get area
    :param poly:
    :return:
    """
    ply = sg.Polygon(poly)
    return ply.area


# judge rotation angle in [90, 270]
def is_rot(rot):
    axis = quaternion_to_axis(rot)
    if axis[1] < 0.0 or axis[3] == 360.0:
        axis[3] = 360.0 - axis[3]

    if axis[3] < 20.0 or (axis[3] > 160.0 and axis[3] < 200.0) or axis[3] > 340.0:
        return False
    else:
        return True


# Quaternion
def quaternion_from_axis(angle, axis):
    """
    quaternion_from_axis
    :param angle
    :param axis: [0,1,0]
    :return:
    """
    result = np.zeros(4)
    halfAngle = 0.5 * to_radian(angle)
    fSin = math.sin(halfAngle)
    result[3] = math.cos(halfAngle)
    result[0] = fSin * axis[0]
    result[1] = fSin * axis[1]
    result[2] = fSin * axis[2]
    return result


def quaternion_to_axis(args):
    """
    quaternion_to_axis
    :param args: [0,0,0,1]
    :return: vector4(x,y,z,angle)
    """
    result = np.array([0.0, 1.0, 0.0, 0.0])
    sqrLen = args[0] * args[0] + args[1] * args[1] + args[2] * args[2]
    if sqrLen > 0.0:
        result[3] = to_degree(2.0 * math.acos(clamp(args[3], -1.0, 1.0)))
        fInvLen = 1.0 / math.sqrt(sqrLen)
        result[0] = args[0] * fInvLen
        result[1] = args[1] * fInvLen
        result[2] = args[2] * fInvLen
    return result


def quaternion_muli(qua1, qua2):
    """
    quaternion_muli
    :param qua1:
    :param qua2:
    :return:
    """
    result = np.zeros(4)
    result[0] = qua1[3] * qua2[0] + qua1[0] * qua2[3] + qua1[1] * qua2[2] - qua1[2] * qua2[1]
    result[1] = qua1[3] * qua2[1] + qua1[1] * qua2[3] + qua1[2] * qua2[0] - qua1[0] * qua2[2]
    result[2] = qua1[3] * qua2[2] + qua1[2] * qua2[3] + qua1[0] * qua2[1] - qua1[1] * qua2[0]
    result[3] = qua1[3] * qua2[3] - qua1[0] * qua2[0] - qua1[1] * qua2[1] - qua1[2] * qua2[2]

    # check if error
    if np.sum(abs(identity_rot + result)) < 0.001:
        result = identity_rot.copy()

    return result


def quaternion_invert(qua):
    """
    :param qua:
    :return:
    """
    result = np.zeros(4)
    norm = qua[0] * qua[0] + qua[1] * qua[1] + qua[2] * qua[2] + qua[3] * qua[3]
    if norm > 0.0:
        result[0] = -qua[0] / norm
        result[1] = -qua[1] / norm
        result[2] = -qua[2] / norm
        result[3] = qua[3] / norm
    return result


def dir_to_quaternion(dir, axis = np.array([0.0, 0.0, 1.0])):
    """
    :param dir: numpy [0,0,1]
    :param axis
    :return:
    """
    angle = calculate_degree(dir, axis)
    if angle >= 360.0:
        angle = 360.0 - angle

    return quaternion_from_axis(angle, np.array([0.0, 1.0, 0.0]))


def quaternion_to_dir(qua, axis = np.array([0, 0, 1])):
    """
    :param qua: quaternion
    :param axis: direction
    :return:
    """
    rotMatrix = quaternion_to_matrix(qua)
    return vector_dot_matrix3(axis, rotMatrix)


def quaternion_to_matrix(args):
    """
    quaternion_to_matrix
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


# get dir by rotate
def get_dir_by_rotate(rotate):
    furniture_qua = quaternion_to_matrix(rotate)
    dir = np.array([0, 0, 1])
    furniture_dir = vector_dot_matrix3(dir, furniture_qua)
    furniture_dir_2d = np.array([furniture_dir[0], furniture_dir[2]])
    furniture_dir_2d = normallize_2d(furniture_dir_2d)
    return furniture_dir_2d


def get_reflect_matrix(normal):
    result = np.zeros((3, 3))
    result[0, 0] = 1.0 - 2.0 * normal[0] * normal[0]
    result[0, 1] = -2.0 * normal[1] * normal[0]
    result[0, 2] = -2.0 * normal[2] * normal[0]
    result[1, 0] = -2.0 * normal[0] * normal[1]
    result[1, 1] = 1.0 - 2.0 * normal[1] * normal[1]
    result[1, 2] = -2.0 * normal[2] * normal[1]
    result[2, 0] = -2.0 * normal[0] * normal[2]
    result[2, 1] = -2.0 * normal[1] * normal[2]
    result[2, 2] = 1.0 - 2.0 * normal[2] * normal[2]
    return result


def get_view_matrix(eye, target, up=np.array([0.0, 1.0, 0.0])):
    f = normalize(target - eye)
    s = normalize(np.cross(f, up))
    u = cross(s, f)

    result = np.zeros((4, 4))
    result[0][0] = s[0]
    result[0][1] = s[1]
    result[0][2] = s[2]
    result[0][3] = -np.dot(s, eye)
    result[1][0] = u[0]
    result[1][1] = u[1]
    result[1][2] = u[2]
    result[1][3] = -np.dot(u, eye)
    result[2][0] = -f[0]
    result[2][1] = -f[1]
    result[2][2] = -f[2]
    result[2][3] = np.dot(f, eye)
    result[3][3] = 1.0
    return result


def get_project_matrix(aspect, fov, near=0.1, far=100.0):
    theta_y = to_radian(fov * 0.5)
    tan_theta_y = math.tan(theta_y)
    tan_theta_x = tan_theta_y * aspect

    half_w = tan_theta_x * near
    half_h = tan_theta_y * near

    left = -half_w
    top = half_h
    right = half_w
    bottom = -half_h

    inv_w = 1.0 / (right - left)
    inv_h = 1.0 / (top - bottom)
    inv_d = 1.0 / (far - near)

    a = 2.0 * near * inv_w
    b = 2.0 * near * inv_h
    c = (right + left) * inv_w
    d = (top + bottom) * inv_h

    q = -(far + near) * inv_d
    qn = -2.0 * (far * near) * inv_d

    result = np.zeros((4, 4))
    result[0][0] = a
    result[0][2] = c
    result[1][1] = b
    result[1][2] = d
    result[2][2] = q
    result[2][3] = qn
    result[3][2] = -1.0
    return result


def is_visible_by_point(point, view_project_matrix):
    # v = np.array([point[0], point[1], point[2], 1.0])
    # p = vector_dot_matrix4(v, view_project_matrix)
    # p_x = p[0] / p[3]
    # p_y = p[1] / p[3]
    # p_depth = p[2] / p[3]

    p_x, p_y, p_depth = project_point(point, view_project_matrix)

    if p_x > 0.99 or p_x < -0.99 or p_y > 0.99 or p_y < -0.99 or p_depth > 0.99 or p_depth < 0.001:
        return False

    return True


def project_point(point, view_project_matrix):
    v = np.array([point[0], point[1], point[2], 1.0])
    p = vector_dot_matrix4(v, view_project_matrix)
    p_x = p[0] / p[3]
    p_y = p[1] / p[3]
    p_depth = p[2] / p[3]

    return np.array([p_x, p_y, p_depth])


def get_nearest_para(line, pt):
    if len(line) != 2:
        return sys.maxsize, sys.maxsize

    pt0 = np.array(line[0])
    pt1 = np.array(line[1])
    line_vt = pt1 - pt0

    line_len = np.linalg.norm(line_vt)

    if line_len < epsilon:
        return sys.maxsize, sys.maxsize

    line_vt = line_vt / line_len
    temp_vt = pt - pt0
    para = np.dot(line_vt, temp_vt)
    projected_pt = pt0 + para * line_vt

    dist_vt = pt - projected_pt

    return para, np.linalg.norm(dist_vt)
