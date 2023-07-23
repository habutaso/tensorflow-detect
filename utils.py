import time
from dataclasses import dataclass
from typing import Tuple

import cv2
import numpy as np
from tflite_support.task import processor


MARGIN = 10
ROW_SIZE = 10
FONT_SIZE = 1
FONT_THICKNESS = 2
TEXT_COLOR = (255, 255, 0)  # cyan

FPS_COUNT = 10
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


def visualize(
    image: np.ndarray,
    detection_result: processor.DetectionResult,
) -> np.ndarray:
    for detection in detection_result.detections:
        coordinate = DetectionCoordinate(detection)

        cv2.rectangle(image, coordinate.start_point.tuple, coordinate.end_point.tuple, TEXT_COLOR, FONT_THICKNESS)

        category = detection.categories[0]
        category_name = category.category_name
        prob = round(category.score, 2)

        text = f"{category_name}({str(prob)})"

        location = (MARGIN + coordinate.origin_x, MARGIN + ROW_SIZE + coordinate.origin_y)

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

    location = (MARGIN, ROW_SIZE)

    cv2.putText(image, fps_text, location, cv2.FONT_HERSHEY_PLAIN, FONT_SIZE, TEXT_COLOR, FONT_THICKNESS)

    return image
