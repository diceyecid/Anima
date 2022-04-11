import cv2
import os
import sys
import glob
import logging
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

VALID_EXTENSIONS = ['jpg', 'png', 'gif', 'JPG']

# logger
logger = logging.getLogger("Detector")
logger.propagate = False
log_lvl = {"debug": logging.DEBUG, "info": logging.INFO,
           "warning": logging.WARNING, "error": logging.ERROR,
           "critical": logging.CRITICAL}
logger.setLevel( log_lvl['info'] )
formatter = logging.Formatter(
    "[%(asctime)s] [%(name)s] [%(levelname)s] %(message)s", "%Y-%m-%d %H:%M:%S")
stdhandler = logging.StreamHandler(sys.stdout)
stdhandler.setFormatter(formatter)
logger.addHandler(stdhandler)


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
            path = './input/default.jpg'

        # otherwise read supplied image
        else:
            path = sys.argv[1]

    # read image from path
    image = cv2.imread( path )

    # if supplied image does not exist, print error and finish execution
    if image is None:
        print( 'Image does not exist' )
        sys.exit( 1 )

    # convert image to RGB channel
    image = cv2.cvtColor( image, cv2.COLOR_BGR2RGB )

    return image


# visualize results
def visualize( image, result ):
    r = result

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

    return

# main execution
def main( inputPath = None ):
    # define lists to contain images and prediction results
    images = []
    results = []

    # get image 
    logger.info( f'Retrieving image from `inputPath`' )
    images.append( getImage( inputPath ) )

    # initilize configuration and display it
    config = InferenceConfig()

    # initialize Mask R-CNN model for inference
    logger.info( f'Loading Mask R-CNN model...' )
    model = mModel.MaskRCNN( mode = 'inference', config = config, model_dir = os.getcwd() )

    # load weight to model
    logger.info( f'Loading pretrained COCO weights...' )
    model.load_weights( filepath = 'mask_rcnn_coco.h5', by_name = True )

    # forward pass
    for im in images:
        res = model.detect( [ im ], verbose = 0 )
        results.append( res[0] )

    # visualize results
    # for im, r in zip( images, results ):
        # visualize( im, r )

    # save results
    # np.save( 'test.npy', r )
    return results


def detect( imagePath, outputDir, ignoreGIF = False ):
    # initilize configuration and display it
    config = InferenceConfig()

    # initialize Mask R-CNN model for inference
    logger.info( f'Loading Mask R-CNN model...' )
    model = mModel.MaskRCNN( mode = 'inference', config = config, model_dir = os.getcwd() )

    # load weight to model
    logger.info( f'Loading pretrained COCO weights...' )
    model.load_weights( filepath = 'mask_rcnn_coco.h5', by_name = True )

    # get file name
    filename = imagePath.split(os.path.sep)[-1]
    
    # make a directory to for storing detected objects
    tempDir = os.path.join( f'{outputDir}', '.tmp')
    pngDir = os.path.join( tempDir, os.path.splitext( filename )[0] )
    objDir = os.path.join( pngDir, 'objects' )
    if not os.path.exists( objDir ):
        logger.debug( f'Creating temporary folder: {objDir} for storing detected objects...' )
        os.makedirs( objDir )

    logger.info( f"Detecting objects in {filename}...." )

    # transform gif
    if filename.endswith( '.gif' ) and not ignoreGIF:
        # find pngs from temporary folder
        pngPaths = []
        pngPaths.extend( glob.glob( os.path.join( pngDir, f"*.png" ) ) )
        pngPaths = sorted( pngPaths, key=lambda x: int(x.split('/')[-1].replace('.png', '')) )
        num_images = len( pngPaths )

        # detect objects
        for i, p in enumerate( pngPaths ):
            logger.debug(f"Detecting {len(pngPaths)} images and saving them to {objDir}....")

            # forward pass
            im = getImage( p )
            res = model.detect( [im], verbose = 0 )
            r = res[0] 

            # save results
            objFilename = f"{i + 1}.npy"
            np.save( os.path.join( objDir, objFilename ), r )

    # transform image
    else:
        # find the image
        preprocessedPath = os.path.join( pngDir, filename )
        im = getImage( preprocessedPath )

        # forward pass
        res = model.detect( [im], verbose = 0 )
        r = res[0] 

        # save results
        objFilename = f"0.npy"
        np.save( os.path.join( objDir, objFilename ), r )
        
                    
# runtime enterance
if __name__ == '__main__':
    main()
