import os, sys
from shapely.geometry import Polygon, mapping, Point, MultiPolygon
from shapely.ops import cascaded_union
import numpy as np
from tools import ToolKit

class FloorTool(object):
    def __init__(self,):
        self.threshold = 1e3
        self.MAX_GRADIENT_VALUE = 90

        self.floor_line_list = []
        self.clockwise_line_list = []
        
        self.floor_polygon_list = []

        self.tool = ToolKit()


    def connect_line_clockwise(self, line_list):
        """converse floor line in clockwise
        
        Arguments:
            line_list {no order} -- a list of line
        
        Returns:
            [x1, y1, x2, y2, ... ] -- a list of clockwise line
        """
        self.clockwise_line_list = []
        self.floor_polygon_list = []

        # duplicate overlap line
        self.floor_line_list = self.deplicate_overlap(line_list)

        while len(self.floor_line_list) > 0:
            floor_polygon = self.generate_floor_polygon()

            if len(floor_polygon) > 0:
                if floor_polygon[0][0] == floor_polygon[-1][1]:
                    self.floor_polygon_list.append(floor_polygon)
                else:
                    continue
            else:
                break

        if len(self.floor_polygon_list) > 0:
            self.clockwise_line_list = self.find_union_polygons()

        if len(self.clockwise_line_list) > 0:
            return True 
        else:
            return False
    
    def deplicate_overlap(self, line_list):

        angle_list = []
        for line in line_list:
            angle = abs(self.tool.comp_line_angle(line))
            if angle == 180:
                angle = 0
            if angle == 270:
                angle = 90
            angle_list.append(angle)

        angle_idx_dict = {}
        for i, angle in enumerate(angle_list):
            if angle not in angle_idx_dict.keys():
                angle_idx_dict[angle] = [i]
            else:
                angle_idx_dict[angle].append(i)

        clear_line_list = []
        for angle, idx_list in angle_idx_dict.items():
            collinear_line_list = []
            if len(idx_list) > 1:
                while len(idx_list) > 1:
                    first_line = line_list[idx_list[0]]

                    tmp_collinear_line_list = []
                    tmp_collinear_line_list.append(first_line)

                    idx_del_list = []
                    idx_del_list.append(idx_list[0])

                    for i, idx in enumerate(idx_list):
                        if i > 0:
                            line_idx = line_list[idx]
                            tmp_angle1 = self.tool.comp_line_angle([line_idx[0], first_line[0]])
                            tmp_angle2 = self.tool.comp_line_angle([line_idx[1], first_line[0]])

                            tmp_angle1 = self.angle_transfer(tmp_angle1)
                            tmp_angle2 = self.angle_transfer(tmp_angle2)

                            if tmp_angle1 != 0 and tmp_angle2 != 0:
                                tmp_angle = 0.5 * (tmp_angle1 + tmp_angle2)
                            elif tmp_angle1 == 0 and tmp_angle2 != 0:
                                tmp_angle = tmp_angle2
                            elif tmp_angle1 != 0 and tmp_angle2 == 0:
                                tmp_angle = tmp_angle1
                            else:
                                tmp_angle = 0

                            tmp_angle = self.angle_transfer(tmp_angle)

                            if tmp_angle == angle:
                                tmp_collinear_line_list.append(line_idx)
                                idx_del_list.append(idx)
                            else:
                                continue

                    if len(tmp_collinear_line_list) > 1:
                        collinear_line_list.append(tmp_collinear_line_list)

                    for idx_del in idx_del_list:
                        idx_list.remove(idx_del)
            
            if len(collinear_line_list) > 0:
                clear_line_list.append(collinear_line_list)

        del_line_list = []
        add_line_list = []

        if len(clear_line_list) > 0:
            for clear_line_4 in  clear_line_list:
                for clear_line_3 in clear_line_4:
                    x_point_list = []
                    y_point_list = []
                    for line in clear_line_3:
                        del_line_list.append(line)
                        x_point_list.append(line[0][0])
                        x_point_list.append(line[1][0])
                        y_point_list.append(line[0][1])
                        y_point_list.append(line[1][1])

                    sorted_point_list = [list(item) for item in zip(np.sort(x_point_list), np.sort(y_point_list))]

                    new_point_list = []
                    for point in sorted_point_list:
                        if point not in new_point_list:
                            new_point_list.append(point)

                    sorted_line_list = []
                    for i in range(len(new_point_list)-1):
                        sorted_line_list.append([new_point_list[i], new_point_list[i+1]])

                    sorted_line_dict = {}
                    
                    for i, sorted_line in enumerate(sorted_line_list):
                        
                        sorted_line_dict[i] = 0
                        occur_num = 0
                        for line in clear_line_3:
                            if self.tool.is_on_line(line[0], line[1], sorted_line[0]) and self.tool.is_on_line(line[0], line[1], sorted_line[1]):
                                occur_num += 1
                        sorted_line_dict[i] = occur_num

                    for index, num in sorted_line_dict.items():
                        if num == 1:
                            add_line_list.append(sorted_line_list[index])

        for del_line in del_line_list:
            line_list.remove(del_line)
        for add_line in add_line_list:
            line_list.append(add_line)

        return line_list


    def angle_transfer(self, angle):
        if angle == 180:
            angle = 0
        if angle == 270 or angle == -90:
            angle = 90
        return angle


    def clear_line(self, line1, line2):
        
        if line1[0] in line2:
            line2_rest_point = line2[1-line2.index(line1[0])]
            angle1 = self.tool.comp_line_angle([line1[1], line2_rest_point])
            angle2 = self.tool.comp_line_angle([line1[1], line1[0]])
            if (angle1 + angle2) == 0 and angle1 != angle2:
                return [line1[1], line2_rest_point]
        
        if line1[1] in line2:
            line2_rest_point = line2[1-line2.index(line1[1])]
            angle1 = self.tool.comp_line_angle([line1[0], line2_rest_point])
            angle2 = self.tool.comp_line_angle([line1[0], line1[1]])
            if (angle1 + angle2) == 0 and angle1 != angle2:
                return [line1[0], line2_rest_point]
        
        return []


    def find_union_polygons(self):

        union_floor_line_list = []
        if len(self.floor_polygon_list) == 1:
            return [self.floor_polygon_list[0]]
        else:
            multi_polygon = []
            for floor_polygon in self.floor_polygon_list:
                polygon_one = []
                for line in floor_polygon:
                    polygon_one.append((line[0][0], line[0][1]))
                polygon_one = Polygon(polygon_one)

                if polygon_one.length < 1 or polygon_one.area < 1:
                    continue
                # print ('polygon_one: ', polygon_one)
                multi_polygon.append(polygon_one)

            # print ('multi_polygon: ', multi_polygon)
            union_polygon = cascaded_union(multi_polygon)
            multi_polygon = union_polygon

            if multi_polygon.is_empty:
                return []

            # union_floor_line_list = mapping(multi_polygon)['coordinates'][0]

            union_polygon_list = mapping(multi_polygon)['coordinates']
            union_polygon_dim = np.ndim(union_polygon_list)

            floor_poly_list = []
            if union_polygon_dim == 3:
                self.floor_line_list = []
                union_floor_line_list = union_polygon_list[0]
                for i in range(len(union_floor_line_list)-1):
                    line = [[union_floor_line_list[i][0], union_floor_line_list[i][1]], 
                            [union_floor_line_list[i+1][0], union_floor_line_list[i+1][1]]]
                    self.floor_line_list.append(line)
                floor_poly_list.append(self.generate_floor_polygon())
                return floor_poly_list

            else:
                for union_poly in union_polygon_list:
                    self.floor_line_list = []
                    union_floor_line_list = union_poly[0]
                    for i in range(len(union_floor_line_list)-1):
                        line = [[union_floor_line_list[i][0], union_floor_line_list[i][1]], 
                                [union_floor_line_list[i+1][0], union_floor_line_list[i+1][1]]]
                        self.floor_line_list.append(line)
                    floor_poly_list.append(self.generate_floor_polygon())

                return floor_poly_list


    def generate_floor_polygon(self):
        floor_polygon = []

        start_line = self.find_start_line(self.floor_line_list)
        if len(start_line) == 0:
            return []
        floor_polygon.append(start_line)

        if start_line in self.floor_line_list:
            self.floor_line_list.remove(start_line)
        start_line_reverse = [start_line[1], start_line[0]]
        if start_line_reverse in self.floor_line_list:
            self.floor_line_list.remove(start_line_reverse)

        while len(self.floor_line_list) > 0:
            next_line = self.find_next_line(start_line, self.floor_line_list)
            if len(next_line) > 0:
                floor_polygon.append(next_line)
                start_line = next_line
            if len(next_line) == 0:
                return floor_polygon

        return floor_polygon


    def find_next_line(self, start_line, line_list):

        next_line = []
        for line in line_list:
            if line[0] == start_line[1]:
                next_line = line
                break
            elif line[1] == start_line[1]:
                next_line = [line[1], line[0]]
                break

        if len(next_line) == 0:
            return []
        else:
            if line in self.floor_line_list:
                self.floor_line_list.remove(line)
            if next_line in self.floor_line_list:
                self.floor_line_list.remove(next_line)

        return next_line


    def find_start_line(self, line_list):
        """find start line, for sorted line in clockwise
        
        Arguments:
            line_list  -- input line list
        
        Returns:
            [x1, y1] -- the top line 
        """
        start_line = []
        # find top point
        top_point = self.find_top_point(line_list)

        # find two line through the top point
        two_top_line = []
        angles_two_top_line = []
        for line in line_list:
            if line[0] == top_point or line[1] == top_point:
                angles_two_top_line.append(self.tool.comp_line_angle(line))
                two_top_line.append(line)
                if len(two_top_line) == 2:
                    break
                    
        if len(angles_two_top_line) == 0:
            return []

        # find the not vertical line
        top_line_not_vertical = []

        for i, angle in enumerate(angles_two_top_line):
            if angle != 90 and angle != -90:
                top_line_not_vertical = two_top_line[i]
                break
        if len(top_line_not_vertical) == 0:
            return []

        # line clockwise
        if top_line_not_vertical[0][0] > top_line_not_vertical[1][0]:
            start_line = [top_line_not_vertical[1], top_line_not_vertical[0]]
        else:
            start_line = top_line_not_vertical

        return start_line


    def find_top_point(self, line_list):
        """find the top point
        
        Returns:
            [x1, y1] -- coordinate of one of top point
        """

        top_point = []
        # find the top line, one
        x_list = []
        z_list = []
        for line in line_list:
            x_list.append(line[0][0])
            x_list.append(line[1][0])
            z_list.append(line[0][1])
            z_list.append(line[1][1])
        
        max_z = max(z_list)
        # num_max_z = z_list.count(max_z)
        index_max_z = z_list.index(max_z)
        top_point = [x_list[index_max_z], z_list[index_max_z]]

        return top_point


