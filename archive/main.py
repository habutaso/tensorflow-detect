import cv2

import RPi.GPIO as GPIO
from typing import Tuple

from tflite_support.task import processor

import archive.visualize as visualize
from devices.camera import Camera
from archive.constants import (
    DEFAULT_MAX_RESULTS,
    DEFAULT_MODEL_FILENAME,
    DEFAULT_SCORE_THRESHOLD,
    DEFAULT_THREADS,
    DEFAULT_FRAME_WIDTH_HALF,
)
from utils.coordinate import Coordinate, DetectionCoordinate
from utils.detector import Detector
from archive.imwrite import ImWrite

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

px_1_duty = 0
px_2_duty = 0


def move_motor(vector: Tuple[int, int]):
    global px_1_duty
    global px_2_duty

    print(vector)
    duty_x = 20 + int(abs(vector[1]) / DEFAULT_FRAME_WIDTH_HALF * 100) / 10
    # duty_x = 6
    # px_1.ChangeDutyCycle(100)
    # px_2.ChangeDutyCycle(100)
    if vector[1] > 0:
        px_2_duty = duty_x
        px_1_duty = 0
    elif vector[1] == 0:
        px_2_duty = 100
        px_1_duty = 100
    else:
        px_2_duty = 0
        px_1_duty = duty_x

    px_1.ChangeDutyCycle(px_1_duty)
    px_2.ChangeDutyCycle(px_2_duty)

    # print(duty_x)
    # px_1.ChangeDutyCycle(duty_x)


def stop_motor():
    px_1.ChangeDutyCycle(100)
    px_2.ChangeDutyCycle(100)


def main():
    px_1.ChangeDutyCycle(0)
    px_2.ChangeDutyCycle(0)
    counter = 0

    camera = Camera(0)

    detector = Detector(
        model_filename=DEFAULT_MODEL_FILENAME,
        num_threads=DEFAULT_THREADS,
        max_results=DEFAULT_MAX_RESULTS,
        score_threshold=DEFAULT_SCORE_THRESHOLD,
    )

    imwrite = ImWrite()

    detection_result = processor.DetectionResult([])

    while camera.device.isOpened():
        counter += 1
        _, image = camera.device.read()
        # image = cv2.flip(image, 1)

        rgb_image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)

        if counter % 3 == 1:
            # start = time.time()
            detection_result = detector.detect(rgb_image)
            # print(f"elapsed time: {end - start}")
            # end = time.time()

        if detection_result.detections:
            image = visualize.show_detect_object_rectangle(image, detection_result)
        else:
            visualize.show_fps(image, counter)

        cv2.imshow("detector", image)
        # imwrite.write(image)

        if len(detection_result.detections) < 1:
            GPIO.output(27, False)
            stop_motor()
        else:
            test_detection = detection_result.detections[0]
            coordinate = DetectionCoordinate(test_detection)
            h, w, _ = image.shape
            point_diff = visualize.get_diff_from_center(Coordinate(w // 2, h // 2), coordinate.gravity)
            move_motor(point_diff)
            GPIO.output(27, True)

        if cv2.waitKey(1) == "q":
            stop_motor()
            break


if __name__ == "__main__":
    main()
