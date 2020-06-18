# JSON to OBJ
This python script is used to output OBJ files from scene json file. The output OBJ files including walls and high-quality furniture shapes with informative texture.

### Dependencies
  + ***numpy***
  + ***libigl***
  + ***trimesh***

### Install
We recommend using anaconda to install dependencies.

`conda create -n front python=3.6`

`conda activate front`

`conda install -c conda-forge igl`

`conda install -c conda-forge trimesh`

### How To Use

`python run.py --future_path=./3D-FUTURE-model --json_path=./3D-FRONT --save_path=./outputs`

  + ***future_path***: 3D-FUTURE models directory
  + ***json_path***: json directory
  + ***save_path***: output directory
  
