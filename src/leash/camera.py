import cv2

class Camera():

    def __init__(self, index = 1):

        # opening camera from config settings, setting frame size
        self._capture = cv2.VideoCapture(index)
        self._capture.set(cv2.CAP_PROP_FRAME_WIDTH, 1280)
        self._capture.set(cv2.CAP_PROP_FRAME_HEIGHT, 720)

            
    def capture(self):
        ret, image = self._capture.read()
        return image