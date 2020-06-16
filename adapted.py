import json
from utils import *
from variables import *
from Generator.run import Generator
from Generator.layout import LayoutInstance



class AdaptedCameras:
    def __init__(self, scene_file):
        self.scene_file = scene_file
        self.scene_content = None
        self.floor_info = None
        self.model_pool = None
        self.model_dict = dict()
        self.initialize()
    
    def initialize(self):
        self.scene_content = read_scene_json(self.scene_file)
        self.floor_info = get_floor_info(self.scene_file)
        self.model_pool = json.load(open(model_pool, 'r'))
        
        furniture_dict = self.scene_content.dict_instance_for_furniture
        for ikey in furniture_dict.keys():
            ivalue = furniture_dict[ikey]
            uid = ikey
            jid = ivalue.jid
            if jid not in self.model_pool.keys():
                continue
                
            model_info = self.model_pool[jid]
            if not model_info:
                print('==> Error:', jid)
                continue
            
            self.model_dict[uid] = {
                'category_id': model_info['category_id'],
                'box': model_info['boundingBox'],
                'jid': jid
            }
       
            
    def run(self):
        room_dict = self.scene_content.dict_room
        ret = list()
        for iname in room_dict.keys():
            room = room_dict[iname]
            if room.type not in SUPPORTED_ROOMS:
                continue
            
            if iname not in self.floor_info.keys():
                continue
            
            floor = self.floor_info[iname]['floor']
            layout_info = dict()
            layout_info['room_floor'] = floor
            layout_info['seed'] = []
            layout_info['furniture'] = []

            furnitures = room.children_for_furniture
            for ifurniture in furnitures:
                uid = ifurniture['id']
                if uid not in self.model_dict.keys():
                    continue

                model_info = self.model_dict[uid]
                cate_id = model_info['category_id']
                layout_info['furniture'].append({
                    'jid': model_info['jid'],
                    'category_id': model_info['category_id'],
                    'size': model_info['box'],
                    'scale': ifurniture['scale'],
                    'pos': ifurniture['pos'],
                    'rot': ifurniture['rot']
                })
                
                if room.type in ['SecondBedroom', 'MasterBedroom']:
                    if cate_id in BED_IDS:
                        layout_info['seed'].append({
                            'jid': model_info['jid'],
                            'category_id': model_info['category_id']
                        })
              
                if room.type in ['LivingDiningRoom', 'LivingRoom', 'DiningRoom']:
                    if cate_id in SOFA_IDS or cate_id in TABLE_IDS:
                        layout_info['seed'].append({
                            'jid': model_info['jid'],
                            'category_id': model_info['category_id']
                        })

            layout = LayoutInstance(layout_info)
            generator = Generator(layout)
            cameras = generator.generate()
            ret.extend(cameras)
            
        return ret

            
    