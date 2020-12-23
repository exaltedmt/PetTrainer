import cv2 as cv
import numpy as np
from time import time
# from PIL import ImageGrab
from windowcapture import WindowCapture
# from vision import findClickPositions
from vision import Vision

class Movement:

    # Properties
    wincap = None
    vision_target = None
    loop_time = time()
    firstRun = True
    points = [] 
    current = ''

    # Constructor
    def __init__(self, target, haystack_wnd='Toontown Rewritten'):
        # Previously, we had to use the object to call this function.
        # Now that it is static, we can call the class directly.
        # wincap.list_window_names()
        WindowCapture.list_window_names()

        # Window Capture has default to TTR, else we choose from main.
        self.wincap = WindowCapture(window_name=haystack_wnd)

        # check foreground window title
        current = self.wincap.title()

        # Target is selectable from main file now.
        if(current == "Toontown Launcher v1.2.5"):
            self.vision_target = Vision('TextBox.png')
            locator_loop()
        else:
            self.vision_target = Vision(target)
            # Only find best match
            locator_loop(False)
            self.vision_target.init_control_gui()

    def locator_loop(self, multi=True):
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
            
            screenshot = self.wincap.get_screenshot()
            # Processed Image shown instead of raw screenshot!
            # We show image in our find() function.
            # cv.imshow('Computer Vision', screenshot)
            # findClickPositions('', screenshot, threshold=0.72, debug_mode='points')
            
            # Show the best match only. Must run find() at least once however.
            if not multi:
                if not firstRun:
                    bestMatch = self.vision_target.bestMatch()
                    self.points = self.vision_target.find(screenshot, bestMatch, 'rectangles')
                else:    
                    self.points = self.vision_target.find(screenshot, 0.9, 'rectangles')
                    firstRun = False
            else:
                self.points = self.vision_target.find(screenshot, 0.9, 'rectangles')

            # debug the loop rate - bad atm
            print('FPS {}'.format(1 / (time() - loop_time)))
            loop_time = time()

            # Press 'q' with the output window focused to exit.
            # Waits 1 ms every loop to process key presses
            if cv.waitKey(1) == ord('q'):
                cv.destroyAllWindows()
                break

        print('Done.')