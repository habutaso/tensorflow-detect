import cv2
import time

import RPi.GPIO as GPIO
from typing import Tuple

from tflite_support.task import processor, vision

import visualize
from camera import Camera
from constants import DEFAULT_MAX_RESULTS, DEFAULT_MODEL_FILENAME, DEFAULT_SCORE_THRESHOLD, DEFAULT_THREADS, DEFAULT_FRAME_WIDTH_HALF
from coordinate import Coordinate, DetectionCoordinate
from detector import Detector

MODEL_FILENAME = "efficientdet_lite0.tflite"

GPIO.setmode(GPIO.BCM)
GPIO.setup(27, GPIO.OUT)
GPIO.setup(17, GPIO.OUT)
GPIO.setup(18, GPIO.OUT)
GPIO.setup(23, GPIO.OUT)

px_1 = GPIO.PWM(17, 50)
px_2 = GPIO.PWM(18, 50)

px_1.start(0)
px_2.start(0)


def move_motor(vector: Tuple[int, int]):
    print(vector)
    duty_x = (10 + int(abs(vector[0]) / DEFAULT_FRAME_WIDTH_HALF * 100) / 5)
    if vector[0] > 0:
        px_1.ChangeDutyCycle(duty_x)
        px_2.ChangeDutyCycle(0)
    elif vector[0] == 0:
        px_1.ChangeDutyCycle(100)
        px_2.ChangeDutyCycle(100)
    else:
        px_1.ChangeDutyCycle(0)
        px_2.ChangeDutyCycle(duty_x)
        
    # print(duty_x)
    # px_1.ChangeDutyCycle(duty_x)


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
            GPIO.output(27, False)
            continue

        test_detection = detection_result.detections[0]
        coordinate = DetectionCoordinate(test_detection)
        h, w, _ = image.shape
        point_diff = visualize.get_diff_from_center(Coordinate(w // 2, h // 2), coordinate.gravity)
        move_motor(point_diff)
        GPIO.output(27, True)

        if cv2.waitKey(1) == "q":
            break


if __name__ == "__main__":
    main()
