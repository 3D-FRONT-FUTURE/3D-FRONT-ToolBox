import os, sys, math
import numpy as np
import operator
from shapely.geometry import Polygon, mapping, Point
from scipy.spatial import ConvexHull


class ToolKit(object):
    def __init__(self):
        self.distance_gap = 5e-3
        self.MAX_GRADIENT_VALUE = 1e4

        self.COLLINEAR_EPSION = 0
        self.COLLINEAR_DIFF = 1e-5

    def is_square(self, points_four):
        """whether the four points of the maindoor can form a rectangle
        
        Arguments:
            points_four {[[x1, y1], [x2, y2], ...]} -- coordinates
        
        Returns:
            bool -- True or False
        """
        diagonal_length1 = self.compute_distance(points_four[0],
                                                 points_four[2])
        diagonal_length2 = self.compute_distance(points_four[1],
                                                 points_four[3])

        if (diagonal_length1 - diagonal_length2) < self.distance_gap:
            return True
        else:
            return False

    def compute_distance(self, pts1, pts2):
        """compute the distance of ywo points
        
        Arguments:
            two_points {[x1, y1], [x2, y2]} -- two points
        
        Returns:
            float -- distance
        """
        dx = pts1[0] - pts2[0]
        dy = pts1[1] - pts2[1]
        return math.sqrt(dx * dx + dy * dy)

    def point_deduplication(self, pts_list, height_list, height_limit_list):
        """point deduplication
        
        Arguments:
            pts_list {list} -- point or single number
        
        Returns:
            list -- deduplocated list
        """
        new_list = []
        new_height_list = []
        new_height_limit_list = []
        for i, item in enumerate(pts_list):
            if item not in new_list:
                new_list.append(item)
                new_height_list.append(height_list[i])
                new_height_limit_list.append(height_limit_list[i])

        return new_list, new_height_list, new_height_limit_list

    def calculate_convexhull(self, coordinate_list):
        """calculate convex hull, use scipy library
        
        Arguments:
            coordinate_list {[[x1, y1],[], ... ]} -- input list
        
        Returns:
            list -- [[x1, y1], [x2, y2], ... ]
        """
        hull_point_list = []

        points_numpy = np.array(coordinate_list)
        hull = ConvexHull(points_numpy)

        hull_index = hull.vertices
        # hull_area = hull.area

        for index in hull_index:
            hull_point_list.append(
                [coordinate_list[index][0], coordinate_list[index][1]])
            # hull_point_list.append(coordinate_list[index][1])

        return hull_point_list

    def mkdir_files(self, file_path):
        if os.path.exists(file_path):
            os.system('rm -rf ' + str(file_path))
            os.makedirs(file_path)
        else:
            os.makedirs(file_path)

    def grid_to_multi_line(self, p1, p2, p3):
        return [[p1, p2], [p2, p3], [p3, p1]]

    def find_once_line(self, line_list):
        """Find the line segment that only appears once
        
        Arguments:
            lines {[[[x1, y1], [x2, y2]], [[], []], ... ]} -- multi line
        
        Returns:
            [[[x1, y1], [x2, y2]], [[], []], ... ] -- line list
        """
        once_line = []

        while len(line_list) > 0:
            count = 0
            line_tmp = line_list
            line = line_list[0]
            line_reserve = [line[1], line[0]]
            count = line_list.count(line) + line_list.count(line_reserve)

            if count == 1:
                if line in line_list:
                    once_line.append(line)
                    line_list.remove(line)
                else:
                    once_line.append(line_reserve)
                    line_list.remove(line_reserve)

            else:
                while count > 0:
                    if line in line_list:
                        line_list.remove(line)
                    if line_reserve in line_list:
                        line_list.remove(line_reserve)
                    count = count - 1

        return once_line

    def line_deduplication(self, line_list):
        """line deduplication
        
        Arguments:
            line_list {[[[x1,y1],[x2,y2]], [[],[]], ... ]} -- input line list
        
        Returns:
            [[[x1,y1],[x2,y2]], [[],[]], ... ] -- output line list
        """
        new_line_list = []
        for line in line_list:
            if line[0] != line[1]:
                new_line_list.append(line)

        return new_line_list

    def comp_line_angle(self, line):
        """compute line gradient
        
        Arguments:
            line [[x1, y1], [x2, y2]] -- input line
        
        Returns:
            float -- line gradient
        """

        angle = np.rad2deg(
            np.arctan2(line[1][1] - line[0][1], line[1][0] - line[0][0]))
        # print ('angle: ',angle)
        return angle

        # if (float(line[1][0]-line[0][0]) == 0):
        #     if line[1][1] > line[0][1]:
        #         line_grad = self.MAX_GRADIENT_VALUE
        #     else:
        #         line_grad = -self.MAX_GRADIENT_VALUE
        # else:
        #     line_grad = (round(float(line[1][1]-line[0][1]) / float(line[1][0]-line[0][0]), 2))

        # return line_grad

    def is_closed(self, line_list):
        """detemine whether line list is closed
        
        Arguments:
            line_list {[[[],[]], [[],[]], ... ]} -- 
        
        Returns:
            [bool] -- [True or False]
        """
        for i, line in enumerate(line_list):
            if i < (len(line_list) - 1):
                if line[1] == line_list[i + 1][0]:
                    continue
                else:
                    return False
            else:
                if line[1] == line_list[0][0]:
                    continue
                else:
                    return False

        return True

    def merge_line(self, clockwise_line_list):
        """merge line in same direction
        
        Arguments:
            clockwise_line_list  -- line list
        
        Returns:
            line list -- merged line list
        """
        merged_line_list = []
        grad_list = []
        for line in clockwise_line_list:
            grad_list.append(abs(self.comp_line_angle(line)))

        # input()
        slice_index = self.slice_array(grad_list)

        # merge
        # 0 -- slice_index[0]
        # if len(slice_index) > 0:
        merged_line_list.append([
            clockwise_line_list[0][0],
            clockwise_line_list[slice_index[0] - 1][1]
        ])

        # slice_index
        for i, index in enumerate(slice_index):
            if i > 0:
                merged_line_list.append([
                    clockwise_line_list[slice_index[i - 1]][0],
                    clockwise_line_list[index - 1][1]
                ])

        # slice_index[-1] -- len(clockwise_line_list)
        merged_line_list.append([
            clockwise_line_list[slice_index[-1]][0],
            clockwise_line_list[len(clockwise_line_list) - 1][1]
        ])
        # print ('merged_line_list: ', merged_line_list)
        return merged_line_list
        # else:
        #     return clockwise_line_list

    def slice_array(self, array_data):
        """sclice array based on continue same element
        
        Arguments:
            array_data {[a, b, c, ... ]} -- a list of number
        
        Returns:
            [a, b, c] -- a list of sliced number
        """
        slice_index = []
        tmp_data_list = []
        for i, data in enumerate(array_data):
            if i == 0:
                tmp_data_list.append(data)
                continue
            if data not in tmp_data_list:
                slice_index.append(i)
                tmp_data_list = []
                tmp_data_list.append(data)

        return slice_index

    def overlap_line_deduplication(self, line_list):
        """deduplicate overlap line
        
        Arguments:
            line_list  -- line list
        
        Returns:
            line list -- deduplicated line list
        """
        deduplicated_line = []

        grad_list = []
        for line in line_list:
            grad_list.append(abs(self.comp_line_angle(line)))

        for i, grad in enumerate(grad_list):
            if i < len(grad_list) - 1:
                if (grad + grad_list[i + 1]) == 0:
                    if line_list[i][0] == line_list[
                            i + 1][1]:  # completely coincident
                        continue
                    else:  # partly coincident
                        deduplicated_line.append(
                            [line_list[i][0], line_list[i + 1][1]])
                else:
                    deduplicated_line.append(line_list[i])

        if (grad_list[-1] + grad_list[-2]) != 0:
            deduplicated_line.append(line_list[-1])

        return deduplicated_line

    def comp_area(self, polygon):
        poly_list = []
        for i in range(len(polygon) // 2):
            poly_list.append((polygon[2 * i], polygon[2 * i + 1]))
        poly = Polygon(poly_list)
        return round(poly.area, 3)

    def eight_points_deduplication(self, eight_points_list, height_list,
                                   height_limt_list):
        """eight points deduplication
        
        Arguments:
            eight_points_list  -- [[x1,y1],[x2,y2],[],...]
        
        Returns:
            [[x1,y1],[x2,y2],...],[],...] -- eight list
        """
        deduplicated_points_list = []
        new_height_list = []
        new_height_limit_list = []
        for i, eight_points in enumerate(eight_points_list):
            tmp_eight_points = sorted(eight_points)
            if tmp_eight_points not in deduplicated_points_list:
                deduplicated_points_list.append(tmp_eight_points)
                new_height_list.append(height_list[i])
                new_height_limit_list.append(height_limt_list[i])

        return deduplicated_points_list, new_height_list, new_height_limit_list

    def is_collinear_three_points(self, pts1, pts2, pts3):
        """determine whether the three points are collinear
        
        Arguments:
            pts1 [x1, y1] -- coordinate
            pts2 [x2, y2] -- ..
            pts3 [x3, y3] -- ..
        
        Returns:
            bool -- True or False
        """
        sum1 = pts1[0] * pts2[1] - pts1[1] * pts2[0]
        sum2 = pts2[0] * pts3[1] - pts2[1] * pts3[0]
        sum3 = pts3[0] * pts1[1] - pts3[1] * pts1[0]
        sum = sum1 + sum2 + sum3

        is_middle = False
        if ((min(pts1[0],pts2[0])-self.COLLINEAR_EPSION) <= pts3[0] <= (max(pts1[0],pts2[0])+self.COLLINEAR_EPSION)) and \
            (min(pts1[1],pts2[1])-self.COLLINEAR_EPSION <= pts3[1] <= max(pts1[1],pts2[1])+self.COLLINEAR_EPSION):
            is_middle = True

        # compute distance between pts3 and pts1-pts2
        distance = 0.0
        if np.linalg.norm([pts2[0] - pts1[0], pts2[1] - pts1[1]]) != 0:
            distance = np.linalg.norm(
                np.cross([pts2[0] - pts1[0], pts2[1] - pts1[1]], [
                    pts1[0] - pts3[0], pts1[1] - pts3[1]
                ])) / np.linalg.norm([pts2[0] - pts1[0], pts2[1] - pts1[1]])
        # distance = np.abs(np.cross([pts2[0]-pts1[0], pts2[1]-pts1[1]], [pts1[0]-pts3[0], pts1[1]-pts3[1]]))/np.linalg.norm([pts2[0]-pts1[0], pts2[1]-pts1[1]])

        if abs(sum) <= self.COLLINEAR_DIFF and is_middle:
            return True, 0.
        else:
            return False, distance

    def rectangele_barrel(self, rectangle_list):

        barrel_rectangle = []
        dis1 = self.compute_distance(rectangle_list[0])

        return barrel_rectangle

    def list_to_tuple(self, ori_list):

        new_list = []
        for data in ori_list:
            new_list.append((data[0], data[1]))
        return new_list

    def compute_door_hole_direction(self, pts):

        angle = np.rad2deg(np.arctan2(pts[1] - pts[7], pts[0] - pts[6]))
        dist = self.compute_distance([pts[0], pts[1]], [pts[6], pts[7]])
        direction = [(pts[0] - pts[6]) / dist, (pts[1] - pts[7]) / dist]

        return angle, direction

    def find_parallel_line(self, line_in_floor, gap):
        """ compute parallel line, up and down
        Returns:
            [[x1, y1], [x2, y2]] -- out floor line list
        """
        out_floor_line_list = []

        x1 = line_in_floor[0][0]
        y1 = line_in_floor[0][1]
        x2 = line_in_floor[1][0]
        y2 = line_in_floor[1][1]

        dx = x1 - x2
        dy = y1 - y2
        dist = np.sqrt(dx * dx + dy * dy)
        dx /= dist
        dy /= dist

        parallel_up = [[x1 + gap * dy, y1 - gap * dx],
                       [x2 + gap * dy, y2 - gap * dx]]
        parallel_down = [[x1 - gap * dy, y1 + gap * dx],
                         [x2 - gap * dy, y2 + gap * dx]]

        out_floor_line_list.append(parallel_up)
        out_floor_line_list.append(parallel_down)

        return out_floor_line_list

    def floor_to_polygon(self, floor_info_list):

        floor_polygon_list = []
        for i in range(len(floor_info_list) // 2):
            floor_polygon_list.append((floor_info_list[2 * i],
                                       floor_info_list[2 * i + 1]))

        return Polygon(floor_polygon_list)

    def is_intersec(self, line1, line2):
        """judfe two line is intersection
        
        Arguments:
            line1 {[[x1, y1], [x2, y2]]} -- line1
            line2 {same as line1} -- [description]
        
        Returns:
            boolean -- True or False
        """
        p1 = line1[0]
        p2 = line1[1]
        p3 = line2[0]
        p4 = line2[1]

        if max(p1[0], p2[0]) >= min(p3[0], p4[0]) and max(p3[0], p4[0]) >= min(
                p1[0], p2[0]) and max(p1[1], p2[1]) >= min(
                    p3[1], p4[1]) and max(p3[1], p4[1]) >= min(p1[1], p2[1]):
            if self.cross(p1, p2, p3) * self.cross(
                    p1, p2, p4) <= 0 and self.cross(p3, p4, p1) * self.cross(
                        p3, p4, p2) <= 0:
                return True
            else:
                return False
        else:
            return False

    def cross(self, pts1, pts2, pts3):
        x1 = pts2[0] - pts1[0]
        y1 = pts2[1] - pts1[1]
        x2 = pts3[0] - pts1[0]
        y2 = pts3[1] - pts1[1]

        return x1 * y2 - x2 * y1

    def is_on_line(self, pts1, pts2, pts3):
        if (pts3[0] - pts1[0]) * (pts2[1] - pts1[1]) == (pts2[0] - pts1[0]) * (
                pts3[1] - pts1[1]) and min(pts1[0], pts2[0]) <= pts3[0] <= max(
                    pts1[0], pts2[0]) and min(
                        pts1[1], pts2[1]) <= pts3[1] <= max(pts1[1], pts2[1]):
            return True
        else:
            return False

    def mesh_duplicate(self, mesh_list):

        del_mesh_list = []

        for i, imesh in enumerate(mesh_list):
            tmp_del_mesh_list = []
            tmp_del_mesh_list.append(imesh)
            for j, jmesh in enumerate(mesh_list):
                if j > i:
                    if operator.eq(imesh, jmesh):
                        tmp_del_mesh_list.append(jmesh)

            if len(tmp_del_mesh_list) > 1:
                del_mesh_list.append(tmp_del_mesh_list)

        for del_mesh in del_mesh_list:
            for i, mesh in enumerate(del_mesh):
                if i > 0:
                    mesh_list.remove(mesh)

        return mesh_list