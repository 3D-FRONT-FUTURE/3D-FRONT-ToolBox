import os, sys, heapq
import numpy as np
from shapely.geometry import Polygon, mapping, Point
from tools import ToolKit
from logger import logger


class PointAlignedToFloor(object):
    """align point to floor, first two point on the floor
    """
    def __init__(self,):
        self.tool = ToolKit()
        self.new_pts_list = []

    def align_point_to_floor(self, pts_list, floor_list):
        """align operator
        Arguments:
            floor_list [x1,y1,x2,y2,...] -- floor list
            pts_list [[x1,y1],[x2,y2],...] -- point list
        Returns:
            point list -- [[x1,y1],[x2,y2],...]
        """
        self.new_pts_list = []

        for pts in pts_list:
            # sort, anticlockwise
            pts = self.tool.calculate_convexhull(pts)

            if len(pts) > 4:
                pts = self.six_to_four(pts)
                pts = self.tool.calculate_convexhull(pts)

            is_found = False
            dis_all_list = []
            sum_dis_list = []
            new_pts = []

            for floor_line in floor_list:
                is_collinear_list = []
                dis_list = []
                first_two_point_dis = 0

                for pts_point in pts:
                    is_collinear, dis = self.tool.is_collinear_three_points(floor_line[0], floor_line[1], pts_point)
                    is_collinear_list.append(is_collinear)
                    dis_list.append(dis)
                    
                # compute sum of the smallest two dis
                smallest_num = heapq.nsmallest(2, dis_list)
                first_two_point_dis = smallest_num[0] + smallest_num[1]

                sum_dis_list.append(first_two_point_dis)
                dis_all_list.append(dis_list)

                if is_collinear_list.count(True) == 2:
                    is_found = True
                    new_pts = self.reorder_point_normal(pts, is_collinear_list)
                    if len(new_pts) == 0:
                        logger.e('find first two closest point error ...')
                        break
                    elif len(new_pts) > 0:
                        self.new_pts_list.append(new_pts)
                        break

            if not is_found:
                
                new_pts = self.reorder_point_abnormal(pts, dis_all_list, sum_dis_list)
                if len(new_pts) == 0:
                    new_floor_list = []
                    for floor_line in floor_list:
                        new_floor_list.append(floor_line[0])
                    floor_poly = Polygon(self.tool.list_to_tuple(new_floor_list))
                    new_pts = self.reorder_point_dysmorphism(pts, floor_poly)
            
                if len(new_pts) == 0:
                    logger.e('find first two closest point error ...')    
                    continue 
                else:
                    self.new_pts_list.append(new_pts)     

        if len(self.new_pts_list) != len(pts_list):
            logger.w('lost object')
        if len(self.new_pts_list) > 0:
            return True
        else:
            return False


    def reorder_point_dysmorphism(self, pts, floor_poly):

        dis_to_polyg_list = []
        for point in pts:
            if floor_poly.contains(Point(point)):
                dis_to_polyg_list.append(0.)
            else:
                dis_to_polyg_list.append(floor_poly.boundary.distance(Point(point)))

        index_list = self.find_nsmallest_num(dis_to_polyg_list, 2)

        if index_list == [0, 1] or index_list == [1, 0]:
            return [pts[1], pts[0], pts[3], pts[2]]
        elif index_list == [1, 2] or index_list == [2, 1]:
            return [pts[2], pts[1], pts[0], pts[3]]           
        elif index_list == [2, 3] or index_list == [3, 2]:
            return [pts[3], pts[2], pts[1], pts[0]]
        elif index_list == [0, 3] or index_list == [3, 0]:
            return [pts[0], pts[3], pts[2], pts[1]]
        else:
            return []


    def reorder_point_abnormal(self, pts, dis_all_list, sum_dis_list):

        small_index = sum_dis_list.index(min(sum_dis_list))

        dis_select = dis_all_list[small_index]
        smallest_two_dis = heapq.nsmallest(2, dis_select)

        index_list = []
        if smallest_two_dis[0] == smallest_two_dis[1]:
            index_list = [i for i, v in enumerate(dis_select) if v == smallest_two_dis[0]]
        else:
            index_list = [dis_select.index(smallest_two_dis[0]), dis_select.index(smallest_two_dis[1])]

        if index_list == [0, 1] or index_list == [1, 0]:
            return [pts[1], pts[0], pts[3], pts[2]]
        elif index_list == [1, 2] or index_list == [2, 1]:
            return [pts[2], pts[1], pts[0], pts[3]]           
        elif index_list == [2, 3] or index_list == [3, 2]:
            return [pts[3], pts[2], pts[1], pts[0]]
        elif index_list == [0, 3] or index_list == [3, 0]:
            return [pts[0], pts[3], pts[2], pts[1]]
        else:
            return []


    def reorder_point_normal(self, pts, is_collinear_list):
        """reorder point, if len(is_collinear_list) == 2
        Arguments:
            pts -- door/hole point(four)
            is_collinear_list -- is collinear flag
        Returns:
            door/hole list -- clockwise point, the first two point in floor
        """

        if is_collinear_list == [True, True, False, False]:
            return [pts[1], pts[0], pts[3], pts[2]]
        elif is_collinear_list == [False, True, True, False]:
            return [pts[2], pts[1], pts[0], pts[3]]
        elif is_collinear_list == [False, False, True, True]:
            return [pts[3], pts[2], pts[1], pts[0]]
        elif is_collinear_list == [True, False, False, True]:
            return [pts[0], pts[3], pts[2], pts[1]]
        else:
            return []                                        


    def six_to_four(self, six_pts_list):

        points_num = len(six_pts_list)
        x_list = []
        z_list = []
        for pts in six_pts_list:
            x_list.append(pts[0])
            z_list.append(pts[1])
        center_point = [sum(x_list)/points_num, sum(z_list)/points_num]

        dis_list = []
        for pts in six_pts_list:
            dis_list.append(self.tool.compute_distance(center_point, pts))

        max_4_index_list = self.find_nlargest_num(dis_list, 4)

        new_pts_list = []
        for idx in max_4_index_list:
            if six_pts_list[idx] not in new_pts_list:
                new_pts_list.append(six_pts_list[idx])

        return new_pts_list


    def find_nsmallest_num(self, pts_list, n):
        tmp = []
        for i in range(n):
            tmp.append(pts_list.index(min(pts_list)))
            pts_list[pts_list.index(min(pts_list))] = n
        tmp.sort()
        return tmp

    def find_nlargest_num(self, pts_list, n):
        tmp = []
        for i in range(n):
            tmp.append(pts_list.index(max(pts_list)))
            pts_list[pts_list.index(max(pts_list))] = 0
        tmp.sort()
        return tmp
