####################
# This file is entrance file to execute our method


#---------- imports ----------#


import os
import sys
import PIL
import glob
import imageio
import logging
import argparse
from tqdm import tqdm
from datetime import datetime
from cartoonize import main as cartoonize
from detect import main as detect
from enhance import main as enhance


#---------- constants ----------# 


STYLES = ['shinkai', 'hayao', 'hosoda', 'paprika']
EDGES = ['adaptive', 'canny', 'morph', 'original']
VALID_EXTENSIONS = ['jpg', 'png', 'gif', 'JPG']


#----------configuration arguments ----------#


parser = argparse.ArgumentParser(description='transform real world images to specified cartoon style(s)')
parser.add_argument('--styles', nargs='+', default=[STYLES[0]],
                    help='specify (multiple) cartoon styles which will be used to transform input images.')
parser.add_argument('--all_styles', action='store_true',
                    help='set true if all styled results are desired')
parser.add_argument('--edges', nargs='+', default=[EDGES[0]],
                    help='specify (multiple) edge styles which will be used to transform input images.')
parser.add_argument('--all_edges', action='store_true',
                    help='set true if all edged results are desired')
parser.add_argument('--input', type=str, default='input',
                    help='image or directory with images to be transformed')
parser.add_argument('--output_dir', type=str, default='output',
                    help='directory where transformed images are saved')
parser.add_argument('--batch_size', type=int, default=1,
                    help='number of images that will be transformed in parallel to speed up processing. '
                         'higher value like 4 is recommended if there are gpus.')
parser.add_argument('--ignore_gif', action='store_true',
                    help='transforming gif images can take long time. enable this when you want to ignore gifs')
parser.add_argument('--overwrite', action='store_true',
                    help='enable this if you want to regenerate outputs regardless of existing results')
parser.add_argument('--skip_comparison', action='store_true',
                    help='enable this if you only want individual style result and to save processing time')
parser.add_argument('--comparison_view', type=str, default='smart',
                    choices=['smart', 'horizontal', 'vertical', 'grid'],
                    help='specify how input images and transformed images are concatenated for easier comparison')
parser.add_argument('--gif_frame_frequency', type=int, default=1,
                    help='how often should a frame in gif be transformed. freq=1 means that every frame '
                         'in the gif will be transformed by default. set higher frequency can save processing '
                         'time while make the transformed gif less smooth')
parser.add_argument('--max_num_frames', type=int, default=100,
                    help='max number of frames that will be extracted from a gif. set higher value if longer gif '
                         'is needed')
parser.add_argument('--keep_original_size', action='store_true',
                    help='by default the input images will be resized to reasonable size to prevent potential large '
                         'computation and to save file sizes. Enable this if you want the original image size.')
parser.add_argument('--max_resized_height', type=int, default=300,
                    help='specify the max height of a image after resizing. the resized image will have the same'
                         'aspect ratio. Set higher value or enable `keep_original_size` if you want larger image.')
parser.add_argument('--convert_gif_to_mp4', action='store_true',
                    help='convert transformed gif to mp4 which is much more smaller and easier to share. '
                         '`ffmpeg` need to be installed at first.')
parser.add_argument('--logging_lvl', type=str, default='info',
                    choices=['debug', 'info', 'warning', 'error', 'critical'],
                    help='logging level which decide how verbosely the program will be. set to `debug` if necessary')
parser.add_argument('--debug', action='store_true',
                    help='show the most detailed logging messages for debugging purpose')
parser.add_argument('--show_tf_cpp_log', action='store_true')

args = parser.parse_args()


#---------- derived constants ----------#


TEMPORARY_DIR = os.path.join( f'{args.output_dir}', '.tmp' )


#---------- logger configs ----------#


logger = logging.getLogger('Driver')
logger.propagate = False
log_lvl = {'debug': logging.DEBUG, 'info': logging.INFO,
           'warning': logging.WARNING, 'error': logging.ERROR,
           'critical': logging.CRITICAL}
if args.debug:
    logger.setLevel(logging.DEBUG)
else:
    logger.setLevel(log_lvl[args.logging_lvl])
formatter = logging.Formatter(
    '[%(asctime)s] [%(name)s] [%(levelname)s] %(message)s', '%Y-%m-%d %H:%M:%S')
stdhandler = logging.StreamHandler(sys.stdout)
stdhandler.setFormatter(formatter)
logger.addHandler(stdhandler)

if not args.show_tf_cpp_log:
    os.environ['TF_CPP_MIN_LOG_LEVEL'] = '3'


#---------- functions ----------#


# handles arguments passed from other function
def handle_args( funArgs ):
    for key in vars( args ):
        if key in funArgs:
            args[key] = funArgs[key]
    return


def preprocess( imagePath ):
    logger.debug(f"`{imagePath}` is an image, preprocess the image from it...")

    # determine where to save
    filename = imagePath.split(os.path.sep)[-1]
    saveDir = os.path.join(TEMPORARY_DIR, os.path.splitext( filename )[0] )
    if not os.path.exists(saveDir):
        logger.debug(f"Creating temporary folder: {saveDir} for storing preprocessed image...")
        os.makedirs(saveDir)

    # preprocess
    input_image = PIL.Image.open( imagePath ).convert("RGB")
    if not args.keep_original_size:
        width, height = input_image.size
        aspect_ratio = width / height
        resized_height = min(height, args.max_resized_height)
        resized_width = int(resized_height * aspect_ratio)
        if width != resized_width:
            logger.debug(f"resized ({width}, {height}) to: ({resized_width}, {resized_height})")
            input_image = input_image.resize((resized_width, resized_height))
    input_image.save( os.path.join( saveDir, filename ) )

    return input_image


def convert_gif_to_png(gif_path):
    logger.debug(f"`{gif_path}` is a gif, extracting png images from it...")
    gif_filename = gif_path.split(os.path.sep)[-1].replace(".gif", "")
    image = PIL.Image.open(gif_path)
    # palette = image.getpalette()
    png_paths = list()
    i = 0

    png_dir = os.path.join(TEMPORARY_DIR, gif_filename)
    if not os.path.exists(png_dir):
        logger.debug(f"Creating temporary folder: {png_dir} for storing separated pngs from gif...")
        os.makedirs(png_dir)

    prev_generated_png_paths = glob.glob(png_dir + '/*.png')
    if prev_generated_png_paths:
        return prev_generated_png_paths

    if( not args.ignore_gif ):
        num_processed_frames = 0
        logger.debug("Generating png images...")
        try:
            while num_processed_frames < args.max_num_frames:
                # image.putpalette(palette)
                extracted_image = PIL.Image.new("RGBA", image.size)
                extracted_image.paste(image)

                if not args.keep_original_size:
                    width, height = extracted_image.size
                    aspect_ratio = width / height
                    resized_height = min(height, args.max_resized_height)
                    resized_width = int(resized_height * aspect_ratio)
                    if width != resized_width:
                        logger.debug(f"resized ({width}, {height}) to: ({resized_width}, {resized_height})")
                        extracted_image = extracted_image.resize((resized_width, resized_height))

                if i % args.gif_frame_frequency == 0:
                    png_filename = f"{i + 1}.png"
                    png_path = os.path.join(png_dir, png_filename)
                    extracted_image.save(png_path)
                    png_paths.append(png_path)
                    num_processed_frames += 1

                image.seek(image.tell() + 1)
                i += 1

        except EOFError:
            pass  # end of sequence

    else:
        # image.putpalette(palette)
        extracted_image = PIL.Image.new("RGBA", image.size)
        extracted_image.paste(image)

        if not args.keep_original_size:
            width, height = extracted_image.size
            aspect_ratio = width / height
            resized_height = min(height, args.max_resized_height)
            resized_width = int(resized_height * aspect_ratio)
            if width != resized_width:
                logger.debug(f"resized ({width}, {height}) to: ({resized_width}, {resized_height})")
                extracted_image = extracted_image.resize((resized_width, resized_height))


    logger.debug(f"Number of {len(png_paths)} png images were generated at {png_dir}.")
    return png_paths


#---------- main execution ----------#


def main():
    start = datetime.now()

    # create output folder
    logger.info( f'Transformed images will be saved to `{args.output_dir}` folder.' )
    if not os.path.exists( args.output_dir ):
        os.makedirs( args.output_dir )

    # create temporary folder which will be deleted after transformations
    if not os.path.exists( TEMPORARY_DIR ):
        os.makedirs( TEMPORARY_DIR )

    # decide what styles to used in this execution
    styles = STYLES if args.all_styles else args.styles
    args.styles = styles

    # decide what edges to used in this execution
    edges = EDGES if args.all_edges else args.edges
    args.edges = edges

    # get all image paths
    imagePaths = []
    if os.path.isdir( args.input ):
        for ext in VALID_EXTENSIONS:
            imagePaths.extend( glob.glob( os.path.join(args.input, f'*.{ext}' ) ) )
        logger.info(f'Preparing to transform {len(imagePaths)} images from `{args.input}` directory...')
    else:
        imagePaths.append( args.input )
        logger.info(f'Preparing to transform `{args.input}` file...')

    # transform each image
    progressBar = tqdm( imagePaths, desc='Transforming' )
    for imagePath in progressBar:
        filename = imagePath.split( os.path.sep )[-1]
        progressBar.set_postfix( File = filename )

        # preprocess
        if( filename.endswith(".gif") ):
            convert_gif_to_png( imagePath )
        else:
            preprocess( imagePath )

        detect( imagePath, args.output_dir )
        cartoonize( imagePath, args )
        enhance( imagePath, args.output_dir, args.edges, args.styles )

        # construct and save gif
        if( filename.endswith(".gif") ):
            for s in args.styles:
                for e in args.edges:
                    # find enhanced cartoon images
                    pngDir = os.path.join( TEMPORARY_DIR, os.path.splitext( filename )[0] )
                    enhancedDir = os.path.join( pngDir, s, e, 'enhanced' )
                    enhancedPaths = []
                    enhancedPaths.extend( glob.glob( os.path.join( enhancedDir, f"*.png" ) ) )

                    # determine path to save
                    saveDir = os.path.join( args.output_dir, s, e )
                    if not os.path.exists( saveDir ):
                        os.makedirs( saveDir )
                    savePath = os.path.join( saveDir, filename )

                    with imageio.get_writer( savePath, mode='I' ) as writer:
                        file_names = sorted( enhancedPaths, key=lambda x: int(x.split('/')[-1].replace('.png', '')) )
                        logger.debug(f"Combining {len(file_names)} png images into {savePath}...")
                        for i, fn in enumerate(file_names):
                            image = imageio.imread(fn)
                            writer.append_data(image)

    # ending
    progressBar.close()
    elapsed = datetime.now() - start
    logger.info( f"Total processing time: {elapsed}" )


    return


if __name__ == '__main__':
    main()
