import time
from dataclasses import dataclass
from typing import Tuple

import cv2
import numpy as np
from tflite_support.task import processor

from archive.constants import (
    FONT_MARGIN,
    FONT_SIZE,
    FONT_THICKNESS,
    FPS_COUNT,
    FRAME_WIDTH_HALF,
    FRAME_HEIGHT_HALF,
    ROW_SIZE,
    TEXT_COLOR,
)


fps = 0

start_time = time.time()


@dataclass
class Coordinate:
    x: int
    y: int

    @property
    def tuple(self) -> Tuple[int, int]:
        return self.x, self.y


class DetectionCoordinate:
    def __init__(self, detection: processor.Detection):
        self.detection = detection
        self.box = self.detection.bounding_box

    @property
    def origin_x(self) -> int:
        return self.box.origin_x

    @property
    def origin_y(self) -> int:
        return self.box.origin_y

    @property
    def width(self) -> int:
        return self.box.width

    @property
    def height(self) -> int:
        return self.box.height

    @property
    def start_point(self) -> Coordinate:
        return Coordinate(x=self.origin_x, y=self.origin_y)

    @property
    def end_point(self) -> Coordinate:
        return Coordinate(x=self.origin_x + self.width, y=self.origin_y + self.height)

    @property
    def gravity(self) -> Coordinate:
        return Coordinate(x=self.origin_x + int(self.width / 2), y=self.origin_y + int(self.height / 2))

    @property
    def gravity_diff_from_center(self) -> Coordinate:
        gravity = self.gravity
        diff_x = gravity.x - FRAME_WIDTH_HALF
        diff_y = gravity.y - FRAME_HEIGHT_HALF
        return Coordinate(x=diff_x, y=diff_y)


def show_detect_object_rectangle(
    image: np.ndarray,
    detection_result: processor.DetectionResult,
) -> np.ndarray:
    for detection in detection_result.detections:
        coordinate = DetectionCoordinate(detection)

        cv2.rectangle(image, coordinate.start_point.tuple, coordinate.end_point.tuple, TEXT_COLOR, FONT_THICKNESS)
        cv2.line(
            image,
            pt1=(FRAME_WIDTH_HALF, FRAME_HEIGHT_HALF),
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
