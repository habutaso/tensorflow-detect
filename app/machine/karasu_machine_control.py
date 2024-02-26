import multiprocessing
from machine.states import States
from app.machine.karasu_detector import KarasuDetector
from detector.detector import DetectionObject


class KarasuMachineControl:
    def __init__(self, machine: KarasuDetector):
        self.machine = machine
        self.detect_history: list[list[DetectionObject]] = []
        self.machine.initialize_done()
    
    def __put_detect_history(self, objects: list[DetectionObject]):
        if len(self.detect_history) > 5:
            self.detect_history.pop(0)
        self.detect_history.append(objects)
    
    def __all_detected(self) -> bool:
        return all(self.detect_history)
    
    def main_process(self):
        while True:
            if self.machine.state == States.search:
                self.__put_detect_history(self.machine.search())

                if self.__all_detected():
                    print("見つかりました")
                    self.machine.crow_detected()
                else:
                    print("見つかりませんでした")
                    self.machine.no_crow_detected()
            elif self.machine.state == States.tracking:
                result = self.machine.track()

                if result:
                    print("カラスを見失いました")
                    self.machine.lose_sight_of_crow()
                else:
                    print("カラスを捕らえました")
                    self.machine.caught_crow()

            elif self.machine.state == States.shooting:
                result = self.machine.shoot()

                if result == 1:
                    print("射撃完了")
                    self.machine.shooting_done()
