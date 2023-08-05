import time
from typing import Tuple

import cv2
import numpy as np
from tflite_support.task import processor

from coordinate import DetectionCoordinate
from constants import TEXT_COLOR, FONT_THICKNESS, FONT_MARGIN, FPS_COUNT, ROW_SIZE


fps = 0
start_time = 0


def show_detect_object_rectangle(
    image: np.ndarray, detection_result: processor.DetectionResult, frame_gravity: Tuple[int, int]
) -> np.ndarray:
    for detection in detection_result.detections:
        coordinate = DetectionCoordinate(detection, frame_gravity)

        cv2.rectangle(image, coordinate.start_point.tuple, coordinate.end_point.tuple, TEXT_COLOR, FONT_THICKNESS)
        cv2.line(
            image,
            pt1=(frame_gravity[0], frame_gravity[1]),
            pt2=coordinate.gravity.tuple,
            color=TEXT_COLOR,
            thickness=FONT_THICKNESS,
            lineType=cv2.LINE_4,
        )
        print(coordinate.gravity_diff_from_center)

        category = detection.categories[0]
        category_name = category.category_name
        prob = round(category.score, 2)

        text = f"{category_name}({str(prob)})"

        location = (FONT_MARGIN + coordinate.origin_x, FONT_MARGIN + ROW_SIZE + coordinate.origin_y)

        cv2.putText(image, text, location, cv2.FONT_HERSHEY_PLAIN, FONT_SIZE, FONT_THICKNESS)
    return image


def show_fps(image: np.ndarray, counter: int) -> np.ndarray:
    global fps
    global start_time

    if counter % FPS_COUNT == 0:
        end_time = time.time()
        fps = FPS_COUNT / (end_time - start_time)
        start_time = time.time()

    fps_text = "FPS {:.1f}".format(fps)

    location = (FONT_MARGIN, ROW_SIZE)

    cv2.putText(image, fps_text, location, cv2.FONT_HERSHEY_PLAIN, FONT_SIZE, TEXT_COLOR, FONT_THICKNESS)

    return image
