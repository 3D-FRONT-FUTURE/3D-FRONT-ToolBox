import os
import sys
import json
import math
import time
import numpy as np

from logger import logger

from json_information_acquirer import JsonInformationAcquirer
from maindoor_generator import MainDoorGenerator
from floor_generator import FloorGenerator

from door_generator import DoorGenerator
from baywindow_generator import BaywindowGenerator

from connect_info_generator import ConnectInfoGenerator
from floorplan_aftertreatment import AfterTreatement

from house_splitter import HouseSplitter

from tools import ToolKit

class FloorplanGenerator(object):
    def __init__(self):
        self.is_vis = False
        self.is_save_mesh = True
        self.house_info_dict = {}

        self.mesh_type_list = ['Floor', 'Door', 'Hole', 'Window', 'BayWindow', 'WallTop']

        self.json_information_acquirer = JsonInformationAcquirer()
        self.maindoor_generator = MainDoorGenerator()
        self.floor_generator = FloorGenerator()

        self.door_generator = DoorGenerator()
        self.baywindow_generator = BaywindowGenerator()

        self.connect_info_generator = ConnectInfoGenerator()
        self.post_processor = AfterTreatement()
        self.house_splitter = HouseSplitter()

        self.tool = ToolKit()
        # self.draw_room = VisHouse()

        self.error_info_dict = {
            "error": "",
            "data": {
                "entrydoor_room": "",
                "room_num": 0,
                "door_num": 0,
                "hole_num": 0,
                "window_num": 0,
                "baywindow_num": 0,
                "room": {
                    "ok": [],
                    "error": []
                }
            }
        }

    def generate_floorplan(self, filename):
        """get floorpaln funciton
        @input: json filename(realpath)
        Returns:
            @dict -- house dict
        """
        self.house_info_dict = {}
        # logger.i('generate floorplan start... ')
        # determine whether the path exist
        if not os.path.exists(filename):
            logger.e('file not exist:%s' % filename)
            return {}

        try:
            json_data = json.load(open(filename, 'r', encoding='utf-8'))
        except Exception as e:
            logger.e('fail to load file %s: %s' % (filename, e))
            return {}

        # read json.
        # result: self.scene_room_list / self.entrydoor_dict / self.mesh_dict
        if self.json_information_acquirer.get_information(json_data):
            # logger.i('read json done. it is OK ... ')
            pass
        else:
            logger.e('read json done. it is ERROR ... ')
            self.error_info_dict['error'] = 'read json error'
            return {}

        # step2, judge whether the maindoor information is right
        # result: self.maindoor_list / self.is_square / self.maindoor_height_min / self.maindoor_height_max
        # if self.maindoor_generator.get_maindoor(
        #         self.json_information_acquirer.entrydoor_dict,
        #         self.json_information_acquirer.mesh_dict):
        #     # logger.i('generate maindoor done. it is OK ... ')
        #     pass
        # else:
        #     self.error_info_dict['error'] = 'generate maindoor error'
        #     logger.e('generate maindoor done. it is ERROR ... ')
        #     return {}

        # generate house infomation
        house_info_list = []
        # step3, generate room info, include floor/door/hole/window/baywindow.
        for room in self.json_information_acquirer.scene_room_list:
            # generate room information
            room_info_dict = self.generate_room_info(room)
            if len(room_info_dict) > 0:
                house_info_list.append(room_info_dict)

        # generate maindoor information
        maindoor_info_dict = self.maindoor_generator.determine_entrydoor(
            house_info_list)

        if len(maindoor_info_dict) > 0 or 1:

            # generate connect information
            house_info_list = self.connect_info_generator.generate_connect_info(
                house_info_list)

            # # merge door/hole, if overlap, after treatement
            if self.post_processor.after_treatement(house_info_list):
                house_info_list = self.post_processor.at_house_info_dict

            self.house_info_dict['floorplan'] = house_info_list
            self.house_info_dict['maindoor'] = [maindoor_info_dict]

            # self.draw_room.visualization(self.house_info_dict)
        else:
            return {}

        return self.house_info_dict

        # one room one entrydoor, 找到房间的入室门
        if self.house_splitter.split_house(self.house_info_dict):
            self.house_info_dict = self.house_splitter.house_splitted_dict

        if len(self.house_info_dict) > 0:
            return self.house_info_dict
        else:
            return {}

    # show
    # self.draw_room.draw_room(room_info_dict)

    def generate_room_info(self, room):
        """generate room information
        
        Arguments:
            room {list} -- include type/roomID/instanceID
        
        Returns:
            bool -- True or False
        """

        room_dict = {}
        try:
            room_dict['type'] = room['type']
            room_dict['room'] = room['instanceid']
            room_children_list = room['children']
            # print('roomid: ', room_dict['room'])

            room_all_mesh_list = []
            floor_mesh_list = []
            door_mesh_list = []
            hole_mesh_list = []
            window_mesh_list = []
            baywindow_mesh_list = []
            top_mesh_list = []

            for children in room_children_list:
                for mesh_uid, mesh_value in self.json_information_acquirer.mesh_dict.items(
                ):
                    if mesh_value[
                            'type'] in self.mesh_type_list and children in mesh_uid:
                        # save all mesh in this room, for test
                        room_all_mesh_list.append(mesh_value)
                        # extract mesh based on category
                        if mesh_value['type'] == 'Floor':
                            floor_mesh_list.append(mesh_value)
                        elif mesh_value['type'] == 'Door':
                            door_mesh_list.append(mesh_value)
                        elif mesh_value['type'] == 'Hole':
                            hole_mesh_list.append(mesh_value)
                        elif mesh_value['type'] == 'Window':
                            window_mesh_list.append(mesh_value)
                        elif mesh_value['type'] == 'BayWindow':
                            baywindow_mesh_list.append(mesh_value)
                        elif mesh_value['type'] == 'WallTop':
                            top_mesh_list.append(mesh_value)

        except Exception as e:
            logger.e('%s does not have the required key: %s' %
                     (room['instanceid'], e))
            return False

        # save room mesh
        # if self.is_save_mesh:
        #     from mesh_save import MeshSaver
        #     mesh_saver = MeshSaver()
        #     mesh_saver.save_mesh(room_all_mesh_list, room['instanceid'])

        # compute floor. return True/False, floor line -- self.clockwise_line_list
        # logger.i('start generate %s floor ...' % room['instanceid'])
        if self.floor_generator.generate_floor(floor_mesh_list,
                                               room['instanceid']):

            line_list = self.floor_generator.clockwise_line_list

            if len(line_list) == 0:
                # logger.e('generate %s floor done. it is ERROR' % room['instanceid'])
                return False

            floor_list = []
            floor_list.append(line_list[0][0][0])
            floor_list.append(line_list[0][0][1])
            for line in line_list:
                floor_list.append(line[1][0])
                floor_list.append(line[1][1])

            room_dict['floor'] = floor_list
            room_dict['area'] = self.tool.comp_area(floor_list)
            # logger.i('generate %s floor done. it is OK' % room['instanceid'])
            # print ('room area: ', room_dict['area'])
            # compute door.
            if len(door_mesh_list) > 0:
                # logger.i('start generate %s door ... ' % room['instanceid'])
                if self.door_generator.generate_door(door_mesh_list,
                                                     line_list):
                    room_dict['door'] = self.door_generator.room_door_list
                    room_dict['door_height'] = self.door_generator.height_list
                    room_dict[
                        'door_height_limit'] = self.door_generator.height_limit_list

                else:
                    room_dict['door'] = []
                    room_dict['door_height'] = []
                    room_dict['door_height_limit'] = []
            else:
                room_dict['door'] = []
                room_dict['door_height'] = []
                room_dict['door_height_limit'] = []

            # compute hole
            if len(hole_mesh_list) > 0:
                # logger.i('start generate %s hole ... ' % room['instanceid'])
                if self.door_generator.generate_door(hole_mesh_list,
                                                     line_list):
                    room_dict['hole'] = self.door_generator.room_door_list
                    room_dict['hole_height'] = self.door_generator.height_list
                    room_dict[
                        'hole_height_limit'] = self.door_generator.height_limit_list
                else:
                    room_dict['hole'] = []
                    room_dict['hole_height'] = []
                    room_dict['hole_height_limit'] = []
            else:
                room_dict['hole'] = []
                room_dict['hole_height'] = []
                room_dict['hole_height_limit'] = []
        else:
            return []

        # compute window
        if self.door_generator.generate_door(window_mesh_list, line_list):
            room_dict['window'] = self.door_generator.room_door_list
            room_dict['window_height'] = self.door_generator.height_list
            room_dict[
                'window_height_limit'] = self.door_generator.height_limit_list
        else:
            room_dict['window'] = []
            room_dict['window_height'] = []
            room_dict['window_height_limit'] = []

        # compute baywindow
        if self.baywindow_generator.generate_baywindow(
                baywindow_mesh_list, line_list, room_dict['area']):
            room_dict['baywindow'] = self.baywindow_generator.baywindow_list
            room_dict[
                'baywindow_height'] = self.baywindow_generator.baywindow_height
            room_dict[
                'baywindow_height_limit'] = self.baywindow_generator.baywindow_height_limit
        else:
            room_dict['baywindow'] = []
            room_dict['baywindow_height'] = []
            room_dict['baywindow_height_limit'] = []

        # compute top height
        if len(top_mesh_list) > 0:
            room_dict['topheight'] = top_mesh_list[0]['xyz'][1]
        else:
            room_dict['topheight'] = 2.8

        # print('room_dict: ', room_dict)
        # input()
        return room_dict
