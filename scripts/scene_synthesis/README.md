# Interior Scene Synthesis

We use the method of Wang et al.[1] [deep_synth](https://github.com/brownvc/deep-synth) to synthesize scenes.

## Data Preparation

To meet the data format [1] used, we provide the prepared data in the dir /data/3d_front. First download the [object.7z]() and then unzip the .7z files (object.7z, house.7z and room.7z) in the same name dir (in /data/3d_front).

Then run 
```
python create_data.py
```
to create the images data (bedroom and livingroom) to input the network.

## Training Network

Please refer to [deep_synth](https://github.com/brownvc/deep-synth) for training details. Here we list the simple process (for bedroom set).

Run
```
python continue_train.py --data-dir bedroom --save-dir bedroom --train-size train_set_size --use-count
```
to train the continue predictor.

Run
```
python location_train.py --data-dir bedroom --save-dir bedroom --train-size train_set_size --use-count --progressive-p 
```
to train the location-category predictor.

Run
```
python rotation_train.py --data-dir bedroom --save-dir bedroom --train-size train_set_size
```
to train the instance-orientation predictor.

## test
Run
```
python batch_synth.py --save-dir results --data-dir bedroom --model-dir bedroom --continue-epoch epoch_number --location-epoch epoch_number --rotation-epoch epoch_number --start start_room_index --end end_room_index
```


[1] K. Wang, M. Savva, A.X. Chang, and D. Ritchie, Deep convolutional priors for indoor scene synthesis. ACM Transactions on Graphics (TOG), 37(4), pp.1-14, 2018