import numpy as np
from Generator.interface import *


class ModelInstance:
    def __init__(self, params):
        self.jid = ''
        self.category = ''
        self.category_id = ''
        self.size = None
        self.scale = None
        self.rot = None
        self.pos = None
        self.bbox = None
        
        self.dir = None
        self.initialize(params)
    
    def initialize(self, params):
        self.jid = params['jid']
        self.category = ''
        self.category_id = params['category_id']
        box = params['size']
        self.bbox = np.array([box['xLen'] / 100.0, box['zLen'] / 100.0, box['yLen'] / 100.0])
        
        self.pos = np.array(params['pos'])
        self.rot = np.array(params['rot'])
        self.scale = np.array(params['scale'])
        
        self.size = self.bbox
        direct = quaternion_to_dir(self.rot)
        self.dir = np.array([direct[0], direct[2]])
        self.dir = normalize(self.dir)
    
    def get_floor_pos(self):
        return np.array([self.pos[0], self.pos[2]])
    
    def get_normal(self):
        return np.array([self.dir[1], -self.dir[0]])
    
    def get_relative_coord(self, target):
        direction = self.dir
        normal = self.get_normal()
        pos = self.get_floor_pos()
        vec = target - pos
        dw = vec.dot(normal)
        dh = vec.dot(direction)
        return [dw, dh]
    
    def get_model_floor_size(self):
        return [self.size[0], self.size[2]]
    
    def get_model_direction(self):
        return self.dir
    
    def get_bounding_box(self):
        w = self.size[0]
        h = self.size[2]
        p = self.get_floor_pos()
        normal = self.get_normal()
        v1 = p - self.dir * h * 0.5 - normal * w * 0.5
        v2 = p - self.dir * h * 0.5 + normal * w * 0.5
        v3 = p + self.dir * h * 0.5 + normal * w * 0.5
        v4 = p + self.dir * h * 0.5 - normal * w * 0.5
        return np.array([v1, v2, v3, v4])
    
    def get_box(self):
        corners = self.get_bounding_box()
        v1, v2, v3, v4 = corners.tolist()
        x_min = np.min([v1[0], v2[0], v3[0], v4[0]])
        x_max = np.max([v1[0], v2[0], v3[0], v4[0]])
        z_min = np.min([v1[1], v2[1], v3[1], v4[1]])
        z_max = np.max([v1[1], v2[1], v3[1], v4[1]])
        return np.array([x_min, z_min]), np.array([x_max, z_max])
    
    def distance(self, instance):
        p1 = self.get_floor_pos()
        p2 = instance.get_floor_pos()
        return length(p1 - p2)
    
    def __str__(self):
        return self.category
    
    @staticmethod
    def merge_boxes(models):
        x_min, x_max = 1e10, -1e10
        z_min, z_max = 1e10, -1e10
        for model in models:
            box_min, box_max = model.get_box()
            if box_min[0] < x_min:
                x_min = box_min[0]
            
            if box_max[0] > x_max:
                x_max = box_max[0]
            
            if box_min[1] < z_min:
                z_min = box_min[1]
                
            if box_max[1] > z_max:
                z_max = box_max[1]
        return np.array([x_min, z_min]), np.array([x_max, z_max])
    
    