import os, sys, math
import numpy as np
from scipy.spatial import ConvexHull
from tools import ToolKit
from logger import logger


class MainDoorGenerator(object):
    """maindoor generator
    
    Arguments:
        maindoor_list -- maindoor coordnate list
        maindoor_height_min -- minimum height of the maindoor
        maindoor_height_max -- maximum height of the maindoor
        is_sauqre -- whether the point of maindoor is a square
    
    Returns:
        bool -- True or False
    """

    def __init__(self):
        """init 
        """
        self.tool = ToolKit()

        self.maindoor_list = []
        self.maindoor_height_min = 0
        self.maindoor_height_max = 0

        # whether the four points of the maindoor can form a rectangle
        self.is_square = False

    def get_maindoor(self, maindoor_dict, mesh_dict):
        """get maindoor list
        
        Arguments:
            maindoor_dict {dict} -- from json_information_acquirer
            mesh_dict {dict} -- from json_information_acquirer

        Returns:
            bool -- True or False
        """
        # logger.i('start generate maindoor ... ')
        try:
            maindoor_tmp_dict = {}
            maindoor_ref_list = []
            for roomID, doorinfo in maindoor_dict.items():
                maindoor_tmp_dict['roomId'] = roomID
                maindoor_ref_list = doorinfo['ref']
        except Exception as e:
            return False

        maindoor_mesh_list = []
        for mesh_uid, mesh_value in mesh_dict.items():
            if mesh_uid in maindoor_ref_list:
                maindoor_mesh_list.append(mesh_value)

        if len(maindoor_mesh_list) == 0:
            logger.e('cannot find maindoor mesh')
            return False

        y_list = []
        xz_list = []
        for maindoor_mesh in maindoor_mesh_list:
            maindoor_xyz_list = maindoor_mesh['xyz']
            maindoor_faces_list = maindoor_mesh['faces']

            for i in range(len(maindoor_xyz_list) // 3):
                y_list.append(float(maindoor_xyz_list[3 * i + 1]))
                xz_list.append([
                    round(float(maindoor_xyz_list[3 * i]), 3),
                    round(float(maindoor_xyz_list[3 * i + 2]), 3)
                ])

        self.maindoor_height_min = round(min(y_list), 3)
        self.maindoor_height_max = round(max(y_list), 3)

        self.maindoor_list = self.tool.calculate_convexhull(xz_list)

        if len(self.maindoor_list) < 4:
            return False
        elif len(self.maindoor_list) == 4:
            return self.tool.is_square(self.maindoor_list)
        else:
            return False

    def determine_entrydoor(self, house_info_list):

        maindoor_dict = {}
        maindoor_dict['point'] = []
        is_found = False
        for room_info in house_info_list:
            door_info_list = room_info['door']
            for door_info in door_info_list:
                if [door_info[0], door_info[1]] in self.maindoor_list:
                    maindoor_dict['point'] = door_info
                    maindoor_dict['room'] = room_info['room']
                    is_found = True
                    break
            if is_found:
                break
        if len(maindoor_dict['point']) > 0:
            angle, direction = self.tool.compute_door_hole_direction(
                maindoor_dict['point'])
            maindoor_dict['angle'] = angle
            maindoor_dict['direction'] = direction
            maindoor_dict['height'] = self.maindoor_height_min
            maindoor_dict['height_limit'] = self.maindoor_height_max

            return maindoor_dict
        else:
            return {}
