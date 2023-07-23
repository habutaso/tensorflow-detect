import cv2
from tflite_support.task import core, processor, vision

import utils

TEXT_COLOR = (255, 255, 0)  # cyan
THREADS = 4
MODEL_FILENAME = "efficientdet_lite0.tflite"


def detect(image, detector):
    tensor = vision.TensorImage.create_from_array(image)
    detection_result = detector.detect(tensor)
    return detection_result


def main():
    counter = 0

    cap = cv2.VideoCapture(0)

    cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
    cap.set(cv2.CAP_PROP_FRAME_WIDTH, 480)
    cap.set(cv2.CAP_PROP_FPS, 15)

    base_options = core.BaseOptions(file_name=MODEL_FILENAME, num_threads=THREADS)
    detection_options = processor.DetectionOptions(max_results=3, score_threshold=0.6)
    detector_options = vision.ObjectDetectorOptions(base_options=base_options, detection_options=detection_options)

    detector = vision.ObjectDetector.create_from_options(detector_options)

    detection_result = processor.DetectionResult([])

    while cap.isOpened():
        counter += 1
        _, image = cap.read()
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
