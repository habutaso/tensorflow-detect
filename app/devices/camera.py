import threading
import time
import cv2
from copy import deepcopy


DEFAULT_FPS = 30
DEFAULT_WIDTH = 640
DEFAULT_HEIGHT = 480
DEFAULT_QUEUE_DENOMINATOR = 2


class Camera:
    def __init__(
        self,
        camera_id: int,
        fps: int = DEFAULT_FPS,
        width: int = DEFAULT_WIDTH,
        height: int = DEFAULT_HEIGHT,
        queue_denominator: int = DEFAULT_QUEUE_DENOMINATOR,
    ):
        self.width = width
        self.height = height
        self.__device = cv2.VideoCapture(camera_id)
        self.__terminate_camera_thread = threading.Event()
        self.__fps = fps
        self.__queue_denominator = queue_denominator
        self.__queue_interval = self.__fps // self.__queue_denominator
        self.__queue_count = 0
        self.__buffer_image = None
        self.__thread = None

        self.set_fps(fps)
        self.set_wh(self.width, self.height)

    @property
    def center(self):
        return {"x": self.width // 2, "y": self.height // 2}

    def __queueable(self):
        self.__queue_count = (self.__queue_count + 1) % self.__fps
        return self.__queue_count % self.__queue_interval == 0

    def set_fps(self, fps):
        self.__device.set(cv2.CAP_PROP_FPS, fps)

    def set_wh(self, width, height):
        self.__device.set(cv2.CAP_PROP_FRAME_WIDTH, width)
        self.__device.set(cv2.CAP_PROP_FRAME_HEIGHT, height)

    def read(self):
        return deepcopy(self.__buffer_image)

    def stream(self):
        while not self.__terminate_camera_thread.is_set():
            if self.__device.isOpened():
                _, frame = self.__device.read()
                self.__buffer_image = frame
                time.sleep(0.01)

    def release(self):
        print("release camera process ...")
        self.__terminate_camera_thread.set()
        self.__device.release()
        exit(0)

    def start_streaming(self):
        self.__thread = threading.Thread(target=self.stream, daemon=True)
        self.__thread.start()

    def __del__(self):
        self.release()
