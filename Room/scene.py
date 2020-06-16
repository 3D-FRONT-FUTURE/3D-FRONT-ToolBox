# -*- coding: utf-8 -*

import numpy as np
from Room.mesh import Mesh
from Room.bounding_box import BoundingBox
import json
import os

from Room.math_engine import *


class Scene:
    """
    scene info
    """

    def __init__(self, uid, content):
        self.uid = uid                                          # uid
        self.dict_instance_for_mesh = {}                        # floor, window ...
        self.dict_instance_for_furniture = {}                   # furniture
        self.dict_room = {}                                     # room
        self.position = np.zeros(3)                             # [0,0,0]
        self.rotation = np.array([0.0, 0.0, 0.0, 1.0])          # [0,0,0,1]
        self.scale = np.array([1.0, 1.0, 1.0])                  # [1,1,1]
        self.content = content                                  # json

    def __repr__(self):
        return 'Scene %s' % (
            self.uid
        )

    def add_instance_for_furniture(self, id, instance):
        """
        :param id:
        :param instance:
        :return: boolean
        """
        if id in self.dict_instance_for_furniture:
            print("Warning - ALScene-add_instance_for_furniture, id.%d is repeat" % id)
            return False

        self.dict_instance_for_furniture[id] = instance
        return True

    def add_instance_for_mesh(self, id, instance):
        """
        :param id:
        :param instance:
        :return: boolean
        """
        if id in self.dict_instance_for_mesh:
            print("Error - ALScene-add_instance_for_mesh, id.%d is repeat" % id)
            return False

        self.dict_instance_for_mesh[id] = instance
        return True

    def add_room(self, id, room):
        """
        :param id:
        :param room:
        :return: boolean
        """
        if id in self.dict_room:
            print("Error - ALScene-add_room, id.%d is repeat" % id)
            return False

        self.dict_room[id] = room
        return True

    def find_instance_for_furniture(self, id):
        """
        :param id:
        :return: instance or 0
        """
        if id in self.dict_instance_for_furniture:
            return self.dict_instance_for_furniture[id]
        else:
            return 0

    def find_instance_for_mesh(self, id):
        """
        :param id:
        :return: instance or 0
        """
        if id in self.dict_instance_for_mesh:
            return self.dict_instance_for_mesh[id]
        else:
            return 0

    def find_room(self, id):
        """
        :param id:
        :return: room or 0
        """
        if id in self.dict_room:
            return self.dict_room[id]
        else:
            return 0


    def delete_furniture_to_content(self, uid):
        """
        :param uid: id
        :return:
        """
        if len(self.content) == 0:
            return

        for i, furniture in enumerate(self.content['furniture']):
            if furniture['uid'] == uid:
                del self.content['furniture'][i]
                return

    def delete_furniture(self, instance):
        """
        :param instance:
        :return:
        """
        instance.ref -= 1
        if (instance.ref == 0):
            del self.dict_instance_for_furniture[instance.uid]
            self.delete_furniture_to_content(instance.uid)

    def delete_all_furniture(self):
        """
        :return:
        """
        for roomId, room in self.dict_room.items():
            room.delete_all_furniture()

    def get_json(self):
        """
        :return:
        """
        return self.content


    def save_json(self, file_name):
        args = self.get_json()
        with open(file_name, 'w') as f:
            json.dump(args, f, ensure_ascii=False)


