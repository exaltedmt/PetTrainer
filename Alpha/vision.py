import cv2 as cv
import numpy as np
from threading import Thread, Lock

class Vision:

    # Threading Properties
    stopped = True
    lock = None
    rectangles = []

    # Properties
    needle_img = None
    needle_w = 0
    needle_h = 0
    method = None
    result = None
    screenshot = None

    # Constructor
    def __init__(self, needle_img_path, method=cv.TM_CCOEFF_NORMED):
        # create a thread lock object
        self.lock = Lock()

        if needle_img_path:
            # load image were trying to match.
            # https://docs.opencv.org/4.2.0/d4/da8/group__imgcodecs.html
            self.needle_img = cv.imread(needle_img_path, cv.IMREAD_UNCHANGED)
        
            # Get dimensions of the needle image
            self.needle_w = self.needle_img.shape[1]
            self.needle_h = self.needle_img.shape[0]
            
        # There are 6 comparison methods to choose from:
        # TM_CCOEFF, TM_CCOEFF_NORMED, TM_CCORR, TM_CCORR_NORMED,
        # TM_SQDIFF, TM_SQDIFF_NORMED
        self.method = method

    def bestMatch(self):
        # Get the best match position from the match result.
        min_val, max_val, min_loc, max_loc = cv.minMaxLoc(self.result)
        # The max location will contain the upper left corner pixel position for the area
        # that most closely matches our needle image. The max value gives an indication
        # of how similar that find is to the original needle, where 1 is perfect and -1
        # is exact opposite.
        
        # print('Best match top left position: %s' % str(max_loc))
        # print('Best match confidence: %s' % max_val)

        return max_val

    # From def findClickPositions(needle_img_path, haystack_img, threshold=0.72, debug_mode=None):
    # To:
    def find(self, haystack_img, threshold=0.9, debug_mode=None):

        # Can use IMREAD flags to do different pre-processing of image files.
        # Like making them grayscale or reducing the size.
        # https://docs.opencv.org/4.2.0/d4/da8/group__imgcodecs.html
        # haystack_img = cv.imread(haystack_img_path, cv.IMREAD_UNCHANGED)
        # No longer using haystack_img_path, passing in screen cap now!
        # We're turning needle_img into a property of self!
        # needle_img = cv.imread(needle_img_path, cv.IMREAD_UNCHANGED)

        # Get dimensions of the needle image
        # needle_w = needle_img.shape[1]
        # needle_h = needle_img.shape[0]

        # There are 6 comparison methods to choose from:
        # TM_CCOEFF, TM_CCOEFF_NORMED, TM_CCORR, TM_CCORR_NORMED,
        # TM_SQDIFF, TM_SQDIFF_NORMED
        # You can see the differences at a glance here:
        # https://docs.opencv.org/master/d4/dc6/tutorial_py_template_matching.html
        # Note that the values are inverted for TM_SQDIFF and TM_SQDIFF_NORMED
        # Best results were with CCOEFF_NORMED.
        # method = cv.TM_CCOEFF_NORMED

        # Apply property tags
        # Making result a property lets us find best match outside of class.
        self.result = cv.matchTemplate(haystack_img, self.needle_img, self.method)
        # print(self.bestMatch())

        # We get the coordinates of the values under a given threshold
        # >= or <= depending on method used in cv.matchTemplate
        locations = np.where(self.result >= threshold)
        # we can zip these values up into tuple values
        locations = list(zip(*locations[::-1]))

        # if we found no results, return now. this reshape of the empty array allows us to 
        # concatenate together results without causing an error
        # Might be the fix for black screen capture
        if not locations:
            print("Target not found.")
            return np.array([], dtype=np.int32).reshape(0, 4)

        # Let's create the list of [x, y, w ,h] rectangles
        for loc in locations:
            rect = [int(loc[0]), int(loc[1]), self.needle_w, self.needle_h]
            self.rectangles.append(rect)
            # Twice to combat cv.groupRectangles problem.
            self.rectangles.append(rect) 

        # You'll notice a lot of overlapping rectangles get drawn. We can eliminate those redundant
        # locations by using groupRectangles().
        # second parameter determines how many rectanlges must overlap to group them.
        # third param - EPS - determines how close in order to group.
        # Returns inaccurate detections for single objects.
        # We can combat this by having at least one overlap.
        self.rectangles, weights = cv.groupRectangles(self.rectangles, groupThreshold=1, eps=0.5)
        # print(rectangles)

        # for performance reasons, return a limited number of results.
        # these aren't necessarily the best results.
        if len(self.rectangles) > max_results:
            print('Warning: too many results, raise the threshold.')
            self.rectangles = self.rectangles[:max_results]

        return self.rectangles

    def get_click_points(self, rectangles):
        # Move this up top.
        # needle_w = needle_img.shape[1]
        # needle_h = needle_img.shape[0]
        points = []

        # Loop over all locations and draw rectangle
        # for loc in locations:
        for (x, y, w, h) in rectangles:
            
            # Selecting the middle point of the box positions.
            center_x = x + int(w/2)
            center_y = y + int(h/2)

            # Save the points
            points.append((center_x, center_y))
        
        return points
    
    def draw_rectangles(self, haystack_img, rectangles):
        # Rectangle details - BGR
        line_color = (0, 255, 0)
        line_type = cv.LINE_4

            # if debug_mode == 'rectangles':
            for (x, y, w, h) in rectangles:
                # Determine the box positions
                # we gave top_left/right and needle_w/h variable names, so use those.
                top_left = (x, y)
    
                # bottom_right = (top_left[0] + needle_w, top_left[1] + needle_h)
                bottom_right = (x + w, y + h)

                # Draw the Box
                cv.rectangle(
                    haystack_img,
                    top_left,
                    bottom_right,
                    line_color,
                    line_type
                )

    def draw_crosshairs(self, haystack_img, crosshairs):
        marker_color = (255, 0, 255)
        marker_type = cv.MARKER_CROSS

        # elif debug_mode == 'points':
        for (center_x, center_y) in points:
            # draw the center point
            cv.drawMarker(haystack_img, (center_x, center_y), marker_color, marker_type)

    # Tabbing over 1 will still give video stream, outside if rectangles stmt,
    # even if we dont find any results.
    def centeroid(self, point_list):
        point_list = np.asarray(point_list, dtype=np.int32)
        length = point_list.shape[0]
        sum_x = np.sum(point_list[:, 0])
        sum_y = np.sum(point_list[:, 1])
        return [np.floor_divide(sum_x, length), np.floor_divide(sum_y, length)]

    # thread functions

    def update(self, screenshot):
        self.lock.acquire()
        self.screenshot = screenshot
        self.lock.release()

    def start(self):
        self.stopped = False
        t = Thread(target=self.run)
        t.start()

    def stop(self):
        self.stopped = True

    def run(self):
        # TODO: you can write your own time/iterations calculation to determine how fast this is
        while not self.stopped:
            if not self.screenshot is None:
                # do object detection
                # Show the best match only. Must run find() at least once however.
                if not self.firstRun:
                    bestMatch = self.bestMatch()
                    rectangles = self.find(screenshot, threshold=bestMatch)
                    output_image = self.draw_rectangles(screenshot, rectangles)
                else:    
                    rectangles = self.find(screenshot)
                    output_image = self.draw_rectangles(screenshot, rectangles)
                    self.firstRun = False
                    
                # lock the thread while updating the results
                self.lock.acquire()
                self.rectangles = rectangles
                self.lock.release()

    """
    Moved to Movement.py
    if debug_mode:
        cv.imshow('Matches', haystack_img)
        # cv.waitKey()
        # Wait key stuff done in Main while loop now.
        # cv.imwrite('result.png', haystack_img)
    
        return points

    else:
        print('Speedchat button not found.')
            
    
    points = findClickPositions('speedchat_bubble.png', 'TTGUI.png', debug_mode='points')
    print(points)

    print('Done.')
    exit()
    """
