import cv2
import RPi.GPIO as GPIO


class Control:
    def __init__(self, camera, detector):
        self.camera = camera
        self.detector = detector

    def read_from_image(self):
        _, image = self.camera.device.read()
        image = cv2.flip(image, 1)
        return cv2.cvtColor(image, cv2.COLOR_BGR2RGB)

    def detect_from_image(self, image):
        res = self.detector.detect(image)




