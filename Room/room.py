# -*- coding: utf-8 -*
import numpy as np
from Room.bounding_box import BoundingBox


class Room:
    """
    Room info
    """

    def __init__(self, uid, scene):
        self.scene = scene                                  # parent
        self.id = uid                                       # id
        self.type = ''                                      # Bedroom
        self.position = np.zeros(3)                         # [0,0,0]
        self.rotation = np.array([0.0, 0.0, 0.0, 1.0])      # [0,0,0,1]
        self.scale = np.array([1.0, 1.0, 1.0])              # [1,1,1]
        self.children_for_mesh = []                         # furniture
        self.children_for_furniture = []                    # floor, window ...
        self.bounding_box = BoundingBox()                  # box

    def __repr__(self):
        return 'Room %s, {type:%s}' % (
            self.id, self.type
        )

    def calculate_bbox(self, scene):
        """
        :param scene:
        :return:
        """
        for instance_info in self.children_for_furniture:
            instanceId = instance_info['id']
            instance = scene.find_instance_for_furniture(instanceId)
            if(instance == 0 or instance.mesh == 0):
                continue

            bbox = instance.mesh.bounding_box.clone()
            bbox.transform(instance_info['pos'], instance_info['rot'], instance_info['scale'])
            self.bounding_box.merge(bbox)
        return self.bounding_box

    def delete_all_furniture(self):
        """
        :return:
        """
        for instance_info in self.children_for_furniture:
            instance_id = instance_info['id']
            instance = self.scene.find_instance_for_furniture(instance_id)
            if instance == 0:
                continue

            self.scene.delete_furniture(instance)

            self.delete_child_to_content(instance_info['instanceid'])

        self.children_for_furniture = []

    def delete_furniture_by_index(self, index):
        """
        :param index:
        :return:
        """
        instance_info = self.children_for_furniture[index]
        instance_id = instance_info['id']
        instance = self.scene.find_instance_for_furniture(instance_id)
        if instance != 0:
            self.scene.delete_furniture(instance)

        del self.children_for_furniture[index]
        self.delete_child_to_content(instance_info['instanceid'])

    def delete_furniture_by_id(self, id):
        """
        :param item:
        :return:
        """
        for i in range(len(self.children_for_furniture)-1, -1, -1):
            instance_info = self.children_for_furniture[i]

            # if not self.equal_furniture(instance_info, item):
            if instance_info['instanceid'] != id:
                continue

            self.delete_furniture_by_index(i)
            break

    def delete_child_to_content(self, child_id):
        """
        :param child_id:
        :return:
        """
        if len(self.scene.content) == 0:
            return

        room_content = self.scene.content['scene']['room']
        for room_info in room_content:
            if room_info['instanceid'] != self.id:
                continue

            room_child = room_info['children']
            for i, child in enumerate(room_child):
                if child['instanceid'] != child_id:
                    continue

                del room_child[i]
                return

    def replace_room(self, group_list):
        """
        :param group_list:
        :return:
        """
        for group_info in group_list:
            group = group_info['group']
            if len(group) == 0:
                continue

            for entity in group:
                if not entity.used:
                    continue

                self.add_entity(entity)

    def delete_entity(self, entity):
        """
        :param entity:
        :return:
        """
        self.delete_furniture_by_id(entity.instance_id)

    def add_entity(self, entity):
        """
        :param entity
        :return:
        """
        instance = self.scene.find_instance_for_furniture(entity.instance_ref)
        if instance == 0:
            entity.instance.ref += 1
            self.scene.add_instance_for_furniture(entity.instance_ref, entity.instance)
            self.add_furniture_to_content(entity)
        else:
            instance.ref += 1

        info = {}
        info['id'] = entity.instance_ref
        info['pos'] = entity.position
        info['rot'] = entity.rotate
        info['scale'] = entity.scale
        info['instanceid'] = entity.instance_id
        self.children_for_furniture.append(info)

        self.add_child_to_content(entity)

        for child in entity.children:
            if not child.used:
                continue

            self.add_entity(child)

    def add_furniture_to_content(self, entity):
        """
        :param entity:
        :return:
        """
        if len(self.scene.content) == 0:
            return

        info = {}
        info['uid'] = entity.instance_ref
        info['jid'] = entity.instance.jid
        info['aid'] = entity.instance.aid
        self.scene.content['furniture'].append(info)

    def add_child_to_content(self, entity):
        """
        :param entity:
        :return:
        """
        if len(self.scene.content) == 0:
            return

        room_content = self.scene.content['scene']['room']
        for room_info in room_content:
            if room_info['instanceid'] != self.id:
                continue

            room_child = room_info['children']

            child_info = {}
            child_info['ref'] = entity.instance_ref
            child_info['instanceid'] = entity.instance_id
            child_info['pos'] = entity.position.tolist()
            child_info['rot'] = entity.rotate.tolist()
            child_info['scale'] = entity.scale.tolist()
            room_child.append(child_info)
            break

