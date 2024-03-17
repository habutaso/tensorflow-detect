import time
from transitions import Machine

from detector.detector import Detector
from devices.camera import Camera
from machine.states import States
from detector.detector import DetectionObject
from .karasu_motor import KarasuMotor


DETECT_HISTORY_LENGTH = 5


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
    def __init__(self, detector: Detector, camera: Camera, motor: KarasuMotor):
        self.machine = Machine(model=self, states=States.states_list, transitions=transitions, initial=States.initial)
        self.detector = detector
        self.detect_history: list[list[DetectionObject]] = []
        self.camera = camera
        self.motor = motor

    def __put_detect_history(self, objects: list[DetectionObject]):
        if len(self.detect_history) > DETECT_HISTORY_LENGTH:
            self.detect_history.pop(0)
        self.detect_history.append(objects)

    def __is_fully_detected(self) -> bool:
        return len(self.detect_history) > DETECT_HISTORY_LENGTH and all(self.detect_history)

    def __centered(self, xcenter: int, ycenter: int) -> bool:
        return abs(xcenter - self.camera.center["x"]) < 50  # and ycenter - self.camera.center["y"] < 50

    def __is_fully_centered(self) -> bool:
        if len(self.detect_history) < 1:
            return False
        for object in self.detect_history:
            if not object:
                return False
            box = object[0]["box"]
            ymin = int(max(1, (box[0] * self.detector.image_height)))
            xmin = int(max(1, (box[1] * self.detector.image_width)))
            ymax = int(min(self.detector.image_height, (box[2] * self.detector.image_height)))
            xmax = int(min(self.detector.image_width, (box[3] * self.detector.image_width)))
            ycenter = (ymin + ymax) // 2
            xcenter = (xmin + xmax) // 2
            if self.__centered(xcenter, ycenter):
                continue
            else:
                return False
        return True

    def __detect_targets(self, preview_mode: States) -> list[DetectionObject]:
        _, frame = self.camera.device.read()
        decisions = self.detector.detect(frame, preview_mode=preview_mode)

        targets = [target for target in decisions["detection_result"] if target["label"] == "bird"]
        print(f"カラスを検出しました: {len(targets)}")

        return targets

    def search(self) -> bool:
        """カラスを探す

        Returns:
            bool: True: カラスを見つけた, False: カラスを見つけられなかった
        """
        count = 0

        while count < 9:
            print("探索モード: カラスを探しています...")
            count = self.motor.search(search_count=count)
            targets = self.__detect_targets(preview_mode=States.search)
            self.__put_detect_history(targets)
            if self.__is_fully_detected():
                self.detect_history.clear()
                return True
            time.sleep(0.5)
        return False

    def track(self) -> bool:
        """カラスを追跡する

        Returns:
            bool: True: カラスを中心に捉えた, False: カラスを見失った
        """
        print("追跡モード: カラスを追跡しています...")
        self.detect_history.clear()

        while True:
            targets = self.__detect_targets(preview_mode=States.tracking)
            self.__put_detect_history(targets)
            if len(self.detect_history) == DETECT_HISTORY_LENGTH:
                if self.__is_fully_centered():
                    return True
                else:
                    break
            # TODO: カラスの位置を算出する
            print("カラスの位置を算出しています...")
            if not targets:
                continue
            box = targets[0]["box"]
            xmin = int(max(1, (box[1] * self.detector.image_width)))
            xmax = int(min(self.detector.image_width, (box[3] * self.detector.image_width)))
            target_x = (xmin + xmax) // 2
            print(f"カラスの位置: {target_x}")
            self.motor.track(target_x, 0)

            time.sleep(0.2)

        return False

    def shoot(self):
        print("射撃モード: カラスを狙っています...")
        self.motor.shoot()

        print("カラスを撃ちました")
        return True

    def quit(self):
        print("終了します...")
