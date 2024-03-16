import asyncio
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
        return xcenter - self.camera.center["x"] < 10 and ycenter - self.camera.center["y"] < 10

    def __is_fully_centered(self) -> bool:
        if len(self.detect_history) < 1:
            return False
        for object in self.detect_history:
            box = object[0]["box"]
            ymin = int(max(1, (box[0] * self.camera.height)))
            xmin = int(max(1, (box[1] * self.camera.width)))
            ymax = int(min(self.camera.height, (box[2] * self.camera.height)))
            xmax = int(min(self.camera.width, (box[3] * self.camera.width)))
            ycenter = (ymin + ymax) // 2
            xcenter = (xmin + xmax) // 2
            if self.__centered(xcenter, ycenter):
                continue
            else:
                return False
        return True

    def __detect_targets(self) -> list[DetectionObject]:
        _, frame = self.camera.device.read()
        decisions = self.detector.detect(frame)

        targets = [target for target in decisions["detection_result"] if target["label"] == "bird"]

        return targets

    async def search(self) -> bool:
        """カラスを探す

        Returns:
            bool: True: カラスを見つけた, False: カラスを見つけられなかった
        """
        print("探索モード: カラスを探しています...")
        motor_task = asyncio.create_task(self.motor.search())
        while motor_task.done() is False:
            targets = self.__detect_targets()
            self.__put_detect_history(targets)
            if self.__is_fully_detected():
                motor_task.cancel()
                self.detect_history.clear()
                return True
            await asyncio.sleep(0.5)
        return False

    async def track(self) -> bool:
        """カラスを追跡する

        Returns:
            bool: True: カラスを中心に捉えた, False: カラスを見失った
        """
        print("追跡モード: カラスを追跡しています...")

        while True:
            targets = self.__detect_targets()
            self.detect_history.append(targets)
            if len(self.detect_history) > DETECT_HISTORY_LENGTH * 2:
                break
            if len(self.detect_history) > DETECT_HISTORY_LENGTH:
                if self.__is_fully_centered():
                    return True
            # TODO: カラスの位置を算出する
            target_x = targets[0]["box"][1]
            motor_task = asyncio.create_task(self.motor.track(target_x, 0))
            await motor_task
            await asyncio.sleep(0.3)

        return False

    async def shoot(self):
        print("射撃モード: カラスを狙っています...")
        motor_task = asyncio.create_task(self.motor.shoot())
        await motor_task

        print("カラスを撃ちました")
        return 1

    def quit(self):
        print("終了します...")
