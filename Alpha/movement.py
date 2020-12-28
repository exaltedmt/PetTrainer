# Skeleton code courtesy of Ben from LearnCodeByGaming

import cv2 as cv
import numpy as np
from time import sleep, time
from windowcapture import WindowCapture
from vision import Vision
from bot import TTRBot, BotState
import pydirectinput as pdi
from cryptography.fernet import Fernet
import win32gui

class Command:
    OPTION = 0
    PETS = 1
    GOOD = 2
    TRICKS = 3
    TRICK = 4
    SCRATCH = 5
    FEED = 6
    TIRED = 7
    EXCITED = 8

class Movement:

    # Properties
    DEBUG = True
    wincap = None
    vision = None
    bot = None
    haystack_wnd = None
    targetList = []
    tooltipList = []
    loginList = []
    state = 0
    isGood = False
    loggingIn = False
    points = [] 
    current = ''
    key = None
    user = b'gAAAAABf470AGsKOJ65Ee9ZxZasRjABVUbdimwfivMloakcKoa20R_guknxp0K7xqYAbLD5IfZ9dUMJP77lKTM6oWRpYl17GHw=='
    pw = b'gAAAAABf470AeGuSrJmZEZrBzs8rJEQqiUDUoArQPNSkMJnlaKyxEknOUXvtvpWlLbTqBkq0SnEnYvjadV7gFI1sd7jtJJbImQ=='

    # Constructor
    def __init__(self, target='doodle.png', tooltip='doodle.png', haystack_wnd='Toontown Rewritten'):

        self.haystack_wnd = haystack_wnd
        # Our list of commands to execute in sequence
        self.targetList = [
            "targets/speedchat_bubble.png",
            "targets/Pets.png",
            "targets/good.png",
            "targets/Tricks.png",
            "targets/Play_dead.png",
            "targets/Scratch.png",
            "targets/Feed.png",
            "targets/Tired.png",
            "targets/Excited.png"
        ]

        self.tooltipList = [
            "tooltips/tooltip.png",
            "tooltips/Pets_tt.png",
            "tooltips/good_tt.png",
            "tooltips/Tricks_tt.png",
            "tooltips/Play_dead_tt.png",
            "tooltips/Scratch_tt.png",
            "tooltips/Feed_tt.png",
            "tooltips/Tired_tt.png",
            "tooltips/Excited_tt.png"
        ]

        # Window Capture has default to TTR, else we choose from main.
        self.wincap = WindowCapture(window_name=haystack_wnd)
        
        # WindowCapture.list_window_names()
        # check foreground window title
        current = self.wincap.title()

        # Only two modes. Does not work from character select.
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

        self.locator()

    def command_chain(self, command, tooltip):
        self.wincap.stop()
        self.vision.stop()
        self.bot.stop()

        self.wincap = WindowCapture(window_name=self.haystack_wnd)
        self.vision = Vision(command)
        self.bot = TTRBot((self.wincap.offset_x, self.wincap.offset_y), (self.wincap.w, self.wincap.h), tooltip)

        self.wincap.start()
        self.vision.start()
        self.bot.start()
        
    """ 
    Cryptology:
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
        self.wincap = WindowCapture(self.haystack_wnd)
        self.vision = Vision("targets/bear.png")
        self.bot = TTRBot((self.wincap.offset_x, self.wincap.offset_y), (self.wincap.w, self.wincap.h), 'tooltips/tooltip_bear.png')

    def locator(self):
        # Too late, lazy to change variables from "self"
        loop_time = time()
        firstRun = True

        while(True):
            # All the classes run in their own thread that's separate from the main thread
            # so that the code here can continue while the bot performs its actions

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
            elif self.bot.state == BotState.MOVING:
                # when moving, we need fresh screenshots to determine when we've stopped moving.
                self.bot.update_screenshot(self.wincap.screenshot)
            elif self.bot.state == BotState.STILL:
                # nothing is needed while we wait for the ui to finish
                """
                class Command:
                    OPTION = 0
                    PETS = 1
                    GOOD = 2
                    TRICKS = 3
                    TRICK = 4
                    TIRED = 5
                    SCRATCH = 6 - To save jellybeans.
                    FEED = 7
                    EXCITED = 8
                """
                # Regular route - On successfull click
                if not self.loggingIn:
                    if self.state + 1 < Command.EXCITED:
                        # Always do one round of excited check. 
                        # Similar to bot's confirm_tooltip method
                        excited = cv.imread(self.targetList[Command.EXCITED], cv.IMREAD_UNCHANGED)
                        excitement = cv.matchTemplate(self.wincap.screenshot, excited, cv.TM_CCOEFF_NORMED)
                        # get the best match postition
                        min_val, bestMatch, min_loc, max_loc = cv.minMaxLoc(excitement)
                        if bestMatch >= 0.60:
                            # No need to feed if excited
                            if self.state == Command.FEED or self.state == Command.SCRATCH:
                                self.state = 0
                                self.isGood = False
                            # If we've already said "Good Boy!"
                            elif self.isGood and Command.GOOD:
                                self.state = Command.TRICKS
                                self.isGood = False
                            # If Good, then naw.
                            elif self.state == Command.GOOD:
                                self.isGood = True
                            self.command_chain(command=self.targetList[self.state], tooltip=self.tooltipList[self.state])
                        # If tired, or neutral, not good.
                        elif self.state == Command.FEED:
                            self.isGood = False
                            self.command_chain(command=self.targetList[self.state], tooltip=self.tooltipList[self.state])
                        else:
                            self.state = Command.SCRATCH
                            self.isGood = False
                            self.command_chain(command=self.targetList[self.state], tooltip=self.tooltipList[self.state])
                        
                        # Increment after everything is done.
                        if firstRun:
                            firstRun = False
                        else: self.state += 1
                    else:
                        self.isGood = False
                        self.state = Command.OPTION
                        self.command_chain(command=self.targetList[self.state], tooltip=self.tooltipList[self.state])
                # Use loginList instead
                else:
                    # for now
                    pass
                
            if self.DEBUG:
                # draw the detection results onto the original image
                detection_image = self.vision.draw_rectangles(self.wincap.screenshot, self.vision.rectangles)
                # display the images
                try: 
                    cv.imshow('Matches', detection_image)
                except:
                    pass
                # sleep(0.5)
                # win32gui.SetForegroundWindow(win32gui.FindWindow(None, "Toontown Rewritten"))

            # debug the loop rate - bad atm
            print('FPS {}'.format(1 / (time() - loop_time)))
            print(self.state)
            loop_time = time()

            # Press 'q' with the output window focused to exit.
            # Waits 1 ms every loop to process key presses
            key = cv.waitKey(1)
            if key == ord('q'):
                self.wincap.stop()
                self.vision.stop()
                self.bot.stop()
                cv.destroyAllWindows()
                break

        print('Done performing {} task.'.format(self.targetList[self.state]))

    # Encrypts our user/pw
    def write_key(self):
        # Generates a key and save it into a file
        self.key = Fernet.generate_key()
        with open("key.key", "wb") as key_file:
            key_file.write(self.key)

    def load_key(self):
        # Loads the key from the current directory named `key.key`
        return open("key.key", "rb").read()