import os, sys
from tools import ToolKit
from shapely.geometry import Polygon, mapping, Point

class AfterTreatement(object):
    def __init__(self, ):
        self.at_house_info_dict = []
        self.tool = ToolKit()
    
    def after_treatement(self, house_info):
        """judge door/hole whether overlap, if overlap, reserve bbox, delete small part

        """

        for room_info in house_info:
            floors = room_info['floor']
            doors = room_info['door']
            holes = room_info['hole']

            # room_info['floor'] = self.floors_clear(floors)

            if len(doors) > 1:
                room_info['door'] = self.del_overlap_rect(doors)
            if len(holes) > 1:
                room_info['hole'] = self.del_overlap_rect(holes)
            
            # if len(room_info['door']) + len(room_info['hole']) + len(room_info['window']) + len(room_info['baywindow'])> 0:
            #     self.at_house_info_dict.append(room_info)

            # doorholes = []
            # if len(doors) > 0:
            #     for door in doors:
            #         doorholes.append(door)
            # if len(holes) > 0:
            #     for hole in holes:
            #         doorholes.append(hole)
                
            # if len(doorholes) > 1:
            #     room_info['door'] = self.del_overlap_rect(doorholes)
            # room_info['hole'] = []
            # if len(room_info['door']) + len(room_info['window']) + len(room_info['baywindow']) > 0:
            self.at_house_info_dict.append(room_info)

        if len(self.at_house_info_dict) > 0:
            return True
        else:
            return False

    # def floors_clear(self, floors_list):
    #     print ('floors_list: ', floors_list)
    #     input()
    #     pass


    def del_overlap_rect(self, pts_list):

        new_pts_list = pts_list.copy()

        while len(pts_list) > 0:
            first_rect = pts_list[0]
            first_poly = Polygon([(first_rect[0], first_rect[1]), (first_rect[2], first_rect[3]), (first_rect[4], first_rect[5]), (first_rect[6], first_rect[7])])

            poly_area_list = [first_poly.area]
            intersec_index_list = [0]

            for i, rest_rect in enumerate(pts_list):
                if i > 0:
                    rest_poly = Polygon([(rest_rect[0], rest_rect[1]), (rest_rect[2], rest_rect[3]), (rest_rect[4], rest_rect[5]), (rest_rect[6], rest_rect[7])])
                    rest_poly_area = rest_poly.area

                    if first_poly.intersects(rest_poly):
                        intersec_index_list.append(i)
                        poly_area_list.append(rest_poly_area)

            if len(intersec_index_list) == 1:
                pts_list.pop(0)
            else:
                max_area_index = poly_area_list.index(max(poly_area_list))
                intersec_index_reverse = sorted(intersec_index_list, reverse = True)
                
                for idx in intersec_index_reverse:
                    if idx != max_area_index:
                        new_pts_list.remove(pts_list[idx])
                    pts_list.pop(idx)


        return new_pts_list


