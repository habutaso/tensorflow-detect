try:
    import RPi.GPIO as GPIO
except ImportError:
    import Mock.GPIO as GPIO

class Motor:
    def __init__(self, pin):
        self.pin = pin

    def start(self):
        print(f"Motor started on pin {self.pin}")

    def stop(self):
        print(f"Motor stopped on pin {self.pin}")