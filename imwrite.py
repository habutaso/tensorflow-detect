import time
import secrets
import cv2

from constants import DEFAULT_WRITE_DIR


class ImWrite:
    def __init__(self, write_dir=DEFAULT_WRITE_DIR):
        self.write_dir = write_dir
        
    def write(self, image):
        filepath = f"{self.write_dir}{time.time()}{secrets.token_hex(6)}.jpg"
        cv2.imwrite(filepath, image)

