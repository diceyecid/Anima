# Anima

An object-aware cartoonization method

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

Use `detect.py` to perform object detection. To run a custom image,
please supply an image path as argument like the example shown below:

```bash
python detect.py ./samples/default.jpg
```
