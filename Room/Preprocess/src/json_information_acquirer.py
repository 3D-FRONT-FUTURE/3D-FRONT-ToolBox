'''
@Author: zbloom
@Date: 2018-09-06 16:49:23
@LastEditors: zbloom
@LastEditTime: 2019-01-15 16:19:00
@Description: get juran json information
    include: json['mesh'], json['extension'], json['scene']

'''
# -*- coding: utf-8 -*-
# from __future__ import unicode_literals

import os
import sys

JSON_INFORMATION_ACQUIRER_PATH = os.path.realpath(os.path.dirname(__file__))
sys.path.append(JSON_INFORMATION_ACQUIRER_PATH)

# for test
sys.path.append(
    os.path.realpath(os.path.join(JSON_INFORMATION_ACQUIRER_PATH, '../')))

from logger import logger
"""get juran json information class

Returns:
    @bool -- True or False
"""


class JsonInformationAcquirer(object):
    def __init__(self):
        self.json_data = {}
        self.scene_room_list = []
        self.entrydoor_dict = {}
        self.mesh_dict = {}

        self.room_type_list = [
            'Hallway', 'LivingRoom', 'DiningRoom', 'LivingDiningRoom',
            'Balcony', 'Kitchen', 'Bathroom', 'MasterBathroom',
            'SecondBathroom', 'Bedroom', 'MasterBedroom', 'SecondBedroom',
            'KidsRoom', 'ElderlyRoom', 'Library', 'CloakRoom', 'StorageRoom',
            'NannyRoom', 'LaundryRoom', 'Lounge', 'Auditorium', 'Stairwell',
            'Aisle', 'Corridor', 'Office', 'Outdoors', 'PublicExterior',
            'PublicInterior', 'ResidentialExterior', 'EntranceHallway',
            'ProductShowcase', 'FloorPlan', 'Studio', 'Basement', 'HomeCinema',
            'Den', 'Sketch', 'PorchBalcony', 'EquipmentRoom', 'Courtyard',
            'Garage', 'Terrace', 'OtherRoom', 'None', 'none'
        ]

        self.entryroom_exclude_list = [
            'EquipmentRoom', 'SecondBathroom', 'none', 'MasterBedroom',
            'Balcony', 'MasterBathroom', 'KidsRoom', 'Bedroom', 'Kitchen',
            'SecondBedroom', 'StorageRoom', 'Stairwell', 'Library', 'Lounge',
            'LaundryRoom', 'Bathroom', 'CloakRoom'
        ]

    def get_information(self, jsonfile):
        """floorplan info interface
        
        Arguments:
            jsonfile {dict} -- juran json
        
        Returns:
            bool -- True or False
        """

        # logger.i('start read json ... ')
        self.json_data = jsonfile

        try:
            mesh_list = self.json_data['mesh']
            scene_list = self.json_data['scene']
            scene_room_list = scene_list['room']
            extension_door_list = self.json_data['extension']['door']
        except Exception as e:
            logger.e('key not exists (%s)' % e)
            return False

        # read scene-room
        self.scene_room_list = self.read_scene_room(scene_room_list)
        if len(self.scene_room_list) == 0:
            logger.e('scene-room is empty')
            return False

        # read extension, get maindoor information
        self.entrydoor_dict = self.read_extension(extension_door_list)
        # if len(self.entrydoor_dict) == 0:
        #     # logger.e('entrydoor is empty')
        #     return False

        # read mesh
        self.mesh_dict = self.read_mesh(mesh_list)
        if len(self.mesh_dict) == 0:
            logger.e('mesh is empty')
            return False

        return True

    def read_mesh(self, mesh_list):
        mesh_dict = {}

        try:
            mesh_uid_list = []
            mesh_xyz_list = []
            for mesh in mesh_list:
                mesh_tmp_dict = {}
                mesh_tmp_dict['xyz'] = mesh['xyz']
                mesh_tmp_dict['faces'] = mesh['faces']
                mesh_tmp_dict['type'] = mesh['type']

                mesh_uid_list.append(mesh['uid'])
                mesh_xyz_list.append(mesh_tmp_dict)

            mesh_dict = dict(zip(mesh_uid_list, mesh_xyz_list))

        except Exception as e:
            return {}

        return mesh_dict

    def read_extension(self, extension_door_list):
        entrydoor_dict = {}

        try:
            roomID_list = []
            entrydoor_list = []

            for door in extension_door_list:
                if 'type' in door.keys() and 'roomId' in door.keys():
                    # if door['type'] == 'entryDoor' and door['roomId'].split('-')[0] not in self.entryroom_exclude_list:
                    if door['type'] == 'entryDoor':
                        if door['roomId'] not in roomID_list:
                            entrydoor_tmp_dict = {}
                            roomID_list.append(door['roomId'])

                            entrydoor_tmp_dict['type'] = door['type']
                            entrydoor_tmp_dict['ref'] = door['ref']
                            entrydoor_list.append(entrydoor_tmp_dict)
                        else:
                            continue

            if len(roomID_list) == 0:
                logger.e('entrydoor number == 0')
                return {}
            elif len(roomID_list) > 1:
                new_roomID_list = []
                add_idx = []
                for i, roomID in enumerate(roomID_list):
                    if roomID.split('-')[0] not in self.entryroom_exclude_list:
                        if roomID not in new_roomID_list:
                            new_roomID_list.append(roomID)
                            add_idx.append(i)

                new_entrydoor_list = []
                for idx in add_idx:
                    new_entrydoor_list.append(entrydoor_list[i])

                if len(new_roomID_list) == 1:
                    entrydoor_dict = dict(
                        zip(new_roomID_list, new_entrydoor_list))
                else:
                    logger.e('entrydoor number > 1')
                    return {}
            else:
                entrydoor_dict = dict(zip(roomID_list, entrydoor_list))

        except Exception as e:
            return {}

        return entrydoor_dict

    def read_scene_room(self, ori_scene_room_list):
        dst_scene_room_list = []

        try:
            for room in ori_scene_room_list:
                room_tmp_dict = {}
                room_tmp_dict['type'] = room['type']

                if room_tmp_dict['type'] not in self.room_type_list:
                    continue
                else:
                    room_tmp_dict['instanceid'] = room['instanceid']

                    room_children_list = room['children']
                    room_child_ref_list = []
                    for room_child in room_children_list:
                        room_child_ref_list.append(room_child['ref'])

                    room_tmp_dict['children'] = room_child_ref_list

                    dst_scene_room_list.append(room_tmp_dict)

        except Exception as e:
            return []

        return dst_scene_room_list
