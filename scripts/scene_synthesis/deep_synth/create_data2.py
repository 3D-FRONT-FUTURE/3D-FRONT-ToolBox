import shutil
from utils import get_data_root_dir
from data.object import parse_objects

root_dir = get_data_root_dir()


from scene_filter import get_filter, run_filter
from model_prior import ModelPrior
print("Creating office dataset...")
filter_description = [("room_type", ["Office"]), ("floor_node",), ("renderable",)]
run_filter(filter_description, "good", "temp2", 1, 1, 0, 1, 0)
filter_description = [("office", "final"), ("collision",)]
run_filter(filter_description, "temp2", "office", 1, 1, 1, 0, 1)
print()
print("Creating model prior for office...")
mp = ModelPrior()
mp.learn("office")
mp.save()
print()
shutil.rmtree(f"{root_dir}/temp2")