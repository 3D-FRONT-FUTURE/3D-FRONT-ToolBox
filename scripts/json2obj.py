import os,argparse
from scene import read_json
from constants import Config

parser = argparse.ArgumentParser()
parser.add_argument(
        '--future_path',
        default = '3D-FUTURE-model',
        help = 'path to 3D FUTURE'
        )
parser.add_argument(
        '--texture_path',
        default = '3D-FRONT-texture',
        help = 'path to hard tex'
        )
parser.add_argument(
        '--json_path',
        default = '3D-FRONT',
        help = 'path to 3D FRONT'
        )

parser.add_argument(
        '--save_path',
        default = './output',
        help = 'path to save result dir'
        )


args = parser.parse_args()

files = os.listdir(args.json_path)

Config.FUTURE_PATH = args.future_path
Config.TEXTURE_PATH = args.texture_path

# get the 3D FUTURE shape info


# process jsons
for m in files:
    if not '.json' in m:
        continue

    scene = read_json(args.json_path+'/'+m, Config.FUTURE_PATH)
    scene.output(args.save_path)


    
