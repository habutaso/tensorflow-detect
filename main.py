import cv2
import time

from tflite_support.task import processor, vision

import visualize
from camera import Camera
from constants import DEFAULT_MAX_RESULTS, DEFAULT_MODEL_FILENAME, DEFAULT_SCORE_THRESHOLD, DEFAULT_THREADS
from detector import Detector

MODEL_FILENAME = "efficientdet_lite0.tflite"


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

        if cv2.waitKey(1) == "q":
            break

        cv2.imshow("detector", image)


if __name__ == "__main__":
    main()
