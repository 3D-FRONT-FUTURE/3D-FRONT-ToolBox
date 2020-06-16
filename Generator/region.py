import shapely.geometry as sg
from Generator.interface import *
from Generator.model import ModelInstance
from Generator.camera import CameraInstance



class RegionGenerator:
    '''
    generate camera params by region
    '''
    def __init__(self, floors, model_list, seed):
        self.floor_info = floors
        self.models = model_list
        self.seed = seed
        
        self.box = None
        self.directions = None
        
        self.xlen = 0
        self.zlen = 0
        self.center = None
        
        self.initialize()
    

    def initialize(self):
        self.box = ModelInstance.merge_boxes(self.models)
        self.xlen, self.zlen = self.box[1] - self.box[0]
        self.center = (self.box[0] + self.box[1]) * 0.5
        self.directions = [[0,1],[0,-1],[1,0],[-1,0]]
        
    
    def get_box_corners(self):
        v1 = self.box[0]
        v3 = self.box[1]
        v2 = np.array([v3[0], v1[1]])
        v4 = np.array([v1[0], v3[1]])
        return np.array([v1, v2, v3, v4])
    
        
    def get_front_viewers(self, direct):
        fov = 60
        
        if direct[0] == 0:
            half_x, half_z = self.xlen * 0.5, self.zlen * 0.5
        else:
            half_x, half_z = self.zlen * 0.5, self.xlen * 0.5
    
        d1 = half_x / np.tan(np.deg2rad(fov * 0.5)) + half_z
        # d1 = 4.0 if d1 < 4.0 else d1
    
        direction = np.array(direct)
        c_pos = self.center + d1 * direction
        c_target = self.center
    
        camera_pos = np.array([c_pos[0], 1.2, c_pos[1]])
        camera_target = np.array([c_target[0], 1.2, c_target[1]])
        ret = list()
        ret.append({
            'pos': camera_pos.tolist(),
            'target': camera_target.tolist(),
            'fov': fov
        })
        return ret


    def get_side_viewers(self, deg_alpha, direct):
        alpha = np.deg2rad(deg_alpha)
        fov = 60
        
        if direct[0] == 0:
            w, h = self.xlen, self.zlen
        else:
            w, h = self.zlen, self.xlen
            
        s1 = np.sqrt(w ** 2 + h ** 2)
        a1 = np.arctan(h / w)
        theta = np.deg2rad(fov * 0.5)
        distance = s1 * np.sin(a1 + np.pi * 0.5 - alpha - theta) * 0.5 / np.sin(theta)
     
        direction = np.array(direct)
        normal = np.array([direction[1], -direction[0]])
        p0 = self.center
    
        p1 = p0 + distance * np.sin(alpha) * normal + distance * np.cos(alpha) * direction
        p2 = p0 - distance * np.sin(alpha) * normal + distance * np.cos(alpha) * direction
    
        camera_target = np.array([p0[0], 1.2, p0[1]])
        ret = list()
        ret.append({
            'pos': np.array([p1[0], 1.2, p1[1]]).tolist(),
            'target': camera_target.tolist(),
            'fov': fov
        })
    
        ret.append({
            'pos': np.array([p2[0], 1.2, p2[1]]).tolist(),
            'target': camera_target.tolist(),
            'fov': fov
        })
    
        return ret


    def get_common_viewers(self):
        ret = list()
        for direct in self.directions:
            front_viewers = self.get_front_viewers(direct)
            ret.extend(front_viewers)
            alphas = [15, 30, 45]
            # alphas = [45]
            for alpha in alphas:
                side_viewers = self.get_side_viewers(alpha, direct)
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

