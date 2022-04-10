import cv2
import os
import sys
import glob
import numpy as np
import mrcnn.config as mConfig
import mrcnn.model as mModel
import mrcnn.visualize as mVisualize

# COCO class labels 
CLASS_NAMES = [ 
        'BG', 'person', 'bicycle', 'car', 'motorcycle', 'airplane', 
        'bus', 'train', 'truck', 'boat', 'traffic light',
        'fire hydrant', 'stop sign', 'parking meter', 'bench', 'bird',
        'cat', 'dog', 'horse', 'sheep', 'cow', 'elephant', 'bear',
        'zebra', 'giraffe', 'backpack', 'umbrella', 'handbag', 'tie',
        'suitcase', 'frisbee', 'skis', 'snowboard', 'sports ball',
        'kite', 'baseball bat', 'baseball glove', 'skateboard',
        'surfboard', 'tennis racket', 'bottle', 'wine glass', 'cup',
        'fork', 'knife', 'spoon', 'bowl', 'banana', 'apple',
        'sandwich', 'orange', 'broccoli', 'carrot', 'hot dog', 'pizza',
        'donut', 'cake', 'chair', 'couch', 'potted plant', 'bed',
        'dining table', 'toilet', 'tv', 'laptop', 'mouse', 'remote',
        'keyboard', 'cell phone', 'microwave', 'oven', 'toaster',
        'sink', 'refrigerator', 'book', 'clock', 'vase', 'scissors',
        'teddy bear', 'hair drier', 'toothbrush' 
        ]

# valid inputs
VALID_EXTENSIONS = [ 'jpg', 'jpeg', 'png' ]

# custom configuration
class InferenceConfig( mConfig.Config ):
    NAME = 'coco_inference'
    GPU_COUNT = 1
    IMAGES_PER_GPU = 1
    NUM_CLASSES = len( CLASS_NAMES )

# resolve image path and return image
def getImage( path = None ):
    # if it is called from command line, read path from system argument
    if( path == None ):
        # if image is not supplied, read default image
        if( len( sys.argv ) < 2 ):
            image = cv2.imread( './input/default.jpg' )

        # otherwise read supplied image
        else:
            image = cv2.imread( sys.argv[1] )

    # otherwise read path from suppied argument
    else:
        image = cv2.imread( path )

    # if supplied image does not exist, print error and finish execution
    if image is None:
        print( 'Image does not exist' )
        sys.exit( 1 )

    # convert image to RGB channel
    image = cv2.cvtColor( image, cv2.COLOR_BGR2RGB )

    return image

# main execution
def detect( imagePath = None ):
    # get image 
    image = getImage( imagePath )

    # initilize configuration and display it
    config = InferenceConfig()

    # initialize Mask R-CNN model for inference
    model = mModel.MaskRCNN( mode = 'inference', config = config, model_dir = os.getcwd() )

    # load weight to model
    model.load_weights( filepath = 'mask_rcnn_coco.h5', by_name = True )

    # forward pass
    res = model.detect( [ image ], verbose = 0 )
    r = res[0]

    # visualize results
    colHead = '%      class      at [ y1  x1  y2  x2]'
    print( colHead )
    print( '-' * len( colHead ) )
    for s, c, b in zip( r['scores'], r['class_ids'], r['rois'] ):
        print( f'{s*100:.2f}% {CLASS_NAMES[ c ]:10} at {b}' )

    mVisualize.display_instances( 
            image = image, 
            boxes = r['rois'], 
            masks = r['masks'],
            class_ids = r['class_ids'],
            class_names = CLASS_NAMES,
            scores = r['scores'] 
            )

    # save results
    # np.save( 'test.npy', r )
    return r

# runtime enterance
if __name__ == '__main__':
    detect()
