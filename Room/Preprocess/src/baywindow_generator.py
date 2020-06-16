import os, sys
import numpy as np
import shapely
from shapely.geometry import Polygon, mapping, Point, LineString
from shapely.wkt import dumps

from tools import ToolKit


class BaywindowGenerator(object):
    def __init__(self, ):
        self.tool = ToolKit()
        self.baywindow_list = []
        self.baywindow_height = []
        self.baywindow_height_limit = []

    def generate_baywindow(self, baywindow_mesh_list, floor_list, room_area):
        self.baywindow_height = []
        self.baywindow_height_limit = []

        if len(baywindow_mesh_list) == 0:
            return False

        xz_list = []
        y_list = []
        xz_single_list = []
        for baywindow_mesh in baywindow_mesh_list:
            baywindow_xyz = baywindow_mesh['xyz']

            for i in range(len(baywindow_xyz) // 3):
                xz_coordinate = [
                    float(baywindow_xyz[3 * i]),
                    float(baywindow_xyz[3 * i + 2])
                ]
                y_coorinate = float(baywindow_xyz[3 * i + 1])
                if xz_coordinate not in xz_list:
                    xz_list.append(xz_coordinate)
                if y_coorinate not in y_list:
                    y_list.append(y_coorinate)

        self.baywindow_height = min(y_list)
        self.baywindow_height_limit = max(y_list)
        xz_convexhull_list = self.tool.calculate_convexhull(xz_list)

        for xz in xz_list:
            xz_single_list.append(xz[0])
            xz_single_list.append(xz[1])
        baywindow_area = self.tool.comp_area(xz_single_list)

        xz_polygon_list = Polygon(self.tool.list_to_tuple(xz_convexhull_list))

        floor_polygon_line = []
        for i in range(len(floor_list)):
            floor_polygon_line.append(
                [(floor_list[i][0][0], floor_list[i][0][1]),
                 (floor_list[i][1][0], floor_list[i][1][1])])

        line_in_floor_list = self.find_line_in_floor(xz_polygon_list,
                                                     floor_polygon_line)

        floor_polygon_list = []
        for floor_line in floor_list:
            floor_polygon_list.append((floor_line[0]))
        floor_polygon_list = Polygon(
            self.tool.list_to_tuple(floor_polygon_list))

        # region_difference = xz_polygon_list.difference(floor_polygon_list)

        # line_in_floor_list = self.find_line_in_floor(region_difference, floor_polygon_list)
        # print ('line_in_floor_list: ', line_in_floor_list)
        # difference_polygon_list = self.find_difference_polygon(region_difference)

        line_out_floor_list = []
        for line_in_floor in line_in_floor_list:
            gap = 0.5
            out_floor_line_list_05 = []

            out_floor_line_list_05, dis_two_list = self.generate_out_floor_line(
                gap, line_in_floor, floor_polygon_list)

            line_out_floor_list.append(
                out_floor_line_list_05[dis_two_list.index(max(dis_two_list))])

        self.baywindow_list = self.clockwise_baywindow(line_in_floor_list,
                                                       line_out_floor_list)

        if len(self.baywindow_list) > 0:
            return True
        else:
            return False

    def clockwise_baywindow(self, line_in_floor_list, line_out_floor_list):

        baywindow_list = []
        for i, line_in_floor in enumerate(line_in_floor_list):
            baywindow = []

            # anticlockwise
            baywindow_convexhull = self.tool.calculate_convexhull([
                line_in_floor[0], line_in_floor[1], line_out_floor_list[i][0],
                line_out_floor_list[i][1]
            ])

            index = []
            for in_floor_pts in line_in_floor:
                for i, pts in enumerate(baywindow_convexhull):
                    if pts == [in_floor_pts[0], in_floor_pts[1]]:
                        index.append(i)

            if index == [0, 1] or index == [1, 0]:
                baywindow = [
                    baywindow_convexhull[1][0], baywindow_convexhull[1][1],
                    baywindow_convexhull[0][0], baywindow_convexhull[0][1],
                    baywindow_convexhull[3][0], baywindow_convexhull[3][1],
                    baywindow_convexhull[2][0], baywindow_convexhull[2][1]
                ]
            if index == [1, 2] or index == [2, 1]:
                baywindow = [
                    baywindow_convexhull[2][0], baywindow_convexhull[2][1],
                    baywindow_convexhull[1][0], baywindow_convexhull[1][1],
                    baywindow_convexhull[0][0], baywindow_convexhull[0][1],
                    baywindow_convexhull[3][0], baywindow_convexhull[3][1]
                ]
            if index == [2, 3] or index == [3, 2]:
                baywindow = [
                    baywindow_convexhull[3][0], baywindow_convexhull[3][1],
                    baywindow_convexhull[2][0], baywindow_convexhull[2][1],
                    baywindow_convexhull[1][0], baywindow_convexhull[1][1],
                    baywindow_convexhull[0][0], baywindow_convexhull[0][1]
                ]
            if index == [0, 3] or index == [3, 0]:
                baywindow = [
                    baywindow_convexhull[0][0], baywindow_convexhull[0][1],
                    baywindow_convexhull[3][0], baywindow_convexhull[3][1],
                    baywindow_convexhull[2][0], baywindow_convexhull[2][1],
                    baywindow_convexhull[1][0], baywindow_convexhull[1][1]
                ]

            baywindow_list.append(baywindow)

        return baywindow_list

    def generate_out_floor_line(self, gap, line_in_floor, floor_polygon_list):

        out_floor_line_list = self.tool.find_parallel_line(line_in_floor, gap)

        dis_two_list = []
        for line in out_floor_line_list:
            dis_list = []
            for point in line:
                if floor_polygon_list.contains(Point(point)):
                    dis_pt_poly = 0
                    continue
                dis_pt_poly = self.is_in_polygon(
                    Point(point), floor_polygon_list)
                dis_list.append(dis_pt_poly)
            dis_two_list.append(sum(dis_list))

        return out_floor_line_list, dis_two_list

    def is_in_polygon(self, pts, polygon_data):

        return polygon_data.boundary.distance(pts)

    def find_difference_polygon(self, region_difference):

        coordinates_region_difference = mapping(
            region_difference)['coordinates']
        region_dimension = np.ndim(coordinates_region_difference)

        difference_polygon_list = []
        if region_dimension == 3:
            tmp_polygon_list = []
            for polygon_list in coordinates_region_difference[0]:
                tmp_polygon_list.append([polygon_list[0], polygon_list[1]])
            difference_polygon_list.append(tmp_polygon_list)

        if region_dimension == 4:
            for region_polygon in coordinates_region_difference:
                tmp_polygon_list = []
                for polygon_list in region_polygon[0]:
                    tmp_polygon_list.append([polygon_list[0], polygon_list[1]])
                difference_polygon_list.append(tmp_polygon_list)

        return difference_polygon_list

    def find_line_in_floor(self, xz_polygon_list, floor_polygon_list):

        line_in_floor_list = []

        for floor_line in floor_polygon_list:
            line = LineString(floor_line)
            # ips = line.intersection(xz_polygon_list)
            ips = xz_polygon_list.intersection(line)

            if not ips.is_empty:
                res = mapping(ips)['coordinates']
                if np.array(res).size == 4:
                    line_in_floor_list.append(res)
        return line_in_floor_list
