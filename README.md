# Object-Aware Cartoonization

An object-aware cartoonization method using CartoonGAN and Mask R-CNN.

## Installation

1. Clone this repository

2. Run setup from the repository root directory

   ```bash
   bash setup.sh
   ```

3. Start Python virtual environment

   ```bash
   source ./venv/bin/activate
   ```

4. Download pre-trained weights inside the root directory from [here](https://github.com/matterport/Mask_RCNN/releases/download/v2.0/mask_rcnn_coco.h5)

## Usage

### Object Detection

Use `detect.py` to perform object detection. To run a custom image,
please supply an image path as argument like the example shown below:

```bash
python detect.py ./input/default.jpg
```

### Cartoonization

Use `cartoonize.py` to perform image cartoonization. By default, it will apply
`shinkai` style transfer on images from `input` directory, the cartoonized images
will be placed in `output` directory.

There are 4 styles available with CartoonGAN:

- `shinkai`
- `hayao`
- `hosoda`
- `paprika`

There are many customization options available. As an example, the following
command specified input and output directories and styles:

```bash
python cartoonize.py \
	--input_dir input \
	--output_dir output \
	--styles shinkai hayao
```

To explore all available customization options, please use the following command
to get detailed explainations:

```bash
python cartoonize.py --help
```

## Acknowledgement

- [Mask R-CNN for Object Detection and Segmentation using TensorFlow 2.0](https://github.com/ahmedfgad/Mask-RCNN-TF2)
- [CartoonGAN-TensorFlow2](https://github.com/mnicnc404/CartoonGan-tensorflow)
