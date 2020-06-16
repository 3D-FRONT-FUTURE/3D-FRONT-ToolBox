# -*- coding: utf-8 -*
import numpy as np
from Room.bounding_box import BoundingBox


class Mesh:
    """
    mesh info
    """

    def __init__(self):
        self.bounding_box = BoundingBox()      # box
        self.vertex_array = []                  # vertex
        self.index_array = []                   # index
        self.normal = 0                         # normal
        self.uv = 0                             # texcoord

    def __repr__(self):
        return 'Mesh '

    def set_data(self, vertex_array, index_array):
        """
        :param vertex_array
        :param index_array
        :return:
        """
        vertex_count = len(vertex_array)
        index_count = len(index_array)
        if(vertex_count < 3 or index_count < 3):
            return

        self.index_array = np.array(index_array)
        self.index_array = self.index_array.astype(int)

        self.vertex_array = np.array(vertex_array)
        self.vertex_array = self.vertex_array.astype(float)

        # # bbox
        # v = []
        # for i in self.index_array:
        #     v.append(self.vertex_array[nDim * int(i)])
        #     v.append(self.vertex_array[nDim * int(i) + 1])
        #     v.append(self.vertex_array[nDim * int(i) + 2])
        # self.bounding_box.setBox(v, 3)

    def set_normal_uv(self, normal, uv):
        """
        :param normal
        :param uv
        :return:
        """
        self.normal = np.array(normal)
        self.uv = np.array(uv)

    def cal_boundingbox(self):
        """
        :return:
        """
        if self.bounding_box.is_valid():
            return

        vertex_count = len(self.vertex_array)
        index_count = len(self.index_array)
        if (vertex_count < 3 or index_count < 3):
            return

        nDim = 3
        # bbox
        vertex_x = []
        vertex_y = []
        vertex_z = []
        for i in self.index_array:
            vertex_x.append(float(self.vertex_array[nDim * int(i)]))
            vertex_y.append(float(self.vertex_array[nDim * int(i) + 1]))
            vertex_z.append(float(self.vertex_array[nDim * int(i) + 2]))

        if (len(vertex_x) < 2):
            return

        self.bounding_box.min[0] = min(vertex_x)
        self.bounding_box.min[1] = min(vertex_y)
        self.bounding_box.min[2] = min(vertex_z)
        self.bounding_box.max[0] = max(vertex_x)
        self.bounding_box.max[1] = max(vertex_y)
        self.bounding_box.max[2] = max(vertex_z)
