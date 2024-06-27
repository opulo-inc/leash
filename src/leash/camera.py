"""Manager for a Lumen camera
"""

import cv2, 
import numpy as np

class Camera():

    def __init__(self, index = 1):

        # opening camera from config settings, setting frame size
        self._capture = cv2.VideoCapture(index)
        self._capture.set(cv2.CAP_PROP_FRAME_WIDTH, 1280)
        self._capture.set(cv2.CAP_PROP_FRAME_HEIGHT, 720)

            
    def capture(self):
        ret, image = self._capture.read()
        return image
    
    def getFidPosition(self, debug=False):

        image = self.capture()

        output = image.copy()

        blur = cv2.blur(image,(10,10))

        mask = cv2.threshold(blur, 128, 255, cv2.THRESH_BINARY)[1]

        if debug:
            cv2.imshow("mask", mask)
            cv2.waitkey(1)

        circles = cv2.HoughCircles(mask, cv2.HOUGH_GRADIENT, 1.2, 100)

        if circles is not None:
            # convert the (x, y) coordinates and radius of the circles to integers
            circles = np.round(circles[0, :]).astype("int")
            # loop over the (x, y) coordinates and radius of the circles
            for (x, y, r) in circles:
                # draw the circle in the output image, then draw a rectangle
                # corresponding to the center of the circle
                cv2.circle(output, (x, y), r, (0, 255, 0), 4)
                cv2.rectangle(output, (x - 5, y - 5), (x + 5, y + 5), (0, 128, 255), -1)
            # show the output image

            if debug:
                cv2.imshow("output", np.hstack([image, output]))
                cv2.waitKey(1)

            return (x, y, r)
        
        return False
        

        