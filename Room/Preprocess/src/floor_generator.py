import os, sys
from logger import logger
import numpy as np
from tools import ToolKit
from floor_tool import FloorTool



class FloorGenerator(object):
    def __init__(self,):
        self.room_floor_list = []
        self.clockwise_line_list = []

        self.tool = ToolKit()
        self.floor_tool = FloorTool()


    def generate_floor(self, floor_mesh_list, room_id):
        """generate floor info
        
        Arguments:
            floor_mesh_list {list} -- floor mesh
        
        Returns:
            bool -- True or False
        """
        if len(floor_mesh_list) == 0:
            logger.e('%s does not have floor.' % room_id)
            return False
        
        xz_faces_list = []
        floor_mesh_list = self.tool.mesh_duplicate(floor_mesh_list)

        for floor_mesh in floor_mesh_list:

            xz_list = []
            floor_mesh_xyz = floor_mesh['xyz']
            floor_mesh_faces = floor_mesh['faces']

            for i in range(len(floor_mesh_xyz)//3):
                xz_list.append([float(floor_mesh_xyz[3*i]), float(floor_mesh_xyz[3*i+2])])

            if len(xz_list) == 0:
                return False

            xz_sorted_list = []
            for index in floor_mesh_faces:
                xz_sorted_list.append(xz_list[index])

            for point in xz_sorted_list:
                xz_faces_list.append(point)

        grid_to_line_list = []
        for i in range(len(xz_faces_list)//3):
            
            if (xz_faces_list[3*i][0] == xz_faces_list[3*i+1][0] and xz_faces_list[3*i][0] == xz_faces_list[3*i+2][0]) or (xz_faces_list[3*i][1] == xz_faces_list[3*i+1][1] and xz_faces_list[3*i][1] == xz_faces_list[3*i+2][1]):
                continue

            grid_line_list = self.tool.grid_to_multi_line(xz_faces_list[3*i], xz_faces_list[3*i+1], xz_faces_list[3*i+2])

            if grid_line_list[0][0] == grid_line_list[0][1] or grid_line_list[1][0] == grid_line_list[1][1] or grid_line_list[2][0] == grid_line_list[2][1]:
                continue

            grid_to_line_list.append(grid_line_list[0])
            grid_to_line_list.append(grid_line_list[1])
            grid_to_line_list.append(grid_line_list[2])

        # count the number of occurrences of a line segment. if ==1, conserve, else, ignore
        once_line_list = self.tool.find_once_line(grid_to_line_list)
        once_line_list = self.tool.line_deduplication(once_line_list)

        if len(once_line_list) == 0:
            return False

        self.clockwise_line_list = []
        # connect all segments clockwise
        if self.floor_tool.connect_line_clockwise(once_line_list):
            if len(self.floor_tool.clockwise_line_list) == 1:
                self.clockwise_line_list = self.floor_tool.clockwise_line_list[0]
            else:
                logger.w('%s appeared multi floor' % room_id)
                idx_len_list = []
                for line_list in self.floor_tool.clockwise_line_list:
                    idx_len_list.append(len(line_list))
                self.clockwise_line_list = self.floor_tool.clockwise_line_list[idx_len_list.index(max(idx_len_list))]
        else:
            logger.e('%s cannot generate floor: %d' % (room_id, len(self.clockwise_line_list)))
            return False

        if self.tool.is_closed(self.clockwise_line_list):
            self.clockwise_line_list = self.tool.merge_line(self.clockwise_line_list)
            self.clockwise_line_list = self.tool.overlap_line_deduplication(self.clockwise_line_list)
        else:
            return False

        return True

