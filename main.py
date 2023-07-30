import cv2
from tflite_support.task import core, processor, vision

import camera
import utils
from detector import DEFAULT_MAX_RESULTS, DEFAULT_MODEL_FILENAME, DEFAULT_SCORE_THRESHOLD, DEFAULT_THREADS, Detector

TEXT_COLOR = (255, 255, 0)  # cyan
THREADS = 4
MODEL_FILENAME = "efficientdet_lite0.tflite"


def detect(image, detector):
    tensor = vision.TensorImage.create_from_array(image)
    detection_result = detector.detect(tensor)
    return detection_result


def main():
    counter = 0

    camera = camera.Camera(0)

    detector = Detector(model_filename=DEFAULT_MODEL_FILENAME, num_threads=DEFAULT_THREADS, max_results=DEFAULT_MAX_RESULTS, score_threshold=DEFAULT_SCORE_THRESHOLD)

    detection_result = processor.DetectionResult([])

    while camera.device.isOpened():
        counter += 1
        _, image = camera.device.read()
        image = cv2.flip(image, 1)

        rgb_image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)

        if counter % 5 == 1:
            detection_result = detect(rgb_image, detector)

        image = utils.visualize(image, detection_result)

        utils.show_fps(image, counter)

        if cv2.waitKey(1) == "q":
            break

        cv2.imshow("detector", image)


if __name__ == "__main__":
    main()
