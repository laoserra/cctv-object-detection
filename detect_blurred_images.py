#!/usr/bin/env python3

import sys
import numpy as np
from skimage import io
from scipy.stats import mode

PIXEL_THRESHOLD = 0.9  # must have 90% or more pixels the same colour
RGB_THRESHOLD = 30  # to be the same colour, rgb value = +-30 (0-255)


def camera_in_use(image):
    """Detects if a camera is being used by GOC.

    Uses image size for this task, as agreed with GCC.
    """
    height, width = image.shape[:2]
    return (1 if (height == 367 and width == 550) else 0)


def detect_one_color(p_thres, rgb_thres, image):
    """Detects one colour images."""
    # Reshape the image to 2D
    # we only need RGB values
    flat_image = image.reshape(-1, 3)
    # Calculate the mode (dominant color)
    # returns the dominant RGB array
    # and the count for each element in the array
    dominant_color, count = mode(flat_image, axis=0, keepdims=False)
    # Set a threshold for the number of similar pixels
    threshold = p_thres * flat_image.shape[0]  # 90% of the image
    # Calculate Euclidean distance between each pixel and dominant color
    # Euclidian distance is the norm of subtracting dominant color vector
    # from each image pixel
    distances = np.linalg.norm(flat_image - dominant_color, axis=1)
    # Count the number of pixels that are close to the dominant color
    # this is an integer corresponding to the sum of the boolean elements
    # in the array
    # consequently, counts the number of pixels which are within the threshold
    close_to_dominant = np.sum(distances < rgb_thres)
    # Check if it's mostly one color based on the threshold
    mostly_one_color = close_to_dominant > threshold

    return (2 if mostly_one_color else 0)


def main(image_path):
    image = io.imread(image_path)
    one_color = detect_one_color(PIXEL_THRESHOLD, RGB_THRESHOLD, image)
    camera = camera_in_use(image)
    functions = [one_color, camera]
    var = 0
    for fn in functions:
        if fn:
            var = fn
            break
    return var


if __name__ == '__main__':
    print(main(sys.argv[1]))
