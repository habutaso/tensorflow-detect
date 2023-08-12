import time
from typing import Tuple

import cv2
import numpy as np
from tflite_support.task import processor

from coordinate import Coordinate, DetectionCoordinate
from constants import TEXT_COLOR, FONT_THICKNESS, FONT_MARGIN, FPS_COUNT, FONT_SIZE, ROW_SIZE


fps = 0
start_time = 0


def get_diff_from_center(frame_center: Coordinate, detect_coord: Coordinate) -> Tuple[int, int]:
    """中心からの差分を出力する

    Args:
        frame_center (Coordinate): 画像の重心座標
        detect_coord (Coordinate): 検出範囲の重心座標

    Returns:
        Tuple[int, int]: [差分w, 差分h]
    """
    diff_w = detect_coord.x - frame_center.x
    diff_h = detect_coord.y - frame_center.y
    return diff_w, diff_h


def show_detect_object_rectangle(image: np.ndarray, detection_result: processor.DetectionResult) -> np.ndarray:
    h, w, _ = image.shape
    frame_center = Coordinate(w // 2, h // 2)

    for detection in detection_result.detections:
        coordinate = DetectionCoordinate(detection)
        point_diff = get_diff_from_center(frame_center, coordinate.gravity)
        print(point_diff)

        cv2.rectangle(image, coordinate.start_point.tuple, coordinate.end_point.tuple, TEXT_COLOR, FONT_THICKNESS)
        cv2.line(
            image,
            pt1=frame_center.tuple,
            pt2=coordinate.gravity.tuple,
            color=TEXT_COLOR,
            thickness=FONT_THICKNESS,
            lineType=cv2.LINE_4,
        )

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
