import cv2


DEFAULT_FPS = 30
DEFAULT_WIDTH = 640
DEFAULT_HEIGHT = 480


class Camera:
    def __init__(
        self, camera_id: int, fps: int = DEFAULT_FPS, width: int = DEFAULT_WIDTH, height: int = DEFAULT_HEIGHT
    ):
        self.device = cv2.VideoCapture(camera_id)

        self.set_fps(fps)
        self.set_wh(width, height)

    def set_fps(self, fps):
        self.device.set(cv2.CAP_PROP_FPS, fps)

    def set_wh(self, width, height):
        self.device.set(cv2.CAP_PROP_FRAME_WIDTH, width)
        self.device.set(cv2.CAP_PROP_FRAME_HEIGHT, height)
