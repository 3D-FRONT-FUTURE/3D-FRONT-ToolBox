# 3D-FRONT-Toolbox
### 2022.4.21
* rewrite json2obj.py to process the updated 3D-FRONT (partial open sourceinterior finish with texture) and add new features.
### Algorithm Description
   + ***Input***: scene json 
      + scene json file, *.json
   + ***Ouput***: camera json 
      + camera parameters(list) json file, *.json
      
   + Parse the information in the *scene json*, including *layouts, floors, furnitures* , and generate camera parameters by these information.
   + The camera parameters can be used to render scenes.
   + ***Bedroom***：referred by bed
   + ***DiningRoom***：referred by dining-table
   + ***LivingRoom***：referred by main-sofa

### How To Use

`python run.py --input=scene.json --output=path/camera.json`
   
   
### Camera Description
  + ***pos***: camera position
  + ***target***: camera viewer
  + ***fov***: viewer angles
  
  
### Other

   + The camera parameters maybe are not that good in some cases, they are some kinds of coarse solutions. You can take them as initial solutions and adjust them.
   
   
