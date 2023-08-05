from dataclasses import dataclass
from typing import Tuple

from tflite_support.task import processor


@dataclass
class Coordinate:
    x: int
    y: int

    @property
    def tuple(self) -> Tuple[int, int]:
        return self.x, self.y


class DetectionCoordinate:
    def __init__(self, detection: processor.Detection, frame_gravity: Tuple[int, int]):
        self.detection = detection
        self.box = self.detection.bounding_box
        self.frame_gravity = Coordinate(x=frame_gravity[0], y=frame_gravity[1])

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
        diff_x = gravity.x - self.frame_gravity.x
        diff_y = gravity.y - self.frame_gravity.y
        return Coordinate(x=diff_x, y=diff_y)
