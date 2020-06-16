import numpy as np
from Generator.interface import *


class CameraInstance:
    def __init__(self, camera_param):
        self.pos = None
        self.view = None
        self.dir = None
        
        self.floor_pos = None
        self.floor_view = None
        self.floor_dir = None
        
        self.fov = 0
        self.pitch_tan = 0
        
        self.initialize(camera_param)
    
    def initialize(self, camera_param):
        self.pos = np.array(camera_param['pos'])
        self.view = np.array(camera_param['target'])
        
        self.floor_pos = np.array([self.pos[0], self.pos[2]])
        self.floor_view = np.array([self.view[0], self.view[2]])
        self.fov = camera_param['fov']
        
        vec = self.view - self.pos
        self.dir = normalize(vec)
        
        vec_floor = np.array([vec[0], vec[2]])
        vec_floor_len = length(vec_floor)
        self.floor_dir = vec_floor / vec_floor_len
        
        dh = self.view[1] - self.pos[1]
        self.pitch_tan = dh / vec_floor_len
    
    def get_camera_height(self):
        return self.pos[1]

