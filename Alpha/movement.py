# Skeleton code courtesy of Ben from LearnCodeByGaming

import cv2 as cv
import numpy as np
from time import sleep, time
from windowcapture import WindowCapture
from vision import Vision
from bot import TTRBot, BotState
import pydirectinput as pdi
from cryptography.fernet import Fernet

class Movement:

    # Properties
    DEBUG = True
    wincap = None
    vision = None
    bot = None
    firstRun = True
    points = [] 
    current = ''
    key = None
    user = b'gAAAAABf470AGsKOJ65Ee9ZxZasRjABVUbdimwfivMloakcKoa20R_guknxp0K7xqYAbLD5IfZ9dUMJP77lKTM6oWRpYl17GHw=='
    pw = b'gAAAAABf470AeGuSrJmZEZrBzs8rJEQqiUDUoArQPNSkMJnlaKyxEknOUXvtvpWlLbTqBkq0SnEnYvjadV7gFI1sd7jtJJbImQ=='

    # Constructor
    def __init__(self, target='speedchat_bubble.png', haystack_wnd='Toontown Rewritten', tooltip='tooltip.png'):
        # Window Capture has default to TTR, else we choose from main.
        self.wincap = WindowCapture(window_name=haystack_wnd)
        
        # WindowCapture.list_window_names()
        # check foreground window title
        current = self.wincap.title()

        # Target is selectable from main file now.
        if(current == "Toontown Rewritten Launcher"):
            self.login()
        else:
            self.vision = Vision(target)
            self.bot = TTRBot((self.wincap.offset_x, self.wincap.offset_y), (self.wincap.w, self.wincap.h))

        

        # When giving our property objects new parameters
        # we must stop and start again, otherwise "stopped"
        # property gets reset to True.
        self.wincap.start()
        self.vision.start()
        self.bot.start()

        # Will only seek best match.
        self.locator()
        
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
    def login(self):
        # empty bits on bitmap, idk how they made the launcher
        # self.locator()
        # Just send input
        # Decrypt our user name and pw. IF you want to continue,
        # generate a new key for your own credentials; or remove the encryption all together.
        self.key = self.load_key()
        f = Fernet(self.key)
        pdi.press(['tab'])
        sleep(0.05)
        pdi.typewrite(f.decrypt(self.user).decode())
        sleep(0.05)
        pdi.press(['tab'])
        sleep(0.05)
        pdi.typewrite(f.decrypt(self.pw).decode())  
        sleep(0.05)
        pdi.press(['enter'])
        sleep(0.05)

        # Wait for TTR
        self.wincap.wait_hwnd()
        sleep(10.5)
        pdi.press(['up'])
        sleep(4.5)
        self.wincap = WindowCapture("Toontown Rewritten")
        self.vision = Vision("bear.png")
        self.bot = TTRBot((self.wincap.offset_x, self.wincap.offset_y), (self.wincap.w, self.wincap.h), 'tooltip_bear.png')

    def locator(self):
        loop_time = time()
        while(True):
                # if we don't have a screenshot yet, don't run the code below this point yet
            if self.wincap.screenshot is None:
                continue
            
            # give vision the current screenshot to search for objects in
            self.vision.update(self.wincap.screenshot)

            # update the bot with the data it needs right now
            if self.bot.state == BotState.INITIALIZING:
                # while bot is waiting to start, go ahead and start giving it some targets to work
                # on right away when it does start
                targets = self.vision.get_click_points(self.vision.rectangles)
                self.bot.update_targets(targets)
            elif self.bot.state == BotState.SEARCHING:
                # when searching for something to click on next, the bot needs to know what the click
                # points are for the current detection results. it also needs an updated screenshot
                # to verify the hover tooltip once it has moved the mouse to that position
                targets = self.vision.get_click_points(self.vision.rectangles)
                self.bot.update_targets(targets)
                self.bot.update_screenshot(self.wincap.screenshot)
            elif self.bot.state == BotState.STILL:
                # nothing is needed while we wait for the mining to finish
                pass

            if self.DEBUG:
                # draw the detection results onto the original image
                detection_image = self.vision.draw_rectangles(self.wincap.screenshot, self.vision.rectangles)
                # display the images
                if detection_image:
                    cv.imshow('Matches', detection_image)

            # Take bot actions
            # Run the funtion in a thread that's separate from the main thread
            # so that the code here can continue while the bot performs its actions
            # Now a part of vision!
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
            key = cv.waitKey(1)
            if key == ord('q'):
                wincap.stop()
                vision.stop()
                bot.stop()
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
        return open("key.key", "rb").read()