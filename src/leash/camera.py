"""Manager for a Lumen camera
"""

import cv2
import numpy as np

class Camera():

    def __init__(self, index = 1):

        # opening camera from config settings, setting frame size
        self._capture = cv2.VideoCapture(index)
        self._capture.set(cv2.CAP_PROP_FRAME_WIDTH, 1280)
        self._capture.set(cv2.CAP_PROP_FRAME_HEIGHT, 720)

    def list_cameras(self):
        index = 0
        cameras = []
        while True:
            cap = cv2.VideoCapture(index)
            if not cap.isOpened():
                break
            cameras.append(index)
            cap.release()
            index += 1
        return cameras
            
    def capture(self):
        ret, image = self._capture.read()
        if ret is True:
            return image
        else:
            return False
    
    def getFidPosition(self, debug=False):

        while True:
            image = self.capture()
            if image.any():
                gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

                blur = cv2.blur(gray,(10,10))

                mask = cv2.threshold(blur, 128, 255, cv2.THRESH_BINARY)[1]

                circles = cv2.HoughCircles(mask, cv2.HOUGH_GRADIENT, 1.2, 100)

                cv2.imshow("img", circles)

                if cv2.waitKey(1) & 0xFF == ord('q'):
                    break
            else:
                print("couldnt take a pic")
    
        self._capture.release()
        cv2.destroyAllWindows()

        # circles = cv2.HoughCircles(mask, cv2.HOUGH_GRADIENT, 1.2, 100)

        # if circles is not None:
        #     # convert the (x, y) coordinates and radius of the circles to integers
        #     circles = np.round(circles[0, :]).astype("int")
        #     # loop over the (x, y) coordinates and radius of the circles
        #     for (x, y, r) in circles:
        #         # draw the circle in the output image, then draw a rectangle
        #         # corresponding to the center of the circle
        #         cv2.circle(output, (x, y), r, (0, 255, 0), 4)
        #         cv2.rectangle(output, (x - 5, y - 5), (x + 5, y + 5), (0, 128, 255), -1)
        #     # show the output image

        #     if debug:
        #         cv2.imshow("output", np.hstack([image, output]))
        #         cv2.waitKey(1)

        #     return (x, y, r)
        
        return False
        

        