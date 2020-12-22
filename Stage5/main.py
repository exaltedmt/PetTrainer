import cv2 as cv
import numpy as np
import os
from time import time
# from PIL import ImageGrab
from windowcapture import WindowCapture
# from vision import findClickPositions
from vision import Vision
# Change the working directory to the folder this script is in.
os.chdir(os.path.dirname(os.path.abspath(__file__)))

wincap = WindowCapture('Toontown Rewritten')
# Previously, we had to use the object to call this function.
# Now that it is static, we can call the class directly.
# wincap.list_window_names()
WindowCapture.list_window_names()

# Initialize the Vision clas
vision_speedchat = Vision('speedchat_bubble.png')

loop_time = time()
points = []
firstRun = True

while(True):
    
    # screenshot = None
    # screenshot = pyautogui.screenshot()
    # cv.imshow is not compatable with pyautogui ss format.
    # so we use numpy.
    # screenshot = ImageGrab.grab()
    # screenshot = np.array(screenshot)
    # Reversing the RGB values
    # screenshot = screenshot[:, :, ::-1].copy()
    # More self-documenting version below:
    # screenshot = cv.cvtColor(screenshot, cv.COLOR_RGB2BGR)
    # screenshot = window_capture()
    
    screenshot = wincap.get_screenshot()
    # Processed Image shown instead of raw screenshot!
    # We show image in our find() function.
    # cv.imshow('Computer Vision', screenshot)
    # findClickPositions('', screenshot, threshold=0.72, debug_mode='points')
    
    # Show the best match only. Must run find() at least once however.
    if not firstRun:
        bestMatch = vision_speedchat.bestMatch()
        points = vision_speedchat.find(screenshot, bestMatch, 'rectangles')
    else:    
        points = vision_speedchat.find(screenshot, 0.72, 'rectangles')
        firstRun = False

    # debug the loop rate - bad atm
    print('FPS {}'.format(1 / (time() - loop_time)))
    loop_time = time()

    # Press 'q' with the output window focused to exit.
    # Waits 1 ms every loop to process key presses
    if cv.waitKey(1) == ord('q'):
        cv.destroyAllWindows()
        break

print('Done.')