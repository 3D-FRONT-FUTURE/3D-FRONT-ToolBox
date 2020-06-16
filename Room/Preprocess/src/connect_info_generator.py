import os, sys
from shapely.geometry import Polygon, mapping, Point
from tools import ToolKit


class ConnectInfoGenerator(object):
    def __init__(self, ):
        self.tool = ToolKit()
        self.house_floorplan_list = []

        self.index_recombination = [4, 5, 6, 7, 0, 1, 2, 3]

        self.new_pts = []
        self.new_height = []
        self.new_height_limit = []

        # self.draw_room = VisHouse()

    def generate_connect_info(self, house_info_list):

        self.new_pts = []
        self.new_height = 0
        self.new_height_limit = 0

        for i, room_info in enumerate(house_info_list):
            room_floor_list = room_info['floor']

            for j, room_info_other in enumerate(house_info_list):
                if i != j:
                    other_door_list = room_info_other['door']
                    other_hole_list = room_info_other['hole']
                    other_window_list = room_info_other['window']

                    other_door_height_list = room_info_other['door_height']
                    other_hole_height_list = room_info_other['hole_height']
                    other_window_height_list = room_info_other['window_height']

                    other_door_height_limit_list = room_info_other[
                        'door_height_limit']
                    other_hole_height_limit_list = room_info_other[
                        'hole_height_limit']
                    other_window_height_limit_list = room_info_other[
                        'window_height_limit']

                    # doorinfo
                    if len(other_door_list) > 0:
                        for k, other_door in enumerate(other_door_list):
                            if self.is_belong_this_room(
                                    other_door, room_floor_list,
                                    other_door_height_list[k],
                                    other_door_height_limit_list[k]):
                                room_info['door'].append(self.new_pts)
                                room_info['door_height'].append(
                                    self.new_height)
                                room_info['door_height_limit'].append(
                                    self.new_height_limit)
                    # holeinfo
                    if len(other_hole_list) > 0:
                        for k, other_hole in enumerate(other_hole_list):
                            if self.is_belong_this_room(
                                    other_hole, room_floor_list,
                                    other_hole_height_list[k],
                                    other_hole_height_limit_list[k]):
                                room_info['hole'].append(self.new_pts)
                                room_info['hole_height'].append(
                                    self.new_height)
                                room_info['hole_height_limit'].append(
                                    self.new_height_limit)

                    # windowinfo
                    if len(other_window_list) > 0:
                        for k, other_window in enumerate(other_window_list):
                            if self.is_belong_this_room(
                                    other_window, room_floor_list,
                                    other_window_height_list[k],
                                    other_window_height_limit_list[k]):
                                room_info['window'].append(self.new_pts)
                                room_info['window_height'].append(
                                    self.new_height)
                                room_info['window_height_limit'].append(
                                    self.new_height_limit)

            # remove duplicate information
            room_info['door'], room_info['door_height'], room_info[
                'door_height_limit'] = self.remove_duplicate(
                    room_info['door'], room_info['door_height'],
                    room_info['door_height_limit'])
            room_info['hole'], room_info['hole_height'], room_info[
                'hole_height_limit'] = self.remove_duplicate(
                    room_info['hole'], room_info['hole_height'],
                    room_info['hole_height_limit'])
            room_info['window'], room_info['window_height'], room_info[
                'window_height_limit'] = self.remove_duplicate(
                    room_info['window'], room_info['window_height'],
                    room_info['window_height_limit'])
            # print ('room-type: ', room_info['room'])
            # self.draw_room.draw_room(room_info)

        # add connect information
        house_info_list = self.compute_connect_relationship(house_info_list)

        return house_info_list

    def compute_connect_relationship(self, house_info_list):

        for i, room_info in enumerate(house_info_list):

            # doorinfo
            room_info['doorinfo'] = self.add_connect_info(
                i, room_info, house_info_list, 'door')
            # holeinfo
            room_info['holeinfo'] = self.add_connect_info(
                i, room_info, house_info_list, 'hole')
            # windowinfo
            room_info['windowinfo'] = self.add_connect_info(
                i, room_info, house_info_list, 'window')

        return house_info_list

    def add_connect_info(self, idx, room_info, house_info_list, type_='door'):

        obj_info_list = []
        if len(room_info[type_]) > 0:
            for obj_ in room_info[type_]:
                obj_info_dict = {}
                for jdx, other_room_info in enumerate(house_info_list):
                    if idx != jdx:
                        if self.is_appeared(obj_, other_room_info[type_]):
                            obj_info_dict['pts'] = obj_
                            obj_info_dict['to'] = other_room_info['room']
                            obj_info_list.append(obj_info_dict)

        return obj_info_list

    def is_appeared(self, pts, other_pts_list):
        one_pts = [pts[0], pts[1], pts[2], pts[3]]
        for other_pts in other_pts_list:
            another_pts = [
                other_pts[4], other_pts[5], other_pts[6], other_pts[7]
            ]
            if one_pts == another_pts:
                return True

        return False

    def remove_duplicate(self, v_list, height_list, height_limit_list):
        new_v_list = []
        new_height_list = []
        new_height_limit_list = []
        for i, v in enumerate(v_list):
            if v not in new_v_list:
                new_v_list.append(v)
                new_height_list.append(height_list[i])
                new_height_limit_list.append(height_limit_list[i])
        return new_v_list, new_height_list, new_height_limit_list

    def is_belong_this_room(self, pts, room_floor_list, height, height_limit):

        self.new_pts = []
        self.new_height = 0
        self.new_height_limit = 0

        pts_parallel_line_list = self.tool.find_parallel_line(
            [[pts[4], pts[5]], [pts[6], pts[7]]], 0.1)

        floor_polygon = self.tool.floor_to_polygon(room_floor_list).buffer(
            0.0005)

        for line in pts_parallel_line_list:
            for point in line:
                if floor_polygon.contains(Point(point)):
                    for idx in self.index_recombination:
                        self.new_pts.append(pts[idx])
                        self.new_height = height
                        self.new_height_limit = height_limit
                    return True
        return False
