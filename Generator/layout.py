from variables import *
from Generator.interface import *
from Generator.camera import CameraInstance
from Generator.model import ModelInstance


class LayoutInstance:
    def __init__(self,  layout_dict):
        self.floor_info = layout_dict['room_floor']
        self.room_info = None
        self.task_id = 'demo'
        self.furniture_list = layout_dict['furniture']
        self.seed_info = layout_dict['seed']
        
        self.seeds = list()
        self.models = list()
        self.initialize()
        
        
    def initialize(self):
        seed_jids = list()
        for value in self.seed_info:
            jid = value['jid']
            seed_jids.append(jid)
        
        for furniture in self.furniture_list:
            data = furniture
            model = ModelInstance(data)
            self.models.append(model)
            if model.jid in seed_jids:
                self.seeds.append(model)
                
    def get_seed_around(self):
        seed_surrounds = dict()
        for seed in self.seeds:
            seed_cate = seed.category
            if seed_cate not in seed_surrounds.keys():
                seed_surrounds[seed_cate] = list()
            
            surrounds = list()
            for model in self.models:
                if seed == model:
                    continue
                dist = seed.distance(model)
                surrounds.append([model, dist])
            
            surrounds = sorted(surrounds, key=lambda value:value[1])
            seed_surrounds[seed_cate].append(surrounds)
        return seed_surrounds

    