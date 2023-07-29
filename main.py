import cv2
import time

from tflite_support.task import core, processor, vision

import utils
from constants import CAMERA_FPS, FRAME_HEIGHT, FRAME_WIDTH, MAX_RESULTS, THREADS, THRESHOLD

MODEL_FILENAME = "efficientdet_lite0.tflite"


def detect(image, detector):
    tensor = vision.TensorImage.create_from_array(image)
    detection_result = detector.detect(tensor)
    return detection_result


def main():
    counter = 0

    cap = cv2.VideoCapture(0)

    cap.set(cv2.CAP_PROP_FRAME_WIDTH, FRAME_WIDTH)
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, FRAME_HEIGHT)
    cap.set(cv2.CAP_PROP_FPS, CAMERA_FPS)

    base_options = core.BaseOptions(file_name=MODEL_FILENAME, num_threads=THREADS)
    detection_options = processor.DetectionOptions(max_results=MAX_RESULTS, score_threshold=THRESHOLD)
    detector_options = vision.ObjectDetectorOptions(base_options=base_options, detection_options=detection_options)

    detector = vision.ObjectDetector.create_from_options(detector_options)

    detection_result = processor.DetectionResult([])

    while cap.isOpened():
        counter += 1
        _, image = cap.read()
        image = cv2.flip(image, 1)

        rgb_image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)

        if counter % 5 == 1:
            start = time.time()
            detection_result = detect(rgb_image, detector)
            end = time.time()
            print(f"elapsed time: {end - start}")

        image = utils.show_detect_object_rectangle(image, detection_result)

        utils.show_fps(image, counter)

        if cv2.waitKey(1) == "q":
            break

        cv2.imshow("detector", image)


if __name__ == "__main__":
    main()
