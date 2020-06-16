# -*- coding: utf-8 -*
"""
instance
"""

import numpy as np
from Room.bounding_box import BoundingBox
from Room.mesh import Mesh


class Instance:
    def __init__(self, uid):
        self.uid = uid                          # unique id
        self.jid = ''                           # object id
        self.aid = []                           
        self.type = ''                          # Floor or Window or ...
        self.bounding_box = BoundingBox()      # bbox
        self.mesh = 0                           # is Mesh object, juran-json 'mesh' info
        self.ref = 0                            # reference count

    def __repr__(self):
        return 'Instance %s, {jid:%s}' % (
            self.uid, self.jid
        )

    def clone(self):
        """
        clone
        :return: copy instance
        """

        instance = Instance(self.uid)
        instance.jid = self.jid
        instance.aid = self.aid[:]
        instance.type = self.type

        instance.bounding_box = self.bounding_box.clone()
        instance.mesh = self.mesh
        instance.ref = self.ref
        return instance

