import cv2 as cv
import numpy as np
import time
# from PIL import ImageGrab
from windowcapture import WindowCapture
# from vision import findClickPositions
from vision import Vision
# Courtesy of Ben from LearnCodeByGaming
import pydirectinput as pdi
from cryptography.fernet import Fernet

class Movement:

    # Properties
    wincap = None
    vision_target = None
    firstRun = True
    points = [] 
    current = ''
    key = None
    user = b'gAAAAABf470AGsKOJ65Ee9ZxZasRjABVUbdimwfivMloakcKoa20R_guknxp0K7xqYAbLD5IfZ9dUMJP77lKTM6oWRpYl17GHw=='
    pw = b'gAAAAABf470AeGuSrJmZEZrBzs8rJEQqiUDUoArQPNSkMJnlaKyxEknOUXvtvpWlLbTqBkq0SnEnYvjadV7gFI1sd7jtJJbImQ=='

    # Constructor
    def __init__(self, target, haystack_wnd='Toontown Rewritten'):
        # Window Capture has default to TTR, else we choose from main.
        self.wincap = WindowCapture(window_name=haystack_wnd)
        # Previously, we had to use the object to call this function.
        # Now that it is static, we can call the class directly.
        # wincap.list_window_names()
        # WindowCapture.list_window_names()

        # check foreground window title
        current = self.wincap.title()

        """ 
        The Encryption Method I used:
            click.write_key()
            key = click.load_key()
            message1 = user.encode()
            print(message1) - bytes now
            message2 = pw.encode()
            print(message2)
            f = Fernet(key)
            encrypted1 = f.encrypt(message1)
            encrypted2 = f.encrypt(message2)

            print(encrypted1)
            print(encrypted2)
        """
        # Decrypt our user name and pw.
        key = self.load_key()
        f = Fernet(key)

        # Target is selectable from main file now.
        if(current == "Toontown Rewritten Launcher"):
            # Make TextBox Bigger
            self.vision_target = Vision('TextBox.png')
            
            # empty bits on bitmap, idk how they made the launcher
            # self.locator()
            # Just send input
            pdi.press(['tab'])
            time.sleep(0.05)
            pdi.typewrite(f.decrypt(self.user).decode())
            time.sleep(0.05)
            pdi.press(['tab'])
            time.sleep(0.05)
            pdi.typewrite(f.decrypt(self.pw).decode())  
            time.sleep(0.05)
            pdi.press(['enter'])
            time.sleep(0.05)
        else:
            self.vision_target = Vision(target)
            # Only find best match
            self.locator(multi=False)

    def locator(self, single=False, multi=True):
        loop_time = time()

        if not single:
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
                    if not self.firstRun:
                        bestMatch = self.vision_target.bestMatch()
                        self.points = self.vision_target.find(screenshot, bestMatch, 'rectangles')
                    else:    
                        self.points = self.vision_target.find(screenshot, 0.9, 'rectangles')
                        self.firstRun = False
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
        
        # For single uses
        else:
            screenshot = self.wincap.get_screenshot()

            if not multi:
                if not self.firstRun:
                    bestMatch = self.vision_target.bestMatch()
                    self.points = self.vision_target.find(screenshot, bestMatch, 'rectangles')
                else:    
                    self.points = self.vision_target.find(screenshot, 0.9, 'rectangles')
                    self.firstRun = False
            else:
                self.points = self.vision_target.find(screenshot, 0.9, 'rectangles')

            while(True):
                if cv.waitKey(1) == ord('q'):
                    cv.destroyAllWindows()
                    break

        print('Done.')

    # Encrypts our user/pw
    def write_key(self):
        # Generates a key and save it into a file
        self.key = Fernet.generate_key()
        with open("key.key", "wb") as key_file:
            key_file.write(self.key)

    def load_key(self):
        # Loads the key from the current directory named `key.key`
        return open("C:\Users\virul\Documents\Projects\Botting\PetTrainer\Stage6\key.key", "rb").read()