import cv2 as cv
import numpy as np
import os
from movement import Movement

# Change the working directory to the folder this script is in.
os.chdir(os.path.dirname(os.path.abspath(__file__)))

# Initialize the Vision class
# If we're at login screen, enter credentials.

click = Movement(target='speedchat_bubble.png')

exit()