import cv2
import time

import RPi.GPIO as GPIO
from typing import Tuple

from tflite_support.task import processor, vision

import visualize
from camera import Camera
from constants import DEFAULT_MAX_RESULTS, DEFAULT_MODEL_FILENAME, DEFAULT_SCORE_THRESHOLD, DEFAULT_THREADS
from coordinate import Coordinate, DetectionCoordinate
from detector import Detector

MODEL_FILENAME = "efficientdet_lite0.tflite"

GPIO.setmode(GPIO.BCM)
GPIO.setup(17, GPIO.OUT)
GPIO.setup(18, GPIO.OUT)
GPIO.setup(23, GPIO.OUT)

px_1 = GPIO.PWM(17, 50)
px_2 = GPIO.PWM(18, 50)

px_1.start(0)
px_2.start(0)


def move_motor(vector: Tuple[int, int]):
    print(vector)
    pass


def main():
    counter = 0

    camera = Camera(0)

    detector = Detector(
        model_filename=DEFAULT_MODEL_FILENAME,
        num_threads=DEFAULT_THREADS,
        max_results=DEFAULT_MAX_RESULTS,
        score_threshold=DEFAULT_SCORE_THRESHOLD,
    )

    detection_result = processor.DetectionResult([])

    while camera.device.isOpened():
        counter += 1
        _, image = camera.device.read()
        image = cv2.flip(image, 1)

        rgb_image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)

        if counter % 5 == 1:
            start = time.time()
            detection_result = detector.detect(rgb_image)
            end = time.time()
            print(f"elapsed time: {end - start}")

        image = visualize.show_detect_object_rectangle(image, detection_result)
        visualize.show_fps(image, counter)

        cv2.imshow("detector", image)

        if len(detection_result.detections) < 1:
            continue

        test_detection = detection_result.detections[0]
        coordinate = DetectionCoordinate(test_detection)
        h, w, _ = image.shape
        point_diff = visualize.get_diff_from_center(Coordinate(w, h), coordinate.gravity)
        move_motor(point_diff)

        if cv2.waitKey(1) == "q":
            break


if __name__ == "__main__":
    main()
