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
from scipy.signal import correlate

IO_ERROR = 2

SUCCESS = 0

DEF_IMAGE_NAME_A = 'im_1.bmp'

DEF_IMAGE_NAME_B = 'im_2.bmp'



def warning(*objs):
    """Writes a message to stderr."""
    print("WARNING: ", *objs, file=sys.stderr)

def load_image( infilename ) :
    img = Image.open( infilename )
    img.load()
    image_data = np.asarray( img, dtype="int32" )
    return image_data

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
    shift = np.zeros(len(image_a_segments))
    for i in range(len(image_a_segments)):
        y1 = image_a_segments[i]
        y2 = image_b_segments[i]
        nsamples = y1.shape[0]
        xcorr = correlate(y1, y2)
        d_shift = np.arange(1-nsamples, nsamples)
        shift[i] = d_shift[xcorr.argmax()]
    return shift


def piv_analysis(args):
    """
    Calculate the 1D velocity profile based on a pair of images.
    Horizontal direction: flow direction.
    Vertical direction: velocity gradient direction.
    Upper boundary of image: upper static wall.
    Lower boundary of image: lower moving wall.

    Parameters
    ----------
    args : input argument
    args.image_a & args.image_b : a image pair in the form of 2D Numpy array
    args.division_pixel : Thickness (number of pixels) of horizontal stripes

    Returns
    -------
    velocity : velocity versus y position
    """
    image_path_a = args.image_file[0]
    image_path_b = args.image_file[1]
    image_a = load_image(image_path_a)
    image_b = load_image(image_path_b)
    division_pixel = args.division_pixel
    image_a_segments, y_position = divid_image(image_a, division_pixel)
    image_b_segments = divid_image(image_b, division_pixel)[0]
    disp_profile = x_corr(image_a_segments, image_b_segments)
    print(disp_profile)
    np.savetxt('im1.txt', image_a_segments[10])
    np.savetxt('im2.txt', image_b_segments[10])


    return None


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
                        default=[DEF_IMAGE_NAME_A, DEF_IMAGE_NAME_B], nargs='*')

    parser.add_argument("-d", "--division_pixel", type=int,help="Thickness (number of pixels) of horizontal stripes",
                        default=5)

    # parser.add_argument("-n", "--no_attribution", help="Whether to include attribution",
    #                    action='store_false')
    args = None
    try:
        args = parser.parse_args(argv)
    except IOError as e:
        warning("Problems reading file:", e)
        parser.print_help()
        return args, IO_ERROR
    return args, SUCCESS


def main(argv=None):
    args, ret = parse_cmdline(argv)
    if ret != SUCCESS:
        return ret
    piv_analysis(args)
    return SUCCESS  # success


if __name__ == "__main__":
    status = main()
    sys.exit(status)
