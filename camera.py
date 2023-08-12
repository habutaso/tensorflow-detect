import cv2

from constants import DEFAULT_FPS, DEFAULT_HEIGHT, DEFAULT_WIDTH


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
