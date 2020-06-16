# -*- coding: utf-8 -*
import os, sys

sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))
from floorplan_generator import FloorplanGenerator


def scene_to_floorplan(filename):

    houseInfo = {}
    floorplan_generator = FloorplanGenerator()
    houseInfo = floorplan_generator.generate_floorplan(filename)
    return houseInfo
