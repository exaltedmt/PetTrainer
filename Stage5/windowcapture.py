import numpy as np
import win32gui, win32ui, win32con

# In classes, every function must have self as first param.
class WindowCapture:

    # define monitor width and height
    # now properties of self
    w = 0
    h = 0
    hwnd = None
    cropped_x = 0
    cropped_y = 0
    offset_x = 0
    offset_y = 0

    # Constructor
    def __init__(self, window_name=None):
        # If no window name is given, capture full screen.
        if window_name is None:
            self.hwnd = win32gui.GetDesktopWindow()
        else:
            # Find the handle for the window we want to capture
            self.hwnd = win32gui.FindWindow(None, window_name)
            if not self.hwnd:
                    raise Exception('Window not found: {}'.format(window_name))
                
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
        
    # Helps when we cant find window name
    # Lists hex values and respective names.
    # Not utilizing the self param inside the function
    # Making this static allows us to call it without needing an instance of this class.
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

        # can be done once in the constructor
        # hwnd = win32gui.FindWindow(None, 'Toontown Rewritten')

        wDC = win32gui.GetWindowDC(self.hwnd)
        dcObj = win32ui.CreateDCFromHandle(wDC)
        cDC = dcObj.CreateCompatibleDC()
        dataBitMap = win32ui.CreateBitmap()
        dataBitMap.CreateCompatibleBitmap(dcObj, self.w, self.h)
        cDC.SelectObject(dataBitMap)
        # cDC.BitBlt((0,0), (self.w, self.h), dcObj, (0,0), win32con.SRCCOPY)
        cDC.BitBlt((0, 0), (self.w, self.h), dcObj, (self.cropped_x, self.cropped_y), win32con.SRCCOPY)

        # Save the screenshot - Creates a bunch of bmps from loop.
        # dataBitMap.SaveBitmapFile(cDC, 'debug.bmp')
        signedIntArray = dataBitMap.GetBitmapBits(True)
        # img = np.array(signedIntArray, dtype = 'uint8')
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