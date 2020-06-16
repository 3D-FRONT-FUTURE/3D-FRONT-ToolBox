import os, sys
from logger import logger
from tools import ToolKit
from points_aligned_to_floor import PointAlignedToFloor


class DoorGenerator(object):
    def __init__(self, ):

        self.room_door_list = []
        self.is_square = False

        self.tool = ToolKit()
        self.points_aligned_to_floor = PointAlignedToFloor()

        self.height_list = []
        self.height_limit_list = []
        # self.height_ori_list = []

    def generate_door(self, door_mesh_list, floor_list):
        """generate all doors
        
        Arguments:
            door_mesh_list  -- mesh list
            floor_list  -- floor list
        
        Returns:
            bool -- True or False
        """
        self.room_door_list = []
        xz_less_four_points_list = []

        self.height_list = []
        self.height_limit_list = []
        if len(door_mesh_list) == 0:
            return False

        # one mesh one door
        for door_mesh in door_mesh_list:
            xyz_list = door_mesh['xyz']
            y_list = []
            xz_list = []
            for i in range(len(xyz_list) // 3):
                xz_coordinate = [
                    round(float(xyz_list[3 * i]), 3),
                    round(float(xyz_list[3 * i + 2]), 3)
                ]
                y_list.append(float(xyz_list[3 * i + 1]))
                if xz_coordinate not in xz_list:
                    xz_list.append(xz_coordinate)

            #
            if len(xz_list) < 4:
                xz_less_four_points_list.append(xz_list)
            else:
                self.room_door_list.append(
                    self.tool.calculate_convexhull(xz_list))

            # height
            if len(y_list) > 0:
                self.height_list.append(min(y_list))
                self.height_limit_list.append(max(y_list))

        # input()
        # deduplication
        self.room_door_list, self.height_list, self.height_limit_list = self.tool.point_deduplication(
            self.room_door_list, self.height_list, self.height_limit_list)
        self.room_door_list, self.height_list, self.height_limit_list = self.tool.eight_points_deduplication(
            self.room_door_list, self.height_list, self.height_limit_list)

        align_before_num = len(self.room_door_list)

        # the points on the door aligned to the floor
        if self.points_aligned_to_floor.align_point_to_floor(
                self.room_door_list, floor_list):
            self.room_door_list = self.points_aligned_to_floor.new_pts_list
        else:
            self.room_door_list = []

        align_after_num = len(self.room_door_list)

        if align_after_num == 0:
            return False

        if align_after_num < align_before_num:
            logger.w('door is getting less')

        new_room_door_list = []
        for room_door in self.room_door_list:
            if not self.tool.is_square(room_door):
                # self.room_door_list = []
                # return False
                continue

            new_room_door_list.append([
                room_door[0][0], room_door[0][1], room_door[1][0],
                room_door[1][1], room_door[2][0], room_door[2][1],
                room_door[3][0], room_door[3][1]
            ])

        self.room_door_list = new_room_door_list

        if len(self.room_door_list) > 0:
            return True
        else:
            return False
