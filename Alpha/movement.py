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
    vision = None
    firstRun = True
    points = [] 
    current = ''
    key = None
    user = b'gAAAAABf470AGsKOJ65Ee9ZxZasRjABVUbdimwfivMloakcKoa20R_guknxp0K7xqYAbLD5IfZ9dUMJP77lKTM6oWRpYl17GHw=='
    pw = b'gAAAAABf470AeGuSrJmZEZrBzs8rJEQqiUDUoArQPNSkMJnlaKyxEknOUXvtvpWlLbTqBkq0SnEnYvjadV7gFI1sd7jtJJbImQ=='

    # Constructor
    def __init__(self, target='speedchat_bubble.png', haystack_wnd='Toontown Rewritten'):
        # Window Capture has default to TTR, else we choose from main.
        self.wincap = WindowCapture(window_name=haystack_wnd)
        self.vision = Vision(target)
        # WindowCapture.list_window_names()
        wincap.start()
        vision.start()

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
        # Decrypt our user name and pw. IF you want to continue,
        # generate a new key for your own credentials; or remove the encryption all together.
        self.key = self.load_key()
        f = Fernet(self.key)

        # Target is selectable from main file now.
        if(current == "Toontown Rewritten Launcher"):
            self.login()
 
        self.vision_target = Vision(target)
        # Will only seek best match.
        self.locator()
        
    def login(self):
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

        wincap.wait_hwnd(haystack_wnd)

        self.Vision = Vision("bear.png")
        # One click
        self.locator(False)

    def locator(self, multi=True):
        loop_time = time()
        if multi:
            while(True):
                 # if we don't have a screenshot yet, don't run the code below this point yet
                if wincap.screenshot is None:
                    continue
                
                # give vision the current screenshot to search for objects in
                vision.update(wincap.screenshot)

                # Display the images
                cv.imshow('Matches', output_image)

                # Take bot actions
                # Run the funtion in a thread that's separate from the main thread
                # so that the code here can continue while the bot performs its actions
                """
                if not is_bot_in_action:
                    is_bot_in_action = False
                    t = Thread(target=bot_actions, args=(rectangles,))
                    t.start()
                """

                # debug the loop rate - bad atm
                print('FPS {}'.format(1 / (time() - loop_time)))
                loop_time = time()

                # Press 'q' with the output window focused to exit.
                # Waits 1 ms every loop to process key presses
                if cv.waitKey(1) == ord('q'):
                    cv.destroyAllWindows()
                    break
        else:
            if wincap.screenshot is None:
                continue
            vision.update(wincap.screenshot)
            cv.imshow('Matches', output_image)

        print('Done.')

    # This function will be performed inside another thread
    def bot_actions(self, rectangles):
        if len(rectangles) > 0:
            # grab the first objects detection in the list and 
            # find the place to click
            targets = vision.get_click_points(rectangles)
            target = wincap.get_screen_position(targets[0])
            pyautogui.moveTo(x=target[0], y=target[1])
            pyautogui.click()
            sleep(3)
        
        # let the main loop know when this process is completed
        # global is_bot_in_action
        # is_bot_in_action = False

    # Encrypts our user/pw
    def write_key(self):
        # Generates a key and save it into a file
        self.key = Fernet.generate_key()
        with open("key.key", "wb") as key_file:
            key_file.write(self.key)

    def load_key(self):
        # Loads the key from the current directory named `key.key`
        return open("key.key", "rb").read()