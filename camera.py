import cv2


DEFAULT_FPS = 15
DEFAULT_WIDTH = 640
DEFAULT_HEIGHT = 480
DEFAULT_WINDOW_NAME = "detector"


class Camera:

    def __init__(self, camera_id: int):
        self.device = cv2.VideoCapture(camera_id)

        self.set_fps(DEFAULT_FPS)
        self.set_wh(DEFAULT_WIDTH, DEFAULT_HEIGHT)
        
    def set_fps(self, fps):
        self.device.set(cv2.CAP_PROP_FPS, fps)
    
    def set_wh(self, width, height):
        self.device.set(cv2.CAP_PROP_FRAME_WIDTH, width)
        self.device.set(cv2.CAP_PROP_FRAME_HEIGHT, height)
        