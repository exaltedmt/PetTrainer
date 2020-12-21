import cv2 as cv
import numpy as np
import os

# Change the working directory to the folder this script is in.
os.chdir(os.path.dirname(os.path.abspath(__file__)))

# Can use IMREAD flags to do different pre-processing of image files.
# Like making them grayscale or reducing the size.
# https://docs.opencv.org/4.2.0/d4/da8/group__imgcodecs.html
haystack_img = cv.imread('TTGUI.png', cv.IMREAD_UNCHANGED)
needle_img = cv.imread('speedchat_bubble.png', cv.IMREAD_UNCHANGED)

# There are 6 comparison methods to choose from:
# TM_CCOEFF, TM_CCOEFF_NORMED, TM_CCORR, TM_CCORR_NORMED,
# TM_SQDIFF, TM_SQDIFF_NORMED
# You can see the differences at a glance here:
# https://docs.opencv.org/master/d4/dc6/tutorial_py_template_matching.html
# Note that the values are inverted for TM_SQDIFF and TM_SQDIFF_NORMED
result = cv.matchTemplate(haystack_img, needle_img, cv.TM_CCOEFF_NORMED)
print(result)

threshold = 0.72
# We get the coordinates of the values under a given threshold
locations = np.where(result >= threshold)
# we can zip these values up into tuple values
locations = list(zip(*locations[::-1]))
print(locations)

if locations:
    print('Found speedchat button.')

    # Rectangle details
    line_color = (0, 255, 0)
    line_type = cv.LINE_4
    # Get dimensions of the needle image
    needle_w = needle_img.shape[1]
    needle_h = needle_img.shape[0]

    # Loop over all locations and draw rectangle
    for loc in locations:
        # Determine the box positions
        top_left = loc
        bottom_right = (top_left[0] + needle_w, top_left[1] + needle_h)

        # Draw the Box
        cv.rectangle(
            haystack_img,
            top_left,
            bottom_right,
            line_color,
            line_type
        )

    cv.imshow('Matches', haystack_img)
    cv.waitKey()
    # cv.imwrite('result.png', haystack_img)
else:
    print('Speedchat button not found.')
