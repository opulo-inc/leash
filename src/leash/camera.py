import cv2
import numpy as np


class Camera:
    """
    Manager for a Lumen camera
    """

    def __init__(self, index=1, resolution=(1280, 720)):
        # ToDo: opening camera from config settings, setting frame size
        self._capture = cv2.VideoCapture(index)
        self._capture.set(cv2.CAP_PROP_FRAME_WIDTH, resolution[0])
        self._capture.set(cv2.CAP_PROP_FRAME_HEIGHT, resolution[1])

    def capture(self):
        ret, image = self._capture.read()
        if ret:
            return image
        else:
            return None

    def get_fid_position(self, debug=False) -> tuple[bool, tuple[float, float, float]]:
        """
        Get the fiducial position from the camera
        :param debug:
        :return:
        """
        image = self.capture()

        output = image.copy()

        blur = cv2.blur(image, (10, 10))

        mask = cv2.threshold(blur, 128, 255, cv2.THRESH_BINARY)[1]

        if debug:
            cv2.imshow("mask", mask)
            cv2.waitKey(1)

        circles = cv2.HoughCircles(mask, cv2.HOUGH_GRADIENT, 1.2, 100)

        x, y, r = 0, 0, 0
        if circles is not None:
            # Convert the (x, y) coordinates and radius of the circles to integers
            circles = np.round(circles[0, :]).astype("int")
            # Loop over the (x, y) coordinates and radius of the circles
            for x, y, r in circles:
                # Draw the circle in the output image, then draw a rectangle corresponding to the center of the circle
                cv2.circle(output, (x, y), r, (0, 255, 0), 4)
                cv2.rectangle(output, (x - 5, y - 5), (x + 5, y + 5), (0, 128, 255), -1)

            # Show the output image
            if debug:
                cv2.imshow("output", np.hstack([image, output]))
                cv2.waitKey(1)

            return True, (x, y, r)

        return False, (x, y, r)
