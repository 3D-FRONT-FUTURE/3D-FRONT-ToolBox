# -*- coding: utf-8 -*
import sys
import numpy as np

from Room.math_engine import *


class BoundingBox:
    """
    bounding box
    """
    def __init__(self):
        self.min = np.array([sys.float_info.max,sys.float_info.max,sys.float_info.max])         # lef bottom corner
        self.max = np.array([-sys.float_info.max,-sys.float_info.max,-sys.float_info.max])      # right top corner

    def __repr__(self):
        return 'BoundingBox, {min: %s, max: %s}' % (
            self.uid, self.jid
        )

    def get_corner_2d(self):
        """
        get 4 cornet point
           x---------x
          /|        /|
         / |       / |
        x---------x  |       y
        |  3------|--2       |
        | /       | /        /-->x
        0---------1         z
        :return: array
        """
        arr = []
        arr.append([self.min[0], self.min[2]])
        arr.append([self.max[0], self.min[2]])
        arr.append([self.max[0], self.max[2]])
        arr.append([self.min[0], self.max[2]])
        return np.array(arr)

    def clone(self):
        """
        clone
        :return:
        """
        bbox = BoundingBox()
        bbox.min[0] = self.min[0]
        bbox.min[1] = self.min[1]
        bbox.min[2] = self.min[2]
        bbox.max[0] = self.max[0]
        bbox.max[1] = self.max[1]
        bbox.max[2] = self.max[2]
        return bbox

    def copy(self, bbox):
        """
        copy
        :param bbox:
        :return:
        """
        self.min[0] = bbox.min[0]
        self.min[1] = bbox.min[1]
        self.min[2] = bbox.min[2]
        self.max[0] = bbox.max[0]
        self.max[1] = bbox.max[1]
        self.max[2] = bbox.max[2]

    def is_valid(self):
        """
        valid
        :return:
        """
        if self.max[0] < self.min[0] or self.max[1] < self.min[1] or self.max[2] < self.min[2]:
            return False
        return True

    def center(self):
        """
        center point
        :return: array
        """
        return (self.max + self.min) * 0.5

    def transform(self, pos, rot, scale):
        """
        transform，scale--->rotation---->translation
        :param pos: translation
        :param rot: Quaternion
        :param scale: scale
        :return:
        """
        if not self.is_valid():
            return

        self.scale(scale[0], scale[1], scale[2])

        bbox = self.clone()
        old_min = self.min.copy()
        old_max = self.max.copy()

        def merge_vector(bbox, vec):
            """
            vector merge box
            :param bbox: boundingbox
            :param vec: array
            :return:
            """
            if bbox.min[0] > vec[0]:
                bbox.min[0] = vec[0]
            if bbox.max[0] < vec[0]:
                bbox.max[0] = vec[0]
            if bbox.min[1] > vec[1]:
                bbox.min[1] = vec[1]
            if bbox.max[1] < vec[1]:
                bbox.max[1] = vec[1]
            if bbox.min[2] > vec[2]:
                bbox.min[2] = vec[2]
            if bbox.max[2] < vec[2]:
                bbox.max[2] = vec[2]

        # 遍历8个角点，重新计算包围盒
        rot_matrix = quaternion_to_matrix(rot)

        # min min min
        corner = old_min.copy()
        v = vector_dot_matrix3(corner, rot_matrix)
        bbox.min = v.copy()
        bbox.max = v.copy()

        # min min max
        corner[2] = old_max[2]
        v = vector_dot_matrix3(corner, rot_matrix)
        merge_vector(bbox, v)

        # min max max
        corner[1] = old_max[1]
        v = vector_dot_matrix3(corner, rot_matrix)
        merge_vector(bbox, v)

        # min max min
        corner[2] = old_min[2]
        v = vector_dot_matrix3(corner, rot_matrix)
        merge_vector(bbox, v)

        # max max min
        corner[0] = old_max[0]
        v = vector_dot_matrix3(corner, rot_matrix)
        merge_vector(bbox, v)

        # max max max
        corner[2] = old_max[2]
        v = vector_dot_matrix3(corner, rot_matrix)
        merge_vector(bbox, v)

        # max min max
        corner[1] = old_min[1]
        v = vector_dot_matrix3(corner, rot_matrix)
        merge_vector(bbox, v)

        # max min min
        corner[2] = old_min[2]
        v = vector_dot_matrix3(corner, rot_matrix)
        merge_vector(bbox, v)

        self.min[0] = min(bbox.min[0], bbox.max[0])
        self.min[1] = min(bbox.min[1], bbox.max[1])
        self.min[2] = min(bbox.min[2], bbox.max[2])
        self.max[0] = max(bbox.min[0], bbox.max[0])
        self.max[1] = max(bbox.min[1], bbox.max[1])
        self.max[2] = max(bbox.min[2], bbox.max[2])

        # translation
        self.min += pos
        self.max += pos

        return self

    def merge(self, bbox):
        """
        merge
        :param bbox: boundingbox
        :return: self
        """
        if not self.is_valid():
            self.copy(bbox)
            return

        if self.min[0] > bbox.min[0]:
            self.min[0] = bbox.min[0]
        if self.max[0] < bbox.max[0]:
            self.max[0] = bbox.max[0]
        if self.min[1] > bbox.min[1]:
            self.min[1] = bbox.min[1]
        if self.max[1] < bbox.max[1]:
            self.max[1] = bbox.max[1]
        if self.min[2] > bbox.min[2]:
            self.min[2] = bbox.min[2]
        if self.max[2] < bbox.max[2]:
            self.max[2] = bbox.max[2]
        return self

    def scale_v(self, vec):
        """
        scale by ratio
        :param vec: [1,1,1]
        :return:
        """
        self.scale(vec[0], vec[1], vec[2])

    def scale(self, dx, dy, dz):
        """
        scale by ratio
        :param dx:
        :param dy:
        :param dz:
        :return:
        """
        if not self.is_valid():
            return

        self.min[0] *= dx
        self.min[1] *= dy
        self.min[2] *= dz
        self.max[0] *= dx
        self.max[1] *= dy
        self.max[2] *= dz

    def intersects(self, other):
        """
        intersects
        :param other: boundingbox
        :return: boolean
        """
        if not self.is_valid():
            return False

        if self.max[0] < other.min[0]:
            return False
        if self.max[1] < other.min[1]:
            return False
        if self.max[2] < other.min[2]:
            return False
        if self.min[0] > other.max[0]:
            return False
        if self.min[1] > other.max[1]:
            return False
        if self.min[2] > other.max[2]:
            return False
        return True

    def zoom(self, inch):
        """
        distance zoom
        :param inch: distance -- float
        :return:
        """
        self.min += inch
        self.max -= inch

        if not self.is_valid():
            self.min -= inch
            self.max += inch

    def zoom_xz(self, inch):
        """
        xz-oriented distance zoom
        :param inch: distance -- float
        :return:
        """
        self.min = np.array([self.min[0] + inch, self.min[1], self.min[2] + inch])
        self.max = np.array([self.max[0] - inch, self.max[1], self.max[2] - inch])

    def intersection(self, other):
        """
        intersection between bounding box
        :param other: boundingbox
        :return:
        """
        if not self.is_valid() or not other.is_valid() or not self.intersects(other):
            return None

        x = np.array([self.min[0], self.max[0], other.min[0], other.max[0]])
        y = np.array([self.min[1], self.max[1], other.min[1], other.max[1]])
        z = np.array([self.min[2], self.max[2], other.min[2], other.max[2]])

        x = sorted(x)
        y = sorted(y)
        z = sorted(z)

        intersection = BoundingBox()
        intersection.min = np.array([x[1], y[1], z[1]])
        intersection.max = np.array([x[2], y[2], z[2]])
        return intersection

    def maximum_xz_length(self):
        """
        xz-oriented max length
        :return: float
        """
        if not self.is_valid():
            return 0
        else:
            return max(self.max[0] - self.min[0], self.max[2] - self.min[2])

    def get_dim_length(self, index):
        """
        get side length
        :param index: 0 = x, 1 = y, 2 = z
        :return:  float
        """
        if index == 0:
            return abs(self.max[0] - self.min[0])
        elif index == 1:
            return abs(self.max[1] - self.min[1])
        else:
            return abs(self.max[2] - self.min[2])

    def alignment_checking(self, other):
        """
        judge if neghbor
        :param other: boundingbox
        :return: boolean
        """
        if self.intersects(other):
            return False

        x_gap = min(abs(self.min[0] - other.max[0]), abs(self.max[0] - other.min[0]))
        z_gap = min(abs(self.min[2] - other.max[2]), abs(self.max[2] - other.min[2]))

        if x_gap < 0.01 or z_gap < 0.01:
            return True
        else:
            return False

    def contain_xz(self, other):
        """
        judge if xz-plane inclusion
        :param other: boundingbox
        :return: boolean
        """
        x_tag = other.min[0] >= self.min[0] and other.max[0] <= self.max[0]
        z_tag = other.min[2] >= self.min[2] and other.max[2] <= self.max[2]

        if x_tag and z_tag:
            return True
        else:
            return False
