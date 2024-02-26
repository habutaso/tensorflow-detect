import time
import random

from transitions import Machine

from detector.detector import Detector
from devices.camera import Camera
from machine.states import States
from detector.detector import DetectionObject


def random_number():
    return random.randint(0, 10)


transitions = [
    {"trigger": "initialize_done", "source": States.initial, "dest": States.search, "after": "search"},
    {"trigger": "no_crow_detected", "source": States.search, "dest": States.search, "after": "search"},
    {"trigger": "crow_detected", "source": States.search, "dest": States.tracking, "after": "track"},
    {"trigger": "lose_sight_of_crow", "source": States.tracking, "dest": States.search, "after": "search"},
    {"trigger": "caught_crow", "source": States.tracking, "dest": States.shooting, "after": "shoot"},
    {"trigger": "continue_tracking", "source": States.tracking, "dest": States.tracking, "after": "track"},
    {"trigger": "shooting_done", "source": States.shooting, "dest": States.search, "after": "search"},
    {"trigger": "abort", "source": "*", "dest": States.quit},  # '*'は全ての状態から遷移可能を意味する
]


class KarasuDetector:
    def __init__(self, detector: Detector, camera: Camera):
        self.machine = Machine(model=self, states=States.states_list, transitions=transitions, initial=States.initial)
        self.detector = detector
        self.camera = camera

    def __detect_targets(self) -> list[DetectionObject]:
        _, frame = self.camera.device.read()
        decisions = self.detector.detect(frame)

        targets = [target for target in decisions["detection_result"] if target["label"] == "bird"]

        return targets

    def search(self):
        print("探索モード: カラスを探しています...")

        return self.__detect_targets()

    def track(self):
        print("追跡モード: カラスを追跡しています...")

        return self.__detect_targets()

    def shoot(self):
        print("射撃モード: カラスを狙っています...")

        time.sleep(2)
        print("カラスを撃ちました")
        return 1

    def quit(self):
        print("終了します...")
