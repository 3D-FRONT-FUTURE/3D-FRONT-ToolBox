"""
Creates all the necessary dataset from raw SUNCG
Make sure to read README
IMPORTANT: make sure you don't have a directory named `temp`
under SCENESYNTH_ROOT_PATH, since that will be removed relentlessly
"""
#Didn't implement any checkpoints, comment out parts as you wish...
import shutil
from utils import get_data_root_dir
from data.object import parse_objects

from scene_filter import get_filter, run_filter
from model_prior import ModelPrior

root_dir = get_data_root_dir()
parse_objects()

from data.dataset import create_dataset
print("Creating initial dataset...")
create_dataset(dest='temp')


from scene_filter import get_filter, run_filter
from model_prior import ModelPrior



print("Creating bedroom dataset...")
filter_description = [("room_type", ["Bedroom","MasterBedroom","SecondBedroom"]), ("floor_node",), ("renderable",)]
run_filter(filter_description, "temp", "bed_temp", 1, 1, 0, 1, 0)

# filter_description = [("bedroom", "final"), ("collision",)]
filter_description = [("bedroom", "final")]
run_filter(filter_description, "bed_temp", "bedroom", 1, 1, 1, 0, 1)

print("Creating model prior for bedroom...")
mp = ModelPrior()
mp.learn("bedroom_new")
mp.save()



print("Creating living room dataset...")
filter_description = [("room_type", ["LivingRoom","LivingDiningRoom"]), ("renderable",)]

run_filter(filter_description, "temp", "livingroom_temp", 1, 1, 0, 1, 0)

filter_description = [("livingroom", "final")]
run_filter(filter_description, "livingroom_temp", "livingroom", 1, 1, 1, 0, 1)


print("Creating model prior for living room...")
mp = ModelPrior()
mp.learn("living_living_collision")
mp.save()


