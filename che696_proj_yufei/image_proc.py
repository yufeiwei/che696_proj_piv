#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
image_proc.py
Particle image velocimetry for simple shear flows

Handles the primary functions
"""

import sys
import argparse
import numpy as np
from PIL import Image
import os
import matplotlib.pyplot as plt

SUCCESS = 0
INVALID_DATA = 1
IO_ERROR = 2
NUMBER_OF_IMAGE = 3

DEF_IMAGE_NAME_A = 'sample_im1.bmp'

DEF_IMAGE_NAME_B = 'sample_im2.bmp'

def warning(*objs):
    """Writes a message to stderr."""
    print("WARNING: ", *objs, file=sys.stderr)

def plot_piv(base_f_name, piv_results):
    """
    Make a plot of the PIV results

    :param base_f_name: str of base output name (without extension)
    :param piv_results: piv results, numpy array, with shape (y_position, displacement)
    :return: save a png file
    """
    plt.plot(piv_results[:,0], piv_results[:,1], 'bs')
    plt.title('PIV results')
    plt.xlabel('Y position (pixel)')
    plt.ylabel('Displacement (pixel)')
    out_name = base_f_name + '.png'
    plt.savefig(out_name)
    print("Wrote file: {}".format(out_name))

def load_image( infilename ) :
    """
    Load image into Numpy array

    :param infilename: input file name
    :return: image_data : image in the form of Numpy array
    """
    try:
        img = Image.open( infilename )
        img.load()
        image_data = np.asarray( img, dtype="int32" )
    except OSError as e:
        warning("Read invalid image:", e)
        return None, e
    return image_data, SUCCESS

def divid_image(image, division_pixel):
    """
    Cut a image into horizontal stripes and compress them into 1D brighness fluctuation profile
    
    Parameters
    ------------
    image : image as a 2D Numpy array
    division_pixel : height of individual stripes (unit, pixels)

    Returns
    ------------
    image_segments : a list a image segments
    y_position : position of image stripes
    """
    height = image.shape[0]
    index_divid = np.arange(0, height-1, division_pixel)
    image_segments = []
    y_position = []
    if index_divid[-1] != height - 1:
        index_divid = np.append(index_divid, height - 1)

    num_stripes = index_divid.size - 1
    for i in range(num_stripes):
        index_a = index_divid[i]
        index_b = index_divid[i + 1]
        y_position.append((index_a + index_b)/2.0)
        stripe = np.mean(image[index_a:index_b, :], axis=0)
        stripe -= stripe.mean(); stripe /= stripe.std()
        image_segments.append(stripe)
    return image_segments, y_position

def x_corr(image_a_segments, image_b_segments):
    """
    Calculate the displacement profile.

    :param image_a_segments: Horizontal stripes from image 1
    :param image_b_segments: Horizontal stripes from image 2
    :return: shift : displacement profile
    """
    import warnings
    warnings.filterwarnings("ignore")
    from scipy.signal import correlate
    shift = np.zeros(len(image_a_segments))
    for i in range(len(image_a_segments)):
        y1 = image_a_segments[i]
        y2 = image_b_segments[i]
        nsamples = y1.shape[0]
        xcorr = correlate(y1, y2)
        d_shift = np.arange(1-nsamples, nsamples)
        shift[i] = -d_shift[xcorr.argmax()]
    return shift


def piv_analysis(image_a_path, image_b_path, division_pixel):
    """
    Calculate the 1D velocity profile based on a pair of images.
    Horizontal direction: flow direction.
    Vertical direction: velocity gradient direction.
    Upper boundary of image: upper static wall.
    Lower boundary of image: lower moving wall.

    Parameters
    ----------
    image_a_path : path of image 1
    image_b_path : path of image 2
    division_pixel : Thickness (number of pixels) of horizontal stripes

    Returns
    -------
    piv_result : displacement profile (column 2) versus y position (column 1)
    """
    image_a, ret_a = load_image(image_a_path)
    image_b, ret_b = load_image(image_b_path)
    if (ret_a!=SUCCESS) or (ret_b!=SUCCESS):
        return IO_ERROR
    if not image_a.shape == image_b.shape:
        warning('Image 1 and image 2 have different sizes')
        return INVALID_DATA
    image_a_segments, y_position = divid_image(image_a, division_pixel)
    y_position = np.asarray(y_position)
    image_b_segments = divid_image(image_b, division_pixel)[0]
    disp_profile = x_corr(image_a_segments, image_b_segments)
    # print(disp_profile)
    piv_results = np.vstack((y_position, disp_profile))
    return piv_results.T


def parse_cmdline(argv):
    """
    Returns the parsed argument list and return code.
    `argv` is a list of arguments, or `None` for ``sys.argv[1:]``.
    """
    if argv is None:
        argv = sys.argv[1:]

    # initialize the parser object:
    parser = argparse.ArgumentParser()

    # print([DEF_IMAGE_NAME_A, DEF_IMAGE_NAME_B])

    parser.add_argument("-m", "--image_file", help="The location of the image files",
                        default=[DEF_IMAGE_NAME_A, DEF_IMAGE_NAME_B], nargs=2)

    parser.add_argument("-d", "--division_pixel", type=int,help="Thickness (number of pixels) of horizontal stripes",
                        default=5)

    # parser.add_argument("-n", "--no_attribution", help="Whether to include attribution",
    #                    action='store_false')
    args = None
    args = parser.parse_args(argv)
    image1_none = not os.path.isfile(args.image_file[0])
    image2_none = not os.path.isfile(args.image_file[1])
    if image1_none or image2_none:
        warning("Either {} or {} does not exist".format(args.image_file[0], args.image_file[1]))
        parser.print_help()
        return args, IO_ERROR
    return args, SUCCESS

def main(argv=None):
    args, ret = parse_cmdline(argv)
    if ret != SUCCESS:
        return ret

    image_a_path = args.image_file[0]
    image_b_path = args.image_file[1]
    division_pixel = args.division_pixel
    piv_results = piv_analysis(image_a_path, image_b_path, division_pixel)
    image_a_name = os.path.basename(image_a_path)
    image_b_name = os.path.basename(image_b_path)
    name_p1 = os.path.splitext(image_a_name)[0]
    name_p2 = os.path.splitext(image_b_name)[0]
    base_f_name = 'piv_results_' + name_p1 + '_' + name_p2
    out_name = base_f_name + '.csv'
    try:
        np.savetxt(out_name, piv_results, delimiter=',')
        print("Wrote file: {}".format(out_name))
    except ValueError as e:
        warning("Data cannot be written to file:", e)
        return INVALID_DATA
    plot_piv(base_f_name, piv_results)
    return SUCCESS  # success

if __name__ == "__main__":
    status = main()
    sys.exit(status)
