import os, sys
from tools import ToolKit


class HouseSplitter(object):
    def __init__(self, ):

        self.house_splitted_dict = {}
        self.room_info_list = []
        self.rest_room_info_list = []

        self.room_delete_list = []
        self.each_room_dict = {}

        self.tool = ToolKit()

    def split_house(self, house_info_dict):

        # self.house_info = house_info_dict

        # single
        # only find entrydoor
        entry_room = house_info_dict['maindoor'][0]
        floorplan = house_info_dict['floorplan']

        # print ('entry_room: ', entry_room)

        self.room_delete_list = []
        self.each_room_dict = {}

        # find entry-room
        for i, room_info in enumerate(floorplan):
            if len(room_info['door']) == 0 and len(room_info['hole']) == 0:
                self.room_delete_list.append(i)

            if room_info['room'] == entry_room['room']:
                self.each_room_dict['maindoor'] = [entry_room]
                self.each_room_dict['floorplan'] = [room_info]

                self.room_info_list.append(self.each_room_dict)
                self.room_delete_list.append(i)

        # delete entry-room
        self.rest_room_info_list = self.delete_room(self.room_delete_list,
                                                    floorplan)
        self.room_delete_list = []

        pre_door_list = self.each_room_dict['floorplan'][0]['door']
        pre_hole_list = self.each_room_dict['floorplan'][0]['hole']

        pre_doorhole_list = []
        if len(pre_door_list) > 0:
            for door in pre_door_list:
                pre_doorhole_list.append(door)
        if len(pre_hole_list) > 0:
            for hole in pre_hole_list:
                pre_doorhole_list.append(hole)

        # self.rest_room_info_list
        while len(self.rest_room_info_list) > 0:
            new_doorhole_list = []
            new_doorhole_list = self.split_room(pre_doorhole_list)
            pre_doorhole_list = new_doorhole_list

            if len(new_doorhole_list) == 0:
                # stairwell
                break
                # pass

        # self.house_splitted_dict['rooms'] = self.room_info_list
        self.house_splitted_dict = self.room_info_list

        if len(self.room_info_list) > 0:
            return True
        else:
            return False

    def split_room(self, pre_doorhole_list):

        new_doorhole_list = []
        self.room_delete_list = []

        if len(pre_doorhole_list) > 0 and len(self.rest_room_info_list) > 0:
            for i, room_info in enumerate(self.rest_room_info_list):
                door_list = room_info['door']
                hole_list = room_info['hole']

                door_height_list = room_info['door_height']
                door_height_limit_list = room_info['door_height_limit']

                hole_height_list = room_info['hole_height']
                hole_height_limit_list = room_info['hole_height_limit']

                # delete door
                if len(door_list) > 0:
                    for x, door in enumerate(door_list):
                        if self.is_appeared(door, pre_doorhole_list):

                            next_doorhole = self.find_next_room(room_info)
                            if len(next_doorhole) > 0:
                                for pts in next_doorhole:
                                    new_doorhole_list.append(pts)

                            maindoor_dict = {}
                            maindoor_dict['room'] = room_info['room']
                            maindoor_dict['point'] = door

                            angle, direction = self.tool.compute_door_hole_direction(
                                door)
                            maindoor_dict['angle'] = angle
                            maindoor_dict['direction'] = direction
                            maindoor_dict['height'] = door_height_list[x]
                            maindoor_dict[
                                'height_limit'] = door_height_limit_list[x]

                            self.each_room_dict = {}
                            self.each_room_dict['maindoor'] = [maindoor_dict]
                            self.each_room_dict['floorplan'] = [room_info]

                            self.room_info_list.append(self.each_room_dict)
                            self.room_delete_list.append(i)

                # delete hole
                if len(hole_list) > 0:
                    for x, hole in enumerate(hole_list):
                        if self.is_appeared(hole, pre_doorhole_list):

                            next_doorhole = self.find_next_room(room_info)
                            if len(next_doorhole) > 0:
                                for pts in next_doorhole:
                                    new_doorhole_list.append(pts)

                            maindoor_dict = {}
                            maindoor_dict['room'] = room_info['room']
                            maindoor_dict['point'] = hole

                            angle, direction = self.tool.compute_door_hole_direction(
                                hole)
                            maindoor_dict['angle'] = angle
                            maindoor_dict['direction'] = direction
                            maindoor_dict['height'] = hole_height_list[x]
                            maindoor_dict[
                                'height_limit'] = hole_height_limit_list[x]

                            self.each_room_dict = {}
                            self.each_room_dict['maindoor'] = [maindoor_dict]
                            self.each_room_dict['floorplan'] = [room_info]

                            self.room_info_list.append(self.each_room_dict)
                            self.room_delete_list.append(i)

        if len(self.room_delete_list) > 0:
            self.rest_room_info_list = self.delete_room(
                self.room_delete_list, self.rest_room_info_list)

        return new_doorhole_list

    def find_next_room(self, room_info):
        doorhole_info = []
        if len(room_info['door']) > 0:
            for door in room_info['door']:
                doorhole_info.append(door)
        if len(room_info['hole']) > 0:
            for hole in room_info['hole']:
                doorhole_info.append(hole)

        return doorhole_info

    def is_appeared(self, obj_pts, pts_list):

        obj_coordnite = [obj_pts[0], obj_pts[1], obj_pts[2], obj_pts[3]]
        for ori_pts in pts_list:
            if [ori_pts[4], ori_pts[5], ori_pts[6],
                    ori_pts[7]] == obj_coordnite:
                return True
        return False

    def delete_room(self, delete_list, floorplan):

        del_reverse_list = sorted(set(delete_list), reverse=True)
        for idx in del_reverse_list:
            floorplan.pop(idx)

        return floorplan
