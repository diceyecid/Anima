import numpy as np
import cv2
import mrcnn.visualize as mVisualize
import cartoonize
from detect import detect

IMAGE_PATH = './input/nyc.png'
CARTOON_PATH = './output/shinkai/nyc.png'

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
            blur = cv2.medianBlur( grey, blurSize )

            # threshold edges
            edge = cv2.adaptiveThreshold( region, 255, cv2.ADAPTIVE_THRESH_MEAN_C, cv2.THRESH_BINARY, lineSize, blurSize )
            edge = 255 - edge
            
            # place regional edge to the whole picture
            edges[ roi[0] : roi[2], roi[1] : roi[3] ] = edge

    return edges


# enhance objects in cartoon image
def enhance( objects, cartoon ):
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


def main():
    objs = detect( IMAGE_PATH )
    # r = np.load( 'test.npy', allow_pickle = True )[()]

    image = cv2.imread( IMAGE_PATH )
    cartoon = cv2.imread( CARTOON_PATH )
    cartoon = cv2.resize( cartoon, image.shape[1::-1] )

    cartoon = enhance( objs, cartoon )

if __name__ == '__main__':
    main()
