import json
import argparse
from adapted import AdaptedCameras

parser = argparse.ArgumentParser(description='Camera Generating...')
parser.add_argument('--input', type=str, default='input.json', help='Input scene json file')
parser.add_argument('--output', type=str, default='output.json', help='Output json file')


args = parser.parse_args()


if __name__ == '__main__':
    scene_file = args.input
    camera = AdaptedCameras(scene_file)
    solutions = camera.run()
    out_file = args.output
    with open(out_file, 'w') as f:
        json.dump(solutions, f, ensure_ascii=False)
    
    



