import numpy as np
import sys
import copy
from Room.math_engine import get_nearest_para
from Room.bounding_box import BoundingBox


dist_epsilon = 1e-2


class CameraRelativePosition:
    def __init__(self, refer_position=np.array([0, 0, 0]), direction_2d=np.array([1, 0]), bbox=BoundingBox(),
                 position_str=['center', 'center', 'center']):
        self.position_str = position_str
        self.direction_3d = np.array([direction_2d[0], 0, direction_2d[1]])
        self.vt_3d = np.array([-direction_2d[1], 0, direction_2d[0]])
        self.z_axis = np.array([0, 1, 0])
        self.bbox = bbox
        self.camera_position = copy.deepcopy(refer_position)

    def get_camera_position(self, offset_3d=np.array([0, 0, 0])):
        if self.position_str[0] == 'max':
            self.camera_position += self.bbox.max[0] * self.vt_3d
        elif self.position_str[0] == 'min':
            self.camera_position += self.bbox.min[0] * self.vt_3d

        if self.position_str[1] == 'max':
            self.camera_position[1] = self.bbox.max[1]
        elif self.position_str[1] == 'min':
            self.camera_position[1] = self.bbox.min[1]

        if self.position_str[2] == 'max':
            self.camera_position += self.bbox.max[2] * self.direction_3d
        elif self.position_str[2] == 'min':
            self.camera_position += self.bbox.min[2] * self.direction_3d

        self.camera_position += offset_3d[0] * self.vt_3d + offset_3d[1] * self.z_axis + offset_3d[2] * self.direction_3d
        return self.camera_position


class FloorLine:
    def __init__(self, start_pt=np.array([0, 0]), end_pt=np.array([0, 0])):
        self.start_pt = start_pt
        self.end_pt = end_pt
        self.start_end_vt = self.end_pt - self.start_pt
        self.center_pt = (self.start_pt + self.end_pt) / 2.
        self.len = np.linalg.norm(self.start_end_vt)
        self.vt = self.start_end_vt / self.len if self.len > dist_epsilon else np.array([0, 0])
        self.normal_vt = np.array([self.vt[1], - self.vt[0]])


class BoundingBox2d:
    def __init__(self):
        self.min = np.array([sys.float_info.max, sys.float_info.max])
        self.max = np.array([-sys.float_info.max, -sys.float_info.max])
        self.len = np.array([0., 0.])
        self.center = np.array([0., 0.])
        self.corner_pts = np.array([])

    def update_corner_pts(self):
        self.corner_pts = np.array([self.min, np.array([self.max[0], self.min[1]]),
                                    self.max, np.array([self.min[0], self.max[1]]), self.min])

    def set_min_max(self, min_pt, max_pt):
        self.min = min_pt
        self.max = max_pt
        self.len = self.max - self.min
        self.center = (self.min + self.max) / 2.
        self.update_corner_pts()

    def is_valid(self):
        if self.max[0] < self.min[0] or self.max[1] < self.min[1]:
            return False
        return True

    def merge(self, bbox=None):
        if self.min[0] > bbox.min[0]:
            self.min[0] = bbox.min[0]
        if self.max[0] < bbox.max[0]:
            self.max[0] = bbox.max[0]
        if self.min[1] > bbox.min[1]:
            self.min[1] = bbox.min[1]
        if self.max[1] < bbox.max[1]:
            self.max[1] = bbox.max[1]

        self.len = self.max - self.min
        self.center = (self.min + self.max) / 2.
        self.update_corner_pts()


class InstanceBox:
    def __init__(self, center_pt_2d=np.array([0, 0]), direction_2d=np.array([0, 0]),
                 width=0, depth=0, height=0., type='', jid=''):
        self.center_pt = center_pt_2d
        self.direction = direction_2d
        self.vt = np.array([self.direction[1], -self.direction[0]])
        self.width = width
        self.depth = depth
        self.height = height
        self.corner_pts = np.array([])
        self.box = BoundingBox2d()
        self.type = type
        self.jid = jid

    def set_center(self, center_pt):
        self.center_pt = center_pt
        self.update_corner_pts()

    def set_direction(self, direction):
        self.direction = direction
        self.vt = np.array([self.direction[1], -self.direction[0]])
        self.update_corner_pts()

    def update_corner_pts(self):
        self.corner_pts = np.array([self.center_pt - self.vt * self.width / 2. - self.direction * self.depth / 2.,
                                    self.center_pt + self.vt * self.width / 2. - self.direction * self.depth / 2.,
                                    self.center_pt + self.vt * self.width / 2. + self.direction * self.depth / 2.,
                                    self.center_pt - self.vt * self.width / 2. + self.direction * self.depth / 2.,
                                    self.center_pt - self.vt * self.width / 2. - self.direction * self.depth / 2.])
        self.box.set_min_max(min_pt=np.array([min(self.corner_pts[:, 0]), min(self.corner_pts[:, 1])]),
                             max_pt=np.array([max(self.corner_pts[:, 0]), max(self.corner_pts[:, 1])]))


class RoomFloor:
    def __init__(self, floor_info=[], window_info=[]):
        self.floor_info = floor_info
        self.window_info = window_info
        self.floor_vertexes = np.array(floor_info)
        self.window_pts = np.array(window_info)
        self.floor_lines = [FloorLine(self.floor_vertexes[i], self.floor_vertexes[i + 1])
                            for i in range(len(self.floor_vertexes) - 1)]
        self.key_lines = []

    def get_nearest_wall_index(self, pt=np.array([0, 0])):
        para_dist_list = [get_nearest_para([floor_line.start_pt, floor_line.end_pt], pt)
                          for floor_line in self.floor_lines]
        min_dist = 1e4
        nearest_wall_index = -1
        for i, para_dist in enumerate(para_dist_list):
            if para_dist[1] < min_dist:
                min_dist = para_dist[1]
                nearest_wall_index = i

        return nearest_wall_index


class ChildrenRoom(RoomFloor):
    def __init__(self, floor_info=[], window_info=[]):
        RoomFloor.__init__(self, floor_info, window_info)

    def calc_key_lines(self):
        window_center_pt = sum(self.window_pts) / 2.

        floor_line_count = len(self.floor_lines)
        for line_index, line in enumerate(self.floor_lines):
            pt_para, pt_dist = get_nearest_para([line.start_pt, line.end_pt], window_center_pt)
            if -dist_epsilon < pt_para < line.len + dist_epsilon and pt_dist < dist_epsilon:
                prev_line = self.floor_lines[(line_index - 1 + floor_line_count) % floor_line_count]
                next_line = self.floor_lines[(line_index + 1) % floor_line_count]

                if pt_para < line.len / 2.:
                    self.key_lines = [{'line': next_line, 'window_side': 'none'},
                                      {'line': prev_line, 'window_side': 'next'}]
                else:
                    self.key_lines = [{'line': prev_line, 'window_side': 'none'},
                                      {'line': next_line, 'window_side': 'prev'}]
                break



