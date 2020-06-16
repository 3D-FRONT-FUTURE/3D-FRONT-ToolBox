# # -*- coding: utf-8 -*
import numpy as np
from Room.bounding_box import BoundingBox
from Room.math_engine import *


class Entity:
    """
    layout object
    """

    def __init__(self, instance):
        self.instance = instance                            # instance object
        self.type = ''                                      # data type
        self.bounding_box = BoundingBox()                  # box
        self.rotate = np.array([0.0, 0.0, 0.0, 1.0])        # [0,0,0,1]
        self.position = np.array([0.0, 0.0, 0.0])           # [0,0,0
        self.scale = np.array([1.0, 1.0, 1.0])              # [1,1,1]
        self.used = True                                    # is used
        self.clamp_wall = False                             # clamp wall
        self.clamp_rotate_list = []                         # clamp direction
        self.children = []                                  # child object
        self.parent = None                                  # parent object
        self.modify = False                                 # is transform
        self.instance_id = 'id'                             # reflect instanceid
        self.instance_ref = ''                              # reflect uid
        self.use_gmm = False                                # is gmm
        self.special_children = []                          # bed and bedstand
        # self.align_neighbours = []

        # 规则摆放
        self.mainObject = False
        self.valid = True

        self.is_sale = False                                # 是否为在售商品

    def __repr__(self):
        return 'Entity %s, {type: %s}' % (
            self.id, self.type
        )

    # def add_align_neighbour(self, obj):
    #     self.align_neighbours.append(obj)

    def add_child(self, node):
        """
        add child node
        :param node:
        :return:
        """
        self.children.append(node)
        node.parent = self

    def set_position(self, pos):
        """
        set position
        :param pos:
        :return:
        """
        offset = pos - self.position
        self.position = pos
        for child in self.children:
            child.transform(offset)

    def set_rotate(self, rot):
        """
        set rotate
        :param rot:
        :return:
        """
        invert_rot = quaternion_invert(self.rotate)
        for i, clp_rot in enumerate(self.clamp_rotate_list):
            cur_rot = quaternion_muli(invert_rot, clp_rot)
            cur_rot = quaternion_muli(rot, cur_rot)
            self.clamp_rotate_list[i] = cur_rot

        self.rotate = rot

        rel_rot = quaternion_muli(rot, invert_rot)
        rotMat = quaternion_to_matrix(rel_rot)
        for child in self.children:
            pos = child.position - self.position
            child.position = vector_dot_matrix3(pos, rotMat) + self.position

            child_rot = quaternion_muli(child.rotate, rel_rot)
            child.set_rotate(child_rot)

        # self.rotate = rot
        # for child in self.children:
        #     child.set_rotate(rot)

    def set_scale(self, scale, is_local=False):
        """
        set scale
        :param scale:
        :param is_local:
        :return:
        """
        t_scale = scale.copy()
        if not is_local and is_rot(self.rotate):
            t_scale[0] = scale[2]
            t_scale[2] = scale[0]

        cur_scale = t_scale / self.scale
        self.scaling(cur_scale, True)

    def transform(self, pos):
        """
        transform
        :param pos:
        :return:
        """
        self.position = self.position + pos
        for child in self.children:
            child.transform(pos)

    def rotation(self, rot):
        """
        rotation
        :param rot:
        :return:
        """
        for i, clp_rot in enumerate(self.clamp_rotate_list):
            self.clamp_rotate_list[i] = quaternion_muli(rot, clp_rot)

        rotMat = quaternion_to_matrix(rot)
        self.position = vector_dot_matrix3(self.position, rotMat)
        self.rotate = np.array(quaternion_muli(rot, self.rotate))
        for child in self.children:
            child.rotation(rot)

    def scaling(self, scale, is_local=False):
        """
        scaling
        :param scale:
        :param is_local:
        :return:
        """
        t_scale = scale.copy()
        if not is_local and is_rot(self.rotate):
            t_scale[0] = scale[2]
            t_scale[2] = scale[0]

        for child in self.children:
            child.transform(-self.position)

            if is_local:
                rot_matrix = quaternion_to_matrix(quaternion_invert(self.rotate))
                pos = vector_dot_matrix3(child.position, rot_matrix)
                pos *= scale
                pos = vector_dot_matrix3(pos, quaternion_to_matrix(self.rotate)) + self.position
            else:
                pos = child.position * scale + self.position

            child.set_position(pos)

            value = min(abs(scale[0]), abs(scale[2]))
            child.scaling(np.array([value, value, value]))

        self.scale = self.scale * t_scale

    def mirror(self, axis):
        """
        mirror
        :param axis: axis = 0, x; axis = 1, y
        :return:
        """
        if axis == 0:
            reflect_matrix = get_reflect_matrix([1, 0, 0])
            scale = np.array([-1, 1, 1])
        else:
            reflect_matrix = get_reflect_matrix([0, 0, 1])
            scale = np.array([-1, 1, 1])

        self.position = vector_dot_matrix3(self.position, reflect_matrix)

        dir = quaternion_to_dir(self.rotate)
        dir = vector_dot_matrix3(dir, reflect_matrix)
        self.rotate = dir_to_quaternion(dir)
        self.scale *= scale

        for child in self.children:
            child.mirror(axis)

        for i, clp_rot in enumerate(self.clamp_rotate_list):
            dir = quaternion_to_dir(clp_rot)
            dir = vector_dot_matrix3(dir, reflect_matrix)

            self.clamp_rotate_list[i] = dir_to_quaternion(dir)

    def set_used(self, value):
        """
        set_used
        :param value:
        :return:
        """
        self.used = value
        for child in self.children:
            child.set_used(value)

    def get_bounding_box(self):
        """
        get_bounding_box
        :return:
        """
        bbox = self.bounding_box.clone()
        bbox.transform(self.position, self.rotate, self.scale)
        return bbox
