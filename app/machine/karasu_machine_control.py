from machine.states import States
from machine.karasu_mashine import KarasuMachine


class KarasuMachineControl:
    def __init__(self, machine: KarasuMachine):
        self.machine = machine
        self.machine.initialize_done()

    def crow_detected(self):
        self.machine.crow_detected()

    def main_process(self):
        while True:
            if self.machine.state == States.search:
                result = self.machine.search()

                if result == 1:
                    print("見つかりました")
                    self.crow_detected()
                else:
                    print("見つかりませんでした")
                    self.machine.no_crow_detected()
            elif self.machine.state == States.tracking:
                result = self.machine.track()

                if result == 1:
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
