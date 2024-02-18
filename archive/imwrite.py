import time
import secrets
import cv2

from archive.constants import DEFAULT_WRITE_DIR


class ImWrite:
    def __init__(self, write_dir=DEFAULT_WRITE_DIR):
        self.write_dir = write_dir
        
    def write(self, image):
        filepath = f"{self.write_dir}{int(time.time() // 1000)}{secrets.token_hex(6)}.jpg"
        print(filepath)
        cv2.imwrite(filepath, image)

