


## Setup
```
conda create --name nerfstudio -y python=3.8
conda activate nerfstudio
python -m pip install --upgrade pip


pip install torch==2.1.2+cu118 torchvision==0.16.2+cu118 --extra-index-url https://download.pytorch.org/whl/cu118

pip install ninja git+https://github.com/NVlabs/tiny-cuda-nn/#subdirectory=bindings/torch

pip install nerfstudio

git clone --recursive https://github.com/cvg/Hierarchical-Localization/
cd Hierarchical-Localization/
python -m pip install -e .


```



## Pose Estimation: Candidate 1
```
ns-process-data images \
  --data dataset/input \
  --output-dir dataset_seq \
  --sfm-tool colmap \
  --matching-method sequential \
  --feature-type sift \
  --verbose
```


## Pose Estimation: Candidate 2

```
rm -rf outputs

ns-process-data images \
  --data input \
  --output-dir dataset_sequential \
  --sfm-tool hloc \
  --feature-type disk \
  --matcher-type disk+lightglue \
  --matching-method sequential \
  --refine-pixsfm \
  --verbose \
  --skip-image-processing

```



## Gaussian Reconstruction: Candidate 1

```
ns-train splatfacto   --data dataset_seq   --pipeline.model.cull-alpha-thresh 0.01   --pipeline.model.densify-grad-thresh 0.001   --pipeline.model.sh-degree 3   --pipeline.datamanager.eval-num-images-to-sample-from 1
```

## Gaussian Reconstruction: Candidate 2
```
ns-train splatfacto \
  --data dataset_seq \
  --pipeline.model.cull-alpha-thresh 0.005 \
  --pipeline.model.use-scale-regularization True \
  --pipeline.model.densify-grad-thresh 0.0002 \
  --pipeline.model.sh-degree 4 \
  --pipeline.model.max-gauss-ratio 5.0 \
  --pipeline.model.densify-size-thresh 0.005 \
  --pipeline.model.cull-screen-size 0.1 \
  --pipeline.model.split-screen-size 0.03 \
  --pipeline.model.reset-alpha-every 50
```



## Export Gaussian Splats as .ply in exports/splat

```
temp_path = $(ls outputs/dataset_seq/splatfacto)
ns-export gaussian-splat --load-config "outputs/dataset_seq/splatfacto/$temp_path/config.yml" --output-dir exports/splat
```

You can view the splats in [PlayCanvas Viewer](https://playcanvas.com/viewer)