import numpy as np
import win32gui, win32ui, win32con
import tkinter as tk
from tkinter import filedialog, Label, messagebox, Tk
import subprocess as sp
from threading import Thread, Lock

# In classes, every function must have self as first param.
class WindowCapture:

    # Threading Properties
    stopped = True
    lock = None
    screenshot = None

    # Properties
    w = 0
    h = 0
    hwnd = None
    cropped_x = 0
    cropped_y = 0
    offset_x = 0
    offset_y = 0
    game = None
    file_path = "C:/Program Files (x86)/Toontown Rewritten/"

    # Constructor
    def __init__(self, window_name=None, select=False):
        # create a thread lock object
        self.lock = Lock()

        # If no window name is given, capture full screen.
        if window_name is None:
            self.hwnd = win32gui.GetDesktopWindow()
        elif select:
            self.launcher(select=True)
        else:
            # Find the handle for the window we want to capture
            # Warning: This will still run if the title of any window matches. 
            self.hwnd = win32gui.FindWindow(None, window_name)
            if not self.hwnd:
                # raise `Ex`ception('Window not found: {}'.format(window_name))
                print('Window not found: {}'.format(window_name))
                # Instead of killing the script we will launch the exe it ourselves.
                self.launcher()
                    
        # define monitor width and height
        # now properties of self
        # self.w = 1920
        # self.h = 1080

        # Get the window size
        window_rect = win32gui.GetWindowRect(self.hwnd)
        self.w = window_rect[2] - window_rect[0]
        self.h = window_rect[3] - window_rect[1]                 

        # Account for window border and titlebar. Cut them off.
        border_pixels = 8
        titlebar_pixels = 32
        self.w = self.w - (border_pixels * 2)
        self.h = self.h - titlebar_pixels - border_pixels
        self.cropped_x = border_pixels
        self.cropped_y = titlebar_pixels

        # Set the cropped coordinates offset, so we can translate screenshot
        # images into actual screen postions.
        self.offset_x = window_rect[0] + self.cropped_x
        self.offset_y = window_rect[1] + self.cropped_y

    def title(self):
        if self.hwnd != None:
            return win32gui.GetWindowText(self.hwnd)
        else:
             print("Not listening to any windows.")
             return None
        
    def launcher(self, select=False):
        # If location not found from default place, ask via dialog box
        # Once login pops up, grab that window
        if not select:
            print('Opening Launcher...')
            # Must specify CWD so that our launcher doesnt download patch files
            # in our script folder
            # shell=True because windows.
            self.game = sp.Popen("Launcher.exe", stdout=sp.PIPE, stderr=sp.PIPE, shell=True, cwd=self.file_path)
            # Wait for TTR Launcher
            while(not self.hwnd):
                self.hwnd = win32gui.FindWindow(None, "Toontown Rewritten Launcher")
            # Dialog Box!
            root = Tk()
            prompt = 'Do not touch other programs until we are logged in!'
            label1 = Label(root, text=prompt, width=len(prompt))
            label1.pack()
                
            root.after(1000, root.destroy())
            root.mainloop()
        else:
            # Dialog box for selecting a file to open.
            print('Please select file to open!')
            root = tk.Tk()
            root.withdraw()
            self.file_path = filedialog.askopenfilename()
            # self.file_paths.rsplit('/', 1)[0]: 
            # Separates string into array before last backslash
            self.game = sp.Popen(self.file_path, stdout=sp.PIPE, stderr=sp.PIPE, shell=True, cwd=self.file_paths.rsplit('/', 1)[0])
            # A less direct approach to getting the window
            time.sleep(7)
            self.hwnd = win32gui.GetForegroundWindow()

    # Helps when we cant find window name
    # Lists hex values and respective names.
    @staticmethod
    def list_window_names():
        def winEnumHandler(hwnd, ctrx):
            if win32gui.IsWindowVisible(hwnd):
                print(hex(hwnd), win32gui.GetWindowText(hwnd))
        win32gui.EnumWindows(winEnumHandler, None)

    # translate a pixel position on a screenshot image to a pixel position on the screen.
    # pos = (x, y)
    # WARNING: if you move the indow being captured after execution is started,
    # this will return incorrect coordinates, because the window position is only
    # calculated in the __init_ constructor.
    def get_screenshot_position(self, pos):
        return (pos[0] + self.offset_x, pos[1] + self.offset_y)

    # Taken from: https://stackoverflow.com/questions/3586046/
    # fastest-way-to-take-a-screenshot-with-python-on-windows/3586280#3586280
    # Win32 calls are a more direct way to do things. Saves resources, less dependencies.
    def get_screenshot(self):
        wDC = win32gui.GetWindowDC(self.hwnd)
        dcObj = win32ui.CreateDCFromHandle(wDC)
        cDC = dcObj.CreateCompatibleDC()
        dataBitMap = win32ui.CreateBitmap()
        dataBitMap.CreateCompatibleBitmap(dcObj, self.w, self.h)
        cDC.SelectObject(dataBitMap)
        cDC.BitBlt((0, 0), (self.w, self.h), dcObj, (self.cropped_x, self.cropped_y), win32con.SRCCOPY)

        signedIntArray = dataBitMap.GetBitmapBits(True)
        img = np.fromstring(signedIntArray, dtype = 'uint8')
        img.shape = (self.h, self.w, 4)

        # Free Resources
        dcObj.DeleteDC()
        cDC.DeleteDC()
        win32gui.ReleaseDC(self.hwnd, wDC)
        win32gui.DeleteObject(dataBitMap.GetHandle())

        # Get rid of the alpha channel, so matchTemplate doesnt get thrown off.
        # ONLY NECESSARY IF OUR NEEDLE IMAGE HAS LESS CHANNELS!
        # img = img[..., :3]

        # Make image C_CONTIGUOUS
        # else we get a TypeError: int from draw_rectangles, from type tuple
        img = np.ascontiguousarray(img)
         
        return img

    # threading methods

    def start(self):
        self.stopped = False
        t = Thread(target=self.run)
        t.start()

    def stop(self):
        self.stopped = True

    def run(self):
        # TODO: you can write your own time/iterations calculation to determine how fast this is
        while not self.stopped:
            # get an updated image of the game
            screenshot = self.get_screenshot()
            # lock the thread while updating the results
            self.lock.acquire()
            self.screenshot = screenshot
            self.lock.release()