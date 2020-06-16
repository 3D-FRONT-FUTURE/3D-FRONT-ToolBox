import shapely.geometry as sg
from Generator.interface import *
from Generator.model import ModelInstance
from Generator.camera import CameraInstance



class SeedGenerator:
    '''
    generate camera params by seed
    '''
    
    def __init__(self, floors, seed, h1 = 1.2, h2 = 1.2):
        self.floor_info = floors
        self.seed = seed
        self.box = None
        self.direction = None
        
        self.xlen = 0
        self.zlen = 0
        self.center = None
        
        self.dist_threshold = 4.0
        
        self.pos_h = h1
        self.target_h = h2
        
        self.initialize()
    
    def initialize(self):
        self.box = self.seed.get_box()
        self.xlen, self.zlen = self.box[1] - self.box[0]
        self.center = (self.box[0] + self.box[1]) * 0.5
        self.direction = self.seed.get_model_direction()
    
    
    def get_front_viewers(self):
        fov = 60
        half_x, half_z = self.xlen * 0.5, self.zlen * 0.5
      
        d1 = half_x / np.tan(np.deg2rad(fov * 0.5)) + half_z
        
        line = [self.center, self.center + self.direction * 1e3]
        k1 = line_line_intersection(line, self.floor_info)
        if len(k1) == 0:
            return list()
        
        dist1 = length(k1 - self.center)
        d1 = d1 if d1 > self.dist_threshold else self.dist_threshold
        d1 = d1 if d1 < dist1 - 0.1 else dist1 - 0.1
    
        c_pos = self.center + d1 * self.direction
        c_target = self.center
        
        camera_pos = np.array([c_pos[0], self.pos_h, c_pos[1]])
        camera_target = np.array([c_target[0], self.target_h, c_target[1]])
        ret = list()
        ret.append({
            'pos': camera_pos.tolist(),
            'target': camera_target.tolist(),
            'fov': fov
        })
        
        return ret
    
    
    def get_side_viewers(self, degree):
        alpha = np.deg2rad(degree)
        fov = 60
        
        w, h = self.xlen, self.zlen
        s1 = np.sqrt(w ** 2 + h ** 2)
        a1 = np.arctan(h / w)
        theta = np.deg2rad(fov * 0.5)
        distance = s1 * np.sin(a1 + np.pi * 0.5 - alpha - theta) * 0.5 / np.sin(theta)
        
        direction = self.seed.get_model_direction()
        normal = self.seed.get_normal()
        p0 = self.center

        d1 = p0 + direction * np.cos(alpha) * 1e3 + normal * np.sin(alpha) * 1e3
        l1 = [p0, d1]
        k1 = line_line_intersection(l1, self.floor_info)

        d2 = p0 + direction * np.cos(alpha) * 1e3 - normal * np.sin(alpha) * 1e3
        l2 = [p0, d2]
        k2 = line_line_intersection(l2, self.floor_info)

        ret = list()
        if len(k1) == 0 and len(k2) == 0:
            return ret
        
        if len(k1) > 0:
            dist = distance if distance > self.dist_threshold else self.dist_threshold
            dist1 = length(k1 - p0)
            dist = dist1 - 0.1 if dist > dist1 else dist

            p1 = p0 + dist * np.sin(alpha) * normal + dist * np.cos(alpha) * direction
            camera_target = np.array([p0[0], self.target_h, p0[1]])
            ret.append({
                'pos': np.array([p1[0], self.pos_h, p1[1]]).tolist(),
                'target': camera_target.tolist(),
                'fov': fov
            })

        if len(k2) > 0:
            dist = distance if distance > self.dist_threshold else self.dist_threshold
            dist2 = length(k2 - p0)
            dist = dist2 - 0.1 if dist > dist2 else dist
            # print('k2 ', dist)

            p2 = p0 - dist * np.sin(alpha) * normal + dist * np.cos(alpha) * direction
            ret.append({
                'pos': np.array([p2[0], self.pos_h, p2[1]]).tolist(),
                'target': camera_target.tolist(),
                'fov': fov
            })
        
        return ret
    
    
    def get_common_viewers(self):
        ret = list()
        front_viewers = self.get_front_viewers()
        ret.extend(front_viewers)

        alphas = [15, 30, 45]
        for alpha in alphas:
            side_viewers = self.get_side_viewers(alpha)
            ret.extend(side_viewers)
        
        return ret
    
    
    def get_viewers(self):
        viewers = self.get_common_viewers()
        ret = list()
        for viewer in viewers:
            try:
                if self.check_valid(viewer):
                    ret.append(viewer)
            except:
                continue
        return ret
    
    
    def check_valid(self, viewer):
        if self.camera_outside_room(viewer):
            return False
        
        visible_coef = self.seed_contain_coef(viewer)
        if visible_coef < 0.8:
            return False
        
        return True
    
    def camera_outside_room(self, viewer):
        pos = viewer['pos']
        viewer_pos = np.array([pos[0], pos[2]])
        floor_poly = sg.Polygon(self.floor_info)
        viewer_point = sg.Point(viewer_pos)
        if not floor_poly.contains(viewer_point):
            return True
        return False
    
    
    def seed_contain_coef(self, viewer):
        box_poly = sg.Polygon(self.seed.get_bounding_box())
        box_area = box_poly.area
        
        visible_poly = get_camera_visible_poly(viewer, self.floor_info)
        box_visible = visible_poly.intersection(box_poly)
        box_visible_area = box_visible.area
        
        coef = box_visible_area / box_area
        return coef

