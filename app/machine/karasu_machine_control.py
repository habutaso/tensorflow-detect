import asyncio

from machine.states import States
from machine.karasu_detector import KarasuDetector
from detector.detector import DetectionObject


class KarasuMachineControl:
    def __init__(self, machine: KarasuDetector):
        self.machine = machine
        self.machine.initialize_done()

    async def main_process(self):
        while True:
            if self.machine.state == States.search:

                result = await self.machine.search()

                if result:
                    print("見つかりました")
                    self.machine.crow_detected()
                else:
                    print("見つかりませんでした")
                    self.machine.no_crow_detected()
            elif self.machine.state == States.tracking:
                result = await self.machine.track()

                if result:
                    print("カラスを捕らえました")
                    self.machine.caught_crow()
                else:
                    print("カラスを見失いました")
                    self.machine.lose_sight_of_crow()

            elif self.machine.state == States.shooting:
                result = await self.machine.shoot()

                if result == 1:
                    print("射撃完了")
                    self.machine.shooting_done()
