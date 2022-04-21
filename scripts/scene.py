import json
import numpy as np
from utils import read_obj, save_obj, read_mesh_attr, transform_v, save_mesh
import os
import urllib.request
from constants import Config



class Scene():
    def __init__(self, uid):
        self.furniture = {}
        self.meshes = {}
        self.material = {}
        self.house = House(uid)
        

    def add_furniture(self, f):
        self.furniture[f.uid] = f
    def add_mesh(self, m):
        self.meshes[m.uid] = m
    def add_material(self, m):
        self.material[m.uid] = m
    def output(self, 
            savepath,
            select_room_type = [],
            select_mesh_type = [],
            select_furniture_type = [],
            ):
        if not os.path.exists(savepath):
            os.mkdir(savepath)
        self.house.output(savepath+'/'+self.house.uid, select_room_type, select_mesh_type, select_furniture_type)
    
    def output_with_room_id(self, savepath, room_id, center = True, select_mesh_type = [], select_furniture_type = []):
        if not os.path.exists(savepath):
            os.mkdir(savepath)
        self.house.output_with_room_id(savepath+'/'+self.house.uid, room_id, center, select_mesh_type, select_furniture_type)

class House():
    def __init__(self, uid):
        self.uid = uid
        self.rooms = {}
    
    def add_room(self, room):
        self.rooms[room.instanceid] = room
        
    def del_room_by_id(self, room_id):
        return self.rooms.pop(room_id)
        

    def output(self, savepath, select_room_type, select_mesh_type, select_furniture_type):
        if not os.path.exists(savepath):
            os.mkdir(savepath)
        for _, room in self.rooms.items():
            room.output(savepath, False, select_room_type, select_mesh_type, select_furniture_type)
        pass

    def output_with_room_id(self, savepath, room_id, center, select_mesh_type, select_furniture_type):
        if not os.path.exists(savepath):
            os.mkdir(savepath)
        self.rooms[room_id].output(savepath, center, [], select_mesh_type, select_furniture_type)


class Room():
    def __init__(self, type, instanceid):
        self.type = type
        self.instanceid = instanceid
        self.furniture = []
        self.meshes = {}
        self.center = 0

        self.default_texture = [220, 220, 220]



    def add_furniture(self, finstance):
        self.furniture.append(finstance)

    def add_mesh(self, mesh):
        if mesh.constructid not in self.meshes:
            self.meshes[mesh.constructid] = []
        self.meshes[mesh.constructid].append(mesh)


    def output(self, savepath, center, select_room_type, select_mesh_type, select_furniture_type):
        if not os.path.exists(savepath):
            os.mkdir(savepath)
        if center:
            self.cal_center()
        if len(select_room_type) > 0:
            if self.type not in select_room_type:
                return
        self.output_meshes(savepath+'/'+self.instanceid, select_mesh_type)
        self.output_furniture(savepath+'/'+self.instanceid, select_furniture_type)

    def cal_center(self):
        for constructid, all_mesh in self.meshes.items():
            for mesh in all_mesh:
                if mesh.type == 'floor':
                    v, faces, vt, mat = read_mesh_attr(mesh)

                    self.center = (np.max(v,0) + np.min(v,0))/2
                    return

        
    def output_meshes(self, savepath, select_mesh_type):
        if not os.path.exists(savepath):
            os.mkdir(savepath)
        all_output = []
        for constructid, all_mesh in self.meshes.items():
            output = []
            for mesh in all_mesh:
                if len(select_mesh_type) > 0:
                    if mesh.type not in select_mesh_type:
                        continue
                v, faces, vt, mat = read_mesh_attr(mesh)
                texture = self.default_texture
                if vt is not None and mat is not None:
                    if mat.texture != '':
                        if not os.path.exists(Config.TEXTURE_PATH+'/' + mat.jid):
                            os.mkdir(Config.TEXTURE_PATH+'/' + mat.jid)
                            try:
                                urllib.request.urlretrieve(mat.texture,Config.TEXTURE_PATH+'/' + mat.jid +'/texture.png')
                            except:
                                pass

                        texture = Config.TEXTURE_PATH+'/' + mat.jid + '/texture.png'

                output.append([mesh.instanceid, v - self.center,faces,vt,texture])
                all_output.append([mesh.instanceid, v - self.center,faces,vt,texture])
            if len(output) == 0:
                continue
            if not os.path.exists(savepath+'/'+mesh.type):
                os.mkdir(savepath+'/'+mesh.type)
            
            save_mesh(savepath+'/'+mesh.type,constructid, *output)

        save_mesh(savepath, 'meshes', *all_output)

    def output_furniture(self, savepath, select_furniture_type):
        if not os.path.exists(savepath):
            os.mkdir(savepath)
        number = 1
        for instance in self.furniture:
            if len(select_furniture_type) > 0:
                    if instance.info.category not in select_furniture_type and instance.info.super_category not in select_furniture_type:
                        continue

            obj_path = Config.FUTURE_PATH + '/' + instance.info.jid+ '/raw_model_tri.obj'
            v = read_obj(obj_path)
            v = transform_v(v, instance)
            save_obj(obj_path, os.path.join(savepath, instance.info.super_category.replace('/','_')+'_'+instance.info.jid + '_' + str(number) + '.obj'), v - self.center, instance.info.jid)

            number = number + 1




class Furniture():
    def __init__(self, uid, jid, super_category, category, size = None, bbox = None):
        self.uid = uid
        self.jid = jid
        self.size = size
        self.bbox = bbox
        self.category = category
        self.super_category = super_category

class Instance():
    def __init__(self, f: Furniture, pos, rot, scale):
        self.info = f
        self.pos = pos
        self.rot = rot
        self.scale = scale
    
class Mesh():
    def __init__(self, uid, xyz, faces, uv, material, type, constructid, instanceid):
        self.uid = uid
        self.xyz = xyz
        self.faces = faces
        self.uv = uv
        self.material = material

        if 'ceil' in type or 'Ceil' in type:
            self.type = 'ceil'
        elif 'floor' in type or 'Floor' in type:
            self.type = 'floor'
        elif 'wall' in type or 'Wall' in type:
            self.type = 'wall'
        else:
            self.type = 'others'

        self.constructid = constructid
        self.instanceid = instanceid

class Material():
    def __init__(self, uid, jid, UVTransform, texture):
        self.uid = uid
        self.jid = jid
        self.UVTransform = UVTransform
        self.texture = texture

def read_json(jsonfile, future_path) -> Scene:
    model_info = json.load(open(future_path+'/model_info.json','r', encoding='utf-8'))
    model_info_dict= {}
    for model in model_info:
        model_info_dict[model['model_id']] = model
    fid = open(jsonfile, 'r', encoding='utf-8')
    data = json.load(fid)
    fid.close()
    scene = Scene(data['uid'])
    
    if 'furniture' in data:
        for furniture in data['furniture']:
            if 'valid' in furniture and furniture['valid']:
                f = Furniture(furniture['uid'],
                            furniture['jid'],
                            model_info_dict[furniture['jid']]['super-category'],
                            model_info_dict[furniture['jid']]['category'],
                            furniture['size'] if 'size' in furniture else None,
                            furniture['bbox'] if 'bbox' in furniture else None
                            )
                scene.add_furniture(f)

    if 'material' in data:
        for mat in data['material']:
            m = Material(mat['uid'],
                        mat['jid'],
                        np.reshape(mat['UVTransform'], [3, 3]) if 'UVTransform' in mat else None,
                        mat['texture'])
            scene.add_material(m)

    if 'mesh' in data:

        for mesh in data['mesh']:
            

            m = Mesh(mesh['uid'],
                    np.reshape(mesh['xyz'], [-1, 3]),
                    np.reshape(mesh['faces'], [-1, 3]),
                    np.reshape(mesh['uv'], [-1, 2]) if 'uv' in mesh else None,
                    scene.material[mesh['material']] if 'material' in mesh and mesh['material'] in scene.material else None,
                    mesh['type'],
                    mesh['constructid'] if 'constructid' in mesh else None,
                    mesh['instanceid'] if 'instanceid' in mesh else None
                    )
            scene.add_mesh(m)


    for r in data['scene']['room']:
        room = Room(r['type'], r['instanceid'])
        
        children = r['children']
        for c in children:
            ref = c['ref']

            if ref in scene.furniture:
                finstance = Instance(scene.furniture[ref], c['pos'], c['rot'], c['scale'])
                room.add_furniture(finstance)

            if ref in scene.meshes:
                room.add_mesh(scene.meshes[ref])
        scene.house.add_room(room)
    return scene

