import numpy as np
from Generator.interface import *
from Generator.region import RegionGenerator
from Generator.seed import SeedGenerator


class Generator:
    def __init__(self, layout):
        self.layout = layout
    
    def floor_generate(self, h1=1.2, h2=1.2):
        ret = list()
        floor_info = self.layout.floor_info
        floors = np.array(floor_info)
        center = np.zeros(2)
        cnt = len(floors)
        for i in range(cnt - 1):
            center += floors[i]
        center /= (cnt - 1)
        
        v1 = np.array(floor_info[0])
        v2 = np.array(floor_info[1])
        mid = (v1 + v2) * 0.5
        direct = normalize(v1 - v2)
        normal = np.array([direct[1], -direct[0]])
        s1 = mid + normal * 0.5
        s2 = mid - normal * 0.5

        floor_poly = sg.Polygon(floor_info)
        p1 = sg.Point(s1)
        p2 = sg.Point(s2)

        camera_target = np.array([center[0], h2, center[1]])
        if floor_poly.contains(p1):
            ret.append({
                'pos': np.array([s1[0], h1, s1[1]]).tolist(),
                'target': camera_target.tolist(),
                'fov': 60
            })

        if floor_poly.contains(p2):
            ret.append({
                'pos': np.array([s2[0], h1, s2[1]]).tolist(),
                'target': camera_target.tolist(),
                'fov': 60
            })
      
        return ret
        
    
    def generate(self, h1=1.2, h2=1.2):
        ret = list()
        seeds = self.layout.seeds
        if len(seeds) == 0:
            ret.extend(self.floor_generate(h1, h2))
            return ret
        
        for seed in seeds:
            cameras = self.seed_generate(self.layout.floor_info, seed, h1, h2)
            ret.extend(cameras)
        return ret
        
        surrounds = self.layout.get_seed_around()
        for seed in seeds:
            cate = seed.category
            print('seed: ', cate)
            values = surrounds[cate]
            for value in values:
                cameras = self.region_generate(self.layout.floor_info, seed, value)
                ret.extend(cameras)
        return ret
        
        
    def region_generate(self, floor_info, seed, surrounds):
        visibles = list()
        visibles.append(seed)
        for data in surrounds:
            dist = data[1]
            if dist < 3.0:
                visibles.append(data[0])
            
        region_instance = RegionGenerator(floor_info, visibles, seed)
        viewers = region_instance.get_viewers()
        return viewers


    def seed_generate(self, floor_info, seed, h1, h2):
        seed_instance = SeedGenerator(floor_info, seed, h1, h2)
        viewers = seed_instance.get_viewers()
        return viewers
        
