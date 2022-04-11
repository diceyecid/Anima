import numpy as np
import cv2
import os
import sys
import glob
import logging
from detect import main as detect


IMAGE_PATH = './input/nyc.png'
CARTOON_PATH = './output/shinkai/nyc.png'
EDGES = ['adaptive', 'canny', 'morph', 'original']


# logger
logger = logging.getLogger("Enhancer")
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


# get canny edges in each of the region of interest
def getCannyEdge( objects, cartoon ):
    # pre-process
    edges = np.zeros( cartoon.shape[:2], np.uint8 )
    grey = cv2.cvtColor( cartoon, cv2.COLOR_BGR2GRAY )
    blur = cv2.GaussianBlur( grey, ( 5, 5 ), 0 )

    # for each region of interest with score larger than 90%
    for score, roi in zip( objects['scores'], objects['rois'] ):
        if( score > 0.9 ):
            # clip to the region
            region = blur[ roi[0] : roi[2], roi[1] : roi[3] ]

            # edge detection
            highThresh, _ = cv2.threshold( region, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU )
            lowThresh = highThresh * 0.75
            edge = cv2.Canny( region, lowThresh, highThresh )

            # edge refinement
            kern = np.ones( ( 3, 3 ), np.uint8 )
            dilate = cv2.dilate( edge, kern )
            erode = cv2.erode( dilate, kern )

            # find contour
            cont, hier = cv2.findContours( erode, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_NONE )
            edge = cv2.drawContours( np.zeros( region.shape[:2], np.uint8 ), cont, -1, 255, 1 )

            # place regional edge to the whole picture
            edges[ roi[0] : roi[2], roi[1] : roi[3] ] = edge
            # edges = cv2.rectangle( edges, ( roi[1], roi[0] ), ( roi[3], roi[2] ), 127, 1 )

    return edges


# get morphologic edge in each of the region of interest
def getMorphEdge( objects, cartoon ):
    # pre-process
    edges = np.zeros( cartoon.shape[:2], np.uint8 )
    grey = cv2.cvtColor( cartoon, cv2.COLOR_BGR2GRAY )

    # for each region of interest with score larger than 90%
    for score, roi in zip( objects['scores'], objects['rois'] ):
        if( score > 0.9 ):
            # clip to the region
            region = grey[ roi[0] : roi[2], roi[1] : roi[3] ]

            # threshold edges
            _, thresh = cv2.threshold( region, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU )

            # dilated edges
            kern = np.ones( ( 3, 3 ), np.uint8 )
            dilate = cv2.dilate( thresh, kern )

            # difference between edges to get actual edges
            edge = cv2.absdiff( dilate, thresh )
            
            # place regional edge to the whole picture
            edges[ roi[0] : roi[2], roi[1] : roi[3] ] = edge

    return edges


# get adaptive edge in each of the region of interest
def getAdaptiveEdge( objects, cartoon ):
    # pre-process
    edges = np.zeros( cartoon.shape[:2], np.uint8 )
    grey = cv2.cvtColor( cartoon, cv2.COLOR_BGR2GRAY )

    # for each region of interest with score larger than 90%
    for score, roi in zip( objects['scores'], objects['rois'] ):
        if( score > 0.9 ):
            # parameters to be tuned
            area = ( roi[2] - roi[0] ) * ( roi[3] - roi[1] ) 
            lineSize = max( round( ( ( area ** 0.5 ) / 61.8 - 1 ) / 2 ) * 2 + 1, 3 )    # has to be odd
            blurSize = 5

            # clip to the region
            region = grey[ roi[0] : roi[2], roi[1] : roi[3] ]
            blur = cv2.medianBlur( region, blurSize )

            # threshold edges
            edge = cv2.adaptiveThreshold( blur, 255, cv2.ADAPTIVE_THRESH_MEAN_C, cv2.THRESH_BINARY, lineSize, blurSize )
            edge = 255 - edge
            
            # place regional edge to the whole picture
            edges[ roi[0] : roi[2], roi[1] : roi[3] ] = edge

    return edges


# get edges and enhanced image base on method
def getEdge( obj, cartoon, method ):
    edgeImage, enhancedImage = None, None

    if method == EDGES[0]:
        edgeImage = getAdaptiveEdge( obj, cartoon )
        enhancedImage = cv2.bitwise_and( cartoon, cartoon, mask = 255 - edgeImage )

    elif method == EDGES[1]:
        edgeImage = getCannyEdge( obj, cartoon )
        enhancedImage = cv2.bitwise_and( cartoon, cartoon, mask = 255 - edgeImage )

    elif method == EDGES[2]:
        edgeImage = getMorphEdge( obj, cartoon )
        enhancedImage = cv2.bitwise_and( cartoon, cartoon, mask = 255 - edgeImage )

    elif method == EDGES[3]:
        edgeImage = np.zeros( cartoon.shape[:2], np.uint8 )
        enhancedImage = cartoon

    return edgeImage, enhancedImage


# enhance objects in cartoon image
def enhance( imagePath, outputDir, edges, styles ):
    logger.info( f'Retrieving images...' )

    # get file name
    filename = imagePath.split(os.path.sep)[-1]

    # useful directory paths
    tempDir = os.path.join( outputDir, '.tmp')
    pngDir = os.path.join( tempDir, os.path.splitext( filename )[0] )

    logger.info( f'Generating {edges} edges with {styles} styles...' )
    for style in styles:
        # find cartoon and objects based on image type
        if filename.endswith( '.gif' ):
            # find cartoons from temporary folder
            cartoonPaths = []
            cartoonPaths.extend( glob.glob( os.path.join( pngDir, style, f"*.png" ) ) )
            cartoonPaths = sorted( cartoonPaths, key=lambda x: int(x.split('/')[-1].replace('.png', '')) )
            num_images = len( cartoonPaths )

            # find objects from temporary folder
            objPaths = []
            objPaths.extend( glob.glob( os.path.join( pngDir, "objects", f"*.npy" ) ) )
            objPaths = sorted( objPaths, key=lambda x: int(x.split('/')[-1].replace('.npy', '')) )
        else:
            # find cartoons from cartoon folder
            cartoonPaths = [ os.path.join( outputDir, style, filename ) ]

            # find objects from temporary folder
            objPaths = [ os.path.join( pngDir, "objects", "0.npy" ) ]

        # generate edges 
        for e in edges:
            logger.debug( f'Generating {e} edge with {style} style...' )
            for i, ( cPath, oPath ) in enumerate( zip( cartoonPaths, objPaths ) ):
                # get edges
                cartoon = cv2.imread( cPath )
                obj = np.load( oPath, allow_pickle = True )[()]
                edgeImage, enhancedImage = getEdge( obj, cartoon, e )

                # create directory and save edges
                edgeDir = os.path.join( pngDir, style, e )
                if not os.path.exists( edgeDir ):
                    os.makedirs( edgeDir )
                edgeFilename = f"{i + 1}.png"
                cv2.imwrite( os.path.join( edgeDir, edgeFilename ), edgeImage )


                # create directory and save enhanced image
                if filename.endswith( '.gif' ):
                    # save image to temporary folder
                    enhancedDir = os.path.join( pngDir, style, e, 'enhanced' )
                    if not os.path.exists( enhancedDir ):
                        os.makedirs( enhancedDir )
                    enhancedFilename = f"{i + 1}.png"
                    cv2.imwrite( os.path.join( enhancedDir, enhancedFilename ), enhancedImage )
                else:
                    # save image to directly to desired output folder
                    enhancedDir = os.path.join( outputDir, style, e )
                    if not os.path.exists( enhancedDir ):
                        os.makedirs( enhancedDir )
                    enhancedFilename = filename
                    cv2.imwrite( os.path.join( enhancedDir, enhancedFilename ), enhancedImage )

    return



def main():
    objects = detect( IMAGE_PATH )
    # r = np.load( 'test.npy', allow_pickle = True )[()]

    image = cv2.imread( IMAGE_PATH )
    cartoon = cv2.imread( CARTOON_PATH )
    cartoon = cv2.resize( cartoon, image.shape[1::-1] )
        
    # edges
    empty = np.ones( cartoon.shape[:2], np.uint8 )
    canny = getCannyEdge( objects, cartoon )
    morph = getMorphEdge( objects, cartoon )
    adapt = getAdaptiveEdge( objects, cartoon )

    # original with boxes
    original = cartoon.copy()
    for score, roi in zip( objects['scores'], objects['rois'] ):
        if( score > 0.9 ):
            original = cv2.rectangle( original, ( roi[1], roi[0] ), ( roi[3], roi[2] ), ( 0, 0, 255 ), 2 )

    # edge enhancement applied
    withCanny = cv2.bitwise_and( cartoon, cartoon, mask = 255 - canny )
    withMorph = cv2.bitwise_and( cartoon, cartoon, mask = 255 - morph )
    withAdapt = cv2.bitwise_and( cartoon, cartoon, mask = 255 - adapt )

    # configure display
    edges = np.concatenate( ( empty, canny, morph, adapt ), axis = 1 )
    edges = cv2.cvtColor( edges, cv2.COLOR_GRAY2BGR )
    out = np.concatenate( ( original, withCanny, withMorph, withAdapt ), axis = 1 )
    disp = np.concatenate( ( edges, out ), axis = 0 )

    # display
    cv2.imshow( 'original vs morph vs canny vs adaptive', disp )
    cv2.waitKey( 0 )
    cv2.destroyAllWindows()



if __name__ == '__main__':
    main()
